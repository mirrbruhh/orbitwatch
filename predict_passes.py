"""
Local utility: Ground station coverage and revisit frequency analysis.
"""

import os
import time
from skyfield.api import load, EarthSatellite
from src.coverage import get_passes_over_location
from fetch_tle import fetch_and_cache_tle

DATA_FILE = "data/iss.txt"
MAX_TLE_AGE_SECONDS = 24 * 3600  

if not os.path.exists(DATA_FILE) or (time.time() - os.path.getmtime(DATA_FILE)) > MAX_TLE_AGE_SECONDS:
    print("No cached TLE found (or it's stale). Downloading from CelesTrak...")
    fetch_and_cache_tle()

with open(DATA_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

name, line1, line2 = lines[0], lines[1], lines[2]
ts = load.timescale()
satellite = EarthSatellite(line1, line2, name, ts)

# Target Ground Station: Mumbai
MUMBAI_LAT, MUMBAI_LON = 19.0760, 72.8777

def get_compass_direction(deg):
    """Maps azimuth degree vectors to nominal compass headings."""
    points = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return points[int((deg + 22.5) % 360 // 45)]

print(f"\nEvaluating Topocentric Geometry: {name} over Ground Station [{MUMBAI_LAT}, {MUMBAI_LON}]")
passes_24h = get_passes_over_location(satellite, MUMBAI_LAT, MUMBAI_LON, duration_days=1, horizon_degrees=10)

if not passes_24h:
    print("STATUS: No passes >10° horizon detected in the 24h operational window.")
else:
    print(f"\nUpcoming Passes (24h Window): {len(passes_24h)} Event(s)")
    for i, p in enumerate(passes_24h, start=1):
        rise = p['rise_time'].utc_iso().replace('T', ' ')
        culm = p['culminate_time'].utc_iso().replace('T', ' ')
        sett = p['set_time'].utc_iso().replace('T', ' ')
        compass = get_compass_direction(p['azimuth_deg'])
        
        print(f"  [{i}] AOS: {rise} | Peak: {culm} (Elev: {p['max_elevation_deg']:.1f}°, Range: {p['distance_km']:.0f}km) | LOS: {sett}")

# Statistical Revisit Analysis
passes_7d = get_passes_over_location(satellite, MUMBAI_LAT, MUMBAI_LON, duration_days=7, horizon_degrees=10)

print("\n" + "=" * 60)
print("REVISIT METRICS (7-DAY BASELINE)")
print("=" * 60)
if passes_7d:
    count = len(passes_7d)
    revisit_hours = (7.0 * 24.0) / count
    print(f"Total Acquisition Opportunities: {count}")
    print(f"Average Revisit Interval:      {revisit_hours:.1f} hours")
else:
    print("STATUS: Unreachable orbit for this ground station.")
print("=" * 60)