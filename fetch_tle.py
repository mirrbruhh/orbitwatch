"""
Local utility for retrieving two-line element sets (TLEs).
Intended for standalone CLI testing; web applications should handle API responses in-memory.
"""

import os
import requests

URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
DATA_DIR = "data"
FILE_PATH = os.path.join(DATA_DIR, "iss.txt")

def fetch_and_cache_tle(url=URL, save_path=FILE_PATH):
    """
    Fetch satellite TLE from the CelesTrak REST API and cache locally.
    Network requests include explicit timeouts to prevent process blocking 
    during upstream API degradation.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Sanitize payload: strip whitespace and filter out empty newlines
        clean_lines = [line.strip() for line in response.text.splitlines() if line.strip()]

        # Basic validation against payload corruption or HTML rate-limit pages
        if len(clean_lines) < 3 or not clean_lines[1].startswith("1 ") or not clean_lines[2].startswith("2 "):
            raise ValueError("Upstream response failed TLE structure validation.")

        clean_text = "\n".join(clean_lines)
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(clean_text)
        print(f"Successfully fetched and cached TLE to {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"Network error fetching TLE: {e}")
        raise

if __name__ == "__main__":
    fetch_and_cache_tle()