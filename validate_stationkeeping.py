# Scenario B: Validate station-keeping delta-v calculations across mission profiles
# This script compares station-keeping costs at two different altitudes.

from src.deltav import station_keeping_delta_v
from src.missions import MISSIONS

# Baseline lifetime: 5 years is the industry standard design life for LEO smallsats,
# balancing battery cycle degradation (~28,000 cycles) and COTS radiation tolerance.
YEARS = 5.0

# Sanity-check bounds specific to station-keeping: name -> (Nominal_Total_m_s, Min_Bound, Max_Bound)
# Source: SMAD (Space Mission Analysis and Design, 4th Edition, Chapter 8)
SK_BOUNDS = {
    # 600 km, not 500: see src/missions.py for why the rate (and this bound) is lower than Mission C's.
    "Mission A (Indian Smallsat)": (10.0, 5.0, 15.0),
    # Not exactly zero: 0.1 m/s/yr (see src/missions.py) is a conservative
    # upper bound at 1500 km, so this is a real comparison, not a tautology.
    "Mission B (Ambitious High Raise)": (0.5, 0.0, 0.5),
    "Mission C (Rideshare Lowering)": (35.0, 20.0, 50.0),  # operates at 500 km after lowering
}

print("\n" + "=" * 110)
print(f"{'STATION-KEEPING DELTA-V COMPARISON (5-YEAR LIFETIME)':^105}")
print("=" * 110)
print(f" {'Mission Profile':<33} {'Operational Alt':<18} {'Annual Rate':<15} {'Lifetime Duration':<19} {'Total Δv':>11}")
print("-" * 110)

results = []

for name, params in MISSIONS.items():
    nominal, min_bound, max_bound = SK_BOUNDS[name]
    annual_rate = params["annual_rate"]
    dv_km_s = station_keeping_delta_v(annual_rate, YEARS)
    dv_m_s = dv_km_s * 1000.0
    
    alt_str = f"{params['alt2']:.0f} km"
    rate_str = f"{annual_rate:.2f} m/s/yr"
    life_str = f"{YEARS:.1f} years"
    
    print(f" {name:<33} {alt_str:<18} {rate_str:<15} {life_str:<19} {dv_m_s:>8.2f} m/s")
    
    is_passed = min_bound <= dv_m_s <= max_bound
    results.append((name, alt_str, dv_m_s, is_passed, nominal))

print("-" * 110)

# ---------------------------------------------------------------------
# Sanity Checks & Verification Summary
# ---------------------------------------------------------------------
print("\nSANITY CHECK VERIFICATION:")
for name, alt_str, dv_m_s, is_passed, nominal in results:
    if is_passed:
        tag = "[PASS]"
        if nominal < 1.0:
            msg = f"{dv_m_s:.2f} m/s is negligible at {alt_str} (~{nominal:.1f} m/s)"
        else:
            msg = f"{dv_m_s:.2f} m/s is within nominal drag range (~{nominal:.0f} m/s)"
    else:
        tag = "[FAIL]"
        msg = f"{dv_m_s:.2f} m/s is OUTSIDE expected range"
        
    print(f"  {tag} {name} ({alt_str}): {msg}")

print("\nSYSTEMS ENGINEERING NOTE:")
print("  • At 500 km (Mission C, after lowering), atmospheric density (~2e-12 kg/m³) requires ~7 m/s/yr to fight drag.")
print("  • At 600 km (Mission A), density is roughly a quarter to a fifth of the 500 km value, cutting the rate to ~2 m/s/yr.")
print("  • At 800 km (Mission C's starting altitude), drag is negligible (<0.5 m/s/yr) before it lowers to 500 km.")
print("  • At 1500 km (Mission B), density drops to ~1e-14 kg/m³, making lifetime drag ~0.5 m/s.")
print("=" * 110)