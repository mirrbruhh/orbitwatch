# Module 4: Validate propulsion trade-study calculations across mission profiles

from src.propulsion import propellant_mass, transfer_time_estimate, exhaust_velocity, thrust_from_power
from src.deltav import (
    hohmann_transfer,
    hohmann_coast_time,
    station_keeping_delta_v,
    deorbit_delta_v,
    EARTH_RADIUS,
)
from src.missions import MISSIONS

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
LIFETIME_YEARS = 5.0
PERIGEE_ALT_KM = 150.0

def mission_total_delta_v(alt1, alt2, annual_rate_m_s):
    """Raise/lower + lifetime station-keeping + deorbit from the final altitude."""
    r1 = EARTH_RADIUS + alt1
    r2 = EARTH_RADIUS + alt2
    _, _, raise_dv = hohmann_transfer(r1, r2)
    sk_dv = station_keeping_delta_v(annual_rate_m_s, LIFETIME_YEARS)
    r_perigee = EARTH_RADIUS + PERIGEE_ALT_KM
    deorbit_dv = deorbit_delta_v(r2, r_perigee)
    return (raise_dv + sk_dv + deorbit_dv) * 1000.0

# Thruster specifications: (Name, Isp_s, Efficiency, Power_W, Thrust_N, Mode)
THRUSTERS = [
    ("Chemical Bipropellant", 300, 0.95, 0.0, 500.0, "Chemical"),
    ("Hall Thruster", 1800, 0.50, 3000.0, None, "Electric"),
    ("Ion Thruster", 3000, 0.70, 5000.0, None, "Electric"),
    ("Water Microwave Plasma", 1200, 0.45, 1500.0, None, "Electric"),  # Isp per Bellatrix's public 4x-chemical-Isp claim
]

print("\n" + "=" * 105)
print(f"{'PROPULSION TRADE STUDY: MISSION COMPARISON':^105}")
print("=" * 105)

for mission_name, params in MISSIONS.items():
    alt1, alt2 = params["alt1"], params["alt2"]
    r1 = EARTH_RADIUS + alt1
    r2 = EARTH_RADIUS + alt2
    dv_total = mission_total_delta_v(alt1, alt2, params["annual_rate"])
    coast_s = hohmann_coast_time(r1, r2)
    coast_str = format_duration(coast_s)
    
    print(f"\n ► {mission_name}")
    print(f"   Total Δv: {dv_total:.1f} m/s | Spacecraft Wet Mass: {M0_KG:.0f} kg")
    print(f"   {'Thruster Technology':<26} {'Isp (s)':>9} {'Exhaust Vel':>15} {'Prop. Mass':>14} {'Burn Time':>12} {'Transit Duration':>18}")
    print("   " + "-" * 100)
    
    for name, isp, eta, power, thrust, mode in THRUSTERS:
        v_e = exhaust_velocity(isp)  # Now actively used in the table!
        mp = propellant_mass(dv_total, isp, M0_KG)
        if mode == "Electric":
            thrust = thrust_from_power(power, eta, v_e)
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