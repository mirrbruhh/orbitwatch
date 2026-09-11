# Predicting ISS passes over Mumbai

import os
from skyfield.api import load, EarthSatellite
from src.coverage import get_passes_over_location
from fetch_tle import fetch_and_cache_tle  # Reusing your ingestion module!

DATA_FILE = "data/iss.txt"

# SMART FALLBACK: If the file doesn't exist, fetch it once automatically!
if not os.path.exists(DATA_FILE):
    print("No cached TLE found. Downloading from CelesTrak...")
    fetch_and_cache_tle()

# Now read the clean local cache
with open(DATA_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

name, line1, line2 = lines[0], lines[1], lines[2]
print(f"Satellite: {name}")

# Creating satellite object
ts = load.timescale()
satellite = EarthSatellite(line1, line2, name, ts)

# Defining Mumbai's coordinates
MUMBAI_LAT = 19.0760
MUMBAI_LON = 72.8777

def get_compass_direction(deg):
    """Convert azimuth degrees (0-360) to compass directions."""
    points = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return points[int((deg + 22.5) % 360 // 45)]

print(f"Evaluating pass geometry for {name} over Mumbai (Lat: {MUMBAI_LAT}, Lon: {MUMBAI_LON})")
passes_24h = get_passes_over_location(satellite, MUMBAI_LAT, MUMBAI_LON, duration_days=1, horizon_degrees=10)

if not passes_24h:
    print("No passes above 10° horizon found in the next 24 hours.")
else:
    print(f"\nNext {len(passes_24h)} pass(es) over Mumbai (24h Window):")
    for i, p in enumerate(passes_24h, start=1):
        rise = p['rise_time'].utc_iso().replace('T', ' ')
        culm = p['culminate_time'].utc_iso().replace('T', ' ')
        sett = p['set_time'].utc_iso().replace('T', ' ')
        compass = get_compass_direction(p['azimuth_deg'])
        print(f"{i}. Rise: {rise} UTC | Peak: {culm} UTC (Elev: {p['max_elevation_deg']:.1f}°, Az: {p['azimuth_deg']:.1f}° {compass}, Range: {p['distance_km']:.0f} km) | Set: {sett} UTC | Dur: {p['duration_seconds']/60:.1f}m")

# Statistically valid 7-day revisit metric :
passes_7d = get_passes_over_location(satellite, MUMBAI_LAT, MUMBAI_LON, duration_days=7, horizon_degrees=10)

print("\n" + "=" * 60)
print("7-DAY REVISIT METRIC")
print("=" * 60)
if passes_7d and len(passes_7d) > 0:
    count_7d = len(passes_7d)
    revisit_hours = (7.0 * 24.0) / count_7d
    print(f"Total passes detected over 7 days: {count_7d}")
    print(f"Average Revisit Interval: {revisit_hours:.1f} hours")
    print(f"The ISS revisits Mumbai roughly every {revisit_hours:.1f} hours on average.")
else:
    print("No passes detected over the 7-day observation window.")