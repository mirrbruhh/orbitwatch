# Module 4: Validate propulsion trade-study calculations across mission profiles

from src.propulsion import propellant_mass, transfer_time_estimate, exhaust_velocity
from src.deltav import hohmann_coast_time, EARTH_RADIUS

def format_duration(seconds):
    """Format seconds into compact human-readable durations."""
    if seconds == float('inf'):
        return "N/A"
    days = int(seconds // 86400)
    remaining = seconds % 86400
    hours = int(remaining // 3600)
    remaining = remaining % 3600
    minutes = int(round(remaining / 60))
    
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

# Baseline satellite wet mass
M0_KG = 1000.0  # kg

# Mission profiles: (Name, Total_Delta_V_m_s, Alt1_km, Alt2_km)
MISSIONS = [
    ("Mission A (Indian Smallsat: 500 → 600 km)", 190.0, 500.0, 600.0),
    ("Mission B (Ambitious High Raise: 500 → 1500 km)", 840.0, 500.0, 1500.0),
    ("Mission C (Rideshare Lowering: 800 → 500 km)", 296.0, 800.0, 500.0),
]

# Thruster specifications: (Name, Isp_s, Efficiency, Power_W, Thrust_N, Mode)
THRUSTERS = [
    ("Chemical Bipropellant", 300, 0.95, 0.0, 500.0, "Chemical"),
    ("Hall Thruster", 1800, 0.55, 3000.0, 0.5, "Electric"),
    ("Ion Thruster", 3000, 0.70, 5000.0, 0.2, "Electric"),
    ("Water Microwave Plasma", 1200, 0.45, 1500.0, 0.1, "Electric"),  # Bellatrix spec
]

print("\n" + "=" * 105)
print(f"{'PROPULSION TRADE STUDY: MISSION COMPARISON':^105}")
print("=" * 105)

for mission_name, dv_total, alt1, alt2 in MISSIONS:
    r1 = EARTH_RADIUS + alt1
    r2 = EARTH_RADIUS + alt2
    coast_s = hohmann_coast_time(r1, r2)
    coast_str = format_duration(coast_s)
    
    print(f"\n ► {mission_name}")
    print(f"   Total Δv: {dv_total:.1f} m/s | Spacecraft Wet Mass: {M0_KG:.0f} kg")
    print(f"   {'Thruster Technology':<26} {'Isp (s)':>9} {'Exhaust Vel':>15} {'Prop. Mass':>14} {'Burn Time':>12} {'Transit Duration':>18}")
    print("   " + "-" * 100)
    
    for name, isp, eta, power, thrust, mode in THRUSTERS:
        v_e = exhaust_velocity(isp)  # Now actively used in the table!
        mp = propellant_mass(dv_total, isp, M0_KG)
        burn_s = transfer_time_estimate(dv_total, thrust, M0_KG)
        burn_str = format_duration(burn_s)
        
        v_e_str = f"{v_e/1000:.2f} km/s"
        isp_str = f"{isp} s"
        transit_str = f"Hohmann (~{coast_str})" if mode == "Chemical" else f"Spiral (~{burn_str})"
            
        print(f"   {name:<26} {isp_str:>9} {v_e_str:>15} {mp:>12.1f} kg {burn_str:>12} {transit_str:>18}")

print("\n" + "=" * 105)
print("SYSTEMS ENGINEERING NOTES:")
print("  • Burn vs Transit: Chemical burns in minutes, then coasts on the Hohmann ellipse (~50m).")
print("    Electric thrusters spiral continuously for days/weeks.")
print("  • Mission B Gravity Losses: Continuous 28m burn in LEO spans ~30% of the orbit. In reality")
print("    (e.g., ISRO Mangalyaan / MOM), this is split into multiple perigee burns to prevent losses.")
print("=" * 105)

# ---------------------------------------------------------------------
# Physics Benchmark: First-Principles Ion Thruster Derivation Check
# ---------------------------------------------------------------------
q = 1.602e-19        # C (Elementary charge)
V = 1000.0           # V (Screen grid accelerating potential)
m_ion = 2.18e-25     # kg (Mass of singly-ionized Xenon)

v_e_calc = (2.0 * q * V / m_ion) ** 0.5
isp_calc = v_e_calc / 9.80665

print("\n" + "=" * 105)
print(f"{'PHYSICS MODEL VERIFICATION: ELECTROSTATIC ION ACCELERATION':^105}")
print("=" * 105)
print(f"  Input Grid Voltage (V):          {V:.1f} V")
print(f"  Propellant Ion:                  Xenon (Xe+, m = {m_ion:.2e} kg, q = {q:.2e} C)")
print(f"  Theoretical Exhaust Velocity:    {v_e_calc/1000:.2f} km/s   [Formula: v_e = sqrt(2*q*V/m)]")
print(f"  Theoretical Specific Impulse:    {isp_calc:.0f} s       [Formula: Isp = v_e / g0]")
if 3000 <= isp_calc <= 4500:
    print("  Benchmark Status:                [PASS] Validates high Isp (>3000s) regime from first principles")
else:
    print("  Benchmark Status:                [FAIL] Outside expected ion propulsion regime")
print("=" * 105)