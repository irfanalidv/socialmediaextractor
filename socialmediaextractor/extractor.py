"""Find a website's social media profile links.

Links are collected from JSON-LD ``sameAs`` entries, ``<link href>`` (for example
``rel="me"``) and ``<a href>``, then matched against per-platform rules that accept
profile/account URLs and reject share buttons, intents, posts and other non-profile
links.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

__all__ = [
    "DEFAULT_HEADERS",
    "PLATFORMS",
    "Platform",
    "SocialMediaExtractorError",
    "classify_url",
    "extract_all_social_links",
    "extract_social_links_from_html",
    "extract_social_media_accounts",
    "fetch_html",
    "iter_candidate_urls",
]

DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; socialmediaextractor; "
        "+https://github.com/irfanalidv/socialmediaextractor)"
    ),
    "Accept": "text/html,application/xhtml+xml",
}


class SocialMediaExtractorError(RuntimeError):
    """Raised when a page cannot be fetched."""


@dataclass(frozen=True)
class Platform:
    """Matching rule for one social network.

    Attributes:
        name: Key used in the result dict (for example ``"LinkedIn"``).
        hosts: Registrable domains; subdomains such as ``www.`` or ``m.`` also match.
        path: Regex that a profile URL's path must fully match (case-insensitive).
        exclude_first_segment: First path segments that are never profiles.
    """

    name: str
    hosts: tuple[str, ...]
    path: str
    exclude_first_segment: frozenset[str] = frozenset()

    def matches(self, url: str) -> bool:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if not any(host == h or host.endswith("." + h) for h in self.hosts):
            return False
        path = parsed.path.rstrip("/") or "/"
        first = path.strip("/").split("/", 1)[0].lower()
        if first in self.exclude_first_segment:
            return False
        return re.fullmatch(self.path, path, flags=re.IGNORECASE) is not None


_SEG = r"[A-Za-z0-9_.\-%]+"

PLATFORMS: tuple[Platform, ...] = (
    Platform(
        "Facebook",
        ("facebook.com", "fb.com", "fb.me"),
        rf"/(?:pg/)?{_SEG}(?:/)?|/profile\.php|/people/{_SEG}/\d+",
        frozenset(
            {
                "sharer",
                "sharer.php",
                "share",
                "share.php",
                "dialog",
                "plugins",
                "tr",
                "login",
                "login.php",
                "privacy",
                "policies",
                "help",
                "events",
                "groups",
                "hashtag",
                "watch",
                "photo.php",
                "story.php",
                "permalink.php",
                "legal",
                "business",
                "ads",
                "home.php",
            }
        ),
    ),
    Platform(
        "LinkedIn",
        ("linkedin.com",),
        rf"/(?:company|in|school|showcase)/{_SEG}(?:/.*)?",
    ),
    Platform(
        "Twitter",
        ("twitter.com", "x.com"),
        r"/[A-Za-z0-9_]{1,15}",
        frozenset(
            {
                "intent",
                "share",
                "home",
                "hashtag",
                "search",
                "i",
                "explore",
                "login",
                "signup",
                "tos",
                "privacy",
                "settings",
                "notifications",
                "messages",
            }
        ),
    ),
    Platform(
        "Instagram",
        ("instagram.com", "instagr.am"),
        r"/[A-Za-z0-9_.]{1,30}",
        frozenset(
            {
                "p",
                "reel",
                "reels",
                "explore",
                "accounts",
                "stories",
                "tv",
                "about",
                "legal",
                "direct",
            }
        ),
    ),
    Platform(
        "YouTube",
        ("youtube.com",),
        rf"/(?:@{_SEG}|(?:channel|c|user)/{_SEG})(?:/.*)?",
    ),
    Platform(
        "TikTok",
        ("tiktok.com",),
        r"/@[A-Za-z0-9_.]{1,24}",
    ),
    Platform(
        "GitHub",
        ("github.com",),
        r"/[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})(?:/[A-Za-z0-9_.\-]+)?",
        frozenset(
            {
                "features",
                "login",
                "join",
                "signup",
                "about",
                "pricing",
                "enterprise",
                "marketplace",
                "explore",
                "topics",
                "collections",
                "trending",
                "sponsors",
                "settings",
                "orgs",
                "site",
                "security",
                "customer-stories",
                "readme",
                "team",
                "contact",
                "apps",
                "search",
                "notifications",
                "new",
            }
        ),
    ),
    Platform(
        "Threads",
        ("threads.net", "threads.com"),
        r"/@[A-Za-z0-9_.]{1,30}",
    ),
    Platform(
        "Bluesky",
        ("bsky.app",),
        r"/profile/[A-Za-z0-9.\-:]+",
    ),
)

_BY_NAME = {p.name.lower(): p for p in PLATFORMS}
_ALIASES = {"x": "twitter", "x (twitter)": "twitter"}


def _select(platforms: Iterable[str] | None) -> tuple[Platform, ...]:
    if platforms is None:
        return PLATFORMS
    selected = []
    for name in platforms:
        key = _ALIASES.get(name.lower(), name.lower())
        if key not in _BY_NAME:
            known = ", ".join(p.name for p in PLATFORMS)
            raise ValueError(f"unknown platform {name!r}; known platforms: {known}")
        selected.append(_BY_NAME[key])
    return tuple(selected)


def _normalize(href: str, base_url: str | None) -> str | None:
    href = href.strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    if href.startswith("//"):
        href = "https:" + href
    elif base_url:
        href = urljoin(base_url, href)
    elif "://" not in href and re.match(r"^(?:www\.)?[a-z0-9.-]+\.[a-z]{2,}/", href, re.I):
        href = "https://" + href
    parsed = urlparse(href)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return href


def _same_as(node: Any) -> Iterator[str]:
    if isinstance(node, dict):
        value = node.get("sameAs")
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            yield from (v for v in value if isinstance(v, str))
        for child in node.values():
            if isinstance(child, (dict, list)):
                yield from _same_as(child)
    elif isinstance(node, list):
        for child in node:
            yield from _same_as(child)


def iter_candidate_urls(html: str, base_url: str | None = None) -> Iterator[str]:
    """Yield absolute http(s) URLs found in a page.

    Sources are yielded in order of how deliberately they declare an identity:
    JSON-LD ``sameAs`` first, then ``<link href>`` (e.g. ``rel="me"``), then ``<a href>``.
    """
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except json.JSONDecodeError:
            continue
        for value in _same_as(data):
            url = _normalize(value, base_url)
            if url:
                yield url
    for tag_name in ("link", "a"):
        for tag in soup.find_all(tag_name, href=True):
            url = _normalize(str(tag["href"]), base_url)
            if url:
                yield url


def classify_url(url: str) -> str | None:
    """Return the platform name for a social profile URL, or ``None``.

    >>> classify_url("https://x.com/github")
    'Twitter'
    >>> classify_url("https://twitter.com/intent/tweet?text=hi") is None
    True
    """
    url = _normalize(url, None) or ""
    for platform in PLATFORMS:
        if platform.matches(url):
            return platform.name
    return None


def extract_all_social_links(
    html: str,
    base_url: str | None = None,
    *,
    platforms: Iterable[str] | None = None,
) -> dict[str, list[str]]:
    """Return every distinct profile link per platform, in page order."""
    selected = _select(platforms)
    found: dict[str, list[str]] = {p.name: [] for p in selected}
    for url in iter_candidate_urls(html, base_url):
        for platform in selected:
            if platform.matches(url):
                if url not in found[platform.name]:
                    found[platform.name].append(url)
                break
    return found


def extract_social_links_from_html(
    html: str,
    base_url: str | None = None,
    *,
    platforms: Iterable[str] | None = None,
) -> dict[str, str | None]:
    """Return the first profile link per platform (``None`` when none is found)."""
    return {
        name: (links[0] if links else None)
        for name, links in extract_all_social_links(html, base_url, platforms=platforms).items()
    }


def fetch_html(
    url: str,
    *,
    timeout: float = 15.0,
    session: requests.Session | None = None,
) -> tuple[str, str]:
    """Fetch ``url`` and return ``(html, final_url)`` after redirects.

    Raises:
        SocialMediaExtractorError: on network errors or HTTP error status codes.
    """
    if "://" not in url:
        url = "https://" + url
    getter = session.get if session is not None else requests.get
    try:
        resp = getter(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise SocialMediaExtractorError(f"could not fetch {url}: {exc}") from exc
    return resp.text, str(getattr(resp, "url", None) or url)


def extract_social_media_accounts(
    url: str,
    *,
    platforms: Iterable[str] | None = None,
    timeout: float = 15.0,
    session: requests.Session | None = None,
) -> dict[str, str | None]:
    """Fetch a website and return its social media profile links.

    Args:
        url: Website URL (``https://`` is added if the scheme is missing).
        platforms: Restrict the result to these platform names, for example
            ``["LinkedIn", "X"]``. ``"X"`` is an alias for ``"Twitter"``.
        timeout: Request timeout in seconds.
        session: Optional ``requests.Session`` to reuse.

    Returns:
        A dict mapping each platform name to the first profile URL found, or ``None``.

    Raises:
        SocialMediaExtractorError: the page could not be fetched.
        ValueError: an unknown platform name was given.
    """
    selected = _select(platforms)
    html, final_url = fetch_html(url, timeout=timeout, session=session)
    return extract_social_links_from_html(html, final_url, platforms=[p.name for p in selected])
