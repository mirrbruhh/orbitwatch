"""
OrbitWatch dashboard.

Ties together the four modules built over the course of the project:
  - src/propagate.py   (Day 1: where is the satellite right now)
  - src/coverage.py    (Day 2: ground track + passes over Mumbai)
  - src/deltav.py      (Day 3: delta-v budget per mission)
  - src/propulsion.py  (Day 4: propellant mass / burn time per thruster)

Run locally with: streamlit run app.py
"""

import os
import time
from datetime import timedelta

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from skyfield.api import EarthSatellite, load

from fetch_tle import FILE_PATH as DATA_FILE
from fetch_tle import fetch_and_cache_tle
from src.coverage import compute_ground_track, get_passes_over_location
from src.deltav import (
    EARTH_RADIUS,
    deorbit_delta_v,
    hohmann_coast_time,
    hohmann_transfer,
    station_keeping_delta_v,
)
from src.missions import MISSIONS
from src.propagate import propagate
from src.propulsion import (
    exhaust_velocity,
    propellant_mass,
    thrust_from_power,
    transfer_time_estimate,
)

st.set_page_config(page_title="OrbitWatch", page_icon="satellite", layout="wide")

MAX_TLE_AGE_SECONDS = 24 * 3600
MUMBAI_LAT, MUMBAI_LON = 19.0760, 72.8777
PERIGEE_ALT_KM = 150.0
M0_KG = 1000.0

LIFETIME_YEARS = 5.0

# Mission parameters live in src/missions.py, shared with every
# validate_*.py script, so altitude and station-keeping assumptions stay
# consistent between the dashboard and the validation scripts.

# (Name, Isp_s, Efficiency, Power_W, Mode). Thrust for electric thrusters
# is derived from power and efficiency rather than assumed independently,
# so it can't imply an efficiency above 100%.
THRUSTERS = [
    ("Chemical Bipropellant", 300, 0.95, None, "Chemical"),
    ("Hall Thruster", 1800, 0.50, 3000.0, "Electric"),
    ("Ion Thruster", 3000, 0.70, 5000.0, "Electric"),
    ("Water Microwave Plasma", 1200, 0.45, 1500.0, "Electric"),  # Isp per Bellatrix's public 4x-chemical-Isp claim
]

CHEMICAL_THRUST_N = 500.0  # only used for the Chemical row's burn-time estimate


def format_duration(seconds):
    if seconds == float("inf"):
        return "N/A"
    days = int(seconds // 86400)
    remaining = seconds % 86400
    hours = int(remaining // 3600)
    remaining = remaining % 3600
    minutes = int(round(remaining / 60))
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


@st.cache_data(ttl=3600)
def load_tle():
    """Fetch a fresh TLE at most once an hour; reuse the cached file otherwise."""
    stale = os.path.exists(DATA_FILE) and (time.time() - os.path.getmtime(DATA_FILE)) > MAX_TLE_AGE_SECONDS
    if not os.path.exists(DATA_FILE) or stale:
        fetch_and_cache_tle()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines[0], lines[1], lines[2]


@st.cache_resource
def build_satellite(name, line1, line2):
    ts = load.timescale()
    return ts, EarthSatellite(line1, line2, name, ts)


def mission_delta_v(mission):
    """Return (raise_dv_m_s, stationkeep_dv_m_s, deorbit_dv_m_s, total_m_s, r1, r2)."""
    r1 = EARTH_RADIUS + mission["alt1"]
    r2 = EARTH_RADIUS + mission["alt2"]
    _, _, raise_dv_km_s = hohmann_transfer(r1, r2)

    sk_dv_km_s = station_keeping_delta_v(mission["annual_rate"], LIFETIME_YEARS)

    r_deorbit = r2  # deorbits from wherever it ends up operating, not the starting altitude
    r_perigee = EARTH_RADIUS + PERIGEE_ALT_KM
    deorbit_dv_km_s = deorbit_delta_v(r_deorbit, r_perigee)

    raise_m_s = raise_dv_km_s * 1000.0
    sk_m_s = sk_dv_km_s * 1000.0
    deorbit_m_s = deorbit_dv_km_s * 1000.0
    return raise_m_s, sk_m_s, deorbit_m_s, raise_m_s + sk_m_s + deorbit_m_s, r1, r2


# ---------------------------------------------------------------------
# Load satellite once per session
# ---------------------------------------------------------------------
try:
    name, line1, line2 = load_tle()
    ts, satellite = build_satellite(name, line1, line2)
    tle_error = None
except Exception as exc:  # noqa: BLE001 - surfaced to the user below, not swallowed
    name, line1, line2, ts, satellite = None, None, None, None, None
    tle_error = str(exc)

st.title("OrbitWatch")
st.caption("Tracking the ISS and modeling propulsion trade-offs for small satellite missions")

if tle_error:
    st.error(f"Couldn't load a TLE: {tle_error}")
    st.stop()

tab_tracking, tab_coverage, tab_mission = st.tabs(["Tracking", "Coverage", "Delta-V & Propulsion"])

# ---------------------------------------------------------------------
# Tab 1: Tracking
# ---------------------------------------------------------------------
with tab_tracking:
    st.subheader(f"Live position: {name}")

    pos_km, vel_km_s = propagate(line1, line2, name, ts.now())
    geo = satellite.at(ts.now())
    subpoint = geo.subpoint()

    col_metrics, col_plot = st.columns([1, 2])
    with col_metrics:
        st.metric("Altitude", f"{subpoint.elevation.km:.1f} km")
        st.metric("Speed", f"{(vel_km_s[0]**2 + vel_km_s[1]**2 + vel_km_s[2]**2) ** 0.5:.2f} km/s")
        st.metric("Sub-satellite point", f"{subpoint.latitude.degrees:.1f}, {subpoint.longitude.degrees:.1f}")
        orbits = st.slider("Orbits to show", 1, 4, 3)

    with col_plot:
        lats, lons = compute_ground_track(satellite, duration_minutes=93 * orbits)
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.plot(lons, lats, color="crimson", linewidth=1.5)
        ax.set_xlim([-180, 180])
        ax.set_ylim([-90, 90])
        ax.set_xlabel("Longitude (deg)")
        ax.set_ylabel("Latitude (deg)")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_title(f"Ground track, next {orbits} orbit(s)")
        st.pyplot(fig)
        st.caption(
            "Simplified world outline (gridlines only), not a full map projection - "
            "each successive orbit shifts west as Earth rotates underneath it."
        )

# ---------------------------------------------------------------------
# Tab 2: Coverage
# ---------------------------------------------------------------------
with tab_coverage:
    st.subheader("Passes over Mumbai")

    passes_24h = get_passes_over_location(satellite, MUMBAI_LAT, MUMBAI_LON, duration_days=1, horizon_degrees=10)

    if not passes_24h:
        st.write("No passes above a 10 degree horizon in the next 24 hours.")
    else:
        rows = []
        for p in passes_24h:
            rows.append({
                "Rise (UTC)": p["rise_time"].utc_strftime("%Y-%m-%d %H:%M"),
                "Peak elevation": f"{p['max_elevation_deg']:.1f} deg",
                "Set (UTC)": p["set_time"].utc_strftime("%Y-%m-%d %H:%M"),
                "Duration": f"{p['duration_seconds'] / 60:.1f} min",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()
    st.caption("7-day revisit metric")
    passes_7d = get_passes_over_location(satellite, MUMBAI_LAT, MUMBAI_LON, duration_days=7, horizon_degrees=10)
    if passes_7d:
        revisit_hours = (7.0 * 24.0) / len(passes_7d)
        st.metric("Average revisit interval", f"{revisit_hours:.1f} hours", help=f"Based on {len(passes_7d)} passes over 7 days")
    else:
        st.write("No passes detected over the 7-day window.")

# ---------------------------------------------------------------------
# Tab 3: Delta-V budget + propulsion trade study
# ---------------------------------------------------------------------
with tab_mission:
    mission_label = st.selectbox("Mission scenario", list(MISSIONS.keys()))
    mission = MISSIONS[mission_label]

    raise_m_s, sk_m_s, deorbit_m_s, total_m_s, r1, r2 = mission_delta_v(mission)

    st.subheader("Delta-V budget")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Raise/lower", f"{raise_m_s:.1f} m/s")
    col_b.metric(f"Station-keep ({LIFETIME_YEARS:.0f} yr)", f"{sk_m_s:.1f} m/s")
    col_c.metric("Deorbit", f"{deorbit_m_s:.1f} m/s")
    col_d.metric("Total", f"{total_m_s:.0f} m/s")

    st.divider()
    st.subheader("Propulsion trade study")
    st.caption(f"Propellant mass and burn/transit time for this mission's {total_m_s:.0f} m/s budget, {M0_KG:.0f} kg wet mass")

    coast_s = hohmann_coast_time(r1, r2)
    rows = []
    chart_data = {}
    for tname, isp, eta, power, mode in THRUSTERS:
        v_e = exhaust_velocity(isp)
        mp = propellant_mass(total_m_s, isp, M0_KG)
        if mode == "Electric":
            thrust = thrust_from_power(power, eta, v_e)
        else:
            thrust = CHEMICAL_THRUST_N
        burn_s = transfer_time_estimate(total_m_s, thrust, M0_KG)
        transit = f"Hohmann (~{format_duration(coast_s)})" if mode == "Chemical" else f"Spiral (~{format_duration(burn_s)})"

        rows.append({
            "Thruster": tname,
            "Isp (s)": isp,
            "Exhaust velocity": f"{v_e / 1000:.2f} km/s",
            "Propellant mass": f"{mp:.1f} kg",
            "Burn time": format_duration(burn_s),
            "Transit": transit,
        })
        chart_data[tname] = mp

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.bar_chart(chart_data)

    with st.expander("Why thrust is derived, not assumed"):
        st.write(
            "Each electric thruster's thrust comes from `thrust_from_power(power, eta, v_e)` "
            "rather than being a separate, independently chosen number. That keeps thrust, "
            "power, and efficiency mutually consistent: a thrust value picked without "
            "checking it against power and efficiency can quietly ask for more kinetic "
            "power out than electrical power in, which is physically impossible."
        )
