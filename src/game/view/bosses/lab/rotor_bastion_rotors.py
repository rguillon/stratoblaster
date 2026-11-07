# Copyright (c) 2026 Renaud Guillon
"""MB-ROTOR-BASTION-05: the Rotor Bastion's arms, rotor ducts and spinning blades.

Logical pixels, nose +Z, Y up (towards the camera); shapes are given in config coordinates (X
right, Y up the screen) and turned into model space here. Each arm is a plated box beam from a
corner of the tower out to a rotor duct: a ring of dark armour round a hub nacelle on three spokes.
The front arms are moving pieces of their own (BOSS-45, folding back against the tower as it
transforms). The blades are a rig of the model's own (`drawing.rig`): they spin in their ducts, the
front ones winding down and stopping as their arms fold, the rear ones tilting forward and
spinning up (the bastion leaning into its attack).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.rotor_bastion import (
    ARM_HIGH,
    ARM_LOW,
    ARM_PIVOT,
    DUCT_HIGH,
    DUCT_IN,
    DUCT_LOW,
    DUCT_OUT,
    FRONT_DUCT,
    HUB_RADIUS,
    HUB_TOP,
    REAR_DUCT,
    ROTOR_BASTION,
    TOWER_HALF,
)
from game.config.bosses.moving_regions import motion_value, move_point
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.final_boss_greebles import SHADE
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.region_motion import progress
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["rotor-bastion"]
DEG = math.pi / 180
# The blades: how many a rotor, their length, width, height over the duct's foot and pitch.
BLADES = 3
BLADE_LENGTH = DUCT_IN - 0.8
BLADE_WIDTH = 2.6
BLADE_LIFT = 3
# How fast the blades spin (radians a second): at rest, and the rear ones once it has transformed;
# how far the rear rotors tilt forward then (radians).
SPIN = 13.0
SPIN_FAST = 21.0
TILT = 0.32


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the config point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def model_outline(outline: list[Any]) -> list[Any]:
    """Return a config outline as a model outline (`[x, z]` points)."""
    return [[-q[0], -q[1]] for q in outline]


def beam(p: Any, a: list[Any], b: list[Any], size: list[Any], color: Any) -> None:
    """Add a box beam from the config point `a` to `b`: `size` `[width, low, high]`."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dx, dy)
    # Model direction (-dx, -dy) in (x, z): a box's local +Z turns to (sin yaw, cos yaw).
    yaw = math.atan2(-dx, -dy)
    mid = pt((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, size[1])
    p.hull.box([size[0], size[2] - size[1], length], color, Placement(mid, yaw), SHADE["panel"])


def draw_arm(p: Any, root: list[Any], duct: list[Any]) -> None:
    """Draw an arm from the tower's corner `root` out to the duct centred on `duct` (config).

    A plated box beam, a lit line along its top, a ribbed conduit under its side, and a brace
    plate where it meets the duct's rim.
    """
    dx = duct[0] - root[0]
    dy = duct[1] - root[1]
    length = math.hypot(dx, dy)
    ux = dx / length
    uy = dy / length
    end = [duct[0] - ux * (DUCT_OUT - 0.6), duct[1] - uy * (DUCT_OUT - 0.6)]
    beam(p, root, end, [5, ARM_LOW, ARM_HIGH], SHADE["base"])
    # A lit line along its top, and two armour bands across it.
    a = [-(root[0] + ux * 4), -(root[1] + uy * 4)]
    b = [-(end[0] - ux * 1.5), -(end[1] - uy * 1.5)]
    edge_strips(p.neon, [a, b], 0.6, [ARM_HIGH + 0.02, ARM_HIGH + 0.14], N)
    for t in [0.35, 0.7]:
        c = [root[0] + (end[0] - root[0]) * t, root[1] + (end[1] - root[1]) * t]
        beam(
            p,
            [c[0] - ux * 1.6, c[1] - uy * 1.6],
            [c[0] + ux * 1.6, c[1] + uy * 1.6],
            [6.4, ARM_LOW - 0.6, ARM_HIGH + 0.6],
            SHADE["mid"],
        )
    # The brace where it meets the rim: a wider plate under the beam.
    beam(
        p,
        [end[0] - ux * 5, end[1] - uy * 5],
        [end[0] + ux * 0.8, end[1] + uy * 0.8],
        [8, ARM_LOW - 1, ARM_LOW + 1.6],
        SHADE["dark"],
    )


def draw_duct(p: Any, centre: list[Any], gun: bool) -> None:
    """Draw a rotor duct centred on the config point `centre` (MB-ROTOR-BASTION-05).

    Its armoured rim (a lit line round its lip, six plates round its outside), three spokes holding
    the hub nacelle, and on a rear duct (no `gun`) a lit cap on the nacelle; a front one's nacelle
    is the seat of its gun pod (the part).
    """
    at = pt(centre[0], centre[1], 0)
    lip = DUCT_HIGH
    p.hull.lathe(
        [
            [DUCT_IN, DUCT_LOW],
            [DUCT_OUT - 0.6, DUCT_LOW],
            [DUCT_OUT, DUCT_LOW + 1.2],
            [DUCT_OUT, lip - 1],
            [DUCT_OUT - 1, lip],
            [DUCT_IN + 0.4, lip],
            [DUCT_IN, lip - 0.6],
            [DUCT_IN, DUCT_LOW],
        ],
        12,
        SHADE["base"],
        Placement(at),
        False,
    )
    # A lit ring on its lip: a flat band facing up.
    p.neon.lathe(
        [[DUCT_IN + 1.8, lip + 0.04], [DUCT_IN + 0.9, lip + 0.12]], 12, N, Placement(at), False
    )
    for k in range(6):
        a = k * math.pi / 3 + math.pi / 6
        q = [
            at[0] + math.cos(a) * (DUCT_OUT - 0.2),
            DUCT_LOW + 1.5,
            at[2] + math.sin(a) * (DUCT_OUT - 0.2),
        ]
        p.hull.box([4.2, lip - DUCT_LOW - 2.2, 1], SHADE["mid"], Placement(q, math.pi / 2 - a))
    # Three spokes from the hub to the rim, under the blades.
    for k in range(3):
        a = k * math.pi * 2 / 3 + math.pi / 2
        mid = [
            at[0] + math.cos(a) * (DUCT_IN + HUB_RADIUS) / 2,
            DUCT_LOW,
            at[2] + math.sin(a) * (DUCT_IN + HUB_RADIUS) / 2,
        ]
        p.hull.box(
            [1.4, 1.6, DUCT_IN - HUB_RADIUS + 1], SHADE["dark"], Placement(mid, math.pi / 2 - a)
        )
    # The hub nacelle: a squat drum, a cooling ring round it.
    top = HUB_TOP if gun else DUCT_LOW + BLADE_LIFT + 1.6
    p.hull.lathe(
        [[HUB_RADIUS * 0.8, DUCT_LOW - 1.5], [HUB_RADIUS, DUCT_LOW], [HUB_RADIUS, top], [0, top]],
        8,
        SHADE["mid"],
        Placement(at, math.pi / 8),
    )
    if not gun:
        p.hull.cylinder(HUB_RADIUS * 0.7, 1.2, 8, SHADE["panel"], Placement([at[0], top, at[2]]))
        p.neon.cylinder(1.2, 0.6, 6, N, Placement([at[0], top + 1.2, at[2]]))


def front_arm(side: float) -> Any:
    """Return the drawing of the front arm on the config side `side`: its beam and its duct.

    Drawn at rest; the engine folds it back about the tower's corner as it transforms.
    """

    def draw(p: Any) -> None:
        draw_arm(p, [side * ARM_PIVOT[0], ARM_PIVOT[1]], [side * FRONT_DUCT[0], FRONT_DUCT[1]])
        draw_duct(p, [side * FRONT_DUCT[0], FRONT_DUCT[1]], True)
        # The hinge: a lit drum at the tower's corner the arm turns about.
        hinge = pt(side * (TOWER_HALF + 0.5), -TOWER_HALF - 0.5, ARM_LOW - 1)
        p.hull.cylinder(3.2, ARM_HIGH - ARM_LOW + 2.4, 8, SHADE["panel"], Placement(hinge))
        p.neon.ring(3.25, 0.6, 8, N, Placement([hinge[0], ARM_HIGH, hinge[2]]))

    return draw


def rotor_arms() -> Any:
    """Return the front arms' drawings by region id (`drawing.armour`); config right is +X."""
    return {
        "front-arm-right": {"whole": front_arm(1)},
        "front-arm-left": {"whole": front_arm(-1)},
    }


def draw_rear_rotors(p: Any) -> None:
    """Draw the two rear arms and their ducts, part of the core (MB-ROTOR-BASTION-05)."""
    for s in [-1, 1]:
        draw_arm(p, [s * TOWER_HALF, TOWER_HALF], [s * REAR_DUCT[0], REAR_DUCT[1]])
        draw_duct(p, [s * REAR_DUCT[0], REAR_DUCT[1]], False)


def _blades(p: Any) -> None:
    """Draw a rotor's blades round its centre (model origin): a hub cap and three blades."""
    for k in range(BLADES):
        a = k * math.pi * 2 / BLADES
        q = [math.cos(a) * BLADE_LENGTH / 2, 0, math.sin(a) * BLADE_LENGTH / 2]
        p.bare.box(
            [BLADE_WIDTH, 0.6, BLADE_LENGTH], SHADE["light"], Placement(q, math.pi / 2 - a, 0, 0.18)
        )
        tip = [math.cos(a) * (BLADE_LENGTH - 0.8), 0.62, math.sin(a) * (BLADE_LENGTH - 0.8)]
        p.neon.box([BLADE_WIDTH * 0.8, 0.12, 1.2], N, Placement(tip, math.pi / 2 - a))
    p.hull.cylinder(2.2, 1.4, 8, SHADE["dark"], Placement([0, -0.2, 0]), 1.6)


def _region(region_id: str) -> Any:
    for region in ROTOR_BASTION.armour:
        if region.id == region_id:
            return region
    raise ValueError('The Rotor Bastion has no region "' + region_id + '"')


class Rotor:
    """One rotor's blades: a `tilt` node at its duct's centre, the `spin` node under it, its model.

    `centre` is its duct's centre (config), `region` the moving region it rides (or None).
    """

    def __init__(self, tilt: Any, spin: Any, model: Any, centre: list[Any], region: Any) -> None:
        self.tilt = tilt
        self.spin = spin
        self.model = model
        self.centre = centre
        self.region = region


def _folding(boss: Any) -> float:
    """How far into its transformation `boss` is (0 at rest, 1 once transformed)."""
    if boss == None:
        return 0
    if boss.form >= 1:
        return 1
    if boss.transforming_into != 1:
        return 0
    return ease(share(boss.transform, [0, 0.8]))


class BladeRig:
    """The four rotors' blades, spinning in their ducts (see the module)."""

    def __init__(self, rotors: list[Rotor]) -> None:
        self.rotors = rotors

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Spin the blades, fold the front ones away with their arms, tilt the rear ones."""
        k = _folding(boss)
        for rotor in self.rotors:
            c = rotor.centre
            h = DUCT_LOW + BLADE_LIFT
            if rotor.region != None:
                motion = rotor.region.motion
                spot = move_point(
                    motion, motion_value(motion, progress(rotor.region, boss)), [c[0], c[1], h]
                )
                at = pt(spot[0], spot[1], spot[2])
                speed = SPIN * (1 - k)
                rotor.tilt.rotation.x = 0
            else:
                at = pt(c[0], c[1], h)
                speed = SPIN + (SPIN_FAST - SPIN) * k
                rotor.tilt.rotation.x = TILT * k
            rotor.tilt.position.set(at[0], at[1], at[2])
            rotor.spin.rotation.y = (rotor.spin.rotation.y + speed * dt) % (math.pi * 2)
            rotor.model.sync(lit, dt)


def build_blade_rig(root: Any, neon: Any, breath: Any) -> BladeRig:
    """Return the four rotors' blades on `root` (the boss model's)."""
    scene = root.getScene()
    rotors: list[Rotor] = []
    spots: list[Any] = [
        [[FRONT_DUCT[0], FRONT_DUCT[1]], "front-arm-right"],
        [[-FRONT_DUCT[0], FRONT_DUCT[1]], "front-arm-left"],
        [[REAR_DUCT[0], REAR_DUCT[1]], None],
        [[-REAR_DUCT[0], REAR_DUCT[1]], None],
    ]
    for i in range(len(spots)):
        name = "rotor-bastion-blades-" + str(i)
        tilt = new_transform_node(name + "-tilt", scene)
        tilt.parent = root
        spin = new_transform_node(name + "-spin", scene)
        spin.parent = tilt
        spin.rotation.y = i * 0.7
        model = build_enemy_model(name, scene, neon, _blades, breath)
        model.root.parent = spin
        region = _region(spots[i][1]) if spots[i][1] != None else None
        rotors.append(Rotor(tilt, spin, model, spots[i][0], region))
    return BladeRig(rotors)


def blade_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52).

    None: the blades spin inside their ducts.
    """
    return []
