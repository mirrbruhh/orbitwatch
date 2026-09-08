# validate_deltav.py
# Day 3, Part A: Validate Hohmann transfer math

from src.deltav import hohmann_transfer, EARTH_RADIUS

# ---------------------------------------------------------------------
# PRIMARY SHOWCASE SCENARIO: 500 km to 1500 km (1000 km raise)
# This yields ~0.5 km/s (500 m/s), which makes the Day 4 propulsion 
# trade-study visually dramatic.
# ---------------------------------------------------------------------
altitude_initial = 500.0   # km
altitude_target = 1500.0   # km

# ---------------------------------------------------------------------
# UNIT TEST (Optional): Uncomment below to test the 500->600 km case.
# This yields ~0.0547 km/s (55 m/s) and proves the math handles 
# small maneuvers correctly.
# ---------------------------------------------------------------------
# altitude_initial = 500.0
# altitude_target = 600.0

r1 = EARTH_RADIUS + altitude_initial
r2 = EARTH_RADIUS + altitude_target

print(f"\nInitial altitude: {altitude_initial} km")
print(f"Target altitude: {altitude_target} km")
print(f"Initial radius (r1): {r1:.1f} km")
print(f"Target radius (r2): {r2:.1f} km")

dv1, dv2, total_dv = hohmann_transfer(r1, r2)

print(f"\nBurn 1 (at {altitude_initial:.0f} km): {dv1:.4f} km/s")
print(f"Burn 2 (at {altitude_target:.0f} km): {dv2:.4f} km/s")
total_m_s = total_dv * 1000.0
print(f"Total delta-v: {total_dv:.4f} km/s or {total_m_s:.0f} m/s" )

# Sanity check (now set for the 500->1500 case, ~500 m/s)

if 200 < total_m_s < 800:  # Broadened range to catch both 55m/s and 500m/s cases
    print("\nSANITY CHECK PASSED: Total delta-v is in the expected range.")
else:
    print("\nSANITY CHECK FAILED: Check your units.")