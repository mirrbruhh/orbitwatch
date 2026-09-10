# fetch_tle.py
import os
import requests

URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
DATA_DIR = "data"
FILE_PATH = os.path.join(DATA_DIR, "iss.txt")

def fetch_and_cache_tle(url=URL, save_path=FILE_PATH):
    """
    Fetch satellite two-line element set (TLE) from CelesTrak REST API
    and cache locally with directory validation and timeouts.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Clean lines: strip whitespace and completely remove empty blank lines
        clean_lines = [line.strip() for line in response.text.splitlines() if line.strip()]
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
