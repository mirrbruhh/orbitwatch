# OrbitWatch

A satellite tracking dashboard built to answer a specific question: for a small satellite operating in low Earth orbit, how much does the choice of propulsion system actually cost you in propellant, and what does that cost you in time?

Most beginner satellite-tracking projects stop at "here's a dot on a map." OrbitWatch does that too, but the actual point of the project is the propulsion trade study: a from-scratch implementation of the Tsiolkovsky rocket equation, a first-principles derivation of ion-thruster exhaust velocity, and a comparison across four real thruster technologies (chemical bipropellant, Hall effect, ion, and a water-fed microwave plasma thruster) for three different mission profiles.

![Multi-orbit ground track](assets/ground_track_multi_orbit.png)

**Live demo:** _add link here after deploying to Streamlit Community Cloud_

---

## Table of contents

- [Why this project is built this way](#why-this-project-is-built-this-way)
- [Mission profiles](#mission-profiles)
- [Modules](#modules)
- [Running it locally](#running-it-locally)
- [Project structure](#project-structure)
- [Sanity-checking the numbers](#sanity-checking-the-numbers)
- [Limitations](#limitations)
- [Possible extensions](#possible-extensions)

---

## Why this project is built this way

Anyone can plot a satellite's position on a map with a TLE and a Python library. That part of this project (Day 1-2 in the build notes) exists because it's genuinely useful and because it's good groundwork, but it's not the differentiator.

The propulsion module is. Given a delta-v budget, four different thruster technologies need wildly different amounts of propellant to deliver it, and that difference is driven by exhaust velocity, which for an ion thruster comes directly from how much electrical energy you can impart to an ion before it leaves the grid:

```
v_e = sqrt(2 * q * V / m_ion)
```

That's a straight line from electrostatics to the Tsiolkovsky rocket equation, and it's the piece of this project that draws on a physics background rather than a tutorial. Thrust for the electric thrusters (Hall, ion, water plasma) is derived from power and efficiency rather than assumed as an independent number, specifically so the propellant-mass and burn-time figures can't quietly imply an efficiency above 100%, which is an easy mistake to make if you pick "typical" thrust, power, and efficiency numbers separately from three different spec sheets.

## Mission profiles

Three profiles, chosen to cover a raise, a high-altitude raise, and a lowering maneuver, so the delta-v math and the Hohmann transfer function both get exercised in more than one direction.

| Mission | Maneuver | Raise/lower | 5-yr station-keep | Deorbit | Total delta-v |
|---|---|---|---|---|---|
| A: Indian Smallsat | 500 to 600 km | ~54.7 m/s | ~10.0 m/s | ~127.0 m/s (from 600 km) | **~191.7 m/s** |
| B: Ambitious High Raise | 500 to 1500 km | ~499.0 m/s | ~0.5 m/s (a conservative upper bound, not exactly zero, at this altitude) | ~341.5 m/s | **~841.0 m/s** |
| C: Rideshare Lowering | 800 to 500 km | ~160.8 m/s | ~35.0 m/s | ~100.0 m/s | **~295.8 m/s** |

Mission A's station-keeping figure (~10.0 m/s) is meaningfully lower than Mission C's (~35.0 m/s) even though both use the same drag-rate function, because Mission A operates at 600 km and Mission C at 500 km. Atmospheric density falls off steeply enough over that 100 km that the assumed annual rate drops from 7.0 to 2.0 m/s/yr accordingly, see `src/missions.py` for the reasoning and its limits.

All three totals are computed, not hardcoded: `src/missions.py` defines each mission's altitudes and station-keeping rate once, and every script (`validate_deltav.py`, `validate_stationkeeping.py`, `validate_deorbit.py`, `validate_propulsion.py`, `app.py`) derives the rest from `src/deltav.py`'s functions. That's also why the totals above carry an extra decimal place: they're the actual sum of three independently-computed components, not a rounded headline number.

Mission A and Mission C both deorbit from wherever they actually end up operating (600 km and 500 km respectively), not from their starting altitude.

### Thrusters compared

| Thruster | Isp | Efficiency | Power | Thrust |
|---|---|---|---|---|
| Chemical Bipropellant | 300 s | 0.95 | n/a | 500 N (fixed) |
| Hall Thruster | 1800 s | 0.50 | 3000 W | derived from power |
| Ion Thruster | 3000 s | 0.70 | 5000 W | derived from power |
| Water Microwave Plasma | 1200 s | 0.45 | 1500 W | derived from power |

The water-fed microwave plasma thruster's Isp is modeled on Bellatrix Aerospace's own claim for their JAL series: "4X higher specific impulse compared to chemical propulsion systems" (300 s x 4 = 1200 s), rather than a directly published absolute Isp figure.
Source: https://bellatrix.aero/jal

### Sanity check against a real mission

A 2018 AIAA study on electric propulsion for small satellites (an Exotrail Hall-effect thruster study, roughly 800 km orbit) modeled a deorbit delta-v around 106 m/s, with a total independently-budgeted mission delta-v around 373 m/s. Mission A's own deorbit estimate (~127 m/s) and total (~192 m/s) land in the same order of magnitude, even though the specific orbit and mission profile differ.
Source: https://arc.aiaa.org/doi/pdf/10.2514/6.2018-2729

## Design note: why mission parameters live in one place

Every `validate_*.py` script and `app.py` import each mission's altitudes and station-keeping rate from `src/missions.py` rather than keeping a local copy, and delta-v totals are always derived from `hohmann_transfer`, `station_keeping_delta_v`, and `deorbit_delta_v` rather than stored as a separate number. Storing the total separately would mean it could silently stop matching its own components if an assumption changes.

Sanity-check bounds (the expected nominal/min/max range for a given calculation) are deliberately kept local to each `validate_*.py` script rather than centralized too, since a mission's raise-burn bound and its deorbit bound are genuinely different numbers, not copies of the same fact.

## Modules

**`src/propagate.py`**
Wraps Skyfield's SGP4 propagator: given a TLE and a time, returns position and velocity in the GCRS frame.

**`src/coverage.py`**
Ground track computation (with antimeridian-safe plotting) and pass prediction over a ground location, including rise/culminate/set times, peak elevation, azimuth, and slant range.

**`src/deltav.py`**
Vis-viva orbital mechanics: Hohmann transfer delta-v (handles both raising and lowering), Hohmann transfer coast time, station-keeping delta-v over a mission lifetime, and deorbit delta-v.

**`src/propulsion.py`**
The Tsiolkovsky rocket equation, exhaust velocity from Isp, thrust from electrical power and efficiency, and a constant-thrust transfer-time estimate.

**`src/missions.py`**
The three mission profiles' physical parameters (altitudes, station-keeping rate), shared by every `validate_*.py` script and `app.py` so they can't drift out of sync with each other.

**`app.py`**
The Streamlit dashboard: live ISS tracking and ground track, passes over Mumbai with a 7-day revisit metric, and the delta-v/propulsion trade study for whichever mission profile is selected.

**`validate_*.py`**
Standalone scripts that exercise each module against the three mission profiles and print pass/fail checks against expected ranges. Not a formal test suite, but they're what actually checks a value like Mission A's station-keeping rate against a plausible range instead of just trusting it.

## Running it locally

```bash
git clone <your-repo-url>
cd orbitwatch
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python fetch_tle.py             # caches a current ISS TLE to data/iss.txt
streamlit run app.py
```

The dashboard re-fetches the TLE automatically if the cached one is more than an hour old, so `fetch_tle.py` only needs to be run manually the first time.

## Project structure

```
orbitwatch/
├── app.py
├── fetch_tle.py
├── requirements.txt
├── README.md
├── data/
│   └── iss.txt                 (generated, not committed)
├── src/
│   ├── propagate.py
│   ├── coverage.py
│   ├── deltav.py
│   ├── propulsion.py
│   └── missions.py
├── predict_passes.py
├── plot_ground_track.py
├── validate_propagation.py
├── validate_deltav.py
├── validate_stationkeeping.py
├── validate_deorbit.py
└── validate_propulsion.py
```

## Sanity-checking the numbers

Each `validate_*.py` script can be run directly and prints its own pass/fail table against an expected range for that calculation:

```bash
python validate_propagation.py       # altitude should land in the ISS's real operating range
python validate_deltav.py            # Hohmann transfer, all three missions
python validate_stationkeeping.py    # drag makeup over a 5-year lifetime
python validate_deorbit.py           # deorbit burn, all three missions
python validate_propulsion.py        # propellant mass and burn time, all four thrusters
```

These ranges are internal consistency checks (does the code agree with itself and with the vis-viva equation), not independent published data. The closest thing to an exception is Mission C's station-keeping rate: SMAD, 4th edition, chapter 8, publishes a range of 5 to 10 m/s/yr at 500 km, and 7.0 m/s/yr is chosen from the middle of that range, not a single value SMAD states outright. Mission A's rate (2.0 m/s/yr at 600 km) is derived from that same range via an atmospheric scale-height estimate, and Mission B's (0.1 m/s/yr at 1500 km) is an assumed conservative upper bound. See `src/missions.py` for the reasoning behind each.

## Limitations

- **Two-burn Hohmann transfers only.** Real transfers can involve plane changes, J2 perturbations, and multi-burn strategies that this project doesn't model.
- **No atmospheric drag simulation.** Station-keeping cost is a published assumption (SMAD, for the 500 km case) multiplied by mission lifetime, not a simulated ballistic-coefficient/solar-activity model. The 600 km and 1500 km rates are a derived estimate and an assumed bound respectively, not separately published figures.
- **Simplified transfer-time estimate for electric propulsion.** `transfer_time_estimate` assumes constant thrust and constant mass, which is a reasonable order-of-magnitude estimate but understates real spiral-transfer time: a continuous-thrust spiral needs more total delta-v than an equivalent single burn, because thrust isn't always applied in the most efficient direction throughout the orbit.
- **Simplified ground track.** Gridlines only, not a full map projection (Cartopy is notoriously fiddly to install and wasn't worth the setup time for this project).
- **TLE freshness.** The dashboard refreshes at most once an hour; TLE accuracy still degrades over the multi-day gaps between CelesTrak's own published updates.
- **Fixed 1000 kg wet mass** across every mission and thruster, for comparability. A real mission's mass budget would vary by payload and propulsion system.

## Possible extensions

- A simple J2 perturbation model for more realistic long-term ground tracks.
- Multi-satellite constellation coverage (revisit time across a Walker constellation, not just one satellite).
- An actual atmospheric density model (NRLMSISE-00 or similar) to replace the fixed station-keeping rate assumption.

## Built with

Python, [Skyfield](https://rhodesmill.org/skyfield/) for orbital mechanics, [Streamlit](https://streamlit.io/) for the dashboard, Matplotlib for plotting.

## License

MIT. See `LICENSE` for details.
