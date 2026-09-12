# Scenario A: Validate Hohmann transfer calculations across mission profiles

from src.deltav import hohmann_transfer, EARTH_RADIUS
from src.missions import MISSIONS

# Sanity-check bounds specific to the raise/lower burn: name -> (Type, Nominal_m_s, Min, Max)
RAISE_BOUNDS = {
    "Mission A (Indian Smallsat)": ("Raise", 55.0, 30.0, 60.0),
    "Mission B (Ambitious High Raise)": ("Raise", 500.0, 450.0, 520.0),
    "Mission C (Rideshare Lowering)": ("Lowering", 161.0, 140.0, 180.0),
}

print("\n" + "=" * 110)
print(f"{'ORBITAL TRANSFER DELTA-V COMPARISON (HOHMANN)':^105}")
print("=" * 110)
print(f" {'Mission Profile':<33} {'Trajectory':<15} {'Type':<11} {'Burn 1 (Δv₁)':>14} {'Burn 2 (Δv₂)':>14} {'Total Δv':>11}")
print("-" * 110)

results = []

for name, params in MISSIONS.items():
    m_type, nominal, min_exp, max_exp = RAISE_BOUNDS[name]
    r1 = EARTH_RADIUS + params["alt1"]
    r2 = EARTH_RADIUS + params["alt2"]
    dv1, dv2, total = hohmann_transfer(r1, r2)
    
    dv1_m_s = dv1 * 1000.0
    dv2_m_s = dv2 * 1000.0
    total_m_s = total * 1000.0
    
    traj_str = f"{params['alt1']:.0f} → {params['alt2']:.0f} km"
    print(f" {name:<33} {traj_str:<15} {m_type:<11} {dv1_m_s:>10.2f} m/s {dv2_m_s:>10.2f} m/s {total_m_s:>8.2f} m/s")
    
    # Save verification status for the summary block
    is_passed = min_exp <= total_m_s <= max_exp
    results.append((name, traj_str, total_m_s, is_passed, nominal))

print("-" * 110)

# ---------------------------------------------------------------------
# Sanity Checks & Verification Summary
# ---------------------------------------------------------------------
print("\nSANITY CHECK VERIFICATION:")
for name, traj_str, total_m_s, is_passed, expected_approx in results:
    if is_passed:
        tag = "[PASS]"
        msg = f"{total_m_s:.2f} m/s is within nominal range (~{expected_approx:.0f} m/s)"
    else:
        tag = "[FAIL]"
        msg = f"{total_m_s:.2f} m/s is OUTSIDE nominal range (~{expected_approx:.0f} m/s)"
        
    print(f"  {tag} {name} ({traj_str}): {msg}")

print("=" * 110)