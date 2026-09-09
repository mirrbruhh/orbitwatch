# Scenario A: Validate Hohmann transfer math
# This script compares orbit raise costs for two different mission profiles.

from src.deltav import hohmann_transfer, EARTH_RADIUS

# ---------------------------------------------------------------------
# Mission A: Indian Smallsat (500 km -> 600 km)
# ---------------------------------------------------------------------
alt_500 = 500.0
alt_600 = 600.0
r1_600 = EARTH_RADIUS + alt_500
r2_600 = EARTH_RADIUS + alt_600
dv1_600, dv2_600, total_600 = hohmann_transfer(r1_600, r2_600)
total_600_m_s = total_600 * 1000.0

# ---------------------------------------------------------------------
# Mission B: Ambitious Raise (500 km -> 1500 km)
# ---------------------------------------------------------------------
alt_1500 = 1500.0
r1_1500 = EARTH_RADIUS + alt_500
r2_1500 = EARTH_RADIUS + alt_1500
dv1_1500, dv2_1500, total_1500 = hohmann_transfer(r1_1500, r2_1500)
total_1500_m_s = total_1500 * 1000.0

# ---------------------------------------------------------------------
# Print Comparison Table
# ---------------------------------------------------------------------
print("\n" + "=" * 50)
print("ORBIT RAISE DELTA-V COMPARISON")
print("=" * 50)

print("\n Mission A (Indian Smallsat):")
print(f"\n Initial altitude: {alt_500} km")
print(f"  Target altitude: {alt_600} km")
print(f"  Burn 1: {dv1_600:.4f} km/s")
print(f"  Burn 2: {dv2_600:.4f} km/s")
print(f"  Total delta-v: {total_600:.4f} km/s ({total_600_m_s:.0f} m/s)")

print("\n Mission B (Ambitious Raise):")
print(f"\n Initial altitude: {alt_500} km")
print(f"  Target altitude: {alt_1500} km")
print(f"  Burn 1: {dv1_1500:.4f} km/s")
print(f"  Burn 2: {dv2_1500:.4f} km/s")
print(f"  Total delta-v: {total_1500:.4f} km/s ({total_1500_m_s:.0f} m/s)")

# Sanity checks
print("\n" + "-" * 50)
if 30 < total_600_m_s < 80:
    print("\n SANITY CHECK PASSED: 500→600 km is in the expected range (~55 m/s).")
else:
    print("\n SANITY CHECK FAILED: 500→600 km outside expected range.")

if 200 < total_1500_m_s < 800:
    print("\n SANITY CHECK PASSED: 500→1500 km is in the expected range (~500 m/s).")
else:
    print("\n SANITY CHECK FAILED: 500→1500 km outside expected range.")