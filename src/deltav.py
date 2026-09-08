# Module 3: Mission Delta-V Scenarios
import math

# Constants (in km and km/s)
GM_EARTH = 398600.4418  # km^3/s^2
EARTH_RADIUS = 6378.0   # km

def vis_viva(r, a):
    """
    Compute orbital speed using the vis-viva equation.
    
    Parameters:
        r (float): Current distance from Earth's center (km).
        a (float): Semi-major axis of the orbit (km).
    
    Returns:
        float: Orbital speed in km/s.
    """
    return math.sqrt(GM_EARTH * (2.0 / r - 1.0 / a))

def hohmann_transfer(r1, r2):
    """
    Compute total delta-v for a Hohmann transfer between two circular orbits.
    
    Parameters:
        r1 (float): Radius of the initial circular orbit (km).
        r2 (float): Radius of the target circular orbit (km).
    
    Returns:
        tuple: (dv1, dv2, total_dv) all in km/s.
            dv1: Burn at r1 to enter transfer ellipse.
            dv2: Burn at r2 to circularize.
            total_dv: Sum of both burns.
    """
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
    
    # Burn 1: Increase speed at r1 to enter the ellipse
    dv1 = v1_transfer - v1_circular
    
    # Burn 2: Increase speed at r2 to circularize
    dv2 = v2_circular - v2_transfer
    
    total_dv = dv1 + dv2
    
    return dv1, dv2, total_dv