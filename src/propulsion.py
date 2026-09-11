import math

# Standard gravity (m/s^2)
G0 = 9.80665  

def exhaust_velocity(isp_s):
    """
    Compute exhaust velocity from specific impulse: v_e = Isp * g0.

    Parameters:
        isp_s (float): Specific impulse in seconds.

    Returns:
        float: Exhaust velocity in m/s.
    """
    if isp_s <= 0.0:
        raise ValueError("Specific impulse must be strictly positive.")
    return isp_s * G0

def propellant_mass(delta_v_m_s, isp_s, m0_kg):
    """
    Compute propellant mass required for a given delta-v using the Tsiolkovsky rocket equation :
     m_p = m0 * (1 - exp(-delta_v / v_e))

    Parameters:
        delta_v_m_s (float): Required delta-v in m/s.
        isp_s (float): Specific impulse of the thruster in seconds.
        m0_kg (float): Initial wet mass of the satellite in kg.

    Returns:
        float: Propellant mass in kg.
    """
    if delta_v_m_s < 0.0:
        raise ValueError("Delta-V magnitude cannot be negative.")
    if m0_kg <= 0.0:
        raise ValueError("Initial wet mass must be strictly positive.")

    v_e = exhaust_velocity(isp_s)
    mf = m0_kg * math.exp(-delta_v_m_s / v_e)
    return m0_kg - mf

def thrust_from_power(power_w, eta, v_e_m_s):
    """
    Compute thrust from electrical power for an electric thruster:
    F = 2 * P * eta / v_e

    Parameters:
        power_w (float): Input electrical power in Watts.
        eta (float): Thruster efficiency (0 to 1).
        v_e_m_s (float): Exhaust velocity in m/s.

    Returns:
        float: Thrust in Newtons.
    """
    if power_w < 0.0 or not (0.0 < eta <= 1.0) or v_e_m_s <= 0.0:
        raise ValueError("Invalid power, efficiency, or exhaust velocity inputs.")
    return 2.0 * power_w * eta / v_e_m_s

def transfer_time_estimate(delta_v_m_s, thrust_n, m0_kg):
    """
    Estimate active burn duration for a continuous burn:
    t = delta_v / (thrust / m0).
    Assumes constant mass m0 (first-order conservative estimate).

    Parameters:
        delta_v_m_s (float): Required delta-v in m/s.
        thrust_n (float): Thrust in Newtons.
        m0_kg (float): Satellite wet mass in kg.

    Returns:
        float: Transfer time in seconds.
    """
    if thrust_n <= 0.0 or m0_kg <= 0.0:
        return float('inf')
    acceleration = thrust_n / m0_kg
    return delta_v_m_s / acceleration