# Copyright (c) 2026 Renaud Guillon
"""FB-STORM-PETREL-05 (D-254): the Storm Petrel's armour, drawn as pieces of its own.

Its body's shell is one carapace drawn in lengths along Z (`draw_shell`): the core draws it short
of the tail region, and the `tail` armour is the length over the tail, with the spine vein and the
barbs on it. Its wing roots (the `wing-roots` armour) and its outer wings (the `outer-wings`
moving pieces) are in `storm_petrel_wings`. Logical pixels, nose +Z, Y up (towards the camera).
"""

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.storm_petrel_wings import outer_wing, wing_root
from game.view.bosses.world_1_organic_kit import F, barbs, spine
from render.geometry.organic import SHELL_SECTION, SegmentedBody, segment_stations
from render.geometry.solids import LoftOptions

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


N = BOSS_LOOK.neon["storm-petrel"]

# The body: from its tail to its beak, `WIDTH` half-wide, its belly from `BOTTOM` to `MID` and its
# shell from `MID` - 1 to `TOP` (as `world_1_organic_kit.hide` draws a body).
TAIL = -64
NOSE = 56
SEGMENTS = 7
WIDTH = 14
BOTTOM = -4
TOP = 15
MID = (BOTTOM + TOP) / 2
# The shell's plates have a seam every other band (`carapace`).
SHELL_PINCH = 0.12
SHELL = SegmentedBody(TAIL, NOSE, SEGMENTS, WIDTH * 0.92, MID - 1, TOP, SHELL_PINCH)
SHELL_COLORS = [F.graphite, F.membrane]
# Where the tail plating lies along the body (model Z).
TAIL_Z = [-48, -18]


def _station_at(stations: list[Any], z: float) -> list[float]:
    """Return the loft station at `z`, interpolated between the two of `stations` around it."""
    for k in range(len(stations) - 1):
        a = stations[k]
        b = stations[k + 1]
        if a[0] <= z <= b[0]:
            t = 0 if b[0] == a[0] else (z - a[0]) / (b[0] - a[0])
            return [a[i] + (b[i] - a[i]) * t for i in range(4)]
    raise ValueError("No shell station at z " + str(z))


def shell_stations(body: SegmentedBody, z0: float, z1: float) -> list[Any]:
    """Return the loft stations of the shell of `body` from `z0` to `z1`.

    `[stations, first]`: the stations between the two heights, interpolated at both ends (an end
    at the body's own end closes to its point), and the index of the body's band `z0` lies in (so
    the seams keep their rhythm from one length to the next).
    """
    stations = segment_stations(body)
    result: list[Any] = [_station_at(stations, z0)]
    result.extend([s for s in stations if z0 < s[0] < z1])
    result.append(_station_at(stations, z1))
    first = len([s for s in stations if s[0] <= z0]) - 1
    return [result, max(0, first)]


def draw_shell(b: Any, z0: float, z1: float) -> None:
    """Draw the body's shell from `z0` to `z1` in `b`: a carapace, its plates seamed."""
    clipped = shell_stations(SHELL, z0, z1)
    offset = clipped[1]

    def paint(_side: int, band: int) -> Any:
        return SHELL_COLORS[1] if (band + offset) % 2 == 1 else None

    b.loft(SHELL_SECTION, clipped[0], SHELL_COLORS[0], None, LoftOptions(False, paint))


def draw_tail_plating(p: Any) -> None:
    """Draw the tail plating (FB-STORM-PETREL-05): the length of shell over the tail.

    From the shell's own bottom (about 5 px) up to its ridge (about 15 px), the magenta vein down
    its spine and the bone barbs on it. The cannon lies folded under it.
    """
    draw_shell(p.flesh, TAIL_Z[0], TAIL_Z[1])
    spine(p, [0, 13.4, -46], [0, 15.3, -20], {"color": N, "width": 1.4, "bow": 1.5})
    barbs(p, [0, 14, -32], {"count": 3, "spacing": 0.1, "size": 4, "dir": [0, 1, -0.5]})


def petrel_armour() -> Any:
    """Return the Storm Petrel's armour drawings by region id (`drawing.armour`, D-254).

    The config's right side (+X) is model -X.
    """
    return {
        "outer-wings-right": {"whole": outer_wing(-1)},
        "outer-wings-left": {"whole": outer_wing(1)},
        "tail": {"whole": draw_tail_plating},
        "wing-roots": {"whole": _wing_roots},
    }


def _wing_roots(p: Any) -> None:
    """Draw both wing roots: the `wing-roots` region is mirrored, one piece for both sides."""
    wing_root(-1)(p)
    wing_root(1)(p)
