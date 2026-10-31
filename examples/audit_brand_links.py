"""Brand-link audit: check which official profiles a website links to, and spot problems.

Shows: ``extract_all_social_links`` to find missing platforms and platforms with more than
one distinct account linked (often an old or regional account), plus legacy ``twitter.com``
links that could be updated to ``x.com``.
Needs: only the package (offline). Audits the bundled pages in ``examples/data``.

Run: python examples/audit_brand_links.py
"""

from __future__ import annotations

from pathlib import Path

from socialmediaextractor import classify_url, extract_all_social_links, iter_candidate_urls

DATA = Path(__file__).resolve().parent / "data"
EXPECTED = ["LinkedIn", "Twitter", "Instagram", "YouTube"]


def audit(name: str, html: str) -> list[str]:
    links = extract_all_social_links(html, f"https://{name}.example/")
    issues = [f"missing {p}" for p in EXPECTED if not links[p]]
    issues += [
        f"{len(urls)} different {p} accounts: {', '.join(urls)}"
        for p, urls in links.items()
        if len(urls) > 1
    ]
    # Check raw candidates: the deduplicated result may already have collapsed
    # twitter.com/acme into an x.com/acme link found earlier on the page.
    issues += [
        f"legacy twitter.com link: {u}"
        for u in dict.fromkeys(iter_candidate_urls(html))
        if "twitter.com" in u and classify_url(u) == "Twitter"
    ]
    return issues


def main() -> None:
    for page in sorted(DATA.glob("*.html")):
        issues = audit(page.stem, page.read_text(encoding="utf-8"))
        print(f"{page.stem}: {'OK' if not issues else f'{len(issues)} issue(s)'}")
        for issue in issues:
            print(f"  - {issue}")


if __name__ == "__main__":
    main()
