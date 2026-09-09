# Scenario C: Validate deorbit delta-v calculation
# This script compares deorbit costs from two different altitudes.

from src.deltav import deorbit_delta_v, EARTH_RADIUS

# ---------------------------------------------------------------------
# Mission A: Indian Smallsat (500 km -> 150 km)
# ---------------------------------------------------------------------
alt_500 = 500.0
alt_perigee = 150.0
r1_500 = EARTH_RADIUS + alt_500
r_perigee = EARTH_RADIUS + alt_perigee
dv_500_km_s = deorbit_delta_v(r1_500, r_perigee)
dv_500_m_s = dv_500_km_s * 1000.0

# ---------------------------------------------------------------------
# Mission B: Ambitious Deorbit (1500 km -> 150 km)
# ---------------------------------------------------------------------
alt_1500 = 1500.0
r1_1500 = EARTH_RADIUS + alt_1500
dv_1500_km_s = deorbit_delta_v(r1_1500, r_perigee)
dv_1500_m_s = dv_1500_km_s * 1000.0

# ---------------------------------------------------------------------
# Print Comparison Table
# ---------------------------------------------------------------------
print("\n" + "=" * 50)
print("DEORBIT DELTA-V COMPARISON")
print("=" * 50)

print("\n Mission A (Indian Smallsat):")
print(f"\n Initial altitude: {alt_500} km")
print(f"  Target perigee: {alt_perigee} km")
print(f"  Deorbit delta-v: {dv_500_m_s:.1f} m/s ({dv_500_km_s:.4f} km/s)")

print("\n Mission B (Ambitious Deorbit):")
print(f"\n Initial altitude: {alt_1500} km")
print(f"  Target perigee: {alt_perigee} km")
print(f"  Deorbit delta-v: {dv_1500_m_s:.1f} m/s ({dv_1500_km_s:.4f} km/s)")

# Sanity checks
print("\n" + "-" * 50)
if 80 < dv_500_m_s < 120:
    print("\n SANITY CHECK PASSED: 500 km deorbit is in the expected range (~100 m/s).")
else:
    print("\n SANITY CHECK FAILED: 500 km deorbit outside expected range.")

if 200 < dv_1500_m_s < 400:
    print("\n SANITY CHECK PASSED: 1500 km deorbit is in the expected range (~340 m/s).")
else:
    print("\n SANITY CHECK FAILED: 1500 km deorbit outside expected range.")