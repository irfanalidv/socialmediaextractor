"""Lead enrichment: add social profile columns to a CSV of company websites.

Shows: ``extract_social_media_accounts`` over many sites with a shared session, a platform
filter, and per-site error handling (one bad site does not stop the batch).
Needs: offline by default (bundled pages in ``examples/data``). Pass ``--live`` to fetch the
real websites listed in your own CSV (network access required; respect each site's terms).

Run: python examples/enrich_leads_csv.py [companies.csv] [--live]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import requests

from socialmediaextractor import SocialMediaExtractorError, extract_social_media_accounts

DATA = Path(__file__).resolve().parent / "data"
PLATFORMS = ["LinkedIn", "X", "Facebook", "Instagram"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Add social profile columns to a CSV.")
    parser.add_argument("csv", nargs="?", type=Path, default=DATA / "companies.csv")
    parser.add_argument("--live", action="store_true", help="fetch real websites")
    args = parser.parse_args()

    if args.live:
        session: object = requests.Session()
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from _offline import BundledPages

        session = BundledPages()

    with args.csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    writer = csv.writer(sys.stdout)
    writer.writerow(["company", "website", *PLATFORMS, "error"])
    for row in rows:
        try:
            links = extract_social_media_accounts(
                row["website"],
                platforms=PLATFORMS,
                timeout=10,
                session=session,  # type: ignore[arg-type]
            )
            values, error = [links[p if p != "X" else "Twitter"] or "" for p in PLATFORMS], ""
        except SocialMediaExtractorError as exc:
            values, error = [""] * len(PLATFORMS), str(exc)
        writer.writerow([row["company"], row["website"], *values, error])


if __name__ == "__main__":
    main()
