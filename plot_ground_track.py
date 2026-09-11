# Visualizing the ground track

import os
import matplotlib.pyplot as plt
from skyfield.api import load, EarthSatellite
from src.coverage import compute_ground_track
from fetch_tle import fetch_and_cache_tle  # Reusing your ingestion module!
import time

DATA_FILE = "data/iss.txt"
MAX_TLE_AGE_SECONDS = 24 * 3600  # TLE accuracy degrades within days; refreshing it at least daily

# SMART FALLBACK: If the file doesn't exist/or is older than 24 hours, fetch it once automatically!
needs_fetch = (
    not os.path.exists(DATA_FILE)
    or (time.time() - os.path.getmtime(DATA_FILE)) > MAX_TLE_AGE_SECONDS
)
if needs_fetch:
    print("No cached TLE found (or it's stale). Downloading from CelesTrak...")
    fetch_and_cache_tle()

# Now read the clean local cache
with open(DATA_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

name, line1, line2 = lines[0], lines[1], lines[2]
print(f"Satellite: {name}")

# 2. Creating the satellite object
ts = load.timescale()
satellite = EarthSatellite(line1, line2, name, ts)

# 3. Computing the ground track
print("Computing 3-orbit ground track (~280 minutes)...")
lats, lons = compute_ground_track(satellite, duration_minutes=280, step_seconds=30)
print(f"Generated {len(lats)} points.")

# 4. Plotting using Matplotlib
fig, ax = plt.subplots(figsize=(13, 6.5))

# Plotting the line and the points
ax.plot(lons, lats, color='crimson', linewidth=1.8, label='Ground Track (3 Orbits)')
ax.scatter(lons[0], lats[0], color='green', s=70, zorder=5, label='Sub-satellite Point at Epoch')

# Set map boundaries
ax.set_xlim([-180, 180])
ax.set_ylim([-90, 90])
ax.set_xticks(range(-180, 181, 30))
ax.set_yticks(range(-90, 91, 30))

# Adding gridlines (this is the "simplified world outline")
ax.grid(True, linestyle='--', alpha=0.6)

# Labels and title
ax.set_xlabel('Longitude (°)')
ax.set_ylabel('Latitude (°)')
ax.set_title(f'Multi-Orbit Ground Track: {name}\nDemonstrating ~23° Westward Longitudinal Drift per Orbit', fontsize=12)
ax.legend(loc='lower left')

# 5. Save and display
plt.savefig('ground_track_multi_orbit.png', dpi=200, bbox_inches='tight')
print("Saved multi-orbit track as ground_track_multi_orbit.png")
plt.show()