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

        # A real TLE is name + 2 lines, with line 1 starting "1 " and line 2
        # starting "2 ". This catches CelesTrak returning an error page, an
        # empty body, or a rate-limit notice with a 200 status.
        if len(clean_lines) < 3 or not clean_lines[1].startswith("1 ") or not clean_lines[2].startswith("2 "):
            raise ValueError(
                f"Response doesn't look like a valid TLE (got {len(clean_lines)} lines). "
                f"Raw response started with: {response.text[:120]!r}"
            )

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
