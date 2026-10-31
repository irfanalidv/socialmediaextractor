"""Shared helper for the examples: a fake ``requests.Session`` that serves bundled pages.

``extract_social_media_accounts(..., session=...)`` accepts any object with a ``get`` method
that returns a ``requests``-like response, which makes offline runs and tests easy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

DATA = Path(__file__).resolve().parent / "data"


@dataclass
class _Response:
    text: str
    url: str
    status_code: int = 200

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"{self.status_code} for {self.url}")


class BundledPages:
    """Serve ``data/<name>.html`` for ``https://<name>.example``; 404 otherwise."""

    def get(self, url: str, **_: Any) -> _Response:
        host = urlparse(url).hostname or ""
        page = DATA / f"{host.removesuffix('.example')}.html"
        if host.endswith(".example") and page.is_file():
            return _Response(page.read_text(encoding="utf-8"), url)
        return _Response("", url, status_code=404)
