import math

# Constants
G0 = 9.80665  # Standard gravity (m/s^2)

def exhaust_velocity(isp_s):
    """
    Compute exhaust velocity from specific impulse.

    Parameters:
        isp_s (float): Specific impulse in seconds.

    Returns:
        float: Exhaust velocity in m/s.
    """
    return isp_s * G0

def propellant_mass(delta_v_m_s, isp_s, m0_kg):
    """
    Compute propellant mass required for a given delta-v using the Tsiolkovsky rocket equation.

    Parameters:
        delta_v_m_s (float): Required delta-v in m/s.
        isp_s (float): Specific impulse of the thruster in seconds.
        m0_kg (float): Initial wet mass of the satellite in kg.

    Returns:
        float: Propellant mass in kg.
    """
    v_e = exhaust_velocity(isp_s)
    mf = m0_kg * math.exp(-delta_v_m_s / v_e)
    mp = m0_kg - mf
    return mp

def thrust_from_power(power_w, eta, v_e_m_s):
    """
    Compute thrust from electrical power for an electric thruster.

    Parameters:
        power_w (float): Input electrical power in Watts.
        eta (float): Thruster efficiency (0 to 1).
        v_e_m_s (float): Exhaust velocity in m/s.

    Returns:
        float: Thrust in Newtons.
    """
    return 2.0 * power_w * eta / v_e_m_s

def transfer_time_estimate(delta_v_m_s, thrust_n, m0_kg):
    """
    Estimate transfer time for a low-thrust maneuver.

    Parameters:
        delta_v_m_s (float): Required delta-v in m/s.
        thrust_n (float): Thrust in Newtons.
        m0_kg (float): Satellite wet mass in kg.

    Returns:
        float: Transfer time in seconds.
    """
    acceleration = thrust_n / m0_kg
    if acceleration == 0.0:
        return float('inf')
    return delta_v_m_s / acceleration