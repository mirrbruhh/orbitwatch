# Visualizing the ground track

import requests
import matplotlib.pyplot as plt
from skyfield.api import load, EarthSatellite
from src.coverage import compute_ground_track

# 1. Fetching the ISS TLE
url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
response = requests.get(url)
lines = response.text.strip().splitlines()

name = lines[0].strip()
line1 = lines[1].strip()
line2 = lines[2].strip()

print(f"Satellite: {name}")

# 2. Creating the satellite object
ts = load.timescale()
satellite = EarthSatellite(line1, line2, name, ts)

# 3. Computing the ground track
print("Computing ground track...")
lats, lons = compute_ground_track(satellite)
print(f"{lats}\n{lons}")
print(f"Generated {len(lats)} points.")

# 4. Plotting using Matplotlib
fig, ax = plt.subplots(figsize=(12, 6))

# Plotting the line and the points
ax.plot(lons, lats, color='red', linewidth=1.5, label='Ground Track')
ax.scatter(lons, lats, color='red', s=5, alpha=0.5)

# Set map boundaries
ax.set_xlim([-180, 180])
ax.set_ylim([-90, 90])

# Adding gridlines (this is the "simplified world outline")
ax.grid(True, linestyle='--', alpha=0.7)

# Labels and title
ax.set_xlabel('Longitude (degrees)')
ax.set_ylabel('Latitude (degrees)')
ax.set_title(f'Ground Track of {name} - One Orbit')
ax.legend()

# 5. Save and display
plt.savefig('ground_track.png', dpi=150, bbox_inches='tight')
print("Plot saved as ground_track.png")
plt.show()