# Copyright (c) 2026 Renaud Guillon
"""MB-CONDOR-LIFTER-05, MB-CONDOR-LIFTER-10: the Condor Lifter's view rig.

Logical pixels, nose +Z, Y up. Its four propellers (spinning; an outer one winds down once its
engine gun is destroyed), its cargo ramp, and the morph of its containers into gun decks: as it
transforms the ramp drops open, the containers' roofs blow off (their armour region), their outer,
front and back walls hinge down flat into gun decks, their inner walls sink into the deck, and
their cargo (a row of five tubes in each) telescopes forward into barrels as the batteries rise
out of them (`boss_reveal`); the tubes are gone once the batteries' turrets are up. Looks only:
the sim knows nothing of them (no part, no muzzle).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.condor_lifter import (
    BATTERY_AT,
    CONTAINER_TOP,
    CONTAINER_X,
    CONTAINER_Y,
    DECK_TOP,
    NACELLE_H,
    NACELLE_X,
    PROP_R,
    PROP_Y,
    RAMP_H,
    RAMP_HALF,
    RAMP_LENGTH,
    RAMP_Y,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.lab.condor_lifter_joints import (
    Joint,
    after,
    build_piece,
    drawn,
    during,
    offset,
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


N = BOSS_LOOK.neon["condor-lifter"]
QUARTER = math.pi / 2
# The propellers' spin (radians a second), and how fast one winds down (radians a second, each
# second).
SPIN = 14
WIND_DOWN = 9
BLADES = 4
# Of the transformation: the ramp drops open, the walls fall, the inner walls sink, the cargo
# telescopes out (stretching `REACH` times), then it is gone.
RAMP_OPEN = [0.0, 0.35]
WALLS_FALL = [0.17, 0.42]
WALL_SINK = [0.2, 0.4]
CARGO_OUT = [0.36, 0.62]
CARGO_GONE = 0.82
BURST = BOSS_LOOK.reveal.burst
REACH = 2.4
# The ramp's open angle (past level, its lip resting low), and the front walls' (they lean on the
# wing's trailing edge).
RAMP_DROP = 1.75
FRONT_FALL = 1.36
WALL = 0.7
HIGH = CONTAINER_TOP - DECK_TOP
LONG = CONTAINER_Y[1] - CONTAINER_Y[0]
WIDE = CONTAINER_X[1] - CONTAINER_X[0]
# The cargo: five tubes at the battery's barrels' spacing, their back, length and radius.
TUBES = 5
TUBE_GAP = 1.8
TUBE_BACK = CONTAINER_Y[1] - 2
TUBE_LENGTH = 7
TUBE_R = 0.8


# --- The drawings, each in its own piece's frame. ---


def draw_blades(p: Any) -> None:
    """Draw a propeller's blades round its hub (spinning about local Z): lit tips."""
    for k in range(BLADES):
        a = k * 2 * math.pi / BLADES + math.pi / 4
        c = math.cos(a)
        s = math.sin(a)
        reach = PROP_R - 0.3
        p.hull.box(
            [reach, 0.45, 2.2],
            M.panel,
            Placement([c * reach / 2, s * reach / 2 - 0.22, 0], 0, 0, a),
        )
        p.neon.box(
            [1.4, 0.5, 2.3], N, Placement([c * (reach - 0.6), s * (reach - 0.6) - 0.25, 0], 0, 0, a)
        )


def draw_ramp(p: Any) -> None:
    """Draw the cargo ramp up from its hinge (local +Y), its outside aft (-Z).

    Lit treads on its inside (+Z), which faces up once it has dropped open.
    """
    p.hull.box([RAMP_HALF * 2, RAMP_LENGTH, 0.8], M.panel, Placement([0, 0, -0.9]))
    for k in range(4):
        p.neon.box([RAMP_HALF * 1.5, 0.5, 0.3], N, Placement([0, 2 + k * 3, -0.15]))
    for side in [-1, 1]:
        p.bare.box([0.6, RAMP_LENGTH, 1.2], M.dark, Placement([side * (RAMP_HALF - 0.3), 0, -1]))


def _corrugated(p: Any, o: Vec3, size: Vec3, along_z: bool, inner: float) -> None:
    """Draw a container wall standing on its hinge `o`: corrugated plate, a lit rim, markings.

    `size` its box; ribs on both faces, and on its inner face (`inner`: +1 or -1 along its thin
    axis) lit chevrons, the gun deck's markings once it lies flat.
    """
    p.hull.box(size, M.panel, Placement(o))
    long = size[2] if along_z else size[0]
    thin = size[0] if along_z else size[2]
    count = math.floor(long / 3.2)
    for k in range(count):
        u = -long / 2 + (k + 0.5) * long / count
        for face in [-1, 1]:
            d = face * (thin / 2 + 0.12)
            at = [d, 0.4, u] if along_z else [u, 0.4, d]
            rib = [0.25, size[1] - 0.8, 0.9] if along_z else [0.9, size[1] - 0.8, 0.25]
            p.bare.box(rib, M.base, Placement(offset(o, at[0], at[1], at[2])))
    lip = [thin + 0.3, 0.45, long - 0.6] if along_z else [long - 0.6, 0.45, thin + 0.3]
    p.neon.box(lip, N, Placement(offset(o, 0, size[1] - 0.45, 0)))
    d = inner * (thin / 2 + 0.3)
    for k in [-1, 1]:
        at = [d, size[1] * 0.55, k * long / 4] if along_z else [k * long / 4, size[1] * 0.55, d]
        mark = [0.2, 0.5, long / 4] if along_z else [long / 4, 0.5, 0.2]
        p.neon.box(mark, N, Placement(offset(o, at[0], at[1], at[2])))


def side_wall_at(p: Any, o: Vec3, inner: float) -> None:
    """Draw a container's outer wall (along Z) on its hinge `o` (`inner`: its inside, in X)."""
    _corrugated(p, o, [WALL, HIGH, LONG], True, inner)


def end_wall_at(p: Any, o: Vec3, inner: float) -> None:
    """Draw a container's front or back wall (along X) on its hinge `o` (`inner`: in Z)."""
    _corrugated(p, o, [WIDE, HIGH, WALL], False, inner)


def inner_wall_at(p: Any, o: Vec3) -> None:
    """Draw a container's inner wall (along Z) on its foot `o`: it sinks into the deck."""
    p.hull.box([WALL, HIGH, LONG - 0.8], M.base, Placement(o))
    p.neon.box([WALL + 0.2, 0.4, LONG - 2], N, Placement(offset(o, 0, HIGH - 0.4, 0)))


ORIGIN = [0, 0, 0]


def side_wall(inner: float) -> Any:
    """Return the drawing of a container's outer wall, in its hinge's frame."""

    def draw(p: Any) -> None:
        side_wall_at(p, ORIGIN, inner)

    return draw


def end_wall(inner: float) -> Any:
    """Return the drawing of a container's front or back wall, in its hinge's frame."""

    def draw(p: Any) -> None:
        end_wall_at(p, ORIGIN, inner)

    return draw


def draw_inner_wall(p: Any) -> None:
    """Draw a container's inner wall in its foot's frame."""
    inner_wall_at(p, ORIGIN)


def draw_container_walls(p: Any) -> None:
    """Draw both containers' walls standing (the armour region's, MB-CONDOR-LIFTER-10)."""
    for spot in wall_spots():
        spot.draw_at(p)
    for foot in inner_spots():
        inner_wall_at(p, foot)


def draw_cargo(p: Any) -> None:
    """Draw the cargo: five tubes in a cradle, along +Z from the frame's origin, lit muzzles."""
    p.bare.box([TUBES * TUBE_GAP + 1, 1, 2.5], M.dark, Placement([0, -0.4, 1.2]))
    for k in range(TUBES):
        x = (k - (TUBES - 1) / 2) * TUBE_GAP
        p.hull.cylinder(TUBE_R, TUBE_LENGTH, 6, M.panel, Placement([x, 0.9, 0], 0, QUARTER))
        p.neon.ring(TUBE_R + 0.1, 0.4, 6, N, Placement([x, 0.9, TUBE_LENGTH - 0.4], 0, QUARTER))


# --- Where the pieces are hung. ---


def prop_hubs() -> list[Vec3]:
    """Return the four propellers' hubs (model space).

    Right outer, right inner, left inner, left outer.
    """
    return [
        boss_point(NACELLE_X[1], PROP_Y, NACELLE_H),
        boss_point(NACELLE_X[0], PROP_Y, NACELLE_H),
        boss_point(-NACELLE_X[0], PROP_Y, NACELLE_H),
        boss_point(-NACELLE_X[1], PROP_Y, NACELLE_H),
    ]


# The engine gun each propeller's engine carries, if any (it winds down once that is destroyed).
PROP_ENGINES = ["engine-right", None, None, "engine-left"]


def ramp_joint(open_: float) -> list[Joint]:
    """Return the ramp's joint, `open_` of the way dropped open."""
    return [Joint(boss_point(0, RAMP_Y, RAMP_H), [-RAMP_DROP * open_, 0, 0])]


class WallSpot:
    """A container wall's hinge (model space), its fall's axis (0: X, 2: Z) and full turn."""

    def __init__(self, hinge: Vec3, axis: int, fall: float, inner: float) -> None:
        self.hinge = hinge
        self.axis = axis
        self.fall = fall
        self.inner = inner
        self.draw = side_wall(inner) if axis == 2 else end_wall(inner)

    def draw_at(self, p: Any) -> None:
        """Draw the wall standing on its hinge, in the boss's frame."""
        if self.axis == 2:
            side_wall_at(p, self.hinge, self.inner)
        else:
            end_wall_at(p, self.hinge, self.inner)

    def joints(self, down: float) -> list[Joint]:
        """Return its joint, fallen `down` of the way."""
        turn: list[float] = [0, 0, 0]
        turn[self.axis] = self.fall * down
        return [Joint(self.hinge, turn)]


def wall_spots() -> list[WallSpot]:
    """Return the falling walls of both containers: outer, front and back each."""
    result: list[WallSpot] = []
    mid_y = (CONTAINER_Y[0] + CONTAINER_Y[1]) / 2
    mid_x = (CONTAINER_X[0] + CONTAINER_X[1]) / 2
    for side in [1, -1]:
        # Model X is the playfield's -X: the right container's inside is at model +X of its outer
        # wall, and its outer wall falls towards model -X (a turn about Z by +, see `Joint`).
        outer = boss_point(side * CONTAINER_X[1], mid_y, DECK_TOP)
        result.append(WallSpot(outer, 2, side * QUARTER, side))
        front = boss_point(side * mid_x, CONTAINER_Y[0], DECK_TOP)
        result.append(WallSpot(front, 0, FRONT_FALL, -1))
        back = boss_point(side * mid_x, CONTAINER_Y[1], DECK_TOP)
        result.append(WallSpot(back, 0, -QUARTER, 1))
    return result


def inner_spots() -> list[Vec3]:
    """Return the containers' inner walls' feet (model space)."""
    mid_y = (CONTAINER_Y[0] + CONTAINER_Y[1]) / 2
    return [
        boss_point(CONTAINER_X[0], mid_y, DECK_TOP),
        boss_point(-CONTAINER_X[0], mid_y, DECK_TOP),
    ]


def cargo_spots() -> list[Vec3]:
    """Return where each container's cargo starts (model space): at the battery's X, at the back."""
    return [
        boss_point(BATTERY_AT[0], TUBE_BACK, DECK_TOP + 0.5),
        boss_point(-BATTERY_AT[0], TUBE_BACK, DECK_TOP + 0.5),
    ]


class CondorRig:
    """The Condor Lifter's propellers, ramp, container walls and cargo."""

    def __init__(
        self, props: list[Any], ramp: Any, walls: list[Any], inners: list[Any], cargo: list[Any]
    ) -> None:
        self.props = props
        self.ramp = ramp
        self.walls = walls
        self.inners = inners
        self.cargo = cargo
        self.turns = [0.0 for _ in props]
        self.spins = [float(SPIN) for _ in props]

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose the rig for `boss` (None: at rest) and sync its models."""
        self._spin(boss, lit, dt)
        self.ramp.pose(ramp_joint(stage(boss, 1, RAMP_OPEN)))
        self.ramp.show(True, lit, dt)
        open_ = after(boss, 1, BURST)
        down = stage(boss, 1, WALLS_FALL)
        spots = wall_spots()
        for k in range(len(self.walls)):
            self.walls[k].pose(spots[k].joints(down))
            self.walls[k].show(open_, lit, dt)
        sink = stage(boss, 1, WALL_SINK)
        feet = inner_spots()
        for k in range(len(self.inners)):
            foot = feet[k]
            self.inners[k].pose([Joint([foot[0], foot[1] - sink * (HIGH - 0.3), foot[2]])])
            self.inners[k].show(open_ and sink < 1, lit, dt)
        out = stage(boss, 1, CARGO_OUT)
        starts = cargo_spots()
        loaded = during(boss, 1, BURST, CARGO_GONE)
        for k in range(len(self.cargo)):
            self.cargo[k].pose([Joint(starts[k], None, [1, 1, 1 + (REACH - 1) * out])])
            self.cargo[k].show(loaded, lit, dt)

    def _spin(self, boss: Any, lit: Any, dt: float) -> None:
        hubs = prop_hubs()
        for k in range(len(self.props)):
            engine = PROP_ENGINES[k]
            stopped = engine != None and boss != None and _destroyed(boss, engine)
            if stopped:
                self.spins[k] = max(0, self.spins[k] - WIND_DOWN * dt)
            else:
                self.spins[k] = SPIN
            way = 1 if k < 2 else -1
            self.turns[k] = (self.turns[k] + way * self.spins[k] * dt) % (2 * math.pi)
            self.props[k].pose([Joint(hubs[k], [0, 0, self.turns[k]])])
            self.props[k].show(True, lit, dt)


def _destroyed(boss: Any, part_id: str) -> bool:
    """Whether the boss's part `part_id` is destroyed."""
    for part in boss.parts:
        if part.spec.id == part_id:
            destroyed: bool = part.destroyed
            return destroyed
    return False


def build_condor_rig(root: Any, neon: Any, breath: Any) -> CondorRig:
    """Return the Condor Lifter's rig on `root` (the boss model's)."""
    name = "condor-lifter-"
    props = [
        build_piece(name + "prop-" + str(k), root, neon, draw_blades, breath, 1) for k in range(4)
    ]
    ramp = build_piece(name + "ramp", root, neon, draw_ramp, breath, 1)
    spots = wall_spots()
    walls = [
        build_piece(name + "wall-" + str(k), root, neon, spots[k].draw, breath, 1)
        for k in range(len(spots))
    ]
    inners = [
        build_piece(name + "inner-" + str(k), root, neon, draw_inner_wall, breath, 1)
        for k in range(2)
    ]
    cargo = [
        build_piece(name + "cargo-" + str(k), root, neon, draw_cargo, breath, 1) for k in range(2)
    ]
    return CondorRig(props, ramp, walls, inners, cargo)


def rig_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): at rest (`unfold` 0) or transformed (1)."""
    result: list[Any] = []
    blades = drawn(draw_blades)
    for hub in prop_hubs():
        result.extend(posed(blades, [Joint(hub)]))
    result.extend(posed(drawn(draw_ramp), ramp_joint(unfold)))
    if unfold > 0:
        for spot in wall_spots():
            result.extend(posed(drawn(spot.draw), spot.joints(1)))
    return result
