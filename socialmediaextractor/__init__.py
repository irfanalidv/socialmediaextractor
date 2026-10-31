"""socialmediaextractor: find a website's social media profile links."""

from importlib.metadata import PackageNotFoundError, version

from .extractor import (
    PLATFORMS,
    Platform,
    SocialMediaExtractorError,
    classify_url,
    extract_all_social_links,
    extract_social_links_from_html,
    extract_social_media_accounts,
    fetch_html,
    iter_candidate_urls,
)

try:
    __version__ = version("socialmediaextractor")
except PackageNotFoundError:  # pragma: no cover - running from a source checkout
    __version__ = "0.0.0"

__all__ = [
    "PLATFORMS",
    "Platform",
    "SocialMediaExtractorError",
    "__version__",
    "classify_url",
    "extract_all_social_links",
    "extract_social_links_from_html",
    "extract_social_media_accounts",
    "fetch_html",
    "iter_candidate_urls",
]
