from skyfield.api import load, EarthSatellite

def propagate(tle_line1, tle_line2, name, when):
    """
    Propagate satellite state vector to a specific epoch using SGP4.

    Parameters:
        tle_line1 (str): NORAD TLE line 1.
        tle_line2 (str): NORAD TLE line 2.
        name (str): Satellite identifier string.
        when (Time): Skyfield Time object.

    Returns:
        tuple: (position_km, velocity_km_s) as 3-element tuples in GCRS.
    """
    ts = load.timescale()
    sat = EarthSatellite(tle_line1, tle_line2, name, ts)
    geo = sat.at(when)
    return geo.position.km, geo.velocity.km_per_s