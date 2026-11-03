# Copyright (c) 2026 Renaud Guillon
"""The wave plans of the four worlds, composed from their tier (WLD-1-17, WLD-2-17, ENM-50).

World N uses the five kinds of tier N and no other (ENM-01). Each level cycles through its own
phrases: a beat every `gap` seconds (from `gap[0]` at the start to `gap[1]` at the end, so the level
fills up as it goes), each beat the next phrase of the cycle, its groups growing by `growth` over
the level (so the second half carries more enemy HP, WLD-2-22). Beats are written in seconds and
turned into distances at the level's ground speed. A phrase is
`[kind, groups, seconds between groups, side, position (0..1), spread]`.
"""

import math

from game.config.enemy_tiers import ENEMY_TIERS
from game.config.record import concat, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# A phrase is `[kind, groups, seconds between groups, side, position, spread]`.
PHRASE_LENGTH = 5

# How each kind comes in: `[groups, seconds between groups, side, position, spread]`.
KIND_ENTRY = record({
    "hornet": [4, 0.8, "top", 0.15, 0.23],
    "scout": [3, 1.2, "top", 0.25, 0.25],
    "rocketeer": [1, 0, "top", 0.5],
    "lancer": [2, 2.5, "top", 0.25, 0.5],
    "carrier": [1, 0, "top", 0.5],
    "wasp": [2, 1.6, "top", 0.4, 0.3],
    "strafer": [2, 1.5, "left", 0.8],
    "harrier": [2, 2, "top", 0.3, 0.4],
    "sweeper": [1, 0, "top", 0.5],
    "hatchery": [1, 0, "top", 0.5],
    "phantom": [1, 0, "top", 0.65],
    "spinner": [2, 2.5, "top", 0.3, 0.4],
    "mortar": [1, 0, "top", 0.6],
    "prism": [1, 0, "top", 0.4],
    "broodmother": [1, 0, "top", 0.5],
    "splitter": [2, 2, "top", 0.3, 0.4],
    "juggernaut": [1, 0, "top", 0.5],
    "hydra": [1, 0, "top", 0.5],
    "scissor": [1, 0, "top", 0.4],
    "hive": [1, 0, "top", 0.5],
})

# The roles in the order a world brings them in over its levels (the cheap ones first).
ROLE_ORDER = ["diver", "shooter", "laser", "missile", "carrier"]
# One cycle of phrases, by role: divers and shooters often, the heavy kinds once. A shooter comes
# first, so a level shows enemy bullets from its first beat.
CYCLE = [
    "shooter",
    "diver",
    "laser",
    "diver",
    "missile",
    "shooter",
    "diver",
    "carrier",
    "laser",
    "shooter",
    "missile",
]

# How many roles a level has, by world: World 1 brings them in one level after the other; the
# later worlds start with three, then four, then all five.
ROLES_IN_LEVEL = {
    1: [2, 3, 4, 5, 5],
    2: [3, 4, 5, 5, 5],
    3: [3, 4, 5, 5, 5],
    4: [3, 4, 5, 5, 5],
}


def roles_of(world: int, level: int) -> list[str]:
    """Return the roles World `world`'s level `level` (1..5) uses."""
    return ROLE_ORDER[: ROLES_IN_LEVEL[world][level - 1]]


def kinds_of(world: int, level: int) -> list[str]:
    """Return the kinds World `world`'s level `level` uses, in the order of the roles."""
    kinds = ENEMY_TIERS[str(world)].kinds
    return [kinds[role] for role in roles_of(world, level)]


def _phrase(kind: str, turn: int) -> list[Any]:
    """Return the phrase of `kind`, mirrored every other turn."""
    entry = KIND_ENTRY[kind]
    side = entry[2]
    position = entry[3]
    flip = turn % 2 == 1
    if flip:
        position = 1 - position
        if side == "left":
            side = "right"
    head = [kind, entry[0], entry[1], side, position]
    if len(entry) > 4:
        spread = entry[4]
        return concat(head, [-spread if flip else spread])
    return head


def level_phrases(world: int, level: int) -> list[Any]:
    """Return the phrases of one level, cycling through its kinds (see `CYCLE`)."""
    roles = roles_of(world, level)
    tier_kinds = ENEMY_TIERS[str(world)].kinds
    phrases: list[Any] = []
    seen: dict[str, int] = {}
    for role in CYCLE:
        if role not in roles:
            continue
        kind = tier_kinds[role]
        turn = seen.get(kind, 0)
        seen[kind] = turn + 1
        phrases.append(_phrase(kind, turn))
    return phrases


def level_plan(world: int, level: int) -> Any:
    """Return the wave plan of World `world`'s level `level` (1..5): its phrases and pace."""
    start = 6.4 - 0.4 * (level - 1) - 0.6 * (world - 1)
    return record({
        "from": 4,
        "to": 226 if world == 1 else 292,
        "gap": [start, start * 0.72],
        "growth": 0.6 + 0.1 * (world - 1) + 0.05 * (level - 1),
        "phrases": level_phrases(world, level),
    })


def compose_beats(plan: Any) -> list[Any]:
    """Return the beats of `plan`, deterministic."""
    beats = []
    span = plan["to"] - plan["from"]
    t = plan["from"]
    i = 0
    while t <= plan["to"] and len(plan["phrases"]) > 0:
        phrase = plan["phrases"][i % len(plan["phrases"])]
        kind = phrase[0]
        count = phrase[1]
        interval = phrase[2]
        side = phrase[3]
        position = phrase[4]
        has_spread = len(phrase) > PHRASE_LENGTH
        grown = max(1, math.floor(count * (1 + (plan["growth"] * (t - plan["from"])) / span) + 0.5))
        head = [math.floor(t * 10 + 0.5) / 10, kind, grown, interval, side, position]
        if has_spread:
            beats.append(concat(head, [phrase[5]]))
        else:
            beats.append(head)
        t = t + (plan["gap"][0] + ((plan["gap"][1] - plan["gap"][0]) * (t - plan["from"])) / span)
        i = i + 1
    return beats


# The filler of each level (D-051): groups of the level's divers and shooters in the lulls, each
# level fuller per minute than the one before (WLD-2-20). Level 1-1's is its diver only, which never
# shoots, so it stays easy (WLD-1-25).
FILLER_GAPS: list[dict[int, list[float]]] = [
    {1: [4.5, 3], 2: [3.4, 2.3], 3: [3.4, 2.3], 4: [3.4, 2.3]},
    {1: [3.5, 2.4], 2: [3.2, 2.1], 3: [3.2, 2.1], 4: [3.2, 2.1]},
    {1: [3.3, 2.2], 2: [3, 2], 3: [3, 2], 4: [3, 2]},
    {1: [3.2, 2], 2: [2.9, 1.8], 3: [2.9, 1.8], 4: [2.9, 1.8]},
    {1: [3, 1.6], 2: [2.8, 1.6], 3: [2.8, 1.6], 4: [2.8, 1.6]},
]


def level_filler(world: int, level: int) -> Any:
    """Return the filler of World `world`'s level `level`: its kinds and the gap between groups."""
    tier_kinds = ENEMY_TIERS[str(world)].kinds
    if world == 1 and level == 1:
        kinds = [tier_kinds.diver]
    else:
        kinds = [tier_kinds.diver, tier_kinds.shooter, tier_kinds.diver, tier_kinds.shooter]
    return record({"kinds": kinds, "maxGap": FILLER_GAPS[level - 1][world]})


def world_fillers(world: int) -> Any:
    """Return the fillers of World `world`, by level id (`'1-1'`...)."""
    return record({
        str(world) + "-" + str(level): level_filler(world, level) for level in range(1, 6)
    })
