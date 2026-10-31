"""Command-line interface: ``socialmediaextractor https://example.com [--all]``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from . import __version__
from .extractor import (
    PLATFORMS,
    SocialMediaExtractorError,
    extract_all_social_links,
    extract_social_links_from_html,
    fetch_html,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="socialmediaextractor",
        description="Print the social media profile links found on a web page as JSON.",
    )
    parser.add_argument("urls", nargs="+", help="one or more website URLs")
    parser.add_argument(
        "--all", action="store_true", help="list every profile link, not just the first"
    )
    parser.add_argument(
        "-p",
        "--platform",
        action="append",
        dest="platforms",
        metavar="NAME",
        help=f"limit to a platform (repeatable): {', '.join(p.name for p in PLATFORMS)}, X",
    )
    parser.add_argument("--timeout", type=float, default=15.0, help="seconds (default: 15)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    results: dict[str, object] = {}
    status = 0
    for url in args.urls:
        try:
            html, final_url = fetch_html(url, timeout=args.timeout)
            func = extract_all_social_links if args.all else extract_social_links_from_html
            results[url] = func(html, final_url, platforms=args.platforms)
        except (SocialMediaExtractorError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            results[url] = None
            status = 1
    out = results[args.urls[0]] if len(args.urls) == 1 else results
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return status


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
