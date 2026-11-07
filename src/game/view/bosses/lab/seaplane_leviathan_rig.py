# Copyright (c) 2026 Renaud Guillon
"""FB-SEAPLANE-LEVIATHAN-05, -09, -10: the Seaplane Leviathan's view rig.

Logical pixels, nose +Z, Y up. Visual only: the sim knows nothing of these pieces (no part, no
muzzle); what fires and what is hit (the mortars, the hangar, the sweepers) is in the config.

- Its propellers: three blades and a spinner on each radial engine's hub, spinning all the time.
- The floats (FB-SEAPLANE-LEVIATHAN-09): at rest an armour region (`floats`), drawn by the model.
  At the first transformation the rig takes over as the region bursts: each float's struts
  telescope in, pulling it up under the wing; it swings forward over the leading edge, half a
  turn, landing keel up on the wingtip; then its hull splits along the keel, the two halves
  folding out flat either side, and the mortar rises out of it.
- The bow's launch deck (FB-SEAPLANE-LEVIATHAN-10): stowed in the keel under the hangar, it slides
  out over the bow once the bow doors have swung apart.
- The inner engines' spinners (FB-SEAPLANE-LEVIATHAN-10): at the second transformation their
  propellers slow to a stop and their blades retract into the hub; each spinner pitches up onto
  its cowling, its four plates peel open into a crown, and the sweeper rises out of it.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.seaplane_leviathan import (
    BAY_FLOOR,
    ENGINES,
    FLOAT_DECK,
    FLOAT_HALF,
    FLOAT_KEEL,
    FLOAT_X,
    HUB_Y,
    LEADING,
    NACELLE_H,
    PROP_RADIUS,
    STRUTS,
    SWEEPER_AT,
    TIP,
    WING_TOP,
    WING_UNDER,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node, set_enabled
from render.geometry.mesh_triangles import Vertex, triangles
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["seaplane-leviathan"]
QUARTER = math.pi / 2
LAYERS = ["hull", "flesh", "bare", "neon", "vein", "charge"]
SPIN = 14
BLADES = 3
# FB-SEAPLANE-LEVIATHAN-09, shares of the first transformation: the struts telescope in, the
# float swings over the leading edge, its halves fold out (each a quarter turn).
RISE = [0.15, 0.27]
FLIP = [0.25, 0.43]
SPLIT = [0.42, 0.6]
# How far each half of a float folds out (radians): open jaws, the mortar's cradle cheeks.
SPLIT_OPEN = 1.0
# The float's pivot (playfield `[x, y, height]`): on its leading edge, inside the wing.
PIVOT = [
    FLOAT_X,
    LEADING[0] + (LEADING[1] - LEADING[0]) * FLOAT_X / TIP,
    (WING_UNDER + WING_TOP) / 2,
]
# FB-SEAPLANE-LEVIATHAN-10, shares of the second transformation: the inner propellers stop and
# retract, the spinners pitch up and peel open; the launch deck slides out.
STOP = [0.08, 0.3]
RETRACT = [0.25, 0.4]
PITCH = [0.35, 0.52]
PEEL = [0.5, 0.64]
LAUNCH = [0.45, 0.8]
# The float's stations (`[y, half width share, keel share]`, nose to tail): its plan and its
# keel's rise towards its ends.
FLOAT_STATIONS: list[Any] = [
    [-24, 0.25, 0.75],
    [-19, 0.8, 0.25],
    [-12, 1, 0],
    [0, 0.95, 0.1],
    [6, 0.5, 0.5],
]
# The halves' section (counter-clockwise seen from the nose): from the deck's edge down the side
# to the keel, and back up the split.
HALF: list[Any] = [[1, 1], [0, 1], [0, 0], [1, 0.55]]
# The spinner: its backplate's radius, its cone's height, and the backplate's offset from its
# pivot (up the spinner's axis); the pivot itself on the nacelle's axis behind the hub, so a
# quarter turn takes the spinner from the hub onto the cowling's top.
CONE_R = 3.6
CONE_H = 5.2
CONE_BASE = 5
PEEL_OPEN = 1.3
# The launch deck: its half width, length, its stowed front's Y and how far it slides out.
DECK_HALF = 5
DECK_LENGTH = 30
DECK_FRONT = -70
DECK_OUT = 28


def ramp(t: float, span: list[float]) -> float:
    """Eased progress of `t` through `span`."""
    return ease(share(t, span))


def stage_of(boss: Any, form: int) -> float:
    """How far transformation `form` has gone for `boss`: 0 before (or None), 1 once done."""
    if boss == None:
        return 0
    if boss.form >= form:
        return 1
    if boss.transforming_into != form:
        return 0
    return float(boss.transform)


# The float's drawings, in a frame of the caller's: `at` its deck's top at its middle (playfield
# Y 0 there is its own stations' 0).


def _station(at: Vec3, s: list[float], deck: float) -> list[float]:
    keel = FLOAT_DECK - FLOAT_KEEL
    low = at[1] - keel + keel * s[2]
    return [at[2] - s[0], FLOAT_HALF * s[1], low, at[1] - deck]


def draw_float_half(p: Any, at: Vec3, side: float) -> None:
    """Draw one half of the float's hull (`side` 1: model +X), split along its keel.

    From the deck down its side to the keel, its edge on the split lit; lit portholes along it.
    """
    section = [[side * q[0], q[1]] for q in HALF]
    if side < 0:
        section = [section[3], section[2], section[1], section[0]]
    stations = [_station(at, s, 0.8) for s in reversed(FLOAT_STATIONS)]
    p.hull.loft(section, stations, M.panel, Placement([at[0], 0, 0]), LoftOptions(False, None))
    p.neon.box([0.4, 0.4, 24], N, Placement([at[0] + side * 0.25, at[1] - 4.6, at[2] + 9]))
    for k in range(3):
        z = at[2] + 14 - k * 7
        p.neon.box([0.3, 0.8, 1], N, Placement([at[0] + side * 3.9, at[1] - 3.4, z]))


def draw_float_deck(p: Any, at: Vec3) -> None:
    """Draw the float's deck: a plate over its hull (its flat top), the struts' sockets on it."""
    n = len(FLOAT_STATIONS)
    outline = [[at[0] + FLOAT_HALF * s[1], at[2] - s[0]] for s in FLOAT_STATIONS]
    outline.extend([
        [at[0] - FLOAT_HALF * FLOAT_STATIONS[n - 1 - k][1], at[2] - FLOAT_STATIONS[n - 1 - k][0]]
        for k in range(n)
    ])
    p.hull.slab(outline, [at[1] - 0.8, at[1]], M.base)
    for y in STRUTS:
        p.bare.cylinder(1.3, 0.5, 6, M.dark, Placement([at[0], at[1], at[2] - y]))


def draw_strut(p: Any, top: Vec3, length: float) -> None:
    """Draw a strut hanging `length` down from `top` (its root under the wing), a lit band on it."""
    p.hull.box([1.2, length, 1.6], M.base, Placement([top[0], top[1] - length, top[2]]))
    p.neon.box([1.3, 0.4, 1.7], N, Placement([top[0], top[1] - length * 0.5, top[2]]))


def draw_float_whole(p: Any) -> None:
    """Draw both floats at rest (the `floats` region's whole armour), hanging on their struts."""
    for side in [-1, 1]:
        mid = boss_point(side * FLOAT_X, 0, FLOAT_DECK)
        draw_float_deck(p, mid)
        draw_float_half(p, mid, 1)
        draw_float_half(p, mid, -1)
        for y in STRUTS:
            draw_strut(p, boss_point(side * FLOAT_X, y, WING_UNDER), WING_UNDER - FLOAT_DECK)


def draw_float_frame(p: Any) -> None:
    """Draw what the floats leave under the wingtips (BOSS-44): the struts' hinge blocks."""
    for side in [-1, 1]:
        for y in STRUTS:
            at = boss_point(side * FLOAT_X, y, WING_UNDER - 1.2)
            p.hull.box([2.6, 1.2, 3], M.base, Placement(at))


# The propellers.


def draw_blade(p: Any) -> None:
    """Draw a blade along local +Y from the hub, its tip lit."""
    p.hull.box([1.7, PROP_RADIUS - 1.6, 0.5], M.panel, Placement([0, 1.2, 0]))
    p.neon.box([1.8, 1.2, 0.55], N, Placement([0, PROP_RADIUS - 1.6, 0]))


def draw_prop(p: Any) -> None:
    """Draw an outer engine's propeller in its hub's frame: blades round Z, a spinner ahead."""
    for k in range(BLADES):
        a = k * 2 * math.pi / BLADES
        p.hull.box([1.7, PROP_RADIUS - 1.6, 0.5], M.panel, Placement([0, 0, 0], 0, 0, a))
        tip = [-math.sin(a) * (PROP_RADIUS - 1.6), math.cos(a) * (PROP_RADIUS - 1.6), 0]
        p.neon.box([1.8, 1.2, 0.55], N, Placement(tip, 0, 0, a))
    p.hull.cylinder(2.2, 3.6, 8, M.base, Placement([0, 0, -0.6], 0, QUARTER), 0.4)


def draw_spinner(p: Any) -> None:
    """Draw an inner spinner's backplate in its pivot's frame (its axis along local +Y)."""
    p.hull.cylinder(CONE_R + 0.4, 0.8, 8, M.base, Placement([0, CONE_BASE - 0.8, 0]))
    p.neon.ring(CONE_R + 0.45, 0.3, 8, N, Placement([0, CONE_BASE - 0.5, 0]))


def petal_lean() -> float:
    """Return the lean of a closed spinner plate towards the axis (radians from upright)."""
    return math.atan2(CONE_R, CONE_H)


def draw_petal(p: Any) -> None:
    """Draw a spinner plate standing on its node's origin, up its local +Y, its face to +Z."""
    length = math.hypot(CONE_R, CONE_H)
    p.hull.box([CONE_R * 1.3, length, 0.45], M.panel, Placement([0, 0, -0.2]))
    p.neon.box([0.5, length * 0.7, 0.2], N, Placement([0, length * 0.1, -0.5]))


def draw_launch_deck(p: Any) -> None:
    """Draw the launch deck in its node's frame, stowed: from `DECK_FRONT` aft along the keel.

    A flat plated ramp, lit lane edges, chevrons and a catapult track down its middle.
    """
    z0 = -DECK_FRONT
    mid = z0 - DECK_LENGTH / 2
    p.hull.box([DECK_HALF * 2, 1, DECK_LENGTH], M.panel, Placement([0, BAY_FLOOR - 1.6, mid]))
    for x in [-DECK_HALF + 0.5, DECK_HALF - 0.5]:
        p.neon.box([0.5, 0.3, DECK_LENGTH - 2], N, Placement([x, BAY_FLOOR - 0.6, mid]))
    p.bare.box([1.2, 0.3, DECK_LENGTH - 4], M.dark, Placement([0, BAY_FLOOR - 0.6, mid]))
    for k in range(3):
        z = z0 - 3 - k * 4
        for dx in [-1, 1]:
            p.neon.box([2.8, 0.3, 0.5], N, Placement([dx * 1.6, BAY_FLOOR - 0.6, z], dx * 0.6))


def hubs() -> list[Vec3]:
    """Return each propeller's hub (model space), right engines then left ones."""
    return [boss_point(side * x, HUB_Y, NACELLE_H) for side in [1, -1] for x in ENGINES]


def spinner_pivot(side: float) -> Vec3:
    """Return an inner spinner's pivot (model space): on the nacelle's axis under its crown."""
    return boss_point(side * SWEEPER_AT[0], SWEEPER_AT[1], NACELLE_H)


class SeaplaneRig:
    """The propellers, the floats' pieces, the inner spinners and the launch deck."""

    def __init__(self) -> None:
        self.models: list[Any] = []
        # Outer propellers: hub nodes; inner ones: `[hub node, blade nodes]`.
        self.props: list[Any] = []
        self.inner: list[Any] = []
        # Each float: `[flip node, lift node, half nodes, strut nodes]`.
        self.floats: list[Any] = []
        # Each inner spinner: `[pitch node, spin node, petal nodes]`.
        self.spinners: list[Any] = []
        self.deck: Any = None
        self.turn = 0.0
        self.inner_turn = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose every piece for the boss (None: at rest), and sync their models."""
        first = stage_of(boss, 1)
        second = stage_of(boss, 2)
        self.turn = (self.turn + SPIN * dt) % (2 * math.pi)
        slow = 1 - ramp(second, STOP)
        self.inner_turn = (self.inner_turn + SPIN * slow * dt) % (2 * math.pi)
        for i in range(len(self.props)):
            self.props[i].rotation.z = self.turn if i % 2 == 0 else -self.turn
        retract = ramp(second, RETRACT)
        for inner in self.inner:
            inner[0].rotation.z = self.inner_turn
            for blade in inner[1]:
                blade.scaling.y = max(0.05, 1 - retract)
                set_enabled(blade, retract < 1)
        self._floats(first)
        pitch = ramp(second, PITCH)
        peel = ramp(second, PEEL)
        for spinner in self.spinners:
            spinner[0].rotation.x = QUARTER * (1 - pitch)
            spinner[1].rotation.y = self.inner_turn
            for petal in spinner[2]:
                petal.rotation.x = -petal_lean() + (PEEL_OPEN + petal_lean()) * peel
        self.deck.position.z = DECK_OUT * ramp(second, LAUNCH)
        set_enabled(self.deck, second > 0.2)
        if lit == None:
            return
        for model in self.models:
            model.sync(lit, dt)

    def _floats(self, t: float) -> None:
        on = t >= RISE[0]
        rise = ramp(t, RISE)
        flip = ramp(t, FLIP)
        split = ramp(t, SPLIT)
        for f in self.floats:
            set_enabled(f[0], on)
            f[0].rotation.x = -math.pi * flip
            f[1].position.y = WING_UNDER - PIVOT[2] - (WING_UNDER - FLOAT_DECK) * (1 - rise)
            f[2][0].rotation.z = SPLIT_OPEN * split
            f[2][1].rotation.z = -SPLIT_OPEN * split
            for strut in f[3]:
                set_enabled(strut, on and rise < 1)
                strut.scaling.y = max(0.05, 1 - rise)


def _node(name: str, parent: Any, at: Vec3) -> Any:
    node = new_transform_node(name, parent.getScene())
    node.parent = parent
    node.position.set(at[0], at[1], at[2])
    return node


def _model(rig: SeaplaneRig, name: str, node: Any, draw: Any, neon: Any, breath: Any) -> None:
    model = build_enemy_model(name, node.getScene(), neon, draw, breath)
    model.root.parent = node
    rig.models.append(model)


def _half_drawing(side: float) -> Any:
    def draw(p: Any) -> None:
        draw_float_half(p, [-side * FLOAT_HALF, 0, 0], side)

    return draw


def float_frame(side: float) -> list[Vec3]:
    """Return a float's flip pivot (model space) and its lift node's offset from it (raised)."""
    pivot = boss_point(side * PIVOT[0], PIVOT[1], PIVOT[2])
    return [pivot, [0, WING_UNDER - PIVOT[2], PIVOT[1]]]


def _float_deck(p: Any) -> None:
    draw_float_deck(p, [0, 0, 0])


def _build_float(rig: SeaplaneRig, root: Any, side: float, neon: Any, breath: Any) -> None:
    tag = "-r" if side > 0 else "-l"
    frame = float_frame(side)
    flip = _node("seaplane-float" + tag, root, frame[0])
    lift = _node("seaplane-float-lift" + tag, flip, frame[1])
    _model(rig, "seaplane-float-deck" + tag, lift, _float_deck, neon, breath)
    halves: list[Any] = []
    for s in [1, -1]:
        # Hinged on the deck's edge, under it (local frame of the lift: deck's top at 0).
        hinge = _node("seaplane-float-half" + tag + str(s), lift, [s * FLOAT_HALF, 0, 0])
        _model(
            rig, "seaplane-float-half-model" + tag + str(s), hinge, _half_drawing(s), neon, breath
        )
        halves.append(hinge)
    struts: list[Any] = []
    for y in STRUTS:
        top = boss_point(side * FLOAT_X, y, WING_UNDER)
        node = _node("seaplane-strut" + tag + str(y), root, top)

        def draw(p: Any) -> None:
            draw_strut(p, [0, 0, 0], WING_UNDER - FLOAT_DECK)

        _model(rig, "seaplane-strut-model" + tag + str(y), node, draw, neon, breath)
        struts.append(node)
    rig.floats.append([flip, lift, halves, struts])


def _blade_drawing(p: Any) -> None:
    draw_blade(p)


def _build_spinner(rig: SeaplaneRig, root: Any, side: float, neon: Any, breath: Any) -> None:
    tag = "-r" if side > 0 else "-l"
    pitch = _node("seaplane-spinner" + tag, root, spinner_pivot(side))
    pitch.rotation.x = QUARTER
    _model(rig, "seaplane-spinner-plate" + tag, pitch, draw_spinner, neon, breath)
    spin = _node("seaplane-spinner-spin" + tag, pitch, [0, CONE_BASE, 0])
    petals: list[Any] = []
    for k in range(4):
        a = k * QUARTER + math.pi / 4
        at = [math.sin(a) * CONE_R * 0.75, 0, math.cos(a) * CONE_R * 0.75]
        yaw = _node("seaplane-petal-yaw" + tag + str(k), spin, at)
        yaw.rotation.y = a
        petal = _node("seaplane-petal" + tag + str(k), yaw, [0, 0, 0])
        _model(rig, "seaplane-petal-model" + tag + str(k), petal, draw_petal, neon, breath)
        petals.append(petal)
    rig.spinners.append([pitch, spin, petals])


def build_seaplane_rig(root: Any, neon: Any, breath: Any) -> SeaplaneRig:
    """Return the rig on `root` (the boss model's), posed at rest."""
    rig = SeaplaneRig()
    points = hubs()
    for i in range(len(points)):
        hub = _node("seaplane-prop-" + str(i), root, points[i])
        if i % 3 == 0:
            blades: list[Any] = []
            for k in range(BLADES):
                blade = _node("seaplane-blade-" + str(i) + "-" + str(k), hub, [0, 0, 0])
                blade.rotation.z = k * 2 * math.pi / BLADES
                _model(
                    rig,
                    "seaplane-blade-model-" + str(i) + str(k),
                    blade,
                    _blade_drawing,
                    neon,
                    breath,
                )
                blades.append(blade)
            rig.inner.append([hub, blades])
        else:
            _model(rig, "seaplane-prop-model-" + str(i), hub, draw_prop, neon, breath)
            rig.props.append(hub)
    for side in [1, -1]:
        _build_float(rig, root, side, neon, breath)
        _build_spinner(rig, root, side, neon, breath)
    rig.deck = _node("seaplane-launch-deck", root, [0, 0, 0])
    _model(rig, "seaplane-launch-deck-model", rig.deck, draw_launch_deck, neon, breath)
    rig.show(None, None, 0)
    return rig


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def _apply(tris: list[Any], steps: list[Any]) -> list[Any]:
    """`tris` through `steps` in order: `["x" | "y" | "z", angle]` turns or `["t", offset]` moves.

    As Babylon nests nodes: a child's position and turn first, then its parent's.
    """
    result: list[Any] = []
    for tri in tris:
        placed: list[Any] = []
        for v in tri:
            q = [v.position[0], v.position[1], v.position[2]]
            for step in steps:
                q = _step(q, step)
            placed.append(Vertex(q, v.color))
        result.append(placed)
    return result


def _step(q: list[float], step: list[Any]) -> list[float]:
    kind = step[0]
    if kind == "t":
        o = step[1]
        return [q[0] + o[0], q[1] + o[1], q[2] + o[2]]
    c = math.cos(step[1])
    s = math.sin(step[1])
    if kind == "x":
        return [q[0], q[1] * c - q[2] * s, q[1] * s + q[2] * c]
    if kind == "y":
        return [q[0] * c + q[2] * s, q[1], -q[0] * s + q[2] * c]
    return [q[0] * c - q[1] * s, q[0] * s + q[1] * c, q[2]]


def rig_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): at rest, or with both transformations done."""
    result: list[Any] = []
    points = hubs()
    for i in range(len(points)):
        if i % 3 != 0:
            result.extend(_apply(_drawn(draw_prop), [["t", points[i]]]))
        elif unfold <= 0:
            for k in range(BLADES):
                turn = k * 2 * math.pi / BLADES
                result.extend(_apply(_drawn(_blade_drawing), [["z", turn], ["t", points[i]]]))
    for side in [1, -1]:
        frame = float_frame(side)
        pivot = frame[0]
        if unfold > 0:
            flip = ["x", -math.pi]
            lift = ["t", frame[1]]
            result.extend(_apply(_drawn(_float_deck), [lift, flip, ["t", pivot]]))
            for s in [1, -1]:
                hinge = ["t", [s * FLOAT_HALF, 0, 0]]
                steps = [["z", s * SPLIT_OPEN], hinge, lift, flip, ["t", pivot]]
                result.extend(_apply(_drawn(_half_drawing(s)), steps))
        pitch = ["x", 0 if unfold > 0 else QUARTER]
        at = ["t", spinner_pivot(side)]
        result.extend(_apply(_drawn(draw_spinner), [pitch, at]))
        open_ = PEEL_OPEN if unfold > 0 else -petal_lean()
        for k in range(4):
            a = k * QUARTER + math.pi / 4
            spot = [math.sin(a) * CONE_R * 0.75, CONE_BASE, math.cos(a) * CONE_R * 0.75]
            steps = [["x", open_], ["y", a], ["t", spot], pitch, at]
            result.extend(_apply(_drawn(draw_petal), steps))
    if unfold > 0:
        result.extend(_apply(_drawn(draw_launch_deck), [["t", [0, 0, DECK_OUT]]]))
    return result
