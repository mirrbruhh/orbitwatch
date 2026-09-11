# Module 3: Mission Delta-V Scenarios
import math

# Constants (in km and km/s)
GM_EARTH = 398600.4418  # Earth gravitational parameter (km^3/s^2)
EARTH_RADIUS = 6378.0   # Earth mean equatorial radius (km)

def vis_viva(r, a):
    """
    Compute orbital velocity using the vis-viva equation.
    Guards against hyperbolic or unphysical geometry.
    
    Parameters:
        r (float): Current distance from Earth's center (km).
        a (float): Semi-major axis of the orbit (km).
    
    Returns:
        float: Orbital velocity in km/s.
    """
    radicand = 2.0 / r - 1.0 / a
    if radicand < 0.0:
        raise ValueError(f"Unphysical geometry: r={r}, a={a} produces negative radicand.")
    return math.sqrt(GM_EARTH * radicand)

def hohmann_transfer(r1, r2):
    """
    Compute total delta-v for a two-impulse Hohmann transfer between two 
    circular coplanar orbits.
    
    Supports both:
    - Orbit raising (r2 > r1): Burn 1 injects into transfer; Burn 2 circularizes at r2.
    - Orbit lowering (r2 < r1): Burn 1 decelerates into transfer; Burn 2 circularizes at r2.
    
    Parameters:
        r1 (float): Radius of the initial circular orbit (km).
        r2 (float): Radius of the target circular orbit (km).
    
    Returns:
        tuple: (dv1, dv2, total_dv) all in km/s.
            dv1: Burn at r1 to enter transfer ellipse.
            dv2: Burn at r2 to circularize.
            total_dv: Sum of both burns.
    """
    if r1 <= 0.0 or r2 <= 0.0:
        raise ValueError("Orbital radii must be strictly positive.")

    # Speed in initial circular orbit
    v1_circular = vis_viva(r1, r1)  # For a circle, a = r
    
    # Speed in target circular orbit
    v2_circular = vis_viva(r2, r2)
    
    # Semi-major axis of the transfer ellipse
    a_transfer = (r1 + r2) / 2.0
    
    # Speed at r1 on the transfer ellipse
    v1_transfer = vis_viva(r1, a_transfer)
    
    # Speed at r2 on the transfer ellipse
    v2_transfer = vis_viva(r2, a_transfer)
    
    # Burn 1: Delta-v magnitude at r1 to inject into the transfer ellipse
    dv1 = abs(v1_transfer - v1_circular)
    
    # Burn 2: Delta-v magnitude at r2 to circularize at the target orbit
    dv2 = abs(v2_circular - v2_transfer)
    
    total_dv = dv1 + dv2
    
    return dv1, dv2, total_dv

def hohmann_coast_time(r1, r2):
    """
    Compute orbital coast duration (half the elliptical period) in seconds.
    This represents the physical transit time between r1 and r2.
    """
    a_transfer = (r1 + r2) / 2.0
    period_seconds = 2.0 * math.pi * math.sqrt((a_transfer ** 3) / GM_EARTH)
    return period_seconds / 2.0

def station_keeping_delta_v(annual_rate_m_s, years):
    """
    Compute total station-keeping delta-v over a mission lifetime.

    This is a generic formula. The annual rate depends on the altitude,
    solar activity, satellite ballistic coefficient, and drag profile.
    Use published mission data (e.g., SMAD, ESA/NASA reports) to determine
    the appropriate annual rate for your specific scenario.

    Parameters:
        annual_rate_m_s (float): Annual delta-v required for station-keeping (m/s).
        years (float): Mission lifetime in years.

    Returns:
        float: Total delta-v in km/s.
    """
    if annual_rate_m_s < 0.0 or years < 0.0:
        raise ValueError("Annual rate and lifetime duration must be non-negative.")
    return (annual_rate_m_s * years) / 1000.0 # Convert to km/s

def deorbit_delta_v(r1, r_perigee):
    """
    Compute the single retrograde delta-v required to lower perigee into 
    Earth's dense atmosphere (typically 100-150 km) for destructive disposal.

    ENGINEERING NOTE:
    Unlike operational orbit lowering (which requires Burn 2 at perigee to 
    re-circularize), deorbiting requires only Burn 1. Aerodynamic drag at perigee 
    provides passive deceleration to complete destruction.

    Parameters:
        r1 (float): Initial circular orbit radius (km).
        r_perigee (float): Target perigee radius (km) (must be < r1).

    Returns:
        float: Retrograde delta-v in km/s (positive value).
    """
    if r_perigee >= r1:
        raise ValueError("Target perigee radius must be strictly less than initial orbit radius.")
    if r_perigee <= 0.0:
        raise ValueError("Perigee radius must be positive.")
    
    # Circular speed at r1
    v_circular = vis_viva(r1, r1)
    
    # Semi-major axis of the deorbit transfer ellipse
    a_transfer = (r1 + r_perigee) / 2.0
    
    # Speed on the transfer ellipse at r1 (which is the apogee of the ellipse)
    v_transfer = vis_viva(r1, a_transfer)
    
    # Retrograde burn: slow down
    return v_circular - v_transfer