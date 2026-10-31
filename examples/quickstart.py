"""Quick start: extract profile links from HTML you already have.

Shows: ``extract_social_links_from_html`` (first link per platform) and
``extract_all_social_links`` (every distinct link), and that share buttons are skipped.
Needs: only the package (offline). Uses ``examples/data/acme.html``.

Run: python examples/quickstart.py
"""

from __future__ import annotations

import json
from pathlib import Path

from socialmediaextractor import extract_all_social_links, extract_social_links_from_html

html = (Path(__file__).resolve().parent / "data" / "acme.html").read_text(encoding="utf-8")

first = extract_social_links_from_html(html, "https://acme.example/")
print("First link per platform:")
print(json.dumps(first, indent=2))

every = extract_all_social_links(html, "https://acme.example/", platforms=["X", "LinkedIn"])
print("\nAll X and LinkedIn links (share buttons and duplicate spellings removed):")
print(json.dumps(every, indent=2))
