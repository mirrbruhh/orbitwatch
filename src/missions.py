"""
Shared mission parameters, used by every validate_*.py script and app.py.

Only physical parameters live here (alt1, alt2, annual_rate) since those
are the numbers that were genuinely duplicated across four files and drove
the Mission A / Mission B drift bugs. Sanity-check bounds (nominal, min,
max) are NOT centralized here on purpose: a mission's raise-burn bound and
its deorbit bound are different facts, not copies of each other, so each
validate_*.py script keeps its own bounds dict.

Names match the short form already used in three of the four validate
scripts (validate_propulsion.py previously used a longer form with the
altitude range baked into the name - that range is available from alt1/
alt2 below, so it doesn't need to live in the name too).

Of the three annual_rate values below, Mission C's is the best
grounded: SMAD publishes a range (5 to 10 m/s/yr at 500 km) and 7.0 is
chosen from the middle of it, not a single figure taken directly from a
source. Mission A's rate is derived from that range via an atmospheric
scale-height estimate, and Mission B's is an assumed conservative upper
bound. None of the three is a point value lifted straight from a
citation, they're progressively less directly grounded, not "cited vs.
assumed" as a binary.
"""

MISSIONS = {
    "Mission A (Indian Smallsat)": {
        "alt1": 500.0,
        "alt2": 600.0,
        # Not the same as Mission C's 500 km rate: atmospheric density at
        # 600 km is roughly a quarter to a fifth of density at 500 km, so
        # station-keeping should be meaningfully lower here. 2.0 m/s/yr is
        # a conservative estimate (biased high, not the optimistic end),
        # not a published figure the way the 500 km rate is - real drag
        # depends heavily on solar activity and ballistic coefficient.
        "annual_rate": 2.0,
    },
    "Mission B (Ambitious High Raise)": {
        "alt1": 500.0,
        "alt2": 1500.0,
        # Not exactly zero: 0.1 m/s/yr is a conservative (deliberately
        # high, not optimistic) upper bound at 1500 km, not a cited
        # figure. An exact 0.0 would make the sanity check in
        # validate_stationkeeping.py compare a hardcoded zero to itself.
        "annual_rate": 0.1,
    },
    "Mission C (Rideshare Lowering)": {
        "alt1": 800.0,
        "alt2": 500.0,
        # SMAD (Space Mission Analysis and Design, 4th edition, chapter 8)
        # gives a published range of 5 to 10 m/s/yr at 500 km. 7.0 is a
        # representative value chosen from the middle of that range, not
        # a single figure SMAD states outright, better grounded than
        # Mission A or B's rates, but still a judgment call, not a
        # citation of "7.0" specifically.
        "annual_rate": 7.0,
    },
}