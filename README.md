# OrbitWatch

**OrbitWatch** is a satellite tracking dashboard built around a specific question: for a small satellite in low Earth orbit, how much does the choice of propulsion system actually cost in propellant and in time?

Most beginner satellite trackers stop at plotting a position on a map. OrbitWatch does that too, but its main focus is the delta-v budget behind three mission profiles (an orbit raise, a high-altitude raise, and a rideshare lowering) and a propulsion trade study comparing chemical, Hall-effect, ion, and water microwave plasma thrusters across all three.

**Live Dashboard:** _[Insert your Streamlit Cloud URL here]_

---

### Dashboard previews

![Multi-Orbit Telemetry](assets/ground_track_multi_orbit.png)
*(Above: the multi-orbit ground track, colored by time progression to show orbital drift.)*

_[Add a screenshot of the Delta-V & Propulsion tab here once deployed. The filename below (`propulsion_trade_study.png`) doesn't exist yet in `assets/`, generate or capture one and place it there, or remove this line.]_

---

## Tech stack
* **Language:** Python 3.9+
* **Orbital Mechanics:** [Skyfield](https://rhodesmill.org/skyfield/) (SGP4 propagation, topocentric geometry)
* **Data Processing:** `NumPy`, `Pandas`
* **Data Visualization:** `Matplotlib`
* **Web Framework:** [Streamlit](https://streamlit.io/)
* **Upstream Data:** CelesTrak / NORAD (Live TLE API)

## Architecture & Engineering Highlights

*   **Physics engine:** implements the vis-viva equation for Hohmann transfers, and the Tsiolkovsky rocket equation for propellant mass.
*   **First-principles electrodynamics:** derives theoretical exhaust velocity for the ion thruster from electrostatic acceleration potentials ($v_e = \sqrt{2qV / m}$), rather than relying on an assumed spec-sheet value.
*   **Energy conservation:** electric thruster force is derived from power, efficiency, and exhaust velocity ($F = 2P\eta / v_e$) rather than assumed independently, so Isp, power, and thrust can't quietly imply an efficiency above 100%.
*   **Vectorized ground track generation:** uses NumPy array operations and vectorized Skyfield time objects instead of a Python loop, and inserts NaN breaks at the International Date Line to avoid canvas-crossing plot artifacts.
*   **In-memory TLE fetch for the web app:** the Streamlit app fetches a TLE directly into memory rather than round-tripping through a shared file on disk, avoiding a narrow race condition if two sessions request a fetch at the same moment. The standalone CLI scripts (`predict_passes.py`, `plot_ground_track.py`, `validate_propagation.py`) still cache to a file on disk between runs, which is a convenience for repeated command-line use, not a concurrency concern for them.
*   **Matplotlib figures scoped per request:** the dashboard builds each chart via `matplotlib.figure.Figure()` directly rather than pyplot's global state, which is the pattern Streamlit's own docs recommend to avoid figures silently accumulating in memory across reruns.
*   **Phase-by-phase mass bookkeeping:** propellant budgets are evaluated in sequence (raise, then station-keeping, then deorbit), with each phase's propellant mass subtracted before the next phase runs. The total propellant mass comes out identical to computing it in one step against the initial mass, since the rocket equation is exponential in delta-v either way, the real value here is the breakdown by phase, plus a small (roughly 0.3%) correction to total transit time from accounting for the spacecraft getting lighter between phases.


## Mission trade studies

The engine evaluates three nominal systems-engineering profiles, calculating orbital raise/lower burns, lifetime drag-makeup (station-keeping), and end-of-life atmospheric disposal:

| Mission Profile | Operational Maneuver | 5-Year Station-Keep | Deorbit Burn | **Total $\Delta V$** |
|---|---|---|---|---|
| **A: LEO Smallsat** | 500 km $\rightarrow$ 600 km | ~10.0 m/s | ~127.0 m/s | **~191.7 m/s** |
| **B: High Altitude** | 500 km $\rightarrow$ 1500 km | ~0.5 m/s | ~341.5 m/s | **~841.0 m/s** |
| **C: Rideshare Lower** | 800 km $\rightarrow$ 500 km | ~35.0 m/s | ~100.0 m/s | **~295.8 m/s** |

## Module breakdown

*   `src/deltav.py`: Core astrodynamics. Evaluates Vis-viva equations, continuous transfer coast durations, atmospheric drag penalties, and retrograde atmospheric disposal vectors. Includes strict mathematical domain guards.
*   `src/propulsion.py`: Translates Delta-V into physical mass arrays. Handles specific impulse, theoretical exit velocities, and first-order continuous-burn transfer durations.
*   `src/coverage.py`: Implements rigorous state-machine evaluation to predict topocentric satellite passes (AOS/LOS boundaries) and statistical revisit frequencies over designated ground stations.
*   `app.py`: The unified Streamlit application integrating real-time API syncs, dynamic UI configuration, and Matplotlib data visualization.

## Project structure

```text
orbitwatch/
├── app.py                      # Main Streamlit web application
├── fetch_tle.py                # Standalone CLI tool for CelesTrak API sync
├── requirements.txt            # Python dependencies
├── src/                        # Core physics & logic modules
│   ├── coverage.py             # Ground track & pass prediction math
│   ├── deltav.py               # Vis-viva & orbital transfer kinematics
│   ├── missions.py             # Centralized mission parameter configurations
│   ├── propagate.py            # SGP4 state vector wrapper
│   └── propulsion.py           # Tsiolkovsky & electrodynamic thrust engine
├── validate_*.py               # Standalone engineering sanity-check scripts
└── plot_ground_track.py        # Matplotlib renderer for multi-orbit telemetry
```

## Local deployment

Requirements: `Python 3.9+`

```bash
git clone https://github.com/yourusername/orbitwatch.git
cd orbitwatch
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the interactive web interface:
streamlit run app.py
```

### CLI Validation Suite
OrbitWatch includes standalone routines to validate mathematical constraints against standard industry bounds (e.g., SMAD 4th Edition limits):

```bash
python validate_propagation.py      # Verifies SGP4 altitudinal regimes
python validate_deltav.py           # Validates Hohmann $\Delta V$ magnitude expectations
python validate_stationkeeping.py   # Audits atmospheric drag profiles
python validate_propulsion.py       # First-principles electrodynamic benchmarks
python plot_ground_track.py         # Renders multi-orbit chronological gradients
```

## Known limitations and scope

*   **Continuous-Thrust Estimation:** `transfer_time_estimate` evaluates a constant-mass approximation. Actual low-thrust electric spirals incur gravity losses due to non-impulsive acceleration vectors, requiring integrated numerical simulation for exact mission durations.
*   **Aerodynamic Modeling:** Drag penalties rely on conservative median values tailored to specific altitude bands, rather than real-time NRLMSISE-00 atmospheric density and variable ballistic coefficient integrations.
*   **J2 Perturbations:** Two-body Keplerian mechanics are assumed for transfer energy budgets; nodal regression and secular variations are excluded from the baseline delta-v calculations.
*   **Impulsive Burn Approximation (Gravity Losses):** The math engine currently assumes instantaneous (impulsive) burns. In physical operations, a chemical engine would not burn continuously for 28 minutes in LEO, as this spans ~30% of the orbit and incurs massive gravity losses. Real missions, such as **ISRO's Mangalyaan (Mars Orbiter Mission)**, mitigate this by segmenting the maneuver into multiple short 5-minute perigee bursts over several orbits. Electric propulsion `transfer_time_estimate` likewise uses a first-order constant-mass approximation rather than a full numerical spiral integration.

## Future extensions
* **J2/J4 Perturbation Modeling:** Integrating nodal regression calculations for sun-synchronous orbit (SSO) mission profiles.
* **Constellation Coverage Analysis:** Expanding the topocentric pass logic to evaluate revisit times across Walker Star/Delta constellations rather than single spacecraft.
* **Dynamic Atmospheric Density:** Replacing the conservative annual drag baseline with the `NRLMSISE-00` empirical atmosphere model for real-time solar flux integration.

## Connect
* **LinkedIn:** [Mihir Satra](www.linkedin.com/in/mihir-satra-b8599b389)

If you're a recruiter, hiring manager, or fellow engineer interested in space systems, feel free to reach out!

## License

This project is licensed under the MIT License - see below for details.

```text
MIT License

Copyright (c) 2026, Mihir Satra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```