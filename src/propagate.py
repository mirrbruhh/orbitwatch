from skyfield.api import load, EarthSatellite

def propagate(tle_line1, tle_line2, name, when):
    ts = load.timescale()
    sat = EarthSatellite(tle_line1, tle_line2, name, ts)
    geo = sat.at(when)
    return geo.position.km, geo.velocity.km_per_s