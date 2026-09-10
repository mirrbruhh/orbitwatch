import os
from skyfield.api import load, EarthSatellite
from src.propagate import propagate

DATA_FILE = "data/iss.txt"
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError("Run fetch_tle.py first to cache satellite orbital elements.")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

name, line1, line2 = lines[0], lines[1], lines[2]
ts = load.timescale()
now = ts.now()

pos, vel = propagate(line1, line2, name, now)

print(f"\nSatellite: {name}")
print(f"Time: {now.utc_iso()}")
print(f"Position (X, Y, Z) in km: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
print(f"Velocity (X, Y, Z) in km/s: [{vel[0]:.4f}, {vel[1]:.4f}, {vel[2]:.4f}]")

# Sanity check for altitude :
sat = EarthSatellite(line1, line2, name, ts)
geo = sat.at(now)
subpoint = geo.subpoint()
altitude_km = subpoint.elevation.km

print(f"Geodetic Altitude: {altitude_km:.2f} km")

if 390.0 <= altitude_km <= 445.0:
    print("\nSANITY CHECK PASSED: Altitude is within expected ISS operating regime.")
else:
    print("\nSANITY CHECK FAILED: Altitude is outside expected ISS regime.")