# Copyright (c) 2026 Renaud Guillon
"""FB-ZEPPELIN-CITADEL-10, FB-ZEPPELIN-CITADEL-11: the Zeppelin Citadel's rig.

Logical pixels, nose +Z, Y up (towards the camera). What the sim does not need to know, animated
from its transformations (`drawing.rig`):

- a propeller at the tail of each outer envelope, spinning, drifting out with it;
- the mooring cables from bollards on the town's edge to each outer envelope's flank, stretching
  out as the envelope casts off;
- the middle envelope's gas cell: once its skin has burst it sags and deflates onto the plaza, and
  is gone.
"""

import math

from game.config.bosses.lab.zeppelin_citadel import DECK, MIDDLE, OUTER, ZEPPELIN_CITADEL
from game.config.bosses.moving_regions import motion_value
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.final_boss_greebles import SHADE
from game.view.bosses.lab.zeppelin_citadel_envelopes import Envelope, N, draw_envelope, pt
from game.view.bosses.region_motion import progress
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node, set_enabled
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# A propeller: its blades' length and width, how fast it spins (radians a second).
PROP_LENGTH = 6.5
PROP_WIDTH = 1.8
PROP_SPIN = 11.0
# The mooring cables of the right side (mirrored on the left): `[bollard, envelope]` each, config
# points `[x, y, height]`: from a bollard on the town's edge to a ring on the envelope's flank.
CABLES = [
    [[45, -30, DECK + 1.6], [OUTER[0] + 10, -30, OUTER[4] - 1]],
    [[45, 34, DECK + 1.6], [OUTER[0] + 10, 34, OUTER[4] - 1]],
]
CABLE_RADIUS = 0.4
# The gas cell's deflation: when in the second transformation it starts and ends (shares of it),
# and how much it keeps across, of its height and of its length once flat.
DEFLATE = [0.15, 0.8]
FLAT = [0.45, 0.12, 0.8]


def _region(region_id: str) -> Any:
    for region in ZEPPELIN_CITADEL.armour:
        if region.id == region_id:
            return region
    raise ValueError('The Zeppelin Citadel has no region "' + region_id + '"')


def _prop(p: Any) -> None:
    """Draw a propeller round its hub (model origin), its blades in the X-Y plane, lit tips."""
    p.hull.cylinder(1.4, 3, 6, SHADE["dark"], Placement([0, 0, -1.5], 0, math.pi / 2), 0.6)
    for k in range(3):
        a = k * math.pi * 2 / 3
        # A box stands along local Y: rolled `a - pi/2` it points (cos a, sin a).
        roll = a - math.pi / 2
        p.bare.box([PROP_WIDTH, PROP_LENGTH, 0.5], SHADE["light"], Placement([0, 0, 0], 0, 0, roll))
        tip = [math.cos(a) * (PROP_LENGTH - 0.9), math.sin(a) * (PROP_LENGTH - 0.9), 0]
        p.neon.box([PROP_WIDTH * 0.9, 0.9, 0.6], N, Placement(tip, 0, 0, roll))


def _cable(p: Any) -> None:
    """Draw a lit tether one px long, up local Y from the origin (its node stretches it)."""
    p.neon.cylinder(CABLE_RADIUS, 1, 4, N)


def _cell(p: Any) -> None:
    """Draw the middle envelope's gas cell round the origin (its node squashes it)."""
    draw_envelope(p, Envelope([0, MIDDLE[1] - 0.6, MIDDLE[2] + 2, MIDDLE[3] - 2, 0], 1), True)


def _mirror(point: list[Any], side: float) -> list[Any]:
    return [point[0] * side, point[1], point[2]]


class ZeppelinRig:
    """The rig's models: the propellers and cables (each `[node, model, ends, side]`), the cell."""

    def __init__(self, props: list[Any], cables: list[Any], cell: list[Any]) -> None:
        self.props = props
        self.cables = cables
        self.cell = cell

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose the rig for `boss` (None: at rest) as its transformations go."""
        drift = [_drift(boss, -1), _drift(boss, 1)]
        for prop in self.props:
            side = prop[3]
            d = drift[0] if side < 0 else drift[1]
            base = prop[2]
            at = pt(base[0] + d[0], base[1] + d[1], base[2] + d[2])
            prop[0].position.set(at[0], at[1], at[2])
            prop[0].rotation.z = (prop[0].rotation.z + PROP_SPIN * dt) % (math.pi * 2)
            prop[1].sync(lit, dt)
        for cable in self.cables:
            side = cable[3]
            d = drift[0] if side < 0 else drift[1]
            ends = cable[2]
            a = pt(ends[0][0], ends[0][1], ends[0][2])
            b = pt(ends[1][0] + d[0], ends[1][1] + d[1], ends[1][2] + d[2])
            _stretch(cable[0], a, b)
            cable[1].sync(lit, dt)
        self._show_cell(boss, lit, dt)

    def _show_cell(self, boss: Any, lit: Any, dt: float) -> None:
        node = self.cell[0]
        t = -1.0
        if boss != None and boss.form < 2 and boss.transforming_into == 2:
            t = boss.transform
        if t < 0 or t >= DEFLATE[1]:
            set_enabled(node, False)
            return
        set_enabled(node, True)
        e = ease(share(t, DEFLATE))
        wobble = math.sin(t * 40) * 0.05 * (1 - e) * min(1, e * 6)
        sx = 1 - (1 - FLAT[0]) * e + wobble
        sy = 1 - (1 - FLAT[1]) * e
        sz = 1 - (1 - FLAT[2]) * e
        node.scaling.set(sx, sy, sz)
        r = MIDDLE[1] - 0.6
        bottom = (MIDDLE[4] - r) + (DECK + 0.6 - (MIDDLE[4] - r)) * e
        node.position.set(0, bottom + r * sy, 0)
        self.cell[1].sync(lit, dt)


def _drift(boss: Any, side: float) -> list[Any]:
    """How far the outer envelope on `side` has drifted for `boss` (config `[dx, dy, dz]`)."""
    region = _region("outer-envelope-right" if side > 0 else "outer-envelope-left")
    value: list[Any] = motion_value(region.motion, progress(region, boss))
    return value


def _stretch(node: Any, a: Vec3, b: Vec3) -> None:
    """Place a cable's node at `a`, turned and stretched so that its local Y reaches `b`."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1
    node.position.set(a[0], a[1], a[2])
    node.rotation.x = math.acos(max(-1, min(1, dy / length)))
    node.rotation.y = math.atan2(dx, dz)
    node.scaling.set(1, length, 1)


def _model(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` on a node of `root`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


def build_zeppelin_rig(root: Any, neon: Any, breath: Any) -> ZeppelinRig:
    """Return the rig on `root` (the boss model's)."""
    props: list[Any] = []
    cables: list[Any] = []
    for side in [-1, 1]:
        name = "zeppelin-citadel-" + ("left" if side < 0 else "right")
        prop = _model(name + "-prop", root, _prop, neon, breath)
        props.append([prop[0], prop[1], [side * OUTER[0], OUTER[3] + 1.6, OUTER[4]], side])
        for k in range(len(CABLES)):
            cable = _model(name + "-cable-" + str(k), root, _cable, neon, breath)
            ends = [_mirror(CABLES[k][0], side), _mirror(CABLES[k][1], side)]
            cables.append([cable[0], cable[1], ends, side])
    cell = _model("zeppelin-citadel-cell", root, _cell, neon, breath)
    set_enabled(cell[0], False)
    return ZeppelinRig(props, cables, cell)


def rig_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52).

    None: the propellers and cables hang on the envelopes, and the cell is gone once it has burst.
    """
    return []
