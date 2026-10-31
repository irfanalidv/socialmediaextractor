"""URL triage: label a list of URLs (backlinks, CRM fields, analytics referrers) by platform.

Shows: ``classify_url``, which tells profile URLs apart from posts, share intents and
non-social pages without fetching anything.
Needs: only the package (offline). Reads ``examples/data/urls.txt`` or a file you pass.

Run: python examples/classify_url_list.py [urls.txt]
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from socialmediaextractor import classify_url

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "data" / "urls.txt"
urls = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

counts: Counter[str] = Counter()
for url in urls:
    platform = classify_url(url) or "(not a profile)"
    counts[platform] += 1
    print(f"{platform:<16} {url}")

print("\nCounts:", dict(counts))
