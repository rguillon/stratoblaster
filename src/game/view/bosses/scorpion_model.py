"""P07-R05, P16-R05, 1-4: the Scorpion: a living desert
scorpion with yellow veins, a segmented shell, two arms out to its claw cannons, and a segmented
tail arched over its back, its stinger hanging in front of the head. Logical pixels, nose +Z, Y up
(towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.mini_bosses import SCORPION  # noqa: E402
from game.config.record import merge  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_greebles import mast  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, offset  # noqa: E402
from game.view.bosses.scorpion_arms import arm_limbs, claw  # noqa: E402
from game.view.bosses.scorpion_look import YELLOW  # noqa: E402
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    graft,
    hide,
    scale_outline,
    spine,
    tentacle,
)
from game.view.enemies.enemy_shapes import SIDES  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    ROUND_SECTION,  # noqa: E402
    SegmentedBody,
    carapace,
    vein,
)
from render.geometry.outline import hypot2  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

# The head plate seen from above.
HEAD = [
    [0, 24],
    [11, 20],
    [17, 10],
    [16, 0],
    [-16, 0],
    [-17, 10],
    [-11, 20],
]
# Where the right legs grow from under the body (mirrored on the left).
LEG_ROOTS = [
    [17, -1, -0.3],
    [18, -7, -0.6],
    [15, -13, -0.9],
]
# The tail's spine, from its root on the abdomen (z, y), up and back, then over the body, its last
# joint above the head, where the stinger hangs: each pair of points is a segment.
TAIL = [
    [-18, 6],
    [-28, 13],
    [-27, 22],
    [-15, 28],
    [2, 29],
    [16, 26],
    [24, 21],
]
# A patch welded on the abdomen's left.
PATCH = [
    [4, -14],
    [12, -15],
    [10, -22],
    [5, -24],
]
# Half widths of the segments, root to tip.
TAIL_WIDTH = [7, 6.5, 6, 5.5, 5, 4.5]
# The stinger around its centre: a bulb along +Z (loft stations), its emitter at the tip.
STINGER = [
    [-11, 4, -4, 4],
    [-4, 7, -6, 6],
    [4, 6, -5, 4.5],
    [11, 2.5, -2.5, 1.5],
]
STINGER_EMITTER = [
    [2.4, 0],
    [1.6, 3.5],
    [0, 5.5],
]
# Height of the stinger, and its downward tilt (it aims at the player).
STINGER_Y = 15
STINGER_TILT = 0.35


def _along(at: Vec3, pitch: float, y: float, z: float) -> Vec3:
    """The point `[0, y, z]` of a solid at `at`, pitched by `pitch`."""
    return offset(
        at,
        0,
        y * math.cos(pitch) - z * math.sin(pitch),
        y * math.sin(pitch) + z * math.cos(pitch),
    )


def _bead_body(bead: list[Any]) -> Any:
    """A tail bead as a ridged shell along its length (P16-R05)."""
    first = bead[0]
    mid = bead[1]
    last = bead[2]
    w = mid[1]
    return SegmentedBody(first[0] - w * 0.4, last[0] + w * 0.4, 1, w, -w * 0.9, w * 0.9)


def _segment(parts: Any, a: list[Any], b: list[Any], w: float) -> None:
    """A tail segment from `a` to `b` ((z, y) points), `w` wide, with a yellow light on its back."""
    dz = b[0] - a[0]
    dy = b[1] - a[1]
    length = hypot2(dz, dy)
    pitch = -math.atan2(dy, dz)
    at = [0, a[1], a[0]]
    bead = [
        [length * 0.14, w * 0.75, -w * 0.7, w * 0.7],
        [length * 0.5, w, -w * 0.9, w * 0.9],
        [length * 0.86, w * 0.75, -w * 0.65, w * 0.65],
    ]
    carapace(parts.flesh, _bead_body(bead), [F.crimson, F.membrane], Placement(at, 0, pitch))
    # The light along the segment's upper side: the section's top, or its bottom where the segment
    # runs backwards (pitched over, the section is upside down).
    up = -1 if math.cos(pitch) < 0 else 1
    parts.neon.box(
        [1, 0.4, length * 0.5],
        YELLOW,
        Placement(_along(at, pitch, w * 0.9 * up, length * 0.5), 0, pitch),
    )


def _draw_body(p: Any) -> None:
    """The body (P16-R05): a swollen, segmented abdomen under a ridged shell, the head plated with
    grafted armour, bone legs, glowing eyes, and the tail of shelled beads."""
    flesh = p.flesh
    hide(
        p,
        {
            "tail": -31,
            "nose": 6,
            "width": 18,
            "bottom": -3,
            "top": 8,
            "segments": 4,
            "shell": [F.crimson, F.membrane],
            "belly": F.sinew,
        },
    )
    flesh.bevel_slab(HEAD, [-3, 0, 6], [1.5, 3], F.sinew, None, F.crimson)
    graft(p, scale_outline(HEAD, 0.7, 0, 5), [6, 7], [0, 0, 0])
    eyes(p, [0, 7, 19], {"count": 4, "size": 0.8, "spacing": 2.2}, YELLOW)
    for s in SIDES:
        roots = LEG_ROOTS if s > 0 else LEG_ROOTS[0:2]
        for root in roots:
            x = root[0]
            z = root[1]
            knee = [s * (x + 6), 3, z - 1]
            tentacle(p, [s * x, 0, z], knee, [0, 1, 0], [1.6, 1.1], F.sinew, 4)
            tentacle(p, knee, [s * (x + 10), -2, z - 4], [0, 0.5, 0], [1.1, 0.15], F.bone, 3)
    for i in range(1, len(TAIL)):
        width = TAIL_WIDTH[i - 1] if i - 1 < len(TAIL_WIDTH) else 4
        _segment(p, TAIL[i - 1], TAIL[i], width)


def _draw_machinery(p: Any) -> None:
    """The living works (P16-R05): sinew rings at the tail's joints, a yellow vein along the tail's
    left, the torn stump of the missing right hind leg, a plate grafted on the abdomen."""
    for i in range(1, len(TAIL) - 1):
        z = TAIL[i][0]
        y = TAIL[i][1]
        width = (TAIL_WIDTH[i - 1] if i - 1 < len(TAIL_WIDTH) else 5) * 0.8
        p.flesh.cylinder(width, width * 2, 6, F.sinew, Placement([width, y, z], 0, 0, QUARTER))
        p.vein.cylinder(
            width * 1.04,
            0.8,
            6,
            YELLOW,
            Placement([0.4, y, z], 0, 0, QUARTER),
        )
    path = []
    for i in range(len(TAIL) - 1):
        path.append([(TAIL_WIDTH[i] if i < len(TAIL_WIDTH) else 5) + 0.6, TAIL[i][1], TAIL[i][0]])
    vein(p.vein, path, 1.2, YELLOW)
    # The missing right hind leg: a torn stump.
    p.flesh.cylinder(1.6, 2.4, 6, F.wound, Placement([-15, -0.5, -13], 0, 0, QUARTER))
    graft(p, PATCH, [5.5, 6.6], [0, 0, 0], {"color": M.base})
    spine(p, [0, 8.5, -26], [0, 8.5, 0], {"color": YELLOW, "width": 1})


def _stinger(p: Any, at: Vec3) -> None:
    """The stinger (P07-R05, P16-R05): a venom bulb hanging from the tail's tip, its emitter in
    front."""
    place_at = offset(at, 0, STINGER_Y, 0)
    place = Placement(place_at, 0, STINGER_TILT)
    p.flesh.loft(ROUND_SECTION, STINGER, F.purple, place)
    p.vein.box(
        [7.5, 0.6, 1],
        YELLOW,
        Placement(_along(place_at, STINGER_TILT, 6, -1), 0, STINGER_TILT),
    )
    # Brightens through the laser's warning, full while it fires.
    tip = _along(place_at, STINGER_TILT, -0.5, 11)
    p.charge.lathe(STINGER_EMITTER, 6, WHITE, Placement(tip, 0, QUARTER + STINGER_TILT))
    p.muzzle(_along(tip, QUARTER + STINGER_TILT, 5.5, 0), "laser")


def build_scorpion(scene: Any) -> Any:
    """P07-R05, P16-R05: the Scorpion, a living desert scorpion with yellow veins: a segmented
    shell, two arms out to its claw cannons, and a segmented tail arched over its back, its stinger
    hanging in front of the head, between the claws."""

    def core(p: Any) -> None:
        _draw_body(p)
        _draw_machinery(p)
        mast(p, [-6, 6, 12], 6, YELLOW)
        # The core's guns: a charge light at the front of the head.
        p.charge.cylinder(1.8, 3, 6, WHITE, Placement([0, 2, 23], 0, QUARTER), 0.8)
        p.muzzle([0, 2, 26], None)
        for s in SIDES:
            reactor_sac(p, [s * 9, 2, -28], 2.8, YELLOW)

    return build_boss_model(
        SCORPION,
        scene,
        YELLOW,
        {
            "core": core,
            "parts": {"claw-left": claw, "claw-right": claw, "stinger": _stinger},
            "limbs": merge(arm_limbs("left"), arm_limbs("right")),
        },
    )
