# Copyright (c) 2026 Renaud Guillon
"""The Scissor (specs/enemies/scissor.md) Logical pixels, nose +Z, Y up (towards the camera)."""

from game.config.enemies_elite import ELITE_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_look_elite import ELITE_NEON
from game.view.bosses.boss_limbs import boss_point
from game.view.enemies.elite_shapes import H, ahead, strip

# Shared with the other elite models: `FIGHTER_SECTION` is in enemy_shapes.
from game.view.enemies.enemy_shapes import (
    FIGHTER_SECTION,
    SIDES,
    canopy_paint,
    flip_x,
)
from game.view.enemies.jointed_model import build_jointed_model
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import (
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
from render.geometry.solids import LoftOptions, Placement

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


CFG = ELITE_CONFIG.scissor
NEON = ELITE_NEON.scissor
F = ENEMY_LOOK.flesh

# ENM-SCISSOR-02: the long, narrow, segmented body under its ridged shell, tail to nose.
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
    """Add the body and its shell, with crimson veins (ENM-SCISSOR-03).

    Metal tail fins, a nose cap, and reactors in sacs (ENM-SCISSOR-04).
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    vein = p.vein
    segmented_body(flesh, BODY, F.slate)
    carapace(flesh, SHELL, [F.sinew, F.slate])
    hull.loft(
        FIGHTER_SECTION,
        NOSE,
        H.base,
        None,
        LoftOptions(False, canopy_paint([2, 3], H.dark)),
    )
    neon.box([1.2, 0.5, 22], NEON, Placement([0, 4.8, -3]))
    for s in SIDES:
        vein_tube(vein, curve([s * 5, 2, -20], [s * 4.5, 2.4, 14], [s * 2.5, 0.6, 0], 3), 0.9, NEON)
        plate(
            hull, SHOULDER if s > 0 else flip_x(SHOULDER), [3.6, 5], [H.panel, H.dark], None, False
        )
        hull.bevel_slab(
            FIN if s > 0 else flip_x(FIN), [-0.5, 0, 0.6], [0.2, 0.4], H.base, None, H.panel
        )
        reactor_sac(p, [s * 3, 0.3, -31], 1.6, NEON)


def shoulder(arm: Any) -> Any:
    """Return a shoulder hinge, a metal joint turning with its arm."""
    at = boss_point(arm.pivot[0], arm.pivot[1], -1.5)

    def draw(p: Any) -> None:
        p.hull.cylinder(3.4, 4.5, 8, H.panel, Placement(at))
        p.neon.ring(3.5, 0.8, 8, NEON, Placement([at[0], 2.2, at[2]]))

    return draw


def arm(spec: Any) -> Any:
    """Return a laser arm (ENM-SCISSOR-05): a flesh limb with a bone blade.

    The blade has a crimson edge; metal cuffs and the emitter complete the arm.
    """
    pivot = boss_point(spec.pivot[0], spec.pivot[1], ARM_Y)
    tip = boss_point(spec.muzzle[0], spec.muzzle[1], spec.muzzle[2])
    yaw = spec.aim

    def draw(p: Any) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        muzzle = p.muzzle
        base = [pivot[0], ARM_Y + 0.6, pivot[2]]
        path = [ahead(base, yaw, d) for d in [0, 8, 16, 23]]
        tendril(flesh, path, [2.6, 1.6], 5, F.sinew)
        flesh.bevel_slab(BLADE, [-1.4, 0, 1.6], [0.4, 0.7], F.bone, Placement(pivot, yaw), F.sinew)
        for d in [6, 17]:
            pt = ahead(pivot, yaw, d)
            hull.box([6, 1, 2.4], H.panel, Placement([pt[0], ARM_Y + 1.6, pt[2]], yaw))
        strip(neon, [pivot[0], ARM_Y + 2.2, pivot[2]], yaw, [13, 18, 1.2], NEON)
        # The emitter at the tip, along the arm: its coils and lens brighten through the warning
        # (ENM-SCISSOR-06).
        muzzle(tip, "laser", "forward", None, None, True, None, yaw)

    return draw


def build_scissor(scene: Any) -> Any:
    """ENM-SCISSOR-01: a long, narrow, shelled body with two crimson laser arms.

    Bone blades on flesh limbs, hinged at its shoulders, within the elite triangle budget
    (ENM-SCISSOR-07).
    """
    limbs = {}
    parts = {}
    for a in CFG.arms:
        limbs[a.joint] = shoulder(a)
        parts[a.id] = arm(a)
    return build_jointed_model(
        "scissor", scene, NEON, CFG.design, {"body": body, "limbs": limbs, "parts": parts}
    )
