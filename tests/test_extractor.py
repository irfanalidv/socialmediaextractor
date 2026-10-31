from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest
import requests

import socialmediaextractor as sme
from socialmediaextractor import cli, extractor

FIXTURES = Path(__file__).parent / "fixtures"
ALL_PLATFORMS = [
    "Facebook",
    "LinkedIn",
    "Twitter",
    "Instagram",
    "YouTube",
    "TikTok",
    "GitHub",
    "Threads",
    "Bluesky",
]


def load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200, url: str = "https://acme.example/"):
        self.text = text
        self.status_code = status_code
        self.url = url

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_version_and_exports():
    assert sme.__version__
    for name in sme.__all__:
        assert hasattr(sme, name)
    assert [p.name for p in sme.PLATFORMS] == ALL_PLATFORMS


def test_company_footer_first_links():
    result = sme.extract_social_links_from_html(
        load("company_footer.html"), "https://acme.example/"
    )
    assert result == {
        "Facebook": "https://www.facebook.com/AcmeCorp/",
        "LinkedIn": "https://www.linkedin.com/company/acme-corp/",
        "Twitter": "https://x.com/acmecorp",
        "Instagram": "https://www.instagram.com/acme.corp/",
        "YouTube": "https://www.youtube.com/@AcmeCorp",
        "TikTok": "https://www.tiktok.com/@acmecorp",
        "GitHub": "https://github.com/acme-corp",
        "Threads": "https://www.threads.net/@acme.corp",
        "Bluesky": "https://bsky.app/profile/acme.example",
    }


def test_company_footer_all_links():
    result = sme.extract_all_social_links(load("company_footer.html"))
    assert result["Twitter"] == ["https://x.com/acmecorp", "https://twitter.com/acmecorp_old"]
    assert result["Facebook"] == ["https://www.facebook.com/AcmeCorp/"]


def test_jsonld_same_as_and_protocol_relative():
    result = sme.extract_all_social_links(load("jsonld_sameas.html"), "https://globex.example/")
    assert result["Twitter"] == ["https://twitter.com/globex"]
    assert result["LinkedIn"] == [
        "https://www.linkedin.com/company/globex",
        "https://www.linkedin.com/in/jane-doe/",
    ]
    assert result["GitHub"] == ["https://github.com/globex"]
    assert result["Threads"] == ["https://www.threads.com/@globex"]
    assert result["TikTok"] == ["https://www.tiktok.com/@globex"]
    assert result["Facebook"] == ["https://www.facebook.com/globex"]
    assert result["YouTube"] == ["https://m.youtube.com/channel/UC1234567890abcdef"]
    assert result["Bluesky"] == ["https://bsky.app/profile/did:plc:abc123xyz"]
    assert result["Instagram"] == []


def test_share_buttons_and_lookalikes_are_ignored():
    result = sme.extract_social_links_from_html(load("share_buttons_only.html"))
    assert result == dict.fromkeys(ALL_PLATFORMS)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://twitter.com/python", "Twitter"),
        ("https://x.com/python", "Twitter"),
        ("https://x.com/python/status/123", None),
        ("https://twitter.com/home", None),
        ("https://www.facebook.com/profile.php?id=100", "Facebook"),
        ("https://www.facebook.com/people/Jane-Doe/100012345", "Facebook"),
        ("https://www.facebook.com/AcmeCorp/posts/1", None),
        ("https://www.linkedin.com/school/mit/", "LinkedIn"),
        ("https://www.linkedin.com/company/acme/about/", "LinkedIn"),
        ("https://www.linkedin.com/feed/", None),
        ("https://www.instagram.com/reel/abc/", None),
        ("https://www.youtube.com/c/Acme", "YouTube"),
        ("https://www.youtube.com/user/acme", "YouTube"),
        ("https://www.youtube.com/@acme/videos", "YouTube"),
        ("https://youtu.be/abc", None),
        ("https://www.tiktok.com/@acme/video/123", None),
        ("https://github.com/psf/requests", "GitHub"),
        ("https://github.com/psf/requests/issues/1", None),
        ("https://github.com/login", None),
        ("https://threads.net/@acme", "Threads"),
        ("https://bsky.app/profile/acme.bsky.social", "Bluesky"),
        ("www.linkedin.com/in/someone/", "LinkedIn"),
        ("https://example.com/twitter.com/acme", None),
        ("not a url", None),
    ],
)
def test_classify_url(url, expected):
    assert sme.classify_url(url) == expected


def test_platform_filter_and_alias():
    html = load("company_footer.html")
    assert sme.extract_social_links_from_html(html, platforms=["X", "github"]) == {
        "Twitter": "https://x.com/acmecorp",
        "GitHub": "https://github.com/acme-corp",
    }
    with pytest.raises(ValueError, match="unknown platform"):
        sme.extract_social_links_from_html(html, platforms=["MySpace"])


def test_relative_links_are_resolved_and_ignored():
    html = '<a href="/facebook.com/acme">x</a><a href="javascript:void(0)">y</a>'
    assert sme.extract_social_links_from_html(html, "https://acme.example/")["Facebook"] is None


def test_extract_social_media_accounts_fetches(monkeypatch):
    calls = []

    def fake_get(url, headers=None, timeout=None):
        calls.append((url, timeout))
        return FakeResponse(load("company_footer.html"))

    monkeypatch.setattr(extractor.requests, "get", fake_get)
    result = sme.extract_social_media_accounts("acme.example", timeout=5)
    assert calls == [("https://acme.example", 5)]
    assert result["LinkedIn"] == "https://www.linkedin.com/company/acme-corp/"
    assert list(result) == ALL_PLATFORMS


def test_legacy_keys_present_with_none(monkeypatch):
    monkeypatch.setattr(extractor.requests, "get", lambda *a, **k: FakeResponse("<html></html>"))
    result = sme.extract_social_media_accounts("https://example.com")
    assert result["Facebook"] is None and result["LinkedIn"] is None and result["Twitter"] is None


def test_http_error_raises(monkeypatch):
    monkeypatch.setattr(extractor.requests, "get", lambda *a, **k: FakeResponse("", 500))
    with pytest.raises(sme.SocialMediaExtractorError):
        sme.extract_social_media_accounts("https://example.com")


def test_network_error_raises(monkeypatch):
    def boom(*a, **k):
        raise requests.ConnectionError("unreachable")

    monkeypatch.setattr(extractor.requests, "get", boom)
    with pytest.raises(sme.SocialMediaExtractorError, match="unreachable"):
        sme.extract_social_media_accounts("https://example.com")


def test_session_is_used():
    session = mock.Mock(spec=requests.Session)
    session.get.return_value = FakeResponse(load("jsonld_sameas.html"))
    result = sme.extract_social_media_accounts("https://globex.example", session=session)
    assert result["GitHub"] == "https://github.com/globex"
    session.get.assert_called_once()


def test_cli_single_and_all(monkeypatch, capsys):
    monkeypatch.setattr(
        extractor.requests, "get", lambda *a, **k: FakeResponse(load("company_footer.html"))
    )
    assert cli.main(["https://acme.example", "-p", "X"]) == 0
    assert json.loads(capsys.readouterr().out) == {"Twitter": "https://x.com/acmecorp"}
    assert cli.main(["https://acme.example", "--all", "-p", "Twitter"]) == 0
    assert len(json.loads(capsys.readouterr().out)["Twitter"]) == 2


def test_cli_multiple_urls_with_error(monkeypatch, capsys):
    def fake_get(url, headers=None, timeout=None):
        if "bad" in url:
            raise requests.ConnectionError("nope")
        return FakeResponse(load("company_footer.html"))

    monkeypatch.setattr(extractor.requests, "get", fake_get)
    assert cli.main(["https://acme.example", "https://bad.example"]) == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["https://bad.example"] is None
    assert data["https://acme.example"]["GitHub"] == "https://github.com/acme-corp"
    assert "nope" in captured.err
