"""
Scenario B: Validate station-keeping delta-v calculations across mission profiles.
"""

from src.deltav import station_keeping_delta_v
from src.missions import MISSIONS

YEARS = 5.0
SK_BOUNDS = {
    "Mission A (Indian Smallsat)": (10.0, 5.0, 15.0),
    "Mission B (Ambitious High Raise)": (0.5, 0.0, 0.5),
    "Mission C (Rideshare Lowering)": (35.0, 20.0, 50.0), 
}

print("\n" + "=" * 110)
print(f"{'STATION-KEEPING DELTA-V COMPARISON (5-YEAR LIFETIME)':^105}")
print("=" * 110)
print(f" {'Mission Profile':<33} {'Operational Alt':<18} {'Annual Rate':<15} {'Lifetime':<19} {'Total Δv':>11}")
print("-" * 110)

results = []

for name, params in MISSIONS.items():
    nominal, min_bound, max_bound = SK_BOUNDS[name]
    annual_rate = params["annual_rate"]
    dv_m_s = station_keeping_delta_v(annual_rate, YEARS) * 1000.0
    
    alt_str, rate_str, life_str = f"{params['alt2']:.0f} km", f"{annual_rate:.2f} m/s/yr", f"{YEARS:.1f} years"
    print(f" {name:<33} {alt_str:<18} {rate_str:<15} {life_str:<19} {dv_m_s:>8.2f} m/s")
    results.append((name, alt_str, dv_m_s, min_bound <= dv_m_s <= max_bound, nominal))

print("-" * 110)
print("\nENGINEERING STATUS & SANITY CHECKS:")
for name, alt_str, dv_m_s, is_passed, nominal in results:
    if is_passed:
        msg = f"Negligible drag profile verified at {alt_str}" if nominal < 1.0 else f"Within standard operational range (~{nominal:.0f} m/s)"
        print(f"  [PASS] {name}: {msg}")
    else:
        print(f"  [FAIL] {name}: {dv_m_s:.2f} m/s is OUTSIDE expected range")
print("=" * 110)