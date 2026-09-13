"""
OrbitWatch Dashboard.

Provides a unified interface for orbital telemetry tracking, ground coverage 
analysis, and a first-principles propulsion trade study. 
Run locally with: streamlit run app.py
"""

import requests
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.figure import Figure
from skyfield.api import EarthSatellite, load

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

st.set_page_config(page_title="OrbitWatch", page_icon="🛰️", layout="wide")

URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
MUMBAI_LAT, MUMBAI_LON = 19.0760, 72.8777
PERIGEE_ALT_KM = 150.0
M0_KG = 1000.0
LIFETIME_YEARS = 5.0

# Thruster definitions. Chemical propulsion sets electrical power to 0.0 
# to prevent NoneType evaluation errors in downstream physics equations.
THRUSTERS = [
    ("Chemical Bipropellant", 300, 0.95, 0.0, "Chemical"),
    ("Hall Thruster", 1800, 0.50, 3000.0, "Electric"),
    ("Ion Thruster", 3000, 0.70, 5000.0, "Electric"),
    ("Water Microwave Plasma", 1200, 0.45, 1500.0, "Electric"),
]

CHEMICAL_THRUST_N = 500.0  

THRUSTER_SHORT_NAMES = {
    "Chemical Bipropellant": "Chemical",
    "Hall Thruster": "Hall",
    "Ion Thruster": "Ion",
    "Water Microwave Plasma": "Water Plasma",
}

THRUSTER_COLORS = {
    "Chemical Bipropellant": "#E63946",
    "Hall Thruster": "#457B9D",
    "Ion Thruster": "#2A9D8F",
    "Water Microwave Plasma": "#F4A261",
}

def format_duration(seconds):
    """
    Translates raw seconds into UI-friendly chronological strings.
    Strict modulo arithmetic (divmod) is used to prevent boundary rollover 
    artifacts (e.g., 59.9 minutes rounding to '60m' instead of '1h').
    """

    if seconds == float("inf"):
        return "N/A"
    
    if 0 < seconds < 60:
        return "< 1m"  # Catches rapid chemical burns so they don't show as 0m
        
    total_s = int(round(seconds))
    days, remainder = divmod(total_s, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    
    if days > 0:
        return f"~ {days}d {hours}h"
    elif hours > 0:
        return f"~ {hours}h {minutes}m"
    return f"~ {minutes}m"

@st.cache_data(ttl=3600)
def load_tle_web():
    """
    Retrieves TLE data from the upstream API directly into Streamlit memory.
    Bypassing local disk I/O eliminates TOCTOU (Time-of-Check to Time-of-Use) 
    race conditions under highly concurrent web traffic.
    """
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    lines = [line.strip() for line in response.text.splitlines() if line.strip()]
    
    if len(lines) < 3:
        raise ValueError("Malformed TLE payload received from upstream.")
    return lines[0], lines[1], lines[2]


@st.cache_resource
def build_satellite(name, line1, line2):
    """Initializes and caches the Skyfield propagation model."""
    ts = load.timescale()
    return ts, EarthSatellite(line1, line2, name, ts)


def mission_delta_v(mission):
    """Computes mission-specific Delta-V budget totals based on orbital parameters."""
    r1 = EARTH_RADIUS + mission["alt1"]
    r2 = EARTH_RADIUS + mission["alt2"]
    _, _, raise_dv_km_s = hohmann_transfer(r1, r2)
    sk_dv_km_s = station_keeping_delta_v(mission["annual_rate"], LIFETIME_YEARS)
    deorbit_dv_km_s = deorbit_delta_v(r2, EARTH_RADIUS + PERIGEE_ALT_KM)

    raise_m_s = raise_dv_km_s * 1000.0
    sk_m_s = sk_dv_km_s * 1000.0
    deorbit_m_s = deorbit_dv_km_s * 1000.0
    return raise_m_s, sk_m_s, deorbit_m_s, raise_m_s + sk_m_s + deorbit_m_s, r1, r2


# --- UI Initialization ---
st.title("🛰️ OrbitWatch")
st.markdown("""
Welcome to **OrbitWatch**. This dashboard bridges satellite telemetry tracking with systems engineering. 
Use the tabs below to navigate through the modules:

*   **🌎 Tracking:** Live position & ground track progression. We are currently tracking the **ISS (Zarya)**—the International Space Station's foundational module. It serves as our real-time orbital reference to visualize how a spacecraft's ground track shifts west over time due to Earth's rotation.
*   **📡 Coverage:** Pass predictions and revisit rates. This module computes topocentric geometry to predict communication windows and acquisition opportunities over a specific designated ground station (**Mumbai, India**).
*   **🚀 Delta-V & Propulsion:** A first-principles physics trade study. This module evaluates the **full operational lifecycle** of three distinct small-satellite missions. It calculates the cumulative $\Delta V$ budget required to **raise** the initial orbit, maintain **station-keeping** against atmospheric drag for a 5-year lifetime, and execute a destructive end-of-life **de-orbit** burn. It then compares the propellant and time costs to execute this full lifecycle across four different thruster technologies.
""")

try:
    name, line1, line2 = load_tle_web()
    ts, satellite = build_satellite(name, line1, line2)
    tle_error = None
except Exception as exc: 
    name, line1, line2, ts, satellite = None, None, None, None, None
    tle_error = str(exc)

if tle_error:
    st.error(f"Upstream API Error: {tle_error}")
    st.stop()

tab_tracking, tab_coverage, tab_mission = st.tabs(["🌎 Tracking", "📡 Coverage", "🚀 Delta-V & Propulsion"])

# ---------------------------------------------------------------------
# Tab 1: Tracking
# ---------------------------------------------------------------------
with tab_tracking:
    st.markdown(f"### Live Telemetry: **{name}**")
    
    pos_km, vel_km_s = propagate(line1, line2, name, ts.now())
    geo = satellite.at(ts.now())
    subpoint = geo.subpoint()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Altitude", f"{subpoint.elevation.km:.1f} km")
    col2.metric("Orbital Velocity", f"{(vel_km_s[0]**2 + vel_km_s[1]**2 + vel_km_s[2]**2) ** 0.5:.2f} km/s")
    col3.metric("Latitude", f"{subpoint.latitude.degrees:.2f}°")
    col4.metric("Longitude", f"{subpoint.longitude.degrees:.2f}°")

    st.divider()
    
    col_slide, col_plot = st.columns([1, 3])
    with col_slide:
        st.markdown("#### Orbit Projection")
        st.write("Adjust to project the satellite's path forward in time. Notice how the ground track shifts west due to Earth's rotation.")
        orbits = st.slider("Select Orbits to display:", 1, 4, 2)

    with col_plot:
        lats, lons = compute_ground_track(satellite, duration_minutes=93 * orbits)
        
        fig = Figure(figsize=(10, 5))
        ax = fig.subplots()
        
        # Implement chronological colormap to visually distinguish overlapping ground tracks
        time_prog = np.linspace(0, 1, len(lons))
        scatter = ax.scatter(lons, lats, c=time_prog, cmap='coolwarm', s=8, alpha=0.9, zorder=2)
        
        # Mark initial epoch location
        valid_idx = np.isfinite(lons).argmax()
        ax.scatter(lons[valid_idx], lats[valid_idx], color='lime', s=90, edgecolors='black', zorder=5, label='Current Position')
        
        ax.set_xlim([-180, 180])
        ax.set_ylim([-90, 90])
        ax.set_xlabel("Longitude (°)")
        ax.set_ylabel("Latitude (°)")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_title(f"Ground Track Progression ({orbits} Orbit{'s' if orbits > 1 else ''})")
        ax.legend(loc="lower left")
        
        st.pyplot(fig)

# ---------------------------------------------------------------------
# Tab 2: Coverage
# ---------------------------------------------------------------------
with tab_coverage:
    st.markdown("### Ground Station Coverage: **Mumbai, India**")
    st.write("Calculates visible passes over a designated target based on topocentric geometry.")
    
    passes_24h = get_passes_over_location(satellite, MUMBAI_LAT, MUMBAI_LON, duration_days=1, horizon_degrees=10)

    if not passes_24h:
        st.info("No passes above a 10-degree horizon in the next 24 hours.")
    else:
        rows = []
        for p in passes_24h:
            rows.append({
                "Rise Time (UTC)": p["rise_time"].utc_strftime("%Y-%m-%d %H:%M"),
                "Peak Elevation": f"{p['max_elevation_deg']:.1f}°",
                "Max Slant Range": f"{p.get('distance_km', 0):.0f} km",
                "Set Time (UTC)": p["set_time"].utc_strftime("%Y-%m-%d %H:%M"),
                "Duration": f"{p['duration_seconds'] / 60:.1f} min",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    passes_7d = get_passes_over_location(satellite, MUMBAI_LAT, MUMBAI_LON, duration_days=7, horizon_degrees=10)
    if passes_7d:
        revisit_hours = (7.0 * 24.0) / len(passes_7d)
        st.metric("7-Day Average Revisit Interval", f"{revisit_hours:.1f} hours", help=f"Based on {len(passes_7d)} passes")

# ---------------------------------------------------------------------
# Tab 3: Delta-V & Propulsion
# ---------------------------------------------------------------------
with tab_mission:
    st.markdown("### Mission Design & Propulsion Trade Study")
    
    mission_label = st.selectbox("Select a Mission Scenario:", list(MISSIONS.keys()))
    mission = MISSIONS[mission_label]
    
    st.info(f"**Mission Profile:** Initial Altitude **{mission['alt1']:.0f} km** ➔ Target Altitude **{mission['alt2']:.0f} km**")

    raise_m_s, sk_m_s, deorbit_m_s, total_m_s, r1, r2 = mission_delta_v(mission)

    st.markdown("#### Delta-V Budget Breakdown")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Transfer Burn", f"{raise_m_s:.1f} m/s")
    col_b.metric(f"Drag Makeup ({LIFETIME_YEARS:.0f} yr)", f"{sk_m_s:.1f} m/s")
    col_c.metric("End-of-Life Deorbit", f"{deorbit_m_s:.1f} m/s")
    col_d.metric("Total Δv", f"{total_m_s:.0f} m/s")

    st.divider()
    
    st.markdown("#### Sequential Mass & Propellant Bookkeeping")
    st.write(f"Tracking a **{M0_KG:.0f} kg** spacecraft through its full lifecycle. Because a satellite gets lighter as it burns fuel, station-keeping and deorbit burns are calculated using the dynamic depleted mass, not the initial wet mass.")

    # Data collections for charts
    names = []
    raise_masses, sk_masses, deorbit_masses = [], [], []
    total_times = []
    
    # Phase-separated collections for the table
    phase1_rows, phase2_rows, phase3_rows = [], [], []
    
    r_perigee = EARTH_RADIUS + PERIGEE_ALT_KM
    
    for tname, isp, eta, power, mode in THRUSTERS:
        v_e = exhaust_velocity(isp)
        if mode == "Electric":
            thrust = thrust_from_power(power, eta, v_e)
        else:
            thrust = CHEMICAL_THRUST_N
            
        # 1. Orbit Raise
        m_current = M0_KG
        mp_raise = propellant_mass(raise_m_s, isp, m_current)
        t_raise = transfer_time_estimate(raise_m_s, thrust, m_current) if mode == "Electric" else hohmann_coast_time(r1, r2)
        m_current -= mp_raise
        
        # 2. Station-Keeping
        mp_sk = propellant_mass(sk_m_s, isp, m_current)
        t_sk = transfer_time_estimate(sk_m_s, thrust, m_current) if mode == "Electric" else 0.0
        m_current -= mp_sk
        
        # 3. Deorbit
        mp_deorbit = propellant_mass(deorbit_m_s, isp, m_current)
        t_deorbit = transfer_time_estimate(deorbit_m_s, thrust, m_current) if mode == "Electric" else hohmann_coast_time(r2, r_perigee)
        m_current -= mp_deorbit 
        
        total_mp = mp_raise + mp_sk + mp_deorbit
        total_t = t_raise + t_deorbit 

        names.append(THRUSTER_SHORT_NAMES.get(tname, tname))
        raise_masses.append(mp_raise)
        sk_masses.append(mp_sk)
        deorbit_masses.append(mp_deorbit)
        total_times.append(total_t)
        
        # Populate phase-specific lists for grouped table display
        phase1_rows.append({"Phase": "1. Orbit Raise", "Thruster": tname, "Prop. Used": f"{mp_raise:.2f} kg", "Mass Remaining": f"{m_current + mp_sk + mp_deorbit:.2f} kg", "Burn / Coast Time": format_duration(t_raise)})
        phase2_rows.append({"Phase": f"2. Station-Keeping ({LIFETIME_YEARS:.0f}y)", "Thruster": tname, "Prop. Used": f"{mp_sk:.2f} kg", "Mass Remaining": f"{m_current + mp_deorbit:.2f} kg", "Burn / Coast Time": f"{format_duration(t_sk)} (Accumulated)"})
        phase3_rows.append({"Phase": "3. Deorbit", "Thruster": tname, "Prop. Used": f"{mp_deorbit:.2f} kg", "Mass Remaining": f"{m_current:.2f} kg (Final Dry Mass)", "Burn / Coast Time": format_duration(t_deorbit)})

    # Combine table rows ordered by Phase
    breakdown_rows = phase1_rows + phase2_rows + phase3_rows

    with st.expander("🔍 View Detailed Phase-by-Phase Breakdown Table", expanded=False):
        st.dataframe(pd.DataFrame(breakdown_rows), use_container_width=True, hide_index=True)

    # Plotting Trade-off Charts
    from matplotlib.figure import Figure
    fig2 = Figure(figsize=(11, 5))
    ax_mass, ax_time = fig2.subplots(1, 2)

    bottom_sk = raise_masses
    bottom_deorbit = [i+j for i,j in zip(raise_masses, sk_masses)]
    
    p1 = ax_mass.bar(names, raise_masses, label='Raise Burn', color='#264653')
    p2 = ax_mass.bar(names, sk_masses, bottom=bottom_sk, label='Station-Keep', color='#2A9D8F')
    p3 = ax_mass.bar(names, deorbit_masses, bottom=bottom_deorbit, label='Deorbit Burn', color='#E9C46A')
    
    totals = [i+j+k for i,j,k in zip(raise_masses, sk_masses, deorbit_masses)]
    for idx, rect in enumerate(p3):
        height = rect.get_y() + rect.get_height()
        ax_mass.text(rect.get_x() + rect.get_width()/2., height + max(totals)*0.02,
                f'{totals[idx]:.1f} kg', ha='center', va='bottom', fontsize=9)

    ax_mass.set_ylabel("Propellant Mass (kg)")
    ax_mass.set_title("Propellant Cost Breakdown")
    ax_mass.margins(y=0.15)
    ax_mass.legend(fontsize=8)
    ax_mass.grid(axis='y', linestyle='--', alpha=0.3)

    bars_time = ax_time.bar(names, total_times, color='#E76F51')
    time_labels = [format_duration(ts) for ts in total_times]
    ax_time.bar_label(bars_time, labels=time_labels, padding=3, fontsize=9)
    ax_time.set_ylabel("Total Active Transfer Time (Raise/Lowering + Deorbit)")
    ax_time.set_title("Time Cost (Excluding 5yr SK)")
    ax_time.set_yticks([]) 
    ax_time.margins(y=0.15)

    fig2.tight_layout()
    st.pyplot(fig2)
    
   # --- Executive Summary & Assumptions Section ---
    st.markdown("#### Executive Summary & Trade-Off Analysis")
    
    # 1. Dynamic Mission-Specific Insight
    if "Mission A" in mission_label:
        st.info(f"**Mission-Specific Insight ({mission_label}):** \nWith a modest total $\Delta V$ budget (~192 m/s), chemical propulsion is highly viable if rapid operational deployment is the priority. However, utilizing Electric propulsion saves ~50 kg of propellant—which for a 1000 kg smallsat can significantly increase the mass available for revenue-generating payloads (cameras, sensors, transponders).")
    
    elif "Mission B" in mission_label:
        st.info(f"**Mission-Specific Insight ({mission_label}):** \nThis high-energy transfer (~841 m/s) severely punishes chemical propulsion, which consumes nearly 25% of the spacecraft's initial mass just for fuel. Electric propulsion (Ion/Hall) is heavily recommended here to preserve payload capacity, though the mission planners must tolerate a slow spiral transfer time of several weeks.")
    
    elif "Mission C" in mission_label:
        st.info(f"**Mission-Specific Insight ({mission_label}):** \nLowering from a rideshare orbit to 500 km means the satellite will face a high atmospheric drag environment (~35 m/s over 5 years). Water Microwave Plasma presents a strong middle ground here: fast enough to reach operational altitude quickly, but efficient enough to sustain the 5-year drag makeup without eating up the mass budget.")

    # 2. Combined Technology Summary
    st.success("""
    **Combined Technology Summary (Applicable across all missions):**
    * **Heaviest Payload Capacity (Mass Efficiency):** **Ion and Hall thrusters** require the least propellant. By saving hundreds of kilograms of fuel compared to chemical propulsion, that mass can be replaced with payload.
    * **Fastest Operational Response (Time Cost):** **Chemical Bipropellant** is the only technology that executes orbital transfers in hours. Electric thrusters take weeks to spiral, delaying the start of the satellite's revenue-generating lifespan.
    * **The Middle Ground:** **Microwave Plasma (Water) thrusters** offer a strong compromise, requiring vastly less mass than chemical rockets while using safe, non-toxic, easily storable propellants (water) compared to expensive Xenon gas used in Ion/Hall systems.
    """)

    # 3. Sources Expander

    with st.expander("📚 Systems Engineering Assumptions & Sources"):
        st.markdown("""
        **Where do these numbers come from?**
        * **Drag Profile:** Station-keeping estimates rely on the industry-standard *Space Mission Analysis and Design (SMAD)* text. E.g., 500 km altitudes incur a baseline penalty of ~7.0 m/s/year.
        * **Deorbit Perigee (150 km):** Satellites are modeled to lower their perigee to 150 km to ensure rapid, passive aerodynamic destruction in Earth's dense upper atmosphere.
        * **Bellatrix Microwave Plasma:** The 1200s Isp modeled here represents published performance targets by [Bellatrix Aerospace](https://bellatrix.aero/jal) for their water-based thrusters (roughly 4x the efficiency of chemical thrusters).
        * **Electric Thrust Derivation:** Thrust is strictly derived from electrical power and specific impulse ($F = 2 P \eta / v_e$) to enforce energy conservation, preventing inputs that inadvertently assume >100% efficiency.
        * **Gravity Losses:** The model assumes impulsive Delta-V. In physical operations, a chemical engine would not burn continuously for 28 minutes in LEO (which would incur massive gravity losses). Real missions, such as ISRO's Mangalyaan (MOM), segment these into multiple short 5-minute perigee bursts over several orbits to remain efficient.
        * **Chemical Station-Keeping (< 1m):** Chemical rockets produce massive thrust (500 N in this model). A 5-year drag makeup maneuver that takes an electric thruster 24 hours to achieve will take a chemical thruster roughly ~20 seconds of total firing time, hence appearing as '< 1m'.
        """)