# Scenario B: Validate station-keeping delta-v calculation
# This script compares station-keeping costs at two different altitudes.

from src.deltav import station_keeping_delta_v

# ---------------------------------------------------------------------
# Mission A: Indian Smallsat (500 km altitude)
# ---------------------------------------------------------------------
# Source: SMAD (Space Mission Analysis and Design, 4th Edition, Chapter 8)
# Typical range for 500 km: 5 to 10 m/s per year.
# We use 7.0 m/s/year as a representative baseline.
ANNUAL_RATE_500 = 7.0          # m/s per year (at 500 km)
YEARS = 5.0

dv_500_km_s = station_keeping_delta_v(ANNUAL_RATE_500, YEARS)
dv_500_m_s = dv_500_km_s * 1000.0

# ---------------------------------------------------------------------
# Mission B: Ambitious Raise (1500 km altitude)
# ---------------------------------------------------------------------
# At 1500 km, atmospheric density is effectively zero (10^-14 kg/m^3).
# Station-keeping cost is negligible (< 0.1 m/s per year).
ANNUAL_RATE_1500 = 0.0         # m/s per year (at 1500 km)

dv_1500_km_s = station_keeping_delta_v(ANNUAL_RATE_1500, YEARS)
dv_1500_m_s = dv_1500_km_s * 1000.0

# ---------------------------------------------------------------------
# Print Comparison Table
# ---------------------------------------------------------------------
print("\n" + "=" * 50)
print("STATION-KEEPING DELTA-V COMPARISON")
print("=" * 50)

print("\n Mission A (Indian Smallsat at 500 km):")
print(f"\n Annual rate: {ANNUAL_RATE_500} m/s/year")
print(f"  Lifetime: {YEARS} years")
print(f"  Total delta-v: {dv_500_m_s:.1f} m/s ({dv_500_km_s:.4f} km/s)")

print("\n Mission B (Ambitious Raise at 1500 km):")
print(f"\n Annual rate: {ANNUAL_RATE_1500} m/s/year")
print(f"  Lifetime: {YEARS} years")
print(f"  Total delta-v: {dv_1500_m_s:.1f} m/s ({dv_1500_km_s:.4f} km/s)")

# Sanity checks
print("\n" + "-" * 50)
if 20 < dv_500_m_s < 60:
    print("\n SANITY CHECK PASSED: 500 km case is in the expected range (30-50 m/s).")
else:
    print("\n SANITY CHECK FAILED: 500 km case is outside the expected range.")

if dv_1500_m_s == 0.0:
    print("\n SANITY CHECK PASSED: 1500 km case is negligible (0 m/s).")
else:
    print("\n SANITY CHECK FAILED: 1500 km case should be 0 m/s.")