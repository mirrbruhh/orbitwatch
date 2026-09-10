# validate_propulsion.py
# Module 4: Validate propulsion trade-study calculations

from src.propulsion import propellant_mass, transfer_time_estimate, exhaust_velocity, thrust_from_power

# ---------------------------------------------------------------------
# Utility: Format seconds into a human-readable duration
# ---------------------------------------------------------------------
def format_duration(seconds):
    if seconds == float('inf'):
        return "N/A"
    days = int(seconds // 86400)
    remaining = seconds % 86400
    hours = int(remaining // 3600)
    remaining = remaining % 3600
    minutes = int(remaining // 60)
    
    if days > 0:
        return f"{days} days {hours} hr"
    elif hours > 0:
        return f"{hours} hr {minutes} mins"
    else:
        return f"{minutes} mins "

# ---------------------------------------------------------------------
# Mission Parameters (from Module 3)
# ---------------------------------------------------------------------
# Mission A: Indian Smallsat (~190 m/s total)
MISSION_A_DELTA_V = 190.0   # m/s
# Mission B: Ambitious Mission (~840 m/s total)
MISSION_B_DELTA_V = 840.0   # m/s

# Satellite wet mass (common assumption)
M0_KG = 1000.0  # kg

# ---------------------------------------------------------------------
# Thruster Parameters
# ---------------------------------------------------------------------
# Format: (Name, Isp_s, Efficiency, Power_W, Thrust_N)
# Note: Thrust and Power are typical values for small satellites.
THRUSTERS = [
    ("Chemical Bipropellant", 300, 0.95, 0.0, 500.0),  # Power not applicable for chemical
    ("Hall Thruster", 1800, 0.55, 3000.0, 0.5),
    ("Ion Thruster", 3000, 0.70, 5000.0, 0.2),
    ("Water Microwave Plasma", 1200, 0.45, 1500.0, 0.1),  # Bellatrix Aerospace spec
]

# ---------------------------------------------------------------------
# Calculate for Mission A
# ---------------------------------------------------------------------
print("\n" + "=" * 80)
print(" PROPULSION TRADE STUDY")
print("=" * 80)
print("\n Mission A (Indian Smallsat):")
print(f"  Total Delta-V: {MISSION_A_DELTA_V} m/s")
print(f"  Satellite Wet Mass: {M0_KG} kg")
print()

print("  Thruster Type          Propellant Mass (kg)     Transfer Time Estimate")
print("  " + "-" * 80)

for name, isp, eta, power, thrust in THRUSTERS:
    mp = propellant_mass(MISSION_A_DELTA_V, isp, M0_KG)
    v_e = exhaust_velocity(isp)
    
    # Estimate transfer time (only meaningful for electric thrusters)
    if thrust > 0:
        time_s = transfer_time_estimate(MISSION_A_DELTA_V, thrust, M0_KG)
        time_str = format_duration(time_s)
    else:
        time_str = "Instant"
    
    print(f"  {name:<22} {mp:>12.1f} kg        {time_str:>20}")

# ---------------------------------------------------------------------
# Calculate for Mission B
# ---------------------------------------------------------------------
print("\n" + "-" * 80)
print("\n Mission B (Ambitious Mission):")
print(f"  Total Delta-V: {MISSION_B_DELTA_V} m/s")
print(f"  Satellite Wet Mass: {M0_KG} kg")
print()

print("  Thruster Type          Propellant Mass (kg)     Transfer Time Estimate")
print("  " + "-" * 80)

for name, isp, eta, power, thrust in THRUSTERS:
    mp = propellant_mass(MISSION_B_DELTA_V, isp, M0_KG)
    v_e = exhaust_velocity(isp)
    
    if thrust > 0:
        time_s = transfer_time_estimate(MISSION_B_DELTA_V, thrust, M0_KG)
        time_str = format_duration(time_s)
    else:
        time_str = "Instant"
    
    print(f"  {name:<22} {mp:>12.1f} kg        {time_str:>20}")

# ---------------------------------------------------------------------
# Additional Physics: Derivation Check for Ion Thruster
# ---------------------------------------------------------------------
print("\n" + "=" * 80)
print("ION THRUSTER EXIT VELOCITY DERIVATION")
print("=" * 80)
print(f"""
An ion thruster applies a high voltage V across two grids.
A singly-charged ion of charge q sitting in this voltage gains electrical
potential energy equal to qV.
\nThis electrical energy is converted entirely into kinetic energy:
    1/2 * m_ion * v_e^2 = qV
\nSolving for the exhaust velocity:
    v_e = sqrt(2 * q * V / m_ion)
""")

# Example calculation for Xenon
q = 1.6e-19          # C (charge of a singly-ionized ion)
V = 1000.0           # V (accelerating voltage)
m_ion = 2.18e-25     # kg (mass of a Xenon ion)
v_e_calc = (2 * q * V / m_ion) ** 0.5
print(f"Example (Xenon, V=1000V): v_e = {v_e_calc/1000:.2f} km/s")
print(f"Equivalent Isp = {v_e_calc / 9.80665:.0f} s")
print("""
(This confirms the high Isp of ion thrusters ~3000s,
though real thrusters use multiple charged ions and more complex physics.)
""")