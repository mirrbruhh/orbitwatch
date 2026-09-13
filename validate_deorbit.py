"""
Scenario C: Validate deorbit delta-v calculations across mission profiles.
"""

from src.deltav import deorbit_delta_v, EARTH_RADIUS
from src.missions import MISSIONS

ALT_PERIGEE = 150.0
r_perigee = EARTH_RADIUS + ALT_PERIGEE

DEORBIT_BOUNDS = {
    "Mission A (Indian Smallsat)": (127.0, 110.0, 145.0),
    "Mission B (Ambitious High Raise)": (340.0, 300.0, 380.0),
    "Mission C (Rideshare Lowering)": (100.0, 80.0, 120.0),
}

print("\n" + "=" * 110)
print(f"{'DEORBIT DELTA-V COMPARISON (TARGET PERIGEE = 150 KM)':^105}")
print("=" * 110)
print(f" {'Mission Profile':<32} {'Initial Orbit':<18} {'Target Perigee':<18} {'Deorbit Δv (m/s)':>16} {'Δv (km/s)':>14}")
print("-" * 110)

results = []

for name, params in MISSIONS.items():
    nominal, min_bound, max_bound = DEORBIT_BOUNDS[name]
    alt_init = params["alt2"]
    dv_km_s = deorbit_delta_v(EARTH_RADIUS + alt_init, r_perigee)
    dv_m_s = dv_km_s * 1000.0
    
    init_str, peri_str, traj_str = f"{alt_init:.0f} km", f"{ALT_PERIGEE:.0f} km", f"{alt_init:.0f} → {ALT_PERIGEE:.0f} km"
    print(f" {name:<33} {init_str:<20} {peri_str:<14} {dv_m_s:>10.2f} m/s {dv_km_s:>14.4f} km/s")
    results.append((name, traj_str, dv_m_s, min_bound <= dv_m_s <= max_bound, nominal))

print("-" * 110)
print("\nENGINEERING STATUS & SANITY CHECKS:")
for name, traj_str, dv_m_s, is_passed, nominal in results:
    if is_passed:
        print(f"  [PASS] {name} ({traj_str}): Destructive disposal verified (~{nominal:.0f} m/s)")
    else:
        print(f"  [FAIL] {name} ({traj_str}): {dv_m_s:.2f} m/s is OUTSIDE expected range")
print("=" * 110)