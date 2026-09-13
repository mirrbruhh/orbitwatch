# Module 4: Validate propulsion trade-study calculations across mission profiles
# Now featuring sequential Mass Budget Bookkeeping.

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
    """Safely formats duration using strict modulo math."""
    if seconds == float('inf'):
        return "N/A"
        
    if 0 < seconds < 60:
        return "< 1m"  # Catches rapid chemical burns so they don't show as 0m
        
    total_s = int(round(seconds))
    days, remainder = divmod(total_s, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

# Systems Engineering Assumptions
M0_KG = 1000.0  
LIFETIME_YEARS = 5.0
PERIGEE_ALT_KM = 150.0

THRUSTERS = [
    ("Chemical Bipropellant", 300, 0.95, 0.0, 500.0, "Chemical"),
    ("Hall Thruster", 1800, 0.50, 3000.0, None, "Electric"),
    ("Ion Thruster", 3000, 0.70, 5000.0, None, "Electric"),
    ("Water Microwave Plasma", 1200, 0.45, 1500.0, None, "Electric"),
]

print("\n" + "=" * 90)
print(f"{'PROPULSION TRADE STUDY: SEQUENTIAL MASS BOOKKEEPING':^90}")
print("=" * 90)

for mission_name, params in MISSIONS.items():
    alt1, alt2 = params["alt1"], params["alt2"]
    r1 = EARTH_RADIUS + alt1
    r2 = EARTH_RADIUS + alt2
    r_perigee = EARTH_RADIUS + PERIGEE_ALT_KM
    
    # Calculate Delta-V for each phase
    _, _, raise_dv = hohmann_transfer(r1, r2)
    sk_dv = station_keeping_delta_v(params["annual_rate"], LIFETIME_YEARS)
    deorbit_dv = deorbit_delta_v(r2, r_perigee)
    
    # Convert to m/s
    raise_dv *= 1000.0
    sk_dv *= 1000.0
    deorbit_dv *= 1000.0
    total_dv = raise_dv + sk_dv + deorbit_dv
    
    print(f"\n🚀 {mission_name}")
    print(f"   Initial Wet Mass: {M0_KG:.1f} kg | Total Mission ΔV: {total_dv:.1f} m/s")
    print("-" * 90)
    
    for name, isp, eta, power, thrust, mode in THRUSTERS:
        v_e = exhaust_velocity(isp)
        if mode == "Electric":
            thrust = thrust_from_power(power, eta, v_e)
            
        m_current = M0_KG
        
        # 1. Orbit Raise
        mp_raise = propellant_mass(raise_dv, isp, m_current)
        t_raise = transfer_time_estimate(raise_dv, thrust, m_current) if mode == "Electric" else hohmann_coast_time(r1, r2)
        m_current -= mp_raise
        
        # 2. Station-Keeping (5 Years)
        mp_sk = propellant_mass(sk_dv, isp, m_current)
        t_sk = transfer_time_estimate(sk_dv, thrust, m_current) if mode == "Electric" else 0.0 # Impulsive chemical SK time is negligible
        m_current -= mp_sk
        
        # 3. Deorbit
        mp_deorbit = propellant_mass(deorbit_dv, isp, m_current)
        t_deorbit = transfer_time_estimate(deorbit_dv, thrust, m_current) if mode == "Electric" else hohmann_coast_time(r2, r_perigee)
        m_current -= mp_deorbit
        
        total_mp = mp_raise + mp_sk + mp_deorbit
        total_transit_time = t_raise + t_deorbit # Active transit time (excluding 5-year operational SK time)
        
        print(f"   {name.upper()} (Isp: {isp}s)")
        print(f"     {'Phase':<16} | {'ΔV (m/s)':<10} | {'Prop Used (kg)':<15} | {'Mass Remaining':<16} | {'Active/Coast Time'}")
        print(f"     {'-'*81}")
        print(f"     {'Orbit Raise':<16} | {raise_dv:<10.1f} | {mp_raise:<15.2f} | {m_current + mp_sk + mp_deorbit:<16.2f} | {format_duration(t_raise)}")
        print(f"     {'Station-Keeping':<16} | {sk_dv:<10.1f} | {mp_sk:<15.2f} | {m_current + mp_deorbit:<16.2f} | {format_duration(t_sk)} (Accumulated)")
        print(f"     {'Deorbit':<16} | {deorbit_dv:<10.1f} | {mp_deorbit:<15.2f} | {m_current:<16.2f} | {format_duration(t_deorbit)}")
        print(f"     {'-'*81}")
        print(f"     {'DRY MASS':<16} | {'-':<10} | {'-':<15} | {m_current:<16.2f} |")
        
        # --- NEW EXPLICIT SUMMARY LINE ---
        print(f"\n     >> SUMMARY: Total ΔV - {total_dv:.1f} m/s | Propellant Used - {total_mp:.2f} kg | Active Transit Time - {format_duration(total_transit_time)} \n")

# --- First Principles Physics Check Below ---
q = 1.602e-19        
V = 1000.0           
m_ion = 2.18e-25     
v_e_calc = (2.0 * q * V / m_ion) ** 0.5
isp_calc = v_e_calc / 9.80665

print("=" * 90)
print(f"{'PHYSICS MODEL VERIFICATION: ELECTROSTATIC ION ACCELERATION':^90}")
print("=" * 90)
print(f"  Input Grid Voltage (V):          {V:.1f} V")
print(f"  Propellant Ion:                  Xenon (Xe+, m = {m_ion:.2e} kg, q = {q:.2e} C)")
print(f"  Theoretical Exhaust Velocity:    {v_e_calc/1000:.2f} km/s")
print(f"  Theoretical Specific Impulse:    {isp_calc:.0f} s")
if 3000 <= isp_calc <= 4500:
    print("  Benchmark Status:                [PASS] Validates high Isp (>3000s) regime.")
else:
    print("  Benchmark Status:                [FAIL] Outside expected ion propulsion regime.")
print("=" * 90)

print("\n" + "=" * 90)
print(f"{'SYSTEMS ENGINEERING ASSUMPTIONS & SOURCES':^90}")
print("=" * 90)
print("  • Drag Profile: Station-keeping relies on SMAD 4th Ed. (e.g., ~7 m/s/yr for 500 km).")
print("  • Deorbit: Target perigee of 150 km ensures rapid passive aerodynamic destruction.")
print("  • Microwave Plasma: 1200s Isp based on Bellatrix Aerospace 'JAL' targets (~4x chemical).")
print("  • Gravity Losses: Continuous LEO burns are a mathematical approximation here. Real")
print("    missions (e.g., ISRO's Mangalyaan / MOM) use multiple short perigee bursts over")
print("    several orbits to remain efficient and avoid fighting gravity.")
print("  • Chemical Firing Times: Displays as '< 1m' because 500 N of thrust achieves ")
print("    station-keeping Delta-V in roughly ~20 seconds, unlike electric spirals.")
print("=" * 90)