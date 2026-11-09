# Copyright (c) 2026 Renaud Guillon
"""The wave plans of the four worlds, composed from a mix of tiers (WLD-1-17, WLD-2-17, ENM-50).

Each level mixes two or three tiers, each with its share of the enemies (`tier_mix`, D-283), and
brings every kind of each of them. A beat is one big wave of one kind alone: the next beat starts
only when the wave has come in, plus a breather (`gap`, from `gap[0]` at the start to `gap[1]` at
the end, so the level fills up as it goes). The groups of a wave grow by `growth` over the level
(so the second half carries more enemy HP, WLD-2-22). Each time a kind comes round it comes in
another way: a line across the top, a column down a side, a pincer from both edges. Beats are
written in seconds and turned into distances at the level's ground speed. A way of coming in is
`[groups, seconds between groups, side, position (0..1), spread, alternate (0 or 1)]`.
"""

import math

from game.config.enemies_veteran import VETERAN_CONFIG
from game.config.enemy_tiers import ENEMY_TIERS
from game.config.level_enemies import LEVEL_ENEMIES
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
# The first five beats of a tier in a level bring each of its kinds once (ENM-50), then its beats
# follow `CYCLE`. The diver comes last: its waves are the biggest (the Wasp's groups are swarms),
# so a tier with a small share meets its other kinds first.
FIRST_PASS = ["shooter", "laser", "missile", "carrier", "diver"]


def tier_mix(world: int, level: int) -> list[list[int]]:
    """Return the tiers of World `world`'s level `level` (1..5), as `[tier, percent]` pairs.

    The percent is the tier's share of the level's enemies (ENM-50, D-283). World 1 goes from 80 %
    tier 1 and 20 % tier 2 in 1-1 to 60 / 40 in 1-5. Worlds 2 and 3 are 60 % their own tier, the
    other 40 % sliding from the tier below (40 % in the first level) to the tier above (40 % in
    the last). World 4 goes from 60 % tier 4 and 40 % tier 3 to tier 4 only in 4-5. The first pair
    is the level's main tier; a tier at 0 % is left out.
    """
    step = level - 1
    if world == 1:
        pairs = [[1, 80 - 5 * step], [2, 20 + 5 * step]]
    elif world == 4:
        pairs = [[4, 60 + 10 * step], [3, 40 - 10 * step]]
    else:
        pairs = [[world, 60], [world - 1, 40 - 10 * step], [world + 1, 10 * step]]
    return [pair for pair in pairs if pair[1] > 0]


def tier_sequence(tier: int) -> list[str]:
    """Return the kinds of `tier` in the order its beats bring them: `FIRST_PASS`, then `CYCLE`."""
    kinds = ENEMY_TIERS[str(tier)].kinds
    return [kinds[role] for role in concat(FIRST_PASS, CYCLE)]


def kinds_of(world: int, level: int) -> list[str]:
    """Return every kind World `world`'s level `level` uses: all the kinds of each of its tiers."""
    kinds: list[str] = []
    for pair in tier_mix(world, level):
        tier_kinds = ENEMY_TIERS[str(pair[0])].kinds
        kinds = concat(kinds, [tier_kinds[role] for role in FIRST_PASS])
    return kinds


def enemies_factor(world: int, level: int, enemies: float | None = None) -> float:
    """Return how many times its composed enemies a level brings (D-307): `enemies`, or its own."""
    if enemies is not None:
        return enemies
    factor: float = LEVEL_ENEMIES[str(world) + "-" + str(level)]
    return factor


def level_plan(world: int, level: int, enemies: float | None = None) -> Any:
    """Return the wave plan of World `world`'s level `level` (1..5): its tiers and pace.

    `enemies`: how many times its composed enemies it brings (default: the level's own, D-307).
    """
    start = 3.4 - 0.2 * (level - 1) - 0.3 * (world - 1)
    return record({
        "world": world,
        "level": level,
        "from": 4,
        "to": 226 if world == 1 else 292,
        "gap": [start, start * 0.7],
        "growth": 0.6 + 0.1 * (world - 1) + 0.05 * (level - 1),
        # How much bigger than written the waves of several groups are: later levels and worlds
        # bring bigger waves (WLD-1-22). A lone heavy enemy stays alone.
        "size": 1.4 + 0.2 * (level - 1) + 0.1 * (world - 1),
        # Each tier's share of the enemies and the order its beats bring its kinds (D-283).
        "tiers": [[pair[1], tier_sequence(pair[0])] for pair in tier_mix(world, level)],
        # The filler, counted with the beats it follows when sharing the enemies out.
        "filler": level_filler(world, level, enemies),
        # How many times its groups each wave brings (D-307).
        "enemies": enemies_factor(world, level, enemies),
    })


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


def wave_duration(groups: int, interval: float) -> float:
    """Return the seconds a beat of `groups` groups keeps coming in, density included."""
    more = max(1, math.floor(groups * WAVE_DENSITY + 0.5))
    if more == groups or groups > 1:
        return (more - 1) * interval
    return (more - 1) * DENSITY_GAP


# Ships in one group of a kind, when more than one: a Wasp group is a swarm.
GROUP_SIZE = {"wasp": VETERAN_CONFIG.wasp.groupSize}


def group_size(kind: str) -> int:
    """Return how many ships one group of `kind` is."""
    size: int = GROUP_SIZE.get(kind, 1)
    return size


def enemies_of(groups: int, kind: str = "") -> int:
    """Return how many ships a beat (or a filler group) of `groups` groups of `kind` brings.

    The density included (WLD-1-20), each group counted with its ships.
    """
    return max(1, math.floor(groups * WAVE_DENSITY + 0.5)) * group_size(kind)


def filler_groups(plan: Any, kind: str, t: float, ends: float, next_t: float) -> int:
    """Return how many filler groups come in after a beat of `kind` at `t` (see `waves.fill`).

    `ends`: when its wave has come in. `next_t`: when the next beat comes. None when the level has
    no filler or `kind` is not one of its kinds. The gap runs over the plan, not over its beats as
    in `fill`, so the count is close, not exact.
    """
    filler = plan["filler"]
    if not filler or kind not in filler["kinds"]:
        return 0
    span = plan["to"] - plan["from"]
    first = filler["maxGap"][0]
    last = filler["maxGap"][1]

    def gap_at(at: float) -> float:
        progress = min(1, max(0, (at - plan["from"]) / span))
        gap: float = first + (last - first) * progress
        return gap

    count = 0
    f = ends + gap_at(t)
    while next_t - f > gap_at(f) / 2:
        count += 1
        f = f + gap_at(f)
    return count


def _quiet_end(quiet: list[list[float]] | None, t: float) -> float:
    """Return when the quiet stretch `t` falls in ends (a little after), or `t` if in none."""
    if quiet is None:
        return t
    for stretch in quiet:
        # Beats are written to a tenth of a second: keep a tenth clear on each side.
        if t > stretch[0] - 0.1 and t <= stretch[1] + 0.1:
            return stretch[1] + 0.2
    return t


def _pick_tier(shares: list[float], counts: list[float]) -> list[float]:
    """Return `[index, shortfall]` of the tier furthest below its share of the enemies so far.

    The shortfall is how many enemies it lacks. Ties go to the first (the level's main tier).
    """
    total = 0.0
    for c in counts:
        total += c
    best = 0
    best_gap = -1e9
    for i in range(len(shares)):
        gap = shares[i] * total - counts[i]
        if gap > best_gap + 1e-9:
            best = i
            best_gap = gap
    return [best, best_gap]


def _beat_of(t: float, kind: str, groups: int, phrase: list[Any]) -> list[Any]:
    """Return the beat of `groups` groups of `kind` at `t`, coming in the way of `phrase`."""
    head = [math.floor(t * 10 + 0.5) / 10, kind, groups, phrase[2], phrase[3], phrase[4]]
    if phrase[6] == 1:
        return concat(head, [phrase[5], 1])
    if phrase[5] != 0:
        return concat(head, [phrase[5]])
    return head


def _groups(plan: Any, t: float, phrase: list[Any], lacking: float, main: bool) -> int:
    """Return how many groups a beat of `phrase` at `t` brings.

    Its written groups, sized and grown over the level, times the level's `enemies` (D-307), but no
    more than its tier lacks (`lacking` ships), so each tier keeps to its share: the main tier's
    never fewer groups than written (times `enemies`), another tier's at least one.
    """
    count = phrase[1]
    if count > 1:
        count = math.floor(count * plan["size"] + 0.5)
    span = plan["to"] - plan["from"]
    growth = 1 + (plan["growth"] * (t - plan["from"])) / span
    grown = max(1, math.floor(count * growth * plan["enemies"] + 0.5))
    fits = math.floor(lacking / group_size(phrase[0]) / WAVE_DENSITY + 0.5)
    least = max(1, math.floor(phrase[1] * plan["enemies"] + 0.5)) if main else 1
    return int(max(1, min(grown, max(least, fits))))


class _TierPicker:
    """Which tier, and which of its kinds, each beat of a plan brings (D-283)."""

    def __init__(self, tiers: list[Any]) -> None:
        self.tiers = tiers
        self.shares = [tier[0] / 100 for tier in tiers]
        # Ships of each tier so far, the filler counted with its beat.
        self.counts = [0.0 for _ in tiers]
        self.next_kind = [0 for _ in tiers]
        self.turns: dict[str, int] = {}

    def pick(self) -> list[Any]:
        """Return `[tier index, kind, its turn, shortfall, introducing]` of the next beat."""
        picked = _pick_tier(self.shares, self.counts)
        tier = int(picked[0])
        sequence = self.tiers[tier][1]
        introducing = self.next_kind[tier] < len(FIRST_PASS)
        kind = sequence[self.next_kind[tier]]
        self.next_kind[tier] = self.next_kind[tier] + 1
        if self.next_kind[tier] >= len(sequence):
            self.next_kind[tier] = len(FIRST_PASS)
        turn = self.turns.get(kind, 0)
        self.turns[kind] = turn + 1
        return [tier, kind, turn, picked[1], introducing]


def compose_beats(plan: Any, quiet: list[list[float]] | None = None) -> list[Any]:
    """Return the beats of `plan`, deterministic, none in the `quiet` `[from, to]` seconds.

    A beat is `[seconds, kind, groups, seconds between groups, side, position]` with, when it has
    them, the spread and the alternate flag (`1`: the groups come in from both edges in turn).
    Each beat goes to the tier furthest below its share of the ships (the filler groups that
    follow a beat counted with it, D-283), which brings the next kind of its sequence. A wave
    brings no more than its tier lacks (see `_groups`); a smaller tier brings each of its kinds
    first as one group, so all of them fit in its share (ENM-50).
    """
    beats: list[Any] = []
    span = plan["to"] - plan["from"]
    t = plan["from"]
    picker = _TierPicker(plan["tiers"])
    last: list[Any] = []
    while t <= plan["to"] and len(plan["tiers"]) > 0:
        held = _quiet_end(quiet, t)
        if held > t:
            # The stretch before a boss stays free (GAME-LEVEL-05): wait for its end.
            t = held
            continue
        if len(last) > 0:
            # `last`: the tier, kind, time and end of the beat before, whose filler comes now.
            fill_count = filler_groups(plan, last[1], last[2], last[3], t)
            picker.counts[last[0]] += enemies_of(1, last[1]) * fill_count
        choice = picker.pick()
        tier = choice[0]
        kind = choice[1]
        phrase = _phrase(kind, choice[2])
        groups = _groups(plan, t, phrase, choice[3], tier == 0)
        if tier > 0 and choice[4]:
            groups = 1
        picker.counts[tier] += enemies_of(groups, kind)
        beat = _beat_of(t, kind, groups, phrase)
        beats.append(beat)
        # The wave comes in, is met, then a breather: no other kind comes in meanwhile.
        breather = plan["gap"][0] + ((plan["gap"][1] - plan["gap"][0]) * (t - plan["from"])) / span
        last = [tier, kind, beat[0], beat[0] + wave_duration(groups, phrase[2])]
        t = t + wave_duration(groups, phrase[2]) + SETTLE + breather
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


def level_filler(world: int, level: int, enemies: float | None = None) -> Any:
    """Return the filler of World `world`'s level `level`: its kinds and the gap between groups.

    The divers and shooters of each of the level's tiers (D-283); 1-1's only the Hornet, which never
    shoots, so it stays easy (WLD-1-25). Its groups come `enemies` times as often (D-307).
    """
    factor = enemies_factor(world, level, enemies)
    if world == 1 and level == 1:
        gaps = FILLER_GAPS[0][1]
        kinds = [ENEMY_TIERS["1"].kinds.diver]
    else:
        gaps = FILLER_GAPS[level - 1][world]
        kinds = []
        for pair in tier_mix(world, level):
            tier_kinds = ENEMY_TIERS[str(pair[0])].kinds
            kinds = concat(kinds, [tier_kinds.diver, tier_kinds.shooter])
    return record({"kinds": kinds, "maxGap": [gaps[0] / factor, gaps[1] / factor]})


def world_fillers(world: int) -> Any:
    """Return the fillers of World `world`, by level id (`'1-1'`...)."""
    return record({
        str(world) + "-" + str(level): level_filler(world, level) for level in range(1, 6)
    })
