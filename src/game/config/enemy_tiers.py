# Copyright (c) 2026 Renaud Guillon
"""The four enemy tiers (ENM-01, ENM-02, ENM-49): their kinds, their world and their colours.

A tier is one world's enemies (tier N is World N's). It holds exactly one kind of each role: a
diver, a shooter, a missile launcher, a laser and a carrier (which launches the tier's diver). Each
tier has its own colour theme (ENM-49): a neon hue on the yellow-green ladder of the enemy colour
family (GFX-READ-04), and a hull tint, picked to stand out from its world's ground.
Colours are linear RGB 0..1, hues in degrees.
"""

from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The roles of a tier, in the order of its kinds.
ROLES = ["diver", "shooter", "missile", "laser", "carrier"]

ENEMY_TIERS = record({
    # World 1 (sea, grass, red desert): yellow neon on a steel-blue hull.
    "1": {
        "world": 1,
        "hue": 60,
        "neon": [1, 1, 0.05],
        "hull": [0.1, 0.4, 1],
        "kinds": {
            "diver": "hornet",
            "shooter": "scout",
            "missile": "rocketeer",
            "laser": "lancer",
            "carrier": "carrier",
        },
    },
    # World 2 (rust desert, concrete, industry): lime neon, the complement of the rust, on a teal
    # hull.
    "2": {
        "world": 2,
        "hue": 110,
        "neon": [0.25, 1, 0.1],
        "hull": [0.05, 0.8, 0.8],
        "kinds": {
            "diver": "wasp",
            "shooter": "strafer",
            "missile": "harrier",
            "laser": "sweeper",
            "carrier": "hatchery",
        },
    },
    # World 3 (damp dark earth, canals, grey stone): bright chartreuse, brighter than the dark
    # ground, on an indigo hull.
    "3": {
        "world": 3,
        "hue": 85,
        "neon": [0.62, 1, 0.08],
        "hull": [0.35, 0.2, 1],
        "kinds": {
            "diver": "phantom",
            "shooter": "spinner",
            "missile": "mortar",
            "laser": "prism",
            "carrier": "broodmother",
        },
    },
    # World 4 (bright midday city, grey concrete): deep emerald, which yellow would wash out on,
    # on a near-black graphite hull.
    "4": {
        "world": 4,
        "hue": 135,
        "neon": [0.05, 1, 0.29],
        "hull": [0, 0, 0],
        "kinds": {
            "diver": "splitter",
            "shooter": "hydra",
            "missile": "juggernaut",
            "laser": "scissor",
            "carrier": "hive",
        },
    },
})

# How much the shots of each tier's kinds take off the player's health (D-314): a bullet, a missile,
# a laser beam. Each kind keeps its tier's for the whole game; the tiers of the later worlds hit
# harder, so a level gets harder with fewer enemies. Ramming stays the hull's rule (`hull.py`).
TIER_DAMAGE = record({
    "1": {"bullet": 10, "missile": 20, "laser": 25},
    "2": {"bullet": 15, "missile": 25, "laser": 30},
    "3": {"bullet": 20, "missile": 35, "laser": 40},
    "4": {"bullet": 40, "missile": 55, "laser": 60},
})

# The models that are not a kind of their own, with the kind they belong to: the pods a Splitter
# breaks into (ENM-SPLITTER-08).
MODEL_KIND = {"splitter-pod": "splitter"}


def tier_kinds(tier: int) -> list[str]:
    """Return the kind ids of tier `tier` (1..4), in the order of `ROLES`."""
    kinds = ENEMY_TIERS[str(tier)].kinds
    return [kinds[role] for role in ROLES]


def all_kinds() -> list[str]:
    """Return the ids of the 20 kinds, tier 1 first, each tier in the order of `ROLES`."""
    out: list[str] = []
    for tier in range(1, 5):
        out.extend(tier_kinds(tier))
    return out


def tier_of(kind: str) -> int:
    """Return the tier (1..4) of a kind id or model key, 0 for one that has none."""
    name = MODEL_KIND.get(kind, kind)
    for tier in range(1, 5):
        if name in tier_kinds(tier):
            return tier
    return 0


def tier_look(kind: str) -> Any:
    """Return the colour theme (`hue`, `neon`, `hull`) of a kind's tier, None if it has none."""
    tier = tier_of(kind)
    return ENEMY_TIERS[str(tier)] if tier > 0 else None


def world_kinds(world: int) -> list[str]:
    """Return the kind ids World `world` uses: its tier's five."""
    return tier_kinds(world)
