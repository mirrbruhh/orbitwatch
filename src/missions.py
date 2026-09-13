"""
Shared mission parameters, used by every validate_*.py script and app.py.

Only physical parameters live here (alt1, alt2, annual_rate): these are
the values every script needs to agree on. Sanity-check bounds (nominal,
min, max) are NOT centralized here on purpose: a mission's raise-burn
bound and its deorbit bound are different facts, not copies of each
other, so each validate_*.py script keeps its own bounds dict.

Mission names are kept short since the altitude range is already
available via alt1 and alt2 below, it doesn't need to be repeated in the
name too.

Of the three annual_rate values below, Mission C's is the best grounded:
SMAD publishes a range (5 to 10 m/s/yr at 500 km), and 7.0 is a
representative value chosen from the middle of it. Mission A's rate is
derived from that range via an atmospheric scale-height estimate, and
Mission B's is an assumed conservative upper bound.
"""

MISSIONS = {
    "Mission A (Indian Smallsat)": {
        "alt1": 500.0,
        "alt2": 600.0,
        # Mission A operates at 600 km, where atmospheric density is roughly
        # a quarter to a fifth of the density at Mission C's 500 km, so
        # this rate is lower accordingly. 2.0 m/s/yr is a conservative
        # estimate (biased high, not optimistic), not a published figure
        # the way the 500 km rate is: real drag depends heavily on solar
        # activity and ballistic coefficient.
        "annual_rate": 2.0,
    },
    "Mission B (Ambitious High Raise)": {
        "alt1": 500.0,
        "alt2": 1500.0,
        # 0.1 m/s/yr is a conservative (deliberately high, not optimistic)
        # upper bound for atmospheric drag at 1500 km, not a cited figure:
        # real drag at this altitude is very low but not literally zero.
        "annual_rate": 0.1,
    },
    "Mission C (Rideshare Lowering)": {
        "alt1": 800.0,
        "alt2": 500.0,
        # SMAD (Space Mission Analysis and Design, 4th edition, chapter 8)
        # gives a published range of 5 to 10 m/s/yr at 500 km. 7.0 is a
        # representative value chosen from the middle of that range:
        # better grounded than Mission A or B's rates, but still a
        # judgment call within a published range, not a single number
        # SMAD states outright.
        "annual_rate": 7.0,
    },
}