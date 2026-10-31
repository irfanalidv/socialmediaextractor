# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
