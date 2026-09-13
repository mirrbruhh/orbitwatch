# 🛰️ OrbitWatch: Systems Engineering & Orbital Analysis

**OrbitWatch** is a Python-based systems engineering toolkit and interactive web dashboard. It extends standard satellite telemetry tracking (SGP4) by implementing a first-principles orbital mechanics and propulsion trade-study engine. 

While typical tracking applications conclude at geospatial plotting, OrbitWatch evaluates the physical reality of spacecraft operations: calculating the precise Delta-V budgets required for orbital maneuvers, and assessing the physical propellant and time costs across different propulsion technologies (Chemical, Hall-Effect, Ion, and Microwave Plasma).

**Live Dashboard:** _[Insert your Streamlit Cloud URL here]_

---

### 📸 Dashboard Previews

![Multi-Orbit Telemetry](assets/ground_track_multi_orbit.png)
*(Above: The vectorized multi-orbit telemetry map utilizing chronological color gradients to demonstrate orbital drift.)*

> **Note:** *Add a screenshot of your Streamlit Delta-V bar charts to the assets folder as `propulsion_trade_study.png`, then uncomment the line below in your repo.*

![Propulsion Trade Study](assets/propulsion_trade_study.png)

---

## 🧰 Tech Stack
* **Language:** Python 3.9+
* **Orbital Mechanics:** [Skyfield](https://rhodesmill.org/skyfield/) (SGP4 propagation, topocentric geometry)
* **Data Processing:** `NumPy`, `Pandas`
* **Data Visualization:** `Matplotlib`
* **Web Framework:** [Streamlit](https://streamlit.io/)
* **Upstream Data:** CelesTrak / NORAD (Live TLE API)

## 🛠️ Architecture & Engineering Highlights

*   **Robust Physics Engine:** Implements the Vis-viva equation for multi-stage Hohmann transfers, and the Tsiolkovsky rocket equation for mass fraction calculations.
*   **First-Principles Electrodynamics:** Dynamically derives theoretical exhaust velocity for Ion thrusters from electrostatic acceleration potentials ($v_e = \sqrt{2qV / m}$), rather than relying on assumed spec-sheet values.
*   **Energy Conservation:** Prevents non-physical modeling by deriving electrical thruster force via $F = 2P\eta / v_e$. This guarantees that user inputs for Specific Impulse, Power, and Thrust remain mathematically coherent and never exceed 100% efficiency.
*   **High-Performance Vectorization:** Replaces slow Python `for`-loops with `NumPy` array transformations and vectorized Skyfield time-objects, accelerating ground track generation and effectively neutralizing canvas-crossing artifacts at the International Date Line.
*   **Concurrency Safe:** The Streamlit deployment bypasses local disk I/O, utilizing in-memory thread-safe caching to prevent Time-of-Check to Time-of-Use (TOCTOU) file corruption under concurrent web traffic. 
*   **Memory Management:** Implements strict teardown procedures for Matplotlib state machines (`plt.close()`) to guarantee continuous uptime without Out-of-Memory (OOM) leaks.
*   **Sequential Mass Bookkeeping:** Evaluates propellant budgets chronologically (Orbit Raise $\rightarrow$ Station-Keeping $\rightarrow$ Deorbit). As fuel is consumed, the spacecraft's dynamic dry mass is updated and passed to the next maneuver phase, ensuring highly accurate $m_0$ inputs for the Tsiolkovsky equation rather than naively applying the initial wet mass to all calculations.

## 🚀 Mission Trade Studies

The engine evaluates three nominal systems-engineering profiles, calculating orbital raise/lower burns, lifetime drag-makeup (station-keeping), and end-of-life atmospheric disposal:

| Mission Profile | Operational Maneuver | 5-Year Station-Keep | Deorbit Burn | **Total $\Delta V$** |
|---|---|---|---|---|
| **A: LEO Smallsat** | 500 km $\rightarrow$ 600 km | ~10.0 m/s | ~127.0 m/s | **~191.7 m/s** |
| **B: High Altitude** | 500 km $\rightarrow$ 1500 km | ~0.5 m/s | ~341.5 m/s | **~841.0 m/s** |
| **C: Rideshare Lower** | 800 km $\rightarrow$ 500 km | ~35.0 m/s | ~100.0 m/s | **~295.8 m/s** |

## ⚙️ Module Breakdown

*   `src/deltav.py`: Core astrodynamics. Evaluates Vis-viva equations, continuous transfer coast durations, atmospheric drag penalties, and retrograde atmospheric disposal vectors. Includes strict mathematical domain guards.
*   `src/propulsion.py`: Translates Delta-V into physical mass arrays. Handles specific impulse, theoretical exit velocities, and first-order continuous-burn transfer durations.
*   `src/coverage.py`: Implements rigorous state-machine evaluation to predict topocentric satellite passes (AOS/LOS boundaries) and statistical revisit frequencies over designated ground stations.
*   `app.py`: The unified Streamlit application integrating real-time API syncs, dynamic UI configuration, and Matplotlib data visualization.

## 📂 Project Structure

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

## 💻 Local Deployment

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

## ⚠️ Known Limitations & Scope

*   **Continuous-Thrust Estimation:** `transfer_time_estimate` evaluates a constant-mass approximation. Actual low-thrust electric spirals incur gravity losses due to non-impulsive acceleration vectors, requiring integrated numerical simulation for exact mission durations.
*   **Aerodynamic Modeling:** Drag penalties rely on conservative median values tailored to specific altitude bands, rather than real-time NRLMSISE-00 atmospheric density and variable ballistic coefficient integrations.
*   **J2 Perturbations:** Two-body Keplerian mechanics are assumed for transfer energy budgets; nodal regression and secular variations are excluded from the baseline delta-v calculations.

## 🔮 Future Extensions
* **J2/J4 Perturbation Modeling:** Integrating nodal regression calculations for sun-synchronous orbit (SSO) mission profiles.
* **Constellation Coverage Analysis:** Expanding the topocentric pass logic to evaluate revisit times across Walker Star/Delta constellations rather than single spacecraft.
* **Dynamic Atmospheric Density:** Replacing the conservative annual drag baseline with the `NRLMSISE-00` empirical atmosphere model for real-time solar flux integration.

## 👨‍💻 Connect :
* **LinkedIn:** [Mihir Satra](www.linkedin.com/in/mihir-satra-b8599b389)

If you're a recruiter, hiring manager, or fellow engineer interested in space systems, feel free to reach out!

## 📄 License

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