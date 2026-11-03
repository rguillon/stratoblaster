# Copyright (c) 2026 Renaud Guillon
"""The wave scripts of World 1 (WLD-1-17, WLD-1-18, WLD-1-19).

Each beat is written in seconds from the start of the level for readability, and turned into a
scrolled distance at the level's ground speed: waves are triggered by distance (GAME-LEVEL-01). A
beat is `[seconds, kind, groups, seconds between groups, side, position (0..1), spread]`.
"""

import math

from game.config.record import concat
from game.config.wave_plans import compose_beats, level_plan, world_fillers

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# Enemy density (WLD-1-20; phase 6 review: +50 %; D-249 raised it from 1.5 to 2 on the wide
# screen, D-252 put it back in the 540 px playfield window, D-253 raised it again in the 1000 px
# one): each beat brings this many times its groups, rounded. A beat of one group gets its extra
# groups `DENSITY_GAP` seconds apart and, from the top, `DENSITY_SPREAD` across the screen, so
# they do not come in on top of each other.
WAVE_DENSITY = 2
DENSITY_GAP = 1.5
DENSITY_SPREAD = 0.3

# Where the filler groups come in from the top, in turn.
FILL_POSITIONS = [0.3, 0.7, 0.5, 0.2, 0.8]
# A beat is `[seconds, kind, groups, interval, side, position]`, with an optional spread.
BEAT_LENGTH = 6


def denser(beat: list[Any], density: float) -> list[Any]:
    """Return a beat with `density` times its groups (see `WAVE_DENSITY`)."""
    seconds = beat[0]
    kind = beat[1]
    count = beat[2]
    interval = beat[3]
    side = beat[4]
    position = beat[5]
    has_spread = len(beat) > BEAT_LENGTH
    more = max(1, math.floor(count * density + 0.5))
    if more == count or count > 1:
        head = [seconds, kind, more, interval, side, position]
        if not has_spread:
            return head
        return concat(head, [beat[6]])
    across = DENSITY_SPREAD if side == "top" else -DENSITY_SPREAD / 2
    spread = beat[6] if has_spread else across
    return [seconds, kind, more, DENSITY_GAP, side, position, spread]


def wave_script(speed: float, beats: list[Any], density: float = WAVE_DENSITY) -> Any:
    """Return the beats as a wave script.

    At `speed` world units per second and `density` (x1: as written).
    """
    waves = []
    for beat in beats:
        d = denser(beat, density)
        wave = {
            "at": d[0] * speed,
            "kind": d[1],
            "count": d[2],
            "interval": d[3],
            "entry": {"side": d[4], "position": d[5]},
        }
        if len(d) > BEAT_LENGTH:
            wave["spread"] = d[6]
        waves.append(wave)
    return waves


def quiet_before(script: list[Any], bosses: list[float], quiet: float) -> Any:
    """Return `script` without the waves in the `quiet` world units before each of `bosses`.

    Those are the waves that would start in that stretch (GAME-LEVEL-05: the stretch before a boss
    is left free).
    """
    kept = []
    for wave in script:
        blocked = False
        for at in bosses:
            if wave["at"] > at - quiet and wave["at"] <= at:
                blocked = True
        if not blocked:
            kept.append(wave)
    return kept


def fill(beats: list[Any], filler: Any) -> list[Any]:
    """`beats` with filler groups in their lulls (WLD-1-21, phase 6 review): after each beat.

    A group of the filler's kinds in turn every `maxGap` seconds, as long as the next beat is more
    than one and a half gaps away.
    """
    # A stable insertion sort by seconds: Transcrypt's sort is not stable and takes no comparator.
    ordered = list(beats)
    index = 1
    while index < len(ordered):
        item = ordered[index]
        j = index - 1
        while j >= 0 and ordered[j][0] > item[0]:
            ordered[j + 1] = ordered[j]
            j = j - 1
        ordered[j + 1] = item
        index = index + 1
    first = ordered[0][0] if len(ordered) > 0 else 0
    last = ordered[len(ordered) - 1][0] if len(ordered) > 0 else 0
    start = filler.maxGap[0]
    end = filler.maxGap[1]
    span = last - first
    if span == 0:
        span = 1

    def gap_at(t: float) -> float:
        gap: float = start + ((end - start) * (t - first)) / span
        return gap

    out: list[Any] = []
    n = 0
    for position_index in range(len(ordered)):
        beat = ordered[position_index]
        out.append(beat)
        next_t = ordered[position_index + 1][0] if position_index + 1 < len(ordered) else beat[0]
        t = beat[0] + gap_at(beat[0])
        while next_t - t > gap_at(t) / 2:
            kind = filler.kinds[n % len(filler.kinds)]
            position = FILL_POSITIONS[n % len(FILL_POSITIONS)]
            if kind:
                out.append([t, kind, 1, 0, "top", position])
            t = t + gap_at(t)
            n = n + 1
    return out


# The written beats of each level (LVL-1-1-08 … LVL-1-5-08), composed from World 1's tier (ENM-49):
# 1-1 has the Hornet and the Scout, and each level brings in one more kind: the Lancer, the
# Rocketeer, then the Carrier, with every kind in 1-5.
WAVES_1_1 = compose_beats(level_plan(1, 1))
WAVES_1_2 = compose_beats(level_plan(1, 2))
WAVES_1_3 = compose_beats(level_plan(1, 3))
WAVES_1_4 = compose_beats(level_plan(1, 4))
WAVES_1_5 = compose_beats(level_plan(1, 5))

# The filler of each level (phase 6 review: the levels felt empty), in level order: LVL-1-1-10 …
# LVL-1-5-10. 1-1 gets only Hornets, which do not shoot, so it stays easy (WLD-1-25); later levels
# fill up sooner and tighter (D-051), so each is harder than the one before (WLD-1-22) and its
# second half than its first (WLD-1-24).
WORLD_1_FILLERS = world_fillers(1)
