"""
Orbital coverage and topocentric geometry module.
Leverages vectorized NumPy operations for high-performance ground track generation.
"""

from skyfield.api import load, wgs84
from datetime import datetime, timedelta, timezone
import numpy as np

def compute_ground_track(satellite, duration_minutes=100, step_seconds=30):
    """
    Computes sub-satellite geodetic coordinates across an orbital time vector.
    
    Parameters:
        satellite: Skyfield EarthSatellite object.
        duration_minutes (int): Temporal evaluation window.
        step_seconds (int): Resolution of the time vector.

    Returns:
        tuple: (latitudes, longitudes) as lists. 
        Longitudes include NaN injections at the International Date Line to 
        prevent rendering artifacts (canvas-crossing lines) during plotting.
    """
    if duration_minutes <= 0 or step_seconds <= 0:
        raise ValueError("Duration and step size must be strictly positive.")

    ts = load.timescale()
    now = datetime.now(timezone.utc)
    total_seconds = int(duration_minutes * 60)

    # Vectorized time array generation
    time_list = [now + timedelta(seconds=i) for i in range(0, total_seconds, step_seconds)]
    t = ts.from_datetimes(time_list)

    # Vectorized propagation
    geocentric = satellite.at(t)
    subpoint = geocentric.subpoint()

    lats = subpoint.latitude.degrees
    lons = subpoint.longitude.degrees

    # Antimeridian wrap detection and NaN injection
    diff = np.diff(lons)
    wrap_indices = np.where(np.abs(diff) > 180)[0]

    if len(wrap_indices) > 0:
        lons = np.insert(lons, wrap_indices + 1, np.nan)
        lats = np.insert(lats, wrap_indices + 1, np.nan)

    return lats.tolist(), lons.tolist()

def get_passes_over_location(satellite, location_lat, location_lon, 
                             start_time=None, duration_days=1, 
                             horizon_degrees=10):
    """
    Computes topocentric satellite pass events over a designated ground station.
    Utilizes a state-machine search to guarantee robust event grouping 
    (Rise -> Culminate -> Set), ignoring partial passes at sequence boundaries.
    """
    ts = load.timescale()
    start_time = start_time or ts.now()
    location = wgs84.latlon(location_lat, location_lon)
    end_time = start_time + timedelta(days=duration_days)
    
    times, events = satellite.find_events(location, start_time, end_time, altitude_degrees=horizon_degrees)
    
    passes = []
    i = 0
    n = len(events) 

    while i < n - 2:
        # Require strict temporal sequence: Rise (0), Peak (1), Set (2)
        if events[i] == 0 and events[i+1] == 1 and events[i+2] == 2:
            rise_t, culm_t, set_t = times[i], times[i+1], times[i+2]
            
            difference = satellite - location
            alt, az, dist = difference.at(culm_t).altaz()
            
            passes.append({
                'rise_time': rise_t,
                'culminate_time': culm_t,
                'set_time': set_t,
                'max_elevation_deg': alt.degrees,
                'azimuth_deg': az.degrees,
                'distance_km': dist.km,
                'duration_seconds': (set_t - rise_t) * 86400 
            })
            i += 3  
        else:
            i += 1  # Resynchronize pointer on partial event
            
    return passes if passes else None