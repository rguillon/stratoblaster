# Copyright (c) 2026 Renaud Guillon
"""The wave plans of the four worlds, composed from their tier (WLD-1-17, WLD-2-17, ENM-50).

World N uses the five kinds of tier N and no other (ENM-01). Each level cycles through the kinds of
its roles, one kind per beat, and a beat is one big wave of that kind alone: the next beat starts
only when the wave has come in, plus a breather (`gap`, from `gap[0]` at the start to `gap[1]` at
the end, so the level fills up as it goes). The groups of a wave grow by `growth` over the level
(so the second half carries more enemy HP, WLD-2-22). Each time a kind comes round it comes in
another way: a line across the top, a column down a side, a pincer from both edges. Beats are
written in seconds and turned into distances at the level's ground speed. A way of coming in is
`[groups, seconds between groups, side, position (0..1), spread, alternate (0 or 1)]`.
"""

import math

from game.config.enemy_tiers import ENEMY_TIERS
from game.config.record import concat, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# Enemy density (WLD-1-20): each beat brings this many times its groups, rounded. A beat of one
# group gets its extra groups `DENSITY_GAP` seconds apart and, from the top, `DENSITY_SPREAD`
# across the screen, so they do not come in on top of each other.
WAVE_DENSITY = 1.5
DENSITY_GAP = 1.5
DENSITY_SPREAD = 0.3

# Seconds after its last group has come in before a wave counts as over (the next one may start
# once the breather has passed): time to meet and clear the wave.
SETTLE = 2

# How each kind comes in, in the order it comes round: `[groups, seconds between groups, side,
# position, spread, alternate]`. Every other time round, a way is mirrored left to right. Only the
# kinds that fly in from a side (the divers and the strafer) have sides; the others come from the
# top, as a line, a mirrored line or a pincer.
KIND_ENTRY = record({
    "hornet": [
        [5, 0.3, "top", 0.15, 0.17, 0],
        [5, 0.35, "left", 0.8, -0.06, 0],
        [6, 0.28, "top", 0.2, 0.1, 1],
        [5, 0.35, "left", 0.65, 0, 1],
    ],
    "scout": [
        [4, 0.6, "top", 0.2, 0.2, 0],
        [4, 0.6, "top", 0.2, 0.2, 1],
        [4, 0.6, "top", 0.5, 0, 0],
    ],
    "rocketeer": [[1, 0, "top", 0.5, 0, 0], [1, 0, "top", 0.25, 0.5, 1]],
    "lancer": [[3, 1.3, "top", 0.25, 0.25, 0], [3, 1.3, "top", 0.2, 0.3, 1]],
    "carrier": [[1, 0, "top", 0.5, 0, 0], [1, 0, "top", 0.3, 0.4, 1]],
    "wasp": [
        [3, 1, "top", 0.3, 0.2, 0],
        [3, 1, "left", 0.8, -0.08, 0],
        [3, 1, "left", 0.7, 0, 1],
        [3, 1, "top", 0.25, 0.5, 1],
    ],
    "strafer": [
        [3, 0.8, "left", 0.8, -0.07, 0],
        [3, 0.9, "top", 0.15, 0.3, 0],
        [4, 0.7, "left", 0.7, 0, 1],
        [3, 0.9, "top", 0.2, 0.25, 1],
    ],
    "harrier": [[3, 1.1, "top", 0.3, 0.2, 0], [3, 1.1, "top", 0.25, 0.5, 1]],
    "sweeper": [[1, 0, "top", 0.5, 0, 0], [1, 0, "top", 0.25, 0.5, 1]],
    "hatchery": [[1, 0, "top", 0.5, 0, 0], [1, 0, "top", 0.3, 0.4, 1]],
    "phantom": [[3, 1.1, "top", 0.3, 0.2, 0], [3, 1.1, "top", 0.25, 0.5, 1]],
    "spinner": [[3, 1.1, "top", 0.3, 0.2, 0], [3, 1.1, "top", 0.25, 0.5, 1]],
    "mortar": [[1, 0, "top", 0.6, 0, 0], [1, 0, "top", 0.3, 0.4, 1]],
    "prism": [[1, 0, "top", 0.4, 0, 0], [1, 0, "top", 0.25, 0.5, 1]],
    "broodmother": [[1, 0, "top", 0.5, 0, 0], [1, 0, "top", 0.3, 0.4, 1]],
    "splitter": [[3, 1.1, "top", 0.3, 0.2, 0], [3, 1.1, "top", 0.25, 0.5, 1]],
    "juggernaut": [[1, 0, "top", 0.5, 0, 0], [1, 0, "top", 0.3, 0.4, 1]],
    "hydra": [[1, 0, "top", 0.5, 0, 0], [1, 0, "top", 0.3, 0.4, 1]],
    "scissor": [[1, 0, "top", 0.4, 0, 0], [1, 0, "top", 0.3, 0.4, 1]],
    "hive": [[1, 0, "top", 0.5, 0, 0], [1, 0, "top", 0.3, 0.4, 1]],
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
    """Return the way `kind` comes in on its `turn`-th time round (0, 1, ...).

    A beat's `[kind, groups, seconds between groups, side, position, spread, alternate]`: the ways
    of the kind in turn, each mirrored every other time the list has gone round.
    """
    ways = KIND_ENTRY[kind]
    entry = ways[turn % len(ways)]
    side = entry[2]
    position = entry[3]
    spread = entry[4]
    if math.floor(turn / len(ways)) % 2 == 1:
        position = 1 - position
        spread = -spread
        if side == "left":
            side = "right"
    return [kind, entry[0], entry[1], side, position, spread, entry[5]]


def level_cycle(world: int, level: int) -> list[str]:
    """Return the kinds of one level in the order its beats bring them (see `CYCLE`)."""
    roles = roles_of(world, level)
    tier_kinds = ENEMY_TIERS[str(world)].kinds
    return [tier_kinds[role] for role in CYCLE if role in roles]


def level_plan(world: int, level: int) -> Any:
    """Return the wave plan of World `world`'s level `level` (1..5): its cycle and pace."""
    start = 3.4 - 0.2 * (level - 1) - 0.3 * (world - 1)
    return record({
        "from": 4,
        "to": 226 if world == 1 else 292,
        "gap": [start, start * 0.7],
        "growth": 0.6 + 0.1 * (world - 1) + 0.05 * (level - 1),
        # How much bigger than written the waves of several groups are: later levels and worlds
        # bring bigger waves (WLD-1-22). A lone heavy enemy stays alone.
        "size": 1.4 + 0.2 * (level - 1) + 0.1 * (world - 1),
        "cycle": level_cycle(world, level),
    })


def wave_duration(groups: int, interval: float) -> float:
    """Return the seconds a beat of `groups` groups keeps coming in, density included."""
    more = max(1, math.floor(groups * WAVE_DENSITY + 0.5))
    if more == groups or groups > 1:
        return (more - 1) * interval
    return (more - 1) * DENSITY_GAP


def compose_beats(plan: Any) -> list[Any]:
    """Return the beats of `plan`, deterministic.

    A beat is `[seconds, kind, groups, seconds between groups, side, position]` with, when it has
    them, the spread and the alternate flag (`1`: the groups come in from both edges in turn).
    """
    beats = []
    span = plan["to"] - plan["from"]
    t = plan["from"]
    i = 0
    turns: dict[str, int] = {}
    while t <= plan["to"] and len(plan["cycle"]) > 0:
        kind = plan["cycle"][i % len(plan["cycle"])]
        turn = turns.get(kind, 0)
        turns[kind] = turn + 1
        phrase = _phrase(kind, turn)
        count = phrase[1]
        if count > 1:
            count = math.floor(count * plan["size"] + 0.5)
        interval = phrase[2]
        grown = max(1, math.floor(count * (1 + (plan["growth"] * (t - plan["from"])) / span) + 0.5))
        head = [math.floor(t * 10 + 0.5) / 10, kind, grown, interval, phrase[3], phrase[4]]
        if phrase[6] == 1:
            beats.append(concat(head, [phrase[5], 1]))
        elif phrase[5] != 0:
            beats.append(concat(head, [phrase[5]]))
        else:
            beats.append(head)
        # The wave comes in, is met, then a breather: no other kind comes in meanwhile.
        breather = plan["gap"][0] + ((plan["gap"][1] - plan["gap"][0]) * (t - plan["from"])) / span
        t = t + wave_duration(grown, interval) + SETTLE + breather
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
