from skyfield.api import load,EarthSatellite
from src.propagate import propagate

with open('data/iss.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

name = lines[0]
line1 = lines[1]
line2 = lines[2]
print("Text extracted : ")
print(f"Satellite: {name}")
print(f"Line 1: {line1}")
print(f"Line 2: {line2}")

ts = load.timescale()
now = ts.now()

pos, vel = propagate(line1, line2, name, now)

print(f"\nSatellite: {name}")
print(f"Time: {now.utc_iso()}")
print(f"Position (X, Y, Z) in km: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
print(f"Velocity (X, Y, Z) in km/s: [{vel[0]:.4f}, {vel[1]:.4f}, {vel[2]:.4f}]")

# Sanity check altitude
sat = EarthSatellite(line1, line2, name, ts)
geo = sat.at(now)
subpoint = geo.subpoint()
altitude_km = subpoint.elevation.km

print(f"Altitude: {altitude_km:.2f} km")

if 390 < altitude_km < 430:
    print("\nSANITY CHECK PASSED: Altitude is in the expected range for ISS.")
else:
    print("\nSANITY CHECK FAILED: Altitude is outside the expected range.")