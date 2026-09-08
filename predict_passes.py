# Predicting ISS passes over Mumbai

import requests
from skyfield.api import load, EarthSatellite
from src.coverage import get_passes_over_location

# 1. Fetching the ISS TLE
url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
response = requests.get(url)
lines = response.text.strip().splitlines()

name = lines[0].strip()
line1 = lines[1].strip()
line2 = lines[2].strip()

print(f"Satellite: {name}")

# 2. Creating satellite object
ts = load.timescale()
satellite = EarthSatellite(line1, line2, name, ts)

# 3. Defining Mumbai's coordinates
MUMBAI_LAT = 19.0760
MUMBAI_LON = 72.8777

# 4. Searching for passes over the next 1 day
print("Searching for passes over Mumbai for the next 24 hours...")
passes = get_passes_over_location(satellite, MUMBAI_LAT, MUMBAI_LON, 
                                  duration_days=1, horizon_degrees=10)

if passes is None or len(passes) == 0:
    print("No passes found.")
else:
    print(f"Found {len(passes)} passes in the next 24 hours.\n")
    
    # Printing the no. of passes
    print(f"Next {len(passes)} passes over Mumbai:")
    for i, p in enumerate(passes[:len(passes)], start=1):
        rise_time = p['rise_time'].utc_iso().replace('T', ' ')
        culm_time = p['culminate_time'].utc_iso().replace('T', ' ')
        set_time = p['set_time'].utc_iso().replace('T', ' ')
        max_el = p['max_elevation_deg']
        duration_min = p['duration_seconds'] / 60
        
        print(f"{i}. Rise: {rise_time} UTC")
        print(f"   Culminate: {culm_time} UTC")
        print(f"   Set: {set_time} UTC")
        print(f"   Max Elevation: {max_el:.1f}°")
        print(f"   Duration: {duration_min:.1f} min\n")

    # 5. Computing the average revisit interval (as the guide asks)
    if len(passes) > 1:
        # Time between consecutive culminations
        intervals = []
        for i in range(1, len(passes)):
            dt = (passes[i]['culminate_time'] - passes[i-1]['culminate_time']) * 86400
            intervals.append(dt)
        avg_interval_sec = sum(intervals) / len(intervals)
        avg_interval_hours = avg_interval_sec / 3600
        print(f"Average revisit interval: {avg_interval_hours:.1f} hours")
        print(f"(The ISS revisits Mumbai roughly every {avg_interval_hours:.1f} hours on average.)")
    else:
        print("Not enough passes to compute a meaningful revisit interval.")