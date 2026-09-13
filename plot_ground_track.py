"""
Local utility for rendering standalone multi-orbit telemetry projections.
"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load, EarthSatellite
from src.coverage import compute_ground_track

from fetch_tle import fetch_and_cache_tle

DATA_FILE = "data/iss.txt"
MAX_TLE_AGE_SECONDS = 24 * 3600  

# Ensure current orbital regime data
needs_fetch = (
    not os.path.exists(DATA_FILE)
    or (time.time() - os.path.getmtime(DATA_FILE)) > MAX_TLE_AGE_SECONDS
)
if needs_fetch:
    print("No valid cached TLE detected. Syncing with CelesTrak upstream...")
    fetch_and_cache_tle()

with open(DATA_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

name, line1, line2 = lines[0], lines[1], lines[2]
print(f"Satellite: {name}")

ts = load.timescale()
satellite = EarthSatellite(line1, line2, name, ts)

print("Computing nominal 3-orbit ground track geometry (~280 minutes)...")
lats, lons = compute_ground_track(satellite, duration_minutes=280, step_seconds=30)
print(f"Propagation successful. Extracted {len(lats)} spatial coordinates.")

fig, ax = plt.subplots(figsize=(13, 6.5))

# Render ground track utilizing a chronological colormap (blue to red)
# to visualize orbital drift due to planetary rotation over the sequence.
time_progression = np.linspace(0, 1, len(lons))
scatter = ax.scatter(lons, lats, c=time_progression, cmap='coolwarm', s=12, alpha=0.9, zorder=2)

# Extract and mark the initial valid spatial coordinate to represent the TLE epoch
valid_idx = np.isfinite(lons).argmax()
ax.scatter(lons[valid_idx], lats[valid_idx], color='lime', edgecolors='black', 
           s=120, zorder=5, label='Epoch Position')

ax.set_xlim([-180, 180])
ax.set_ylim([-90, 90])
ax.set_xticks(range(-180, 181, 30))
ax.set_yticks(range(-90, 91, 30))

ax.grid(True, linestyle='--', alpha=0.6)
ax.set_xlabel('Longitude (°)')
ax.set_ylabel('Latitude (°)')
ax.set_title(f'Multi-Orbit Ground Track Projection: {name}\nChronological Gradient denotes temporal progression (+3 Orbits)', fontsize=12)
ax.legend(loc='lower left')

cbar = plt.colorbar(scatter, ax=ax, fraction=0.02, pad=0.02)
cbar.set_label('Temporal Sequence')
cbar.set_ticks([0, 0.5, 1])
cbar.set_ticklabels(['T+0 (Epoch)', 'T+140m', 'T+280m'])

plt.savefig('ground_track_multi_orbit.png', dpi=200, bbox_inches='tight')
print("Output successfully rendered to ground_track_multi_orbit.png")
plt.show()