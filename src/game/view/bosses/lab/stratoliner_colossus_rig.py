# Copyright (c) 2026 Renaud Guillon
"""FB-STRATOLINER-COLOSSUS-05, -10, -11: the Stratoliner Colossus's view rig, its morphs.

Logical pixels, nose +Z, Y up. Looks only: the sim knows nothing of them (no part, no muzzle);
the weapons they turn into are its hidden weapons, drawn by the engine.

- Its outer engines' cowlings, four petals each, and their cores. As it first transforms (the fans'
  armour region bursts: each fan disc splits in two halves that fly off) the petals peel back from
  their hinge behind the nacelle's middle, the core telescopes out ahead into a cluster of three
  barrels, and the gatling rises out of the opened nacelle (`boss_reveal`); the core is gone once
  the gatling's turret is up, the peeled petals stay round it.
- Its inner flaps, and the second wing tier they unfold into: as it transforms the second time
  (the flaps' armour region gives way to these pieces) each flap swings up on its leading edge,
  two struts telescope up under it lifting it, it lies back down flat on them, a second wing tier,
  and an outer panel folded on its top unfolds outward; the racks slide out along it.
- Its nose cone's halves: they split open like a clamshell, then close up straight, apart, and
  slide forward, telescoping: the rails of the lance that rises between them.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.stratoliner_colossus import (
    ENGINE_H,
    ENGINE_HALF,
    ENGINE_R,
    ENGINE_X,
    FLAP_CHORD,
    FLAP_X,
    FUSELAGE,
    NOSE_JOINT,
    OUTER_Y,
    PETAL_HINGE,
    TIER_H,
    TIER_REACH,
    WING_TOP,
    trailing_edge,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.lab.condor_lifter_joints import (
    Joint,
    after,
    build_piece,
    drawn,
    posed,
    stage,
)
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


QUARTER = math.pi / 2
# Of the first transformation: the petals peel back (by `PEEL`), the core telescopes out (to
# `REACH` times its length), then is gone.
PEEL_SPAN = [0.15, 0.45]
PEEL = 1.95
CORE_OUT = [0.28, 0.56]
CORE_GONE = 0.8
REACH = 1.6
PETALS = 4
# Of the second: the flaps swing up, are lifted, lie down; their outer panels unfold; the nose
# cone's halves open, then close up apart and slide forward (`RAIL_*`), telescoping.
FLAP_UP = [0.15, 0.26]
FLAP_LIFT = [0.24, 0.36]
FLAP_DOWN = [0.34, 0.44]
FLAP_OUT = [0.44, 0.6]
NOSE_OPEN = [0.15, 0.33]
NOSE_RAIL = [0.35, 0.6]
NOSE_SWING = 0.5
RAIL_GAP = 6.8
RAIL_AHEAD = 4
RAIL_STRETCH = 1.3
FLAP_THICK = 1.4
LIFT = TIER_H - WING_TOP
STRUT_R = 0.8
CORE_LENGTH = 12
BARREL_LENGTH = 3.5
N = BOSS_LOOK.neon["stratoliner-colossus"]


# --- The outer nacelles: petals and cores. ---


def petal_length() -> float:
    """Return how long a petal is, from its hinge to the nacelle's front."""
    return ENGINE_HALF + PETAL_HINGE


def draw_petal(p: Any) -> None:
    """Draw a petal in its hinge's frame: a quarter of the cowling round the axis below.

    The axis is at local (0, -R, 0); it reaches from the hinge (z 0) forward to the nacelle's
    front. Three facets, a lit seam down the middle outside and a lit line inside.
    """
    r = ENGINE_R
    length = petal_length()
    width = 2 * r * math.sin(math.pi / 12) * 1.08
    for k in [-1, 0, 1]:
        a = k * math.pi / 6
        at = [r * math.sin(a), r * math.cos(a) - r, length / 2]
        p.hull.box([width, 0.5, length], M.panel, Placement(at, 0, 0, -a))
    p.neon.box([0.5, 0.3, length - 3], N, Placement([0, 0.45, length / 2]))
    p.neon.box([0.6, 0.2, length - 4], N, Placement([0, -0.25, length / 2]))
    p.bare.box([width * 3, 0.6, 1.2], M.dark, Placement([0, -0.3, length - 0.6]))


def draw_core(p: Any) -> None:
    """Draw an outer engine's core in its frame (+Z ahead): a drum, three barrels, lit muzzles."""
    p.hull.cylinder(2.6, CORE_LENGTH, 8, M.base, Placement([0, 0, 0], 0, QUARTER))
    p.neon.ring(2.7, 0.5, 8, N, Placement([0, 0, CORE_LENGTH - 1.5], 0, QUARTER))
    for k in range(3):
        a = k * 2 * math.pi / 3 + math.pi / 2
        x = math.cos(a) * 1.3
        y = math.sin(a) * 1.3
        p.hull.cylinder(0.7, BARREL_LENGTH, 6, M.panel, Placement([x, y, CORE_LENGTH], 0, QUARTER))
        p.neon.ring(
            0.8, 0.4, 6, N, Placement([x, y, CORE_LENGTH + BARREL_LENGTH - 0.4], 0, QUARTER)
        )


def nacelle_hinges() -> list[Vec3]:
    """Return the outer nacelles' petal hinges' centre, on their axes (model space): right, left."""
    y = OUTER_Y + PETAL_HINGE
    return [boss_point(ENGINE_X[2], y, ENGINE_H), boss_point(-ENGINE_X[2], y, ENGINE_H)]


def petal_joints(hinge: Vec3, k: int, peel: float) -> list[Joint]:
    """Return petal `k`'s joints on the nacelle hinged at `hinge`, peeled `peel` of the way."""
    roll = math.pi / 4 + k * QUARTER
    return [Joint(hinge, [0, 0, roll]), Joint([0, ENGINE_R, 0], [-PEEL * peel, 0, 0])]


def core_joints(hinge: Vec3, out: float) -> list[Joint]:
    """Return a core's joint, telescoped `out` of the way."""
    return [Joint(hinge, None, [1, 1, 1 + (REACH - 1) * out])]


# --- The flaps and the second wing tier. ---


class FlapFrame:
    """A flap's hinge (its leading edge's middle, model space), its turn about Y, its span (`span`).

    Its chord (local -Z is aft) and `out`, which way its local X points outboard (+1 or -1).
    """

    def __init__(self, side: float) -> None:
        x0 = FLAP_X[0]
        x1 = FLAP_X[1]
        a = boss_point(side * x0, trailing_edge(x0) - FLAP_CHORD, WING_TOP)
        b = boss_point(side * x1, trailing_edge(x1) - FLAP_CHORD, WING_TOP)
        dx = b[0] - a[0]
        dz = b[2] - a[2]
        self.out = 1
        if dx < 0:
            dx = -dx
            dz = -dz
            self.out = -1
        self.span = math.sqrt(dx * dx + dz * dz)
        self.yaw = math.atan2(-dz, dx)
        self.chord = FLAP_CHORD * dx / self.span
        self.mid = [(a[0] + b[0]) / 2, WING_TOP + 0.35, (a[2] + b[2]) / 2]

    def local(self, x: float, z: float) -> Vec3:
        """Return the point `(x, 0, z)` of its rest frame in the boss's frame."""
        c = math.cos(self.yaw)
        s = math.sin(self.yaw)
        return [self.mid[0] + x * c + z * s, self.mid[1], self.mid[2] - x * s + z * c]


FLAP_FRAMES = [FlapFrame(1), FlapFrame(-1)]


def flap_drawing(frame: FlapFrame) -> Any:
    """Return the drawing of a flap in its hinge's frame: a plate aft of its leading edge."""
    half = frame.span / 2
    chord = frame.chord

    def draw(p: Any) -> None:
        p.hull.box([frame.span, FLAP_THICK, chord], M.base, Placement([0, -FLAP_THICK, -chord / 2]))
        p.neon.box([frame.span - 2, 0.3, 0.5], N, Placement([0, 0, -chord + 0.6]))
        p.neon.box([frame.span - 2, 0.3, 0.5], N, Placement([0, 0, -0.6]))
        for k in range(5):
            x = -half + (k + 0.5) * frame.span / 5
            p.bare.box([0.5, 0.25, chord - 1.6], M.dark, Placement([x, 0, -chord / 2]))

    return draw


def panel_drawing(frame: FlapFrame) -> Any:
    """Return the drawing of a flap's outer panel in its hinge's frame (its outboard edge's).

    It reaches `TIER_REACH` outboard, a lit tip.
    """
    chord = frame.chord
    reach = frame.out * TIER_REACH

    def draw(p: Any) -> None:
        p.hull.box(
            [TIER_REACH, FLAP_THICK, chord],
            M.base,
            Placement([reach / 2, -FLAP_THICK, -chord / 2]),
        )
        p.neon.box([1, 0.35, chord - 1], N, Placement([reach - frame.out * 0.6, 0, -chord / 2]))
        p.neon.box([TIER_REACH - 2, 0.3, 0.5], N, Placement([reach / 2, 0, -chord + 0.6]))
        p.neon.box([TIER_REACH - 2, 0.3, 0.5], N, Placement([reach / 2, 0, -0.6]))

    return draw


def draw_strut(p: Any) -> None:
    """Draw a strut standing on the wing up to the tier: a lit collar halfway."""
    height = LIFT - FLAP_THICK
    p.hull.cylinder(STRUT_R, height, 6, M.base)
    p.neon.ring(STRUT_R + 0.15, 0.5, 6, N, Placement([0, height * 0.5, 0]))


def flap_joints(frame: FlapFrame, up: float, lift: float, down: float) -> list[Joint]:
    """Return a flap's joints: swung `up`, lifted `lift`, laid back `down` (shares)."""
    turn = QUARTER * (up - down)
    at = [frame.mid[0], frame.mid[1] + LIFT * lift, frame.mid[2]]
    return [Joint(at, [0, frame.yaw, 0]), Joint([0, 0, 0], [turn, 0, 0])]


def panel_joints(frame: FlapFrame, flap: list[Joint], out: float) -> list[Joint]:
    """Return a flap's outer panel's joints after `flap`'s, unfolded `out` of the way."""
    hinge = Joint([frame.out * frame.span / 2, 0, 0], [0, 0, math.pi * (1 - out)])
    return [flap[0], flap[1], hinge]


def strut_spots(frame: FlapFrame) -> list[Vec3]:
    """Return where a flap's struts stand on the wing (model space)."""
    return [
        frame.local(-frame.span / 4, -frame.chord / 2),
        frame.local(frame.span / 4, -frame.chord / 2),
    ]


def strut_joint(spot: Vec3, lift: float) -> list[Joint]:
    """Return a strut's joint, telescoped up `lift` of the way."""
    return [Joint(spot, None, [1, max(0.04, lift), 1])]


# --- The nose cone's halves. ---

HALF_SIDES = 7


def _half_section(side: float) -> list[list[float]]:
    """Return a nose half's section (`side` +1: model +X), counter-clockwise seen from the nose."""
    result: list[list[float]] = []
    for k in range(HALF_SIDES + 1):
        a = -QUARTER + math.pi * k / HALF_SIDES
        result.append([math.cos(a), (1 + math.sin(a)) / 2])
    if side < 0:
        return [[-q[0], q[1]] for q in reversed(result)]
    return result


def nose_pivot(side: float) -> Vec3:
    """Return a nose half's hinge (model space): its outer rear corner, `side` +1 model +X."""
    joint = next(s for s in FUSELAGE if s[0] == NOSE_JOINT)
    return [side * joint[1], 0, -NOSE_JOINT]


def nose_drawing(side: float) -> Any:
    """Return the drawing of a nose half in its hinge's frame: half the radome, its cut face lit."""
    pivot = nose_pivot(side)
    stations = [
        [-s[0] - pivot[2], s[1], s[2], s[3]] for s in reversed(FUSELAGE) if s[0] <= NOSE_JOINT
    ]
    section = _half_section(side)

    def draw(p: Any) -> None:
        p.hull.loft(section, stations, M.panel, Placement([-pivot[0], 0, 0]))
        p.neon.box([0.3, 0.8, 16], N, Placement([-pivot[0] + side * 0.1, 9.5, 8], 0, -0.12))
        p.neon.box([0.3, 0.6, 12], N, Placement([-pivot[0] + side * 0.1, 4, 7]))
        p.bare.box([0.5, 0.5, 6], M.dark, Placement([-pivot[0] + side * 4, 13.6, 4]))

    return draw


def nose_joints(side: float, open_: float, rail: float) -> list[Joint]:
    """Return a nose half's joint: swung open `open_`, then closed up apart as a rail `rail`."""
    pivot = nose_pivot(side)
    yaw = side * NOSE_SWING * (open_ - rail)
    at = [pivot[0] + side * RAIL_GAP * rail, 0, pivot[2] + RAIL_AHEAD * rail]
    return [Joint(at, [0, yaw, 0], [1, 1, 1 + (RAIL_STRETCH - 1) * rail])]


SIDES = [1, -1]


class ColossusRig:
    """The Stratoliner Colossus's petals, cores, flaps, panels, struts and nose halves."""

    def __init__(self, pieces: Any) -> None:
        self.petals = pieces["petals"]
        self.cores = pieces["cores"]
        self.flaps = pieces["flaps"]
        self.panels = pieces["panels"]
        self.struts = pieces["struts"]
        self.noses = pieces["noses"]

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose the rig for `boss` (None: at rest) and sync its models."""
        peel = stage(boss, 1, PEEL_SPAN)
        out = stage(boss, 1, CORE_OUT)
        loaded = boss == None or (boss.form < 1 and not after(boss, 1, CORE_GONE))
        hinges = nacelle_hinges()
        for i in range(2):
            for k in range(PETALS):
                piece = self.petals[i * PETALS + k]
                piece.pose(petal_joints(hinges[i], k, peel))
                piece.show(True, lit, dt)
            self.cores[i].pose(core_joints(hinges[i], out))
            self.cores[i].show(loaded, lit, dt)
        tier = after(boss, 2, 0.15)
        up = stage(boss, 2, FLAP_UP)
        lift = stage(boss, 2, FLAP_LIFT)
        down = stage(boss, 2, FLAP_DOWN)
        unfold = stage(boss, 2, FLAP_OUT)
        for i in range(2):
            frame = FLAP_FRAMES[i]
            joints = flap_joints(frame, up, lift, down)
            self.flaps[i].pose(joints)
            self.flaps[i].show(tier, lit, dt)
            self.panels[i].pose(panel_joints(frame, joints, unfold))
            self.panels[i].show(tier, lit, dt)
            spots = strut_spots(frame)
            for k in range(2):
                strut = self.struts[i * 2 + k]
                strut.pose(strut_joint(spots[k], lift))
                strut.show(tier, lit, dt)
        opening = stage(boss, 2, NOSE_OPEN)
        rail = stage(boss, 2, NOSE_RAIL)
        for i in range(2):
            self.noses[i].pose(nose_joints(SIDES[i], opening, rail))
            self.noses[i].show(tier, lit, dt)


def _pieces(root: Any, neon: Any, breath: Any) -> Any:
    name = "stratoliner-colossus-"
    petals = [
        build_piece(name + "petal-" + str(k), root, neon, draw_petal, breath, 2)
        for k in range(2 * PETALS)
    ]
    cores = [
        build_piece(name + "core-" + str(i), root, neon, draw_core, breath, 1) for i in range(2)
    ]
    flaps = [
        build_piece(name + "flap-" + str(i), root, neon, flap_drawing(FLAP_FRAMES[i]), breath, 2)
        for i in range(2)
    ]
    panels = [
        build_piece(name + "panel-" + str(i), root, neon, panel_drawing(FLAP_FRAMES[i]), breath, 3)
        for i in range(2)
    ]
    struts = [
        build_piece(name + "strut-" + str(k), root, neon, draw_strut, breath, 1) for k in range(4)
    ]
    noses = [
        build_piece(name + "nose-" + str(i), root, neon, nose_drawing(SIDES[i]), breath, 1)
        for i in range(2)
    ]
    return {
        "petals": petals,
        "cores": cores,
        "flaps": flaps,
        "panels": panels,
        "struts": struts,
        "noses": noses,
    }


def build_colossus_rig(root: Any, neon: Any, breath: Any) -> ColossusRig:
    """Return the Stratoliner Colossus's rig on `root` (the boss model's)."""
    return ColossusRig(_pieces(root, neon, breath))


def rig_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): at rest (`unfold` 0) or transformed (1).

    Transformed is after both transformations: petals peeled, the tier up, the rails out.
    """
    result: list[Any] = []
    k = 1 if unfold > 0 else 0
    petal = drawn(draw_petal)
    for hinge in nacelle_hinges():
        for j in range(PETALS):
            result.extend(posed(petal, petal_joints(hinge, j, k)))
        if k == 0:
            result.extend(posed(drawn(draw_core), core_joints(hinge, 0)))
    if k == 0:
        return result
    for frame in FLAP_FRAMES:
        joints = flap_joints(frame, 1, 1, 1)
        result.extend(posed(drawn(flap_drawing(frame)), joints))
        result.extend(posed(drawn(panel_drawing(frame)), panel_joints(frame, joints, 1)))
        for spot in strut_spots(frame):
            result.extend(posed(drawn(draw_strut), strut_joint(spot, 1)))
    for side in SIDES:
        result.extend(posed(drawn(nose_drawing(side)), nose_joints(side, 1, 1)))
    return result


def rest_flaps() -> list[Any]:
    """Return each flap's drawing and its joints at rest (for the flaps' armour region)."""
    return [[flap_drawing(f), flap_joints(f, 0, 0, 0)] for f in FLAP_FRAMES]


def rest_noses() -> list[Any]:
    """Return each nose half's drawing and its joints at rest (for the nose's armour region)."""
    return [[nose_drawing(s), nose_joints(s, 0, 0)] for s in SIDES]
