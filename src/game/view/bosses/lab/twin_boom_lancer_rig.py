# Copyright (c) 2026 Renaud Guillon
"""MB-TWIN-BOOM-LANCER-10: the Twin-Boom Lancer's view rig, the morph of its booms into one gun.

Logical pixels, nose +Z, Y up. What the simulation does not need: on each boom (following its
moving piece as it slides in, `boss_armour.MovingView`) the two upper petals of its engine
cowling, the half of the tailplane on its inner side, the radiator blades hidden in its tail and
the latches in its inner side; and the middle sleeve of each inner wing. As it transforms, in turn:
the tailplane splits on the centre line and each half folds up about its root (0.04-0.3 of the
transformation); the inner wings telescope, the middle sleeves sliding in under the outer ones,
as the booms slide in (`reveal.move`); the latches shoot across the gap and lock the booms together
(0.58-0.72); the cowlings' petals peel open forward (0.45-0.68) as the cannons rise out of them
(the cannons are parts, drawn with the boss's parts); the radiator blades rise out of the merged
tail beside the folded tailplane and the fins (0.62-0.85).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.twin_boom_lancer import (
    BOOM_H,
    BOOM_R,
    BOOM_X,
    COWL,
    COWL_R,
    TAILPLANE,
    TAILPLANE_H,
    TWIN_BOOM_LANCER,
    WING_ROOT,
    WING_Y,
)
from game.config.bosses.moving_regions import motion_value
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.region_motion import progress
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node
from render.geometry.mesh_triangles import Vertex, triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["twin-boom-lancer"]
QUARTER = math.pi / 2
LAYERS = ["hull", "bare", "neon", "vein", "charge"]
SOOT = [0.035, 0.035, 0.042]
# The shares of the transformation each move takes (see the module).
FOLD = [0.04, 0.3]
PEEL = [0.45, 0.68]
LATCH = [0.58, 0.72]
RADIATE = [0.62, 0.85]
# How far the petals open (radians): the top one, the outer one.
PETAL_OPEN = [2.0, 1.75]
# The cowling's upper facets (in a boom's cross section, outward +X for the right boom's outer
# side): `[centre x, centre height, roll, width]`, the top one and the outer one.
FACET_OUT = math.atan2(8, 4)
# How far the radiator blades sink when hidden, and how far a latch shoots across.
SUNK = 7.5
LATCH_TRAVEL = 3.2
# The tailplane half's span, from its boom's inner side to the centre line's seam.
HALF_SPAN = BOOM_X - BOOM_R - 0.6
LENGTH = COWL[1] - COWL[0]


def _region(side: float) -> Any:
    """Return the moving region of the boom on `side` (1: right)."""
    name = "boom-right" if side > 0 else "boom-left"
    for region in TWIN_BOOM_LANCER.armour:
        if region.id == name:
            return region
    return None


def _offset(side: float, k: float) -> Vec3:
    """Where the boom on `side` is from where it is drawn, `k` of its slide (model space)."""
    value = motion_value(_region(side).motion, k)
    return [-value[0], value[2], -value[1]]


def _share(boss: Any, span: list[float]) -> float:
    """How far a move over `span` of the transformation has gone for `boss` (None: at rest)."""
    if boss == None:
        return 0
    if boss.form >= 1:
        return 1
    if boss.transforming_into != 1:
        return 0
    return ease(share(boss.transform, span))


def _slid(boss: Any, side: float) -> float:
    """How far the boom on `side` has slid for `boss`, as its moving piece (0 to 1)."""
    if boss == None:
        return 0
    return progress(_region(side), boss)


def _facets(side: float) -> list[list[float]]:
    """Return a cowling's two petals' hinges `[x, height, roll, width]` in model space.

    The top facet's and the outer upper facet's middle, at the cowling's back; their roll turns
    the petal's +Y to the facet's outward normal.
    """
    x = -side * BOOM_X
    r = COWL_R
    out = -side
    return [
        [x, BOOM_H + r, 0.0, r],
        [x + out * r * 0.75, BOOM_H + r * 0.5, -out * FACET_OUT, math.hypot(r / 2, r)],
    ]


def draw_petal(width: float) -> Any:
    """Return the drawing of a petal `width` wide, in its hinge's frame: forward along +Z.

    A plate of the cowling's shell under its hinge's plane, a lit lip at its front, a dark seam
    and two lit ribs along it.
    """

    def draw(p: Any) -> None:
        p.hull.box([width, 0.9, LENGTH], M.panel, Placement([0, -0.9, LENGTH / 2]), M.base)
        p.neon.box([width * 0.9, 0.4, 0.7], N, Placement([0, -0.2, LENGTH - 0.5]))
        for d in [-1, 1]:
            p.neon.box([0.35, 0.3, LENGTH - 4], N, Placement([d * width * 0.28, 0, LENGTH / 2]))
        p.bare.box([width * 0.8, 0.3, 0.5], SOOT, Placement([0, 0, 2]))

    return draw


def draw_tailplane(side: float) -> Any:
    """Return the drawing of the tailplane's half on `side`, in its root hinge's frame.

    From the boom's inner side towards the centre line (the model's +X for the right boom), a
    lit seam at its end, a light along its leading edge: it folds up about its root.
    """
    toward = side
    chord = TAILPLANE[1] - TAILPLANE[0]

    def draw(p: Any) -> None:
        p.hull.box(
            [HALF_SPAN, 1.2, chord], M.base, Placement([toward * HALF_SPAN / 2, -0.6, 0]), M.panel
        )
        p.neon.box([0.6, 0.5, chord - 1], N, Placement([toward * (HALF_SPAN - 0.4), 0.1, 0]))
        p.neon.box(
            [HALF_SPAN - 2, 0.4, 0.5], N, Placement([toward * HALF_SPAN / 2, 0.5, chord / 2 - 0.6])
        )
        for k in range(3):
            p.bare.box([0.4, 0.3, chord - 2], SOOT, Placement([toward * (4 + k * 6), 0.6, 0]))

    return draw


def draw_radiator(side: float) -> Any:
    """Return the drawing of the radiator blades in the tail of the boom on `side` (model space).

    Five blades across its back between the gun pack and the fin, lit along their tops, drawn
    risen (the rig sinks them into the boom until they rise).
    """
    x = -side * BOOM_X

    def draw(p: Any) -> None:
        for k in range(5):
            z = -(16 + k * 4.5)
            p.hull.box([7, 6.4, 0.8], M.panel, Placement([x, BOOM_H + BOOM_R - 1.4, z]), M.base)
            p.neon.box([6.2, 0.4, 0.9], N, Placement([x, BOOM_H + BOOM_R + 5, z]))

    return draw


def draw_latches(side: float) -> Any:
    """Return the drawing of the latches in the inner side of the boom on `side` (model space).

    Two lit clamp blocks drawn retracted in the boom; they shoot across towards the other boom.
    """
    inner = BOOM_X - BOOM_R
    x = -side * (inner + 2.2)

    def draw(p: Any) -> None:
        for y in [-12, 26]:
            p.hull.box([4.4, 4, 5], M.panel, Placement([x, BOOM_H - 1, -y]), M.base)
            p.neon.box([4.4, 0.4, 1], N, Placement([x, BOOM_H + 3, -y]))

    return draw


def draw_sleeve(side: float) -> Any:
    """Return the drawing of the inner wing's middle sleeve on `side` (model space), as it rests.

    It slides in under the outer sleeve (drawn with the boom) as the boom slides in.
    """
    x0 = 4
    x1 = BOOM_X - BOOM_R + 0.5 - 7
    z0 = -WING_ROOT[0] - 0.5
    z1 = -WING_ROOT[1] + 0.5

    def draw(p: Any) -> None:
        outline = [[-side * x0, z0], [-side * x1, z0], [-side * x1, z1], [-side * x0, z1]]
        p.hull.bevel_slab(
            outline,
            [WING_Y[0] + 0.3, WING_Y[1] - 0.8, WING_Y[1] - 0.3],
            [0, 0.4],
            M.base,
            None,
            M.panel,
        )
        p.bare.box(
            [0.4, 0.3, z0 - z1 - 1],
            SOOT,
            Placement([-side * (x0 + x1) / 2, WING_Y[1] - 0.3, (z0 + z1) / 2]),
        )

    return draw


def _tail_hinge(side: float) -> Vec3:
    """Return the root hinge of the tailplane's half on `side` (model space)."""
    return [-side * (BOOM_X - BOOM_R), TAILPLANE_H, -(TAILPLANE[0] + TAILPLANE[1]) / 2]


class BoomRig:
    """The rig of one boom: its nodes and models (see the module)."""

    def __init__(self, side: float, nodes: Any, models: list[Any]) -> None:
        self.side = side
        self.boom = nodes["boom"]
        self.petals = nodes["petals"]
        self.tailplane = nodes["tailplane"]
        self.radiator = nodes["radiator"]
        self.latches = nodes["latches"]
        self.sleeve = nodes["sleeve"]
        self.models = models

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose the boom's pieces for `boss` and sync their models."""
        s = self.side
        k = _slid(boss, s)
        at = _offset(s, k)
        self.boom.position.set(at[0], at[1], at[2])
        half = _offset(s, k * 0.5)
        self.sleeve.position.set(half[0], half[1], half[2])
        peel = _share(boss, PEEL)
        for i in range(len(self.petals)):
            self.petals[i].rotation.x = -PETAL_OPEN[i] * peel
        self.tailplane.rotation.z = s * QUARTER * _share(boss, FOLD)
        self.radiator.position.y = -SUNK * (1 - _share(boss, RADIATE))
        self.latches.position.x = s * LATCH_TRAVEL * _share(boss, LATCH)
        for model in self.models:
            model.sync(lit, dt)


class LancerRig:
    """Both booms' rigs."""

    def __init__(self, booms: list[BoomRig]) -> None:
        self.booms = booms

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose both booms' pieces."""
        for boom in self.booms:
            boom.show(boss, lit, dt)


def _node(name: str, parent: Any, at: Vec3, roll: float = 0) -> Any:
    node = new_transform_node(name, parent.getScene())
    node.parent = parent
    node.position.set(at[0], at[1], at[2])
    node.rotation.z = roll
    return node


def _model(name: str, holder: Any, neon: Any, draw: Any, breath: Any, models: list[Any]) -> None:
    model = build_enemy_model(name, holder.getScene(), neon, draw, breath)
    model.root.parent = holder
    models.append(model)


def _build_boom(root: Any, side: float, neon: Any, breath: Any) -> BoomRig:
    name = "twin-boom-lancer-" + ("right" if side > 0 else "left")
    models: list[Any] = []
    boom = _node(name + "-boom", root, [0, 0, 0])
    petals: list[Any] = []
    facets = _facets(side)
    for i in range(len(facets)):
        f = facets[i]
        mount = _node(name + "-petal-" + str(i), boom, [f[0], f[1], -COWL[1]], f[2])
        hinge = _node(name + "-petal-hinge-" + str(i), mount, [0, 0, 0])
        _model(name + "-petal-model-" + str(i), hinge, neon, draw_petal(f[3]), breath, models)
        petals.append(hinge)
    tailplane = _node(name + "-tailplane", boom, _tail_hinge(side))
    _model(name + "-tailplane-model", tailplane, neon, draw_tailplane(side), breath, models)
    radiator = _node(name + "-radiator", boom, [0, -SUNK, 0])
    _model(name + "-radiator-model", radiator, neon, draw_radiator(side), breath, models)
    latches = _node(name + "-latches", boom, [0, 0, 0])
    _model(name + "-latches-model", latches, neon, draw_latches(side), breath, models)
    sleeve = _node(name + "-sleeve", root, [0, 0, 0])
    _model(name + "-sleeve-model", sleeve, neon, draw_sleeve(side), breath, models)
    nodes = {
        "boom": boom,
        "petals": petals,
        "tailplane": tailplane,
        "radiator": radiator,
        "latches": latches,
        "sleeve": sleeve,
    }
    return BoomRig(side, nodes, models)


def build_lancer_rig(root: Any, neon: Any, breath: Any) -> LancerRig:
    """Return both booms' rigs on `root` (the boss model's)."""
    return LancerRig([_build_boom(root, 1, neon, breath), _build_boom(root, -1, neon, breath)])


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def _turned(v: Vec3, axis: str, angle: float) -> Vec3:
    """`v` turned `angle` about the model's `axis` (as Babylon's `rotation.x`, `.y` or `.z`)."""
    c = math.cos(angle)
    s = math.sin(angle)
    if axis == "x":
        return [v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c]
    if axis == "y":
        return [v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c]
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2]]


def placed_triangles(tris: list[Any], chain: list[Any]) -> list[Any]:
    """`tris` through a chain of nodes `[position, axis, angle]`, innermost first."""
    result: list[Any] = []
    for tri in tris:
        placed: list[Any] = []
        for vertex in tri:
            v = vertex.position
            for link in chain:
                t = _turned(v, link[1], link[2])
                v = [t[0] + link[0][0], t[1] + link[0][1], t[2] + link[0][2]]
            placed.append(Vertex(v, vertex.color))
        result.append(placed)
    return result


def lancer_triangles(form: int) -> list[Any]:
    """Return the rig's triangles (model space), at rest (`form` 0) or transformed."""
    k = 1 if form >= 1 else 0
    result: list[Any] = []
    for side in [1, -1]:
        boom = [_offset(side, k), "x", 0]
        facets = _facets(side)
        for i in range(len(facets)):
            f = facets[i]
            chain = [
                [[0, 0, 0], "x", -PETAL_OPEN[i] * k],
                [[f[0], f[1], -COWL[1]], "z", f[2]],
                boom,
            ]
            result.extend(placed_triangles(_drawn(draw_petal(f[3])), chain))
        fold = [_tail_hinge(side), "z", side * QUARTER * k]
        result.extend(placed_triangles(_drawn(draw_tailplane(side)), [fold, boom]))
        rise = [[0, -SUNK * (1 - k), 0], "x", 0]
        result.extend(placed_triangles(_drawn(draw_radiator(side)), [rise, boom]))
        latch = [[side * LATCH_TRAVEL * k, 0, 0], "x", 0]
        result.extend(placed_triangles(_drawn(draw_latches(side)), [latch, boom]))
        result.extend(
            placed_triangles(_drawn(draw_sleeve(side)), [[_offset(side, k * 0.5), "x", 0]])
        )
    return result
