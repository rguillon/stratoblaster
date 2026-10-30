"""P05-R21, P16-R04: the Scissor, ported from `enemies/elite-scissor-model.ts`. Logical pixels, nose
+Z, Y up (towards the camera).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemies_elite import ELITE_CONFIG  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.config.enemy_look_elite import ELITE_NEON  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.enemies.elite_shapes import QUARTER, WHITE, H, ahead, strip  # noqa: E402

# Shared with the other elite models: `FIGHTER_SECTION` is in enemy_shapes.
from game.view.enemies.enemy_shapes import (  # noqa: E402
    FIGHTER_SECTION,  # noqa: E402
    SIDES,
    canopy_paint,
    flip_x,
)
from game.view.enemies.jointed_model import build_jointed_model  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    SegmentedBody,
    carapace,
    curve,
    plate,
    segmented_body,
    tendril,
)
from render.geometry.organic import (
    vein as vein_tube,
)
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

CFG = ELITE_CONFIG.scissor
NEON = ELITE_NEON.scissor
F = ENEMY_LOOK.flesh

# P16-R04: the long, narrow, segmented body under its ridged shell, tail to nose.
BODY = SegmentedBody(-31, 29, 5, 8.5, -2.5, 3.2)
SHELL = SegmentedBody(-24, 18, 4, 6.5, 0.6, 4.6, None, None, [False, False])
# The right tail fin (mirrored for the left).
FIN = [[-3, -20], [-11, -30], [-10.5, -33], [-3, -28]]  # type: list[list[float]]
# Its metal nose cap, tail to nose.
NOSE = [[17, 4, -1.4, 2.6], [23, 2.6, -1, 1.8], [29.5, 0, 0, 0]]  # type: list[list[float]]
# The right shoulder's armour plate (mirrored for the left), over the arm's hinge.
SHOULDER = [[3, 12], [9, 9], [9, 3], [3, 4]]  # type: list[list[float]]
# How high the arms ride.
ARM_Y = 1
# An arm from its hinge along +Z: a blade narrowing to the emitter at its tip.
BLADE = [[-2.8, -2.5], [2.8, -2.5], [2.2, 27], [-2.2, 27]]  # type: list[list[float]]


def body(p: Any) -> None:
    """The body and its shell, crimson veins, metal tail fins, a nose cap, reactors in sacs."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    vein = p.vein
    segmented_body(flesh, BODY, F.crimson)
    carapace(flesh, SHELL, [F.sinew, F.crimson])
    hull.loft(
        FIGHTER_SECTION,
        NOSE,
        H.base,
        None,
        LoftOptions(False, canopy_paint([2, 3], H.dark)),
    )
    neon.box([1.2, 0.5, 22], NEON, Placement([0, 4.8, -3]))
    eyes(p, [0, 1.8, 22], {"count": 2, "size": 0.6, "spacing": 3}, NEON)
    for s in SIDES:
        vein_tube(vein, curve([s * 5, 2, -20], [s * 4.5, 2.4, 14], [s * 2.5, 0.6, 0], 3), 0.9, NEON)
        plate(hull, SHOULDER if s > 0 else flip_x(SHOULDER), [3.6, 5], [H.panel, H.dark])
        hull.bevel_slab(
            FIN if s > 0 else flip_x(FIN), [-0.5, 0, 0.6], [0.2, 0.4], H.base, None, H.panel
        )
        reactor_sac(p, [s * 3, 0.3, -31], 1.6, NEON)


def shoulder(arm: Any) -> Any:
    """A shoulder hinge, a metal joint turning with its arm."""
    at = boss_point(arm.pivot[0], arm.pivot[1], -1.5)

    def draw(p: Any) -> None:
        p.hull.cylinder(3.4, 4.5, 8, H.panel, Placement(at))
        p.neon.ring(3.5, 0.8, 8, NEON, Placement([at[0], 2.2, at[2]]))

    return draw


def arm(spec: Any) -> Any:
    """A laser arm: a flesh limb, a bone blade with a crimson edge, metal cuffs, the emitter."""
    pivot = boss_point(spec.pivot[0], spec.pivot[1], ARM_Y)
    tip = boss_point(spec.muzzle[0], spec.muzzle[1], spec.muzzle[2])
    yaw = spec.aim

    def draw(p: Any) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        charge = p.charge
        muzzle = p.muzzle
        base = [pivot[0], ARM_Y + 0.6, pivot[2]]
        path = [ahead(base, yaw, d) for d in [0, 8, 16, 23]]
        tendril(flesh, path, [2.6, 1.6], 5, F.sinew)
        flesh.bevel_slab(BLADE, [-1.4, 0, 1.6], [0.4, 0.7], F.bone, Placement(pivot, yaw), F.sinew)
        for d in [6, 17]:
            pt = ahead(pivot, yaw, d)
            hull.box([6, 1, 2.4], H.panel, Placement([pt[0], ARM_Y + 1.6, pt[2]], yaw))
        strip(neon, [pivot[0], ARM_Y + 2.2, pivot[2]], yaw, [13, 18, 1.2], NEON)
        # The emitter: a cone ending at the tip, brightening through the warning.
        lens = [[2, 0], [1.2, 2.2], [0, 3]]
        charge.lathe(lens, 6, WHITE, Placement(ahead(tip, yaw, -3), yaw, QUARTER))
        muzzle(tip, "laser")

    return draw


def build_scissor(scene: Any) -> Any:
    """P05-R21, P16-R04: a long, narrow, shelled body with two crimson laser arms, bone blades on
    flesh limbs, hinged at its shoulders."""
    limbs = {}
    parts = {}
    for a in CFG.arms:
        limbs[a.joint] = shoulder(a)
        parts[a.id] = arm(a)
    return build_jointed_model(
        "scissor", scene, NEON, CFG.design, {"body": body, "limbs": limbs, "parts": parts}
    )
