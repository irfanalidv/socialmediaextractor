<div align="center">

# socialmediaextractor

**Find a website's social media profiles in one call, without picking up share buttons.**

[![PyPI](https://img.shields.io/pypi/v/socialmediaextractor?color=3fb950&label=PyPI)](https://pypi.org/project/socialmediaextractor/)
[![Python](https://img.shields.io/pypi/pyversions/socialmediaextractor)](https://pypi.org/project/socialmediaextractor/)
[![Tests](https://github.com/irfanalidv/socialmediaextractor/actions/workflows/tests.yml/badge.svg)](https://github.com/irfanalidv/socialmediaextractor/actions/workflows/tests.yml)
[![Downloads](https://static.pepy.tech/badge/socialmediaextractor)](https://pepy.tech/project/socialmediaextractor)
[![License: MIT](https://img.shields.io/github/license/irfanalidv/socialmediaextractor)](https://github.com/irfanalidv/socialmediaextractor/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

</div>

`socialmediaextractor` fetches a web page and returns the organization's profile links on
**X/Twitter, LinkedIn, Instagram, Facebook, YouTube, TikTok, GitHub, Threads and Bluesky**.

## Why socialmediaextractor?

A plain "does the link contain `twitter.com`?" check also matches share buttons
(`twitter.com/intent/tweet`), single posts, embeds and look-alike domains. This library uses
per-platform URL rules instead, so you get account and profile URLs only.

## Features

- Covers 9 platforms. `twitter.com` and `x.com` are both reported under `Twitter`, and `X` is
  accepted as an alias.
- Reads `<a href>`, `<link href>` (for example `rel="me"`) and JSON-LD `sameAs` declarations.
- Skips share, intent and dialog URLs, posts, reels, videos, embeds, GitHub issue pages,
  site-navigation pages and look-alike hosts.
- Resolves relative and protocol-relative (`//facebook.com/...`) links.
- Can return only the first link per platform or every distinct link (`extract_all_social_links`).
- Works on HTML you already have, so it fits into existing crawlers.
- Includes a `socialmediaextractor` command, type hints (`py.typed`) and clear errors
  (`SocialMediaExtractorError`).

## Installation

```bash
pip install socialmediaextractor
```

Requires Python 3.10+. Dependencies: `requests` and `beautifulsoup4`.

## Quick start

```python
from socialmediaextractor import extract_social_media_accounts

links = extract_social_media_accounts("https://www.djangoproject.com")
print(links)
```

Output (run on 2026-10-31):

```python
{'Facebook': None,
 'LinkedIn': 'https://www.linkedin.com/company/django-software-foundation',
 'Twitter': 'https://x.com/djangoproject',
 'Instagram': None,
 'YouTube': None,
 'TikTok': None,
 'GitHub': 'https://github.com/django/django',
 'Threads': None,
 'Bluesky': 'https://bsky.app/profile/djangoproject.com'}
```

Every platform key is always present. Platforms with no link found are `None`.

### Only some platforms

```python
extract_social_media_accounts("https://example.com", platforms=["LinkedIn", "X"])
# {'LinkedIn': ..., 'Twitter': ...}
```

### HTML you already fetched

```python
from socialmediaextractor import extract_social_links_from_html, extract_all_social_links

first = extract_social_links_from_html(html, base_url="https://example.com/")
every = extract_all_social_links(html, base_url="https://example.com/")  # dict[str, list[str]]
```

### Classify a single URL

```python
from socialmediaextractor import classify_url

classify_url("https://x.com/github")                       # 'Twitter'
classify_url("https://twitter.com/intent/tweet?text=hi")   # None
```

### Command line

```bash
socialmediaextractor https://www.python.org
socialmediaextractor https://www.mozilla.org --all -p Bluesky -p Instagram
socialmediaextractor site-a.com site-b.com      # several URLs -> one JSON object keyed by URL
```

The command prints JSON to stdout and exits with code `1` if any URL fails.

## Use cases

- **Lead enrichment:** add social profiles to a list of company domains.
- **Brand monitoring:** check which networks a competitor is active on.
- **Data hygiene:** confirm that your own site links to the right profiles.
- **Crawlers:** call `extract_social_links_from_html` on pages you have already downloaded.

## API overview

| Function | Returns |
| --- | --- |
| `extract_social_media_accounts(url, *, platforms=None, timeout=15.0, session=None)` | Fetches `url`; `dict[str, str \| None]` with the first profile link per platform. |
| `extract_social_links_from_html(html, base_url=None, *, platforms=None)` | Same, from an HTML string. |
| `extract_all_social_links(html, base_url=None, *, platforms=None)` | `dict[str, list[str]]` with every distinct profile link. |
| `classify_url(url)` | Platform name or `None`. |
| `fetch_html(url, *, timeout=15.0, session=None)` | `(html, final_url)`; raises `SocialMediaExtractorError`. |
| `PLATFORMS` | The `Platform` rules (name, hosts, path regex) used for matching. |

### Upgrading from 0.x

- `from socialmediaextractor import extract_social_media_accounts` works again. The 0.2 to 0.4
  wheels on PyPI shipped without any Python code, so the import failed.
- The `Facebook`, `LinkedIn` and `Twitter` keys are unchanged. Six new platform keys were added,
  and `Twitter` now also matches `x.com`.
- Share buttons and other non-profile links are no longer returned.
- Network and HTTP errors now raise `SocialMediaExtractorError`. Before, an error page was
  silently parsed.

## Contributing

Pull requests are welcome. See [CONTRIBUTING.md](https://github.com/irfanalidv/socialmediaextractor/blob/main/CONTRIBUTING.md).

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check . && pytest
```

The tests run offline against saved HTML fixtures in `tests/fixtures/`. To add a platform, add a
`Platform` entry in `socialmediaextractor/extractor.py` along with fixture cases.

## License

MIT. See [LICENSE](https://github.com/irfanalidv/socialmediaextractor/blob/main/LICENSE).
