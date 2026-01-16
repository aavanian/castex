#!/usr/bin/env python3
"""Fetch and parse a single BBC episode for testing.

Usage:
    uv run python scripts/fetch_episode.py https://www.bbc.co.uk/programmes/p0054578
    uv run python scripts/fetch_episode.py p0054578
"""

import asyncio
import json
import sys

import httpx

from castex.scraper.bbc import parse_bbc_html

USER_AGENT = "CastexBot/1.0 (https://github.com/aavanian/castex) httpx/0.28"


async def fetch_episode(url: str) -> None:
    """Fetch and parse a single episode."""
    # Handle short form (just programme ID)
    if not url.startswith("http"):
        url = f"https://www.bbc.co.uk/programmes/{url}"

    print(f"Fetching: {url}", file=sys.stderr)

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        html = response.text

    result = parse_bbc_html(html)

    print(json.dumps(result, indent=2, ensure_ascii=False))


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/fetch_episode.py <url_or_programme_id>")
        sys.exit(1)

    asyncio.run(fetch_episode(sys.argv[1]))


if __name__ == "__main__":
    main()
