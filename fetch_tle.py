"""
Local utility for retrieving two-line element sets (TLEs) from CelesTrak.

fetch_tle_lines() does the actual fetch and validation and returns the
parsed lines without touching disk. fetch_and_cache_tle() wraps it for
callers that want a cached file on disk. app.py's in-memory path calls
fetch_tle_lines() directly, so there is one fetch implementation, not two.
"""

import os
import requests

URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
DATA_DIR = "data"
FILE_PATH = os.path.join(DATA_DIR, "iss.txt")


def fetch_tle_lines(url=URL, timeout=10):
    """
    Fetch and validate a TLE from CelesTrak, returning (name, line1, line2).
    Does not touch disk; callers decide whether and where to cache it.
    Network requests include an explicit timeout to prevent process
    blocking during upstream API degradation.
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    clean_lines = [line.strip() for line in response.text.splitlines() if line.strip()]

    # Basic validation against payload corruption or HTML rate-limit pages
    if len(clean_lines) < 3 or not clean_lines[1].startswith("1 ") or not clean_lines[2].startswith("2 "):
        raise ValueError("Upstream response failed TLE structure validation.")

    return clean_lines[0], clean_lines[1], clean_lines[2]


def fetch_and_cache_tle(url=URL, save_path=FILE_PATH):
    """Fetch a TLE via fetch_tle_lines() and cache it locally as a 3-line file."""
    try:
        name, line1, line2 = fetch_tle_lines(url)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(f"{name}\n{line1}\n{line2}")
        print(f"Successfully fetched and cached TLE to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching TLE: {e}")
        raise


if __name__ == "__main__":
    fetch_and_cache_tle()