from skyfield.api import load,wgs84
from datetime import datetime, timedelta, timezone
import numpy as np

# Part a) :

def compute_ground_track(satellite, duration_minutes=95, step_seconds=30):
    """
    Compute latitude and longitude points of a satellite's ground track.
    
    Parameters:
        satellite: A Skyfield EarthSatellite object.
        duration_minutes (int): Total duration to sample (default 100 minutes).
        step_seconds (int): Time between samples in seconds (default 30 seconds).

    Returns:
        tuple: (latitudes, longitudes) as lists of floats.
               Longitudes are split with NaN at the International Date Line
               to prevent horizontal line artifacts when plotting.
    """
    ts = load.timescale()

    # 1. Generate the time steps as standard UTC datetimes
    now = datetime.now(timezone.utc)
    total_seconds = int(duration_minutes * 60)

    # Create a list of datetime objects: [now, now+30s, now+60s, ...]
    time_list = [now + timedelta(seconds=i) for i in range(0, total_seconds, step_seconds)]

    # Convert the entire list to Skyfield Time objects in one go (vectorized)
    t = ts.from_datetimes(time_list)

    # 2. Propagate all times at once (vectorized, far faster than a Python loop)
    geocentric = satellite.at(t)
    subpoint = geocentric.subpoint()

    # Extract the coordinates as NumPy arrays
    lats = subpoint.latitude.degrees
    lons = subpoint.longitude.degrees

    # 3. Insert NaN where longitude wraps across the +/-180 degree boundary
    #    This prevents Matplotlib from drawing a straight line across the map.
    diff = np.diff(lons)
    wrap_indices = np.where(np.abs(diff) > 180)[0]

    # np.insert with an array of indices is the correct, vectorized way.
    # It inserts a NaN after each crossing point without corrupting indices.
    if len(wrap_indices) > 0:
        lons = np.insert(lons, wrap_indices + 1, np.nan)
        lats = np.insert(lats, wrap_indices + 1, np.nan)

    # Return as Python lists (compatible with your existing plotting code)
    return lats.tolist(), lons.tolist()

# Part b) : 

def get_passes_over_location(satellite, location_lat, location_lon, 
                             start_time=None, duration_days=1, 
                             horizon_degrees=10):
    """
    Compute satellite passes over a specific location.

    Parameters:
        satellite: Skyfield EarthSatellite object.
        location_lat, location_lon: Latitude and longitude of the ground location (degrees).
        start_time: Skyfield Time object. If None, uses current time.
        duration_days (int): How many days to search for passes (default 1).
        horizon_degrees (int): Minimum elevation angle for a pass to count (default 10).

    Returns:
        list of dicts: Each dict contains 'rise_time', 'culminate_time', 'set_time', 
                        'max_elevation_deg', and 'duration_seconds'.
        None if no passes are found.
    """
    ts = load.timescale()
    
    # Set start time to now if not provided
    if start_time is None:
        start_time = ts.now()
    
    # Convert location to Skyfield's Topos object
    location = wgs84.latlon(location_lat, location_lon)
    
    # Define the end time
    end_time = start_time + timedelta(days=duration_days)
    
    # Find all events (rise, culminate, set) in the time window
    times, events = satellite.find_events(location, start_time, end_time, 
                                          altitude_degrees=horizon_degrees)
    
    # events: 0 = rise, 1 = culminate, 2 = set
    # We need to group them into complete passes (rise -> culminate -> set)
    passes = []
    for i in range(0, len(times) - 2, 3):
        # Ensure we have a complete triple (rise, culminate, set)
        if events[i] == 0 and events[i+1] == 1 and events[i+2] == 2:
            rise_t = times[i]
            culm_t = times[i+1]
            set_t = times[i+2]
            
            # Compute max elevation during this pass
            # We can sample the elevation at the culmination time, or do a fine search.
            # The simplest: propagate at culmination time and compute elevation.
            geo = satellite.at(culm_t)
            alt_deg = geo.subpoint().elevation.km  # This is altitude in km, not elevation angle.
            # Wait: `find_events` uses elevation angle (degrees above horizon).
            # To get the actual max elevation angle, we need to compute it at culmination.
            # Let's compute the elevation angle at the culmination time.
            alt, az, distance = (satellite - location).at(culm_t).altaz()
            max_elevation_deg = alt.degrees
            
            # Duration in seconds
            duration = (set_t - rise_t) * 86400  # timedelta in days, convert to seconds
            
            passes.append({
                'rise_time': rise_t,
                'culminate_time': culm_t,
                'set_time': set_t,
                'max_elevation_deg': max_elevation_deg,
                'duration_seconds': duration
            })
    
    return passes if passes else None