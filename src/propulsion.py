"""
Spacecraft propulsion physics engine.
Implements Tsiolkovsky equations and electrodynamic performance metrics.
"""

import math

G0 = 9.80665  # Standard gravity (m/s^2)

def exhaust_velocity(isp_s):
    """Derives physical exhaust velocity from specific impulse."""
    if isp_s <= 0.0:
        raise ValueError("Specific impulse must be strictly positive.")
    return isp_s * G0

def propellant_mass(delta_v_m_s, isp_s, m0_kg):
    """
    Evaluates required propellant mass via the Tsiolkovsky rocket equation.
    m_p = m0 * (1 - exp(-delta_v / v_e))
    """
    if delta_v_m_s < 0.0:
        raise ValueError("Delta-V magnitude cannot be negative.")
    if m0_kg <= 0.0:
        raise ValueError("Initial spacecraft mass must be strictly positive.")

    v_e = exhaust_velocity(isp_s)
    mf = m0_kg * math.exp(-delta_v_m_s / v_e)
    return m0_kg - mf

def thrust_from_power(power_w, eta, v_e_m_s):
    """
    Derives physical thrust from available bus power and thruster efficiency.
    F = 2 * P * eta / v_e
    """
    if power_w < 0.0 or not (0.0 < eta <= 1.0) or v_e_m_s <= 0.0:
        raise ValueError("Invalid power, efficiency, or exhaust velocity metrics.")
    return 2.0 * power_w * eta / v_e_m_s

def transfer_time_estimate(delta_v_m_s, thrust_n, m0_kg):
    """
    First-order approximation of continuous active burn duration.
    Assumes invariant mass (m0) for conservative systems engineering estimates.
    """
    if thrust_n <= 0.0 or m0_kg <= 0.0:
        return float('inf')
    acceleration = thrust_n / m0_kg
    return delta_v_m_s / acceleration


def format_duration(seconds):
    """
    Format a duration in seconds as a compact string (e.g. "~ 13d 1h").
    Shared by app.py and validate_propulsion.py so both report the same
    number the same way, rather than keeping two copies that can drift.
    """
    if seconds == float("inf"):
        return "N/A"

    if 0 < seconds < 60:
        return "< 1m"  # catches rapid chemical burns so they don't show as 0m

    total_s = int(round(seconds))
    days, remainder = divmod(total_s, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60

    if days > 0:
        return f"~ {days}d {hours}h"
    elif hours > 0:
        return f"~ {hours}h {minutes}m"
    return f"~ {minutes}m"