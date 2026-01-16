#!/usr/bin/env python3
"""Update script - orchestrates feed fetching and database updates.

Usage:
    uv run python scripts/update.py

This script runs the update pipeline:
1. Fetch RSS feeds and save to JSON (update_feed.py)
2. Process feeds and update SQLite database (update_db.py)
"""

import subprocess
import sys


def main() -> None:
    """Run the update pipeline."""
    # Step 1: Fetch RSS feeds
    print("Step 1: Fetching RSS feeds...")
    result = subprocess.run([sys.executable, "scripts/update_feed.py"], check=False)
    if result.returncode != 0:
        print("Feed update failed")
        sys.exit(1)

    # Step 2: Process feeds and update database
    print("Step 2: Processing feeds and updating database...")
    result = subprocess.run([sys.executable, "scripts/update_db.py"], check=False)
    if result.returncode != 0:
        print("Database update failed")
        sys.exit(1)

    print("Update complete")


if __name__ == "__main__":
    main()
