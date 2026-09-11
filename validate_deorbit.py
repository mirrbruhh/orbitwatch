# Scenario C: Validate deorbit delta-v calculations across mission profiles

from src.deltav import deorbit_delta_v, EARTH_RADIUS

# 150 km target perigee dips the spacecraft into Earth's dense upper atmosphere,
# where aerodynamic drag guarantees rapid, passive re-entry and destruction.
ALT_PERIGEE = 150.0
r_perigee = EARTH_RADIUS + ALT_PERIGEE

# Mission definitions: (Name, Initial_Alt_km, Nominal_Target_m_s, Min_Bound, Max_Bound)
MISSIONS = [
    ("Mission A (Indian Smallsat)", 500.0, 100.0, 80.0, 120.0),
    ("Mission B (Ambitious High Raise)", 1500.0, 340.0, 300.0, 380.0),
    ("Mission C (Rideshare Lowering)", 500.0, 100.0, 80.0, 120.0),  # Deorbits from 500 km working orbit
]

print("\n" + "=" * 110)
print(f"{'DEORBIT DELTA-V COMPARISON (PERIGEE = 150 KM)':^105}")
print("=" * 110)
print(f" {'Mission Profile':<32} {'Initial Orbit':<18} {'Target Perigee':<18} {'Deorbit Δv (m/s)':>16} {'Δv (km/s)':>14}")
print("-" * 110)

results = []

for name, alt_init, nominal, min_bound, max_bound in MISSIONS:
    r1 = EARTH_RADIUS + alt_init
    dv_km_s = deorbit_delta_v(r1, r_perigee)
    dv_m_s = dv_km_s * 1000.0
    
    init_str = f"{alt_init:.0f} km"
    peri_str = f"{ALT_PERIGEE:.0f} km"
    traj_str = f"{alt_init:.0f} → {ALT_PERIGEE:.0f} km"
    
    print(f" {name:<33} {init_str:<20} {peri_str:<14} {dv_m_s:>10.2f} m/s {dv_km_s:>14.4f} km/s")
    
    is_passed = min_bound <= dv_m_s <= max_bound
    results.append((name, traj_str, dv_m_s, is_passed, nominal))

print("-" * 110)

# ---------------------------------------------------------------------
# Sanity Checks & Verification Summary
# ---------------------------------------------------------------------
print("\nSANITY CHECK VERIFICATION:")
for name, traj_str, dv_m_s, is_passed, nominal in results:
    if is_passed:
        tag = "[PASS]"
        msg = f"{dv_m_s:.2f} m/s is within nominal range (~{nominal:.0f} m/s)"
    else:
        tag = "[FAIL]"
        msg = f"{dv_m_s:.2f} m/s is OUTSIDE expected range"
        
    print(f"  {tag} {name} ({traj_str}): {msg}")

print("\nSYSTEMS ENGINEERING NOTE:")
print("  • 150 km target perigee places the spacecraft inside dense upper atmosphere for passive destruction.")
print("  • Deorbiting from 1500 km requires >3x more delta-v (340 m/s) than from 500 km (100 m/s), demanding")
print("    substantial propellant reserves for end-of-life disposal.")
print("=" * 110)