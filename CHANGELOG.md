# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-10-31

### Fixed
- A single malformed or deeply nested JSON-LD block raised `RecursionError` and aborted
  extraction for the whole page. Such blocks are now skipped (logged at `DEBUG`), and the
  `sameAs` walk is iterative.
- The CLI validates `--platform` names before fetching anything and exits with code 2 and a
  clear message, instead of reporting the same error once per URL.

### Changed
- `extract_all_social_links` reports each account once: links that differ only in scheme,
  `www.`/`m.` subdomain, alias domain (`twitter.com` vs `x.com`), letter case, trailing slash
  or `utm_*` parameters are collapsed, keeping the first spelling on the page.
- Stricter linting (ruff `C4`, `PTH`, `RET`, `PIE`) and a mypy configuration; the package
  type-checks cleanly.
- CI runs ruff, ruff format, mypy and pytest with a 100% coverage gate on Python 3.10 to 3.13
  using `uv`, with concurrency cancellation. Added CodeQL analysis and pre-commit hooks.
- README rewritten: architecture diagram, configuration and API tables, limitations.

### Added
- Offline examples: `quickstart.py`, `enrich_leads_csv.py`, `audit_brand_links.py`,
  `classify_url_list.py`, with bundled sample pages.

## [1.0.0] - 2026-10-31

### Fixed
- **Packaging:** the 0.2 to 0.4 wheels on PyPI contained no Python code, because the module
  sat at the repo root as `__init__.py` and `find_packages()` found nothing. As a result
  `from socialmediaextractor import extract_social_media_accounts` failed after `pip install`.
  The code now lives in a real `socialmediaextractor/` package.
- Share buttons and intents (`facebook.com/sharer`, `twitter.com/intent`,
  `linkedin.com/shareArticle`, ...) are no longer reported as profiles.
- Look-alike domains (for example `notfacebook.com`) no longer match.
- HTTP errors and network failures raise `SocialMediaExtractorError` instead of the error page
  being parsed silently. Requests now have a timeout.

### Added
- New platforms: Instagram, YouTube, TikTok, GitHub, Threads and Bluesky. `Twitter` also
  matches `x.com`, and `X` is accepted as an alias.
- Links are also read from JSON-LD `sameAs` and `<link rel="me">`. Relative and
  protocol-relative URLs are resolved.
- `extract_social_links_from_html`, `extract_all_social_links`, `classify_url`, `fetch_html`
  and the `PLATFORMS` rule table. A `platforms=` filter, plus `timeout=` and `session=` options.
- `socialmediaextractor` CLI with JSON output.
- `__version__`, `py.typed`, type hints, an offline pytest suite with HTML fixtures, and CI on
  Python 3.10 to 3.13 with ruff.
- `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CITATION.cff`, issue/PR templates and
  Dependabot.

### Changed
- Python 3.10+ required. Packaging moved to `pyproject.toml` (PEP 639 license metadata).
  `setup.py` and the committed `dist/` archives were removed.

## [0.4] - 2024-04-18

- Last 0.x release.
