import math

# Constants
GM_EARTH = 398600.4418  # Earth gravitational parameter (km^3/s^2)
EARTH_RADIUS = 6378.0   # Earth mean equatorial radius (km)

def vis_viva(r, a):
    """
    Compute orbital velocity using the vis-viva equation.

    Raises a clear ValueError instead of computing nonsense (a negative
    number under a square root) for hyperbolic or otherwise unphysical
    combinations of r and a.
    """
    radicand = 2.0 / r - 1.0 / a
    if radicand < 0.0:
        raise ValueError(f"Unphysical geometry: r={r}, a={a} produces negative radicand.")
    return math.sqrt(GM_EARTH * radicand)

def hohmann_transfer(r1, r2):
    """
    Compute total delta-v for a two-impulse Hohmann transfer between two 
    circular coplanar orbits.
    
    Supports both orbit raising (r2 > r1) and orbit lowering (r2 < r1) by 
    evaluating absolute velocity differences.
    """
    if r1 <= 0.0 or r2 <= 0.0:
        raise ValueError("Orbital radii must be strictly positive.")

    v1_circular = vis_viva(r1, r1)
    v2_circular = vis_viva(r2, r2)
    a_transfer = (r1 + r2) / 2.0
    v1_transfer = vis_viva(r1, a_transfer)
    v2_transfer = vis_viva(r2, a_transfer)
    
    # Absolute difference handles both acceleration (raise) and deceleration (lower)
    dv1 = abs(v1_transfer - v1_circular)
    dv2 = abs(v2_circular - v2_transfer)
    
    return dv1, dv2, dv1 + dv2

def hohmann_coast_time(r1, r2):
    """
    Compute orbital coast duration (half the elliptical period) in seconds.
    Represents the physical transit time between r1 and r2.
    """
    if r1 <= 0.0 or r2 <= 0.0:
        raise ValueError("Orbital radii must be strictly positive.")
        
    a_transfer = (r1 + r2) / 2.0
    period_seconds = 2.0 * math.pi * math.sqrt((a_transfer ** 3) / GM_EARTH)
    return period_seconds / 2.0

def station_keeping_delta_v(annual_rate_m_s, years):
    """Compute total station-keeping delta-v over a mission lifetime."""
    if annual_rate_m_s < 0.0 or years < 0.0:
        raise ValueError("Annual rate and lifetime duration must be non-negative.")
    return (annual_rate_m_s * years) / 1000.0

def deorbit_delta_v(r1, r_perigee):
    """
    Compute the single retrograde delta-v required to lower perigee into 
    Earth's dense atmosphere for end-of-life destructive disposal.
    """
    if r_perigee >= r1:
        raise ValueError("Target perigee radius must be strictly less than initial orbit radius.")
    if r_perigee <= 0.0:
        raise ValueError("Perigee radius must be positive.")
    
    v_circular = vis_viva(r1, r1)
    a_transfer = (r1 + r_perigee) / 2.0
    v_transfer = vis_viva(r1, a_transfer)
    
    return v_circular - v_transfer