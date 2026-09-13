"""
Systems Engineering Mission Profiles.

Defines the physical operational bounds for orbital trade studies.
Centralized to guarantee identical assumptions across all validation tests 
and downstream UI applications.
"""

MISSIONS = {
    "Mission A (Indian Smallsat)": {
        "alt1": 500.0,
        "alt2": 600.0,
        # Rationale: Operational altitude is 600 km. Atmospheric density here 
        # is ~20-25% of the density at 500 km. 2.0 m/s/yr serves as a nominal 
        # engineering baseline for drag makeup.
        "annual_rate": 2.0,
    },
    "Mission B (Ambitious High Raise)": {
        "alt1": 500.0,
        "alt2": 1500.0,
        # Rationale: Beyond 1000 km, atmospheric drag is essentially negligible 
        # (~1e-14 kg/m^3). 0.1 m/s/yr provides a conservative upper bound.
        "annual_rate": 0.1,
    },
    "Mission C (Rideshare Lowering)": {
        "alt1": 800.0,
        "alt2": 500.0,
        # Rationale: Operational altitude is 500 km. Standard industry reference 
        # (SMAD 4th Ed.) assigns a drag penalty of 5-10 m/s/yr. 
        # 7.0 m/s/yr is utilized as the baseline median.
        "annual_rate": 7.0,
    },
}