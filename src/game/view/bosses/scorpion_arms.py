"""P07-R05, P16-R05, 1-4: the Scorpion's arms and claws, moving on their joints (phase 7 review)
Logical pixels, nose +Z, Y up (towards the camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.mini_bosses import SCORPION  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, offset, scaled, socket  # noqa: E402
from game.view.bosses.scorpion_look import YELLOW  # noqa: E402
from game.view.bosses.world_1_organic_kit import F, graft, sac, tentacle, vein_line  # noqa: E402
from game.view.enemies.enemy_shapes import flip_x  # noqa: E402
from render.geometry.organic import organ  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

M = ENEMY_LOOK.hull

# The left (+X) arm from the head out to the claw's socket (mirrored on the right): a dark bed of
# machinery, under two fat armour plates with a gap between them over the elbow. The upper arm and
# the forearm are drawn on their own joints (phase 7 review), their beds overlapping under the
# elbow so that it does not open as the arm bends.
UPPER_ARM = [
    [12, 16],
    [29, 26.8],
    [29, 11.2],
    [16, 4],
]
FOREARM = [
    [26, 24.9],
    [34, 30],
    [44, 27],
    [44, 17],
    [36, 15],
    [26, 9.5],
]
ARM_ARMOUR = [
    [
        [12, 16],
        [22.5, 22.7],
        [26.5, 10],
        [16, 4],
    ],
    [
        [28.5, 26.5],
        [34, 30],
        [44, 27],
        [44, 17],
        [36, 15],
        [32.5, 13],
    ],
]
# Direction of the arm seen from above (a yaw), and its lights' centres on the armour.
ARM_YAW = math.atan2(26, 12)
ARM_LIGHTS = [
    [19.5, 13.5],
    [37, 21.5],
]
# A claw around its centre, its jaws open to the front (+Z), and its knuckle.
JAW = [
    [3, -6],
    [10, -2],
    [11, 6],
    [7, 14],
    [4.5, 12.5],
    [6.5, 6],
    [5, 0],
    [2, -1],
]
# The armour cap over the back of a knuckle, leaving its front machinery bare.
KNUCKLE_CAP = [
    [-8.5, -2.5],
    [8.5, -2.5],
    [9.5, -6.5],
    [6, -11.5],
    [-6, -11.5],
    [-9.5, -6.5],
]
# The claws are drawn this much bigger than their outlines: the left (+X) one is oversized.
CLAW_SCALE = {"left": 1.45, "right": 1.22}
# Length of the cannon between the jaws.
CLAW_BARREL = 13


def _knuckle() -> list[Any]:
    """The knuckle: an octagon of radius 9 by 8, shifted back by 4."""
    result: list[Any] = []
    for k in range(8):
        a = (2 * math.pi * (k + 0.5)) / 8
        result.append([math.sin(a) * 9, math.cos(a) * 8 - 4])
    return result


KNUCKLE = _knuckle()


def _sign(x: float) -> float:
    """`Math.sign(x)`."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def _on_side(s: float, outline: list[Any]) -> list[Any]:
    """`outline` on the arm of side `s` (+1 left, at +X; -1 right)."""
    return outline if s > 0 else flip_x(outline)


def upper_arm(s: float) -> Any:
    """An upper arm (side `s`), on its shoulder joint: its bed and armour plate, its light, and the
    machinery seen at the elbow (its cog, a ram and a lit conduit)."""

    def draw(p: Any) -> None:
        p.flesh.bevel_slab(_on_side(s, UPPER_ARM), [-1.5, -0.5, 1.5], [0.8, 1.2], F.sinew)
        p.flesh.bevel_slab(_on_side(s, ARM_ARMOUR[0]), [-1, 0.5, 5], [0.8, 1.8], F.crimson)
        graft(
            p,
            scaled(_on_side(s, ARM_ARMOUR[0]), 0.75, s * 4.75, 3.25),
            [5, 6],
            [0, 0, 0],
            {"color": M.base},
        )
        x = ARM_LIGHTS[0][0]
        z = ARM_LIGHTS[0][1]
        p.neon.box([1, 0.3, 7], YELLOW, Placement([s * x, 6.3, z], s * ARM_YAW))
        sac(p, [s * 27.5, 0, 18], 3.6, F.purple, {"stretch": 0.45})
        tentacle(p, [s * 19, 2.6, 11.5], [s * 27, 2.8, 15.5], [0, 0.8, 0], [1.2, 0.9], F.sinew)
        vein_line(p, [s * 25, 1.4, 12], [s * 29.5, 1.4, 24], [0, 0.6, 0], 1.2, YELLOW)

    return draw


def forearm(s: float) -> Any:
    """A forearm (side `s`), on its elbow joint: its bed, armour plate, light, ram and claw
    socket."""

    def draw(p: Any) -> None:
        p.flesh.bevel_slab(_on_side(s, FOREARM), [-1.5, -0.5, 1.5], [0.8, 1.2], F.sinew)
        p.flesh.bevel_slab(
            _on_side(s, ARM_ARMOUR[1]),
            [-1, 0.5, 6],
            [0.8, 1.8],
            F.crimson,
            None,
            F.membrane,
        )
        x = ARM_LIGHTS[1][0]
        z = ARM_LIGHTS[1][1]
        p.neon.box([1, 0.3, 7], YELLOW, Placement([s * x, 6, z], s * ARM_YAW))
        tentacle(p, [s * 29, 2.8, 16], [s * 35, 3, 19.5], [0, 0.8, 0], [1.2, 0.9], F.sinew)
        socket(p.hull, [s * 40, 3.5, 22], 7, 1)

    return draw


def arm_limbs(side: str) -> Any:
    """The limbs of the arm on `side` (phase 7 review): the upper arm on the shoulder, the forearm
    on the elbow, and the claw's jaws on their hinges, going with the claw."""
    s = 1 if side == "left" else -1
    claw_id = "claw-" + side
    at = boss_point(0, 0)
    for part in SCORPION.stats.parts:
        if part.id == claw_id:
            at = boss_point(part.x, part.y)
    # The jaw on the claw's +X is its outer one on the left, its inner one on the right.
    plus_x = "outer" if s > 0 else "inner"
    minus_x = "inner" if s > 0 else "outer"
    limbs: Any = {}
    limbs["shoulder-" + side] = {"draw": upper_arm(s)}
    limbs["elbow-" + side] = {"draw": forearm(s)}
    limbs["jaw-" + side + "-" + plus_x] = {"draw": _jaw_drawing(at, JAW), "part": claw_id}
    limbs["jaw-" + side + "-" + minus_x] = {
        "draw": _jaw_drawing(at, flip_x(JAW)),  # type: ignore[arg-type]
        "part": claw_id,
    }
    return limbs


def _jaw_drawing(at: Vec3, jaw: list[Any]) -> Any:
    """A jaw of the claw at `at`, as a limb's drawing."""

    def draw(p: Any) -> None:
        draw_jaw(p, at, jaw)

    return draw


def claw_place(at: Vec3) -> list[Any]:
    """How a claw centred on `at` (side from its X) is drawn: its scale, its placement (scaled,
    turned a little towards the head) and `put`, a point of its own frame in model space."""
    s = _sign(at[0])
    k = CLAW_SCALE["left"] if s > 0 else CLAW_SCALE["right"]
    # Turned a little towards the centre line, so the claws close in front of the head.
    yaw = -s * 0.18
    centre = offset(at, 0, 3, 0)

    def put(x: float, y: float, z: float) -> Vec3:
        return offset(
            centre,
            x * math.cos(yaw) + z * math.sin(yaw),
            y,
            -x * math.sin(yaw) + z * math.cos(yaw),
        )

    return [k, Placement(centre, yaw), put]


def draw_jaw(p: Any, at: Vec3, jaw: list[Any]) -> None:
    """One jaw of the claw at `at`, from its outline (on its hinge's joint)."""
    placed = claw_place(at)
    k = placed[0]
    place = placed[1]
    p.flesh.bevel_slab(scaled(jaw, k), [-1, 1, 4.5], [0.6, 1.4], F.crimson, place, F.bone)


def claw(p: Any, at: Vec3) -> None:
    """A claw cannon (P07-R05, P16-R05), on its wrist joint: a swollen knuckle under a grafted cap,
    a cannon between its two pincers (drawn on their own hinges, `draw_jaw`), and the sinews that
    work them. The left (+X) claw is the bigger one, a fiddler crab's."""
    placed = claw_place(at)
    k = placed[0]
    place = placed[1]
    put = placed[2]
    p.flesh.bevel_slab(scaled(KNUCKLE, k), [-2, 1, 3], [1, 1.2], F.sinew, place)
    organ(p.flesh, 8 * k, 7, F.crimson, Placement(put(0, 0, -4 * k)), 0.4)
    p.hull.bevel_slab(scaled(KNUCKLE_CAP, k), [5, 5.5, 8], [0, 2.2], M.panel, place, M.base)
    for x in [-1, 1]:
        tentacle(
            p,
            put(x * 4 * k, 5, -5 * k),
            put(x * 8 * k, 4.6, 5 * k),
            [0, 0.6, 0],
            [0.9, 0.7],
        )
    p.neon.box([5 * k, 0.4, 0.8], YELLOW, Placement(put(0, 8, -6.5 * k), place.yaw))
    vein_line(p, put(-5 * k, 3.4, -0.5 * k), put(5 * k, 3.4, -0.5 * k), [0, 0.8, 0], 1, YELLOW)
    length = CLAW_BARREL * k * 0.85
    p.hull.cylinder(
        2.4,
        length,
        6,
        M.dark,
        Placement(put(0, 2.5, 0), place.yaw, QUARTER),
        2,
    )
    p.charge.cylinder(
        2.2,
        1.6,
        6,
        WHITE,
        Placement(put(0, 2.5, length), place.yaw, QUARTER),
        1.4,
    )
    p.muzzle(put(0, 2.5, length + 1.6), None)
