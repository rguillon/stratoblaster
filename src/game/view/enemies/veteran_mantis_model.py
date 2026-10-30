"""P05-R16, P16-R04: the Mantis, its arms on their shoulders (P05-R13), ported from
`enemies/veteran-mantis-model.ts`. Logical pixels, nose +Z, Y up. A point (x, y) of the design
(X right, Y up, facing down) is at `boss_point(x, y)`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemies_veteran import VETERAN_CONFIG  # noqa: E402
from game.config.enemies_veteran import VETERAN_NEON as N
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.sim.enemies.mantis import MANTIS_DESIGN  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.enemies.jointed_model import build_jointed_model  # noqa: E402
from game.view.enemies.organic_parts import eyes  # noqa: E402
from game.view.enemies.vetelite_organic import LEAN_SECTION  # noqa: E402
from game.view.enemies.veteran_shapes import back_band, nose_gun  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    SegmentedBody,
    carapace,
    organ,
    segment_stations,
    segmented_body,
    tendril,
)
from render.geometry.solids import Placement  # noqa: E402

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
QUARTER = math.pi / 2
CFG = VETERAN_CONFIG.mantis
ARM = CFG.arm
WHITE = [1, 1, 1]  # type: list[float]

# P16-R04: its long, swollen abdomen and plated thorax, tail to neck.
ABDOMEN = SegmentedBody(-20, -1.5, 3, 4.8, -1.4, 2.6)
THORAX = SegmentedBody(-2, 8.5, 1, 3.6, -1, 2.4)
# The blade (right arm, along its length from the shoulder `t`, and across it `w`, outwards): a
# forearm, then a scythe hooking in, its cutting edge on the inside.
BLADE = [
    [0, -1.3],
    [0, 1.3],
    [11, 1.7],
    [19, 1.4],
    [24.5, 0],
    [23, -0.9],
    [18, -2.4],
    [13, -2.8],
    [11, -1.3],
]
# The lime neon along the blade's cutting edge.
EDGE = [  # type: list[list[float]]
    [12, -1.5],
    [13, -2.6],
    [18, -2.2],
    [23, -0.7],
    [22.6, -0.2],
    [18, -1.5],
    [13, -1.8],
]


def blade_point(s: float, tw: list[float], h: float = 0) -> list[float]:
    """The blade's local point `(t, w)` on side `s`, in model space at height `h`."""
    out = (ARM.outDeg * math.pi) / 180
    sx = s * CFG.shoulder[0]
    sy = CFG.shoulder[1]
    t = tw[0]
    w = tw[1]
    x = sx + t * s * math.sin(out) + w * s * math.cos(out)
    y = sy - t * math.cos(out) + w * math.sin(out)
    return list(boss_point(x, y, h))


def outline(s: float, points: list[list[float]]) -> list[list[float]]:
    """An outline of the blade's local points, on side `s`, in model XZ."""
    result = []
    for p in points:
        q = blade_point(s, p)
        result.append([q[0], q[2]])
    return result


def draw_arm(s: float) -> Any:
    """The arm on side `s`: a flesh forearm, a bone scythe, lime along its edge, its muzzles."""

    def draw(p: Any) -> None:
        flesh = p.flesh
        neon = p.neon
        charge = p.charge
        muzzle = p.muzzle
        # P16-R04: the forearm a sinew, the scythe grown out of it.
        fore = [blade_point(s, [t, 0], 1.2) for t in [0, 6, 11.5]]
        tendril(flesh, fore, [1.5, 1.1], 3, F.sinew)
        flesh.slab(outline(s, BLADE), [0.6, 1.8], F.bone, None, F.sinew)
        neon.slab(outline(s, EDGE), [1.85, 2.05], N.mantis, None)
        muzzles = ARM.muzzles.right if s == 1 else ARM.muzzles.left
        for m in muzzles:
            at = boss_point(m[0], m[1], m[2])
            charge.box([0.9, 0.5, 0.9], WHITE, Placement([at[0], 1.9, at[2]]))
            muzzle(at, "gun")

    return draw


def draw_shoulder(s: float) -> Any:
    """The shoulder on side `s`: a metal knuckle turning with the arm, not to be shot off."""

    def draw(p: Any) -> None:
        at = blade_point(s, [0, 0], 0.2)
        p.hull.cylinder(2.2, 2, 6, H.panel, Placement(at), 1.6)

    return draw


def draw_body(p: Any) -> None:
    """The body: abdomen striped with lime, plated thorax, the head with its eyes and gun."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    segmented_body(flesh, ABDOMEN, F.teal, None, LEAN_SECTION)
    carapace(flesh, THORAX, [F.sinew, F.teal])
    # The narrow head, a bulb on its neck, a metal plate on its brow.
    organ(flesh, 2.4, 5, F.teal, Placement([0, 0.3, 9.4], 0, QUARTER), 1.1)
    hull.box([3, 0.5, 2.4], H.panel, Placement([0, 2.6, 11]))
    stations = segment_stations(ABDOMEN)
    for band in [[-15, -14], [-11.5, -10.5], [-8, -7]]:
        back_band(neon, stations, band, N.mantis)
    eyes(p, [0, 1.6, 12.6], {"count": 2, "size": 0.7, "spacing": 2.8}, N.mantis)
    p.reactor([0, 0.3, -20], 1.1)
    nose_gun(p, [0, 1.4, 11.8], 2)


def build_mantis(scene: Any) -> Any:
    """P05-R16, P16-R04: an insect with a narrow head and two long bone scythes on flesh forearms,
    folded forward, lime neon along the blades. The arms swing on their shoulders and go when shot
    off."""
    return build_jointed_model(
        "mantis",
        scene,
        N.mantis,
        MANTIS_DESIGN,
        {
            "body": draw_body,
            "limbs": {"left-shoulder": draw_shoulder(-1), "right-shoulder": draw_shoulder(1)},
            "parts": {"left-arm": draw_arm(-1), "right-arm": draw_arm(1)},
        },
    )
