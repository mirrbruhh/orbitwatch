"""
Core orbital propagation module utilizing the SGP4 mathematical model.
"""

from skyfield.api import load, EarthSatellite

def propagate(tle_line1, tle_line2, name, when):
    """
    Evaluates satellite state vectors at a specific epoch using SGP4.

    Parameters:
        tle_line1 (str): NORAD TLE line 1.
        tle_line2 (str): NORAD TLE line 2.
        name (str): Spacecraft identifier.
        when (Time): Skyfield Time object representing the target epoch.

    Returns:
        tuple: (position_km, velocity_km_s) as 3-element GCRS vectors.
    """
    ts = load.timescale()
    sat = EarthSatellite(tle_line1, tle_line2, name, ts)
    geo = sat.at(when)
    return geo.position.km, geo.velocity.km_per_s