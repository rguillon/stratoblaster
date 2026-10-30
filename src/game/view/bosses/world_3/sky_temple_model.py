"""P09-R09, 3-3: the Sky Temple. Ported from `view/bosses/world-3/sky-temple-model.ts`. Logical
pixels, nose +Z (its grand stair, down the screen), Y up (towards the camera)."""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_3.sky_temple import (
    OBELISKS,
    SKY_TEMPLE,
    TEMPLE_CRYSTAL,
    TEMPLE_GUNS,
    TEMPLE_PARTS,
)
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import barrels
from game.view.bosses.mini_boss_shapes import (
    WHITE,
    H,
    neon_band,
    socket,
)
from game.view.bosses.world_3.jungle_flesh import F, table
from game.view.bosses.world_3.sky_temple_details import temple_jungle, temple_machinery
from game.view.bosses.world_3.sky_temple_flesh import temple_body
from game.view.bosses.world_3.sky_temple_parts import (
    SQUARE,
    SUMMIT,
    TEMPLE_CYAN,
    TEMPLE_GOLD,
    TIERS,
    beacon,
    obelisk,
)
from game.view.bosses.world_3.stone_idol_stone import STONE, bar
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The rock it was torn from, under its base: an upside-down four-sided cone (lathe profile).
ROOTS = table([[0, -34], [57, -20], [99, -4], [104.6, 0]])
# The grand stair up its front face: steps from beyond the base to the summit.
STAIR = record({"steps": 9, "width": 20, "front": 88, "depth": 5.8, "bottom": -4})
# The sanctum on the summit (the core): its centre along Z, its size, its door's face.
SANCTUM = record({"z": -8, "size": [30, 10, 24], "door": 4})


def square(half: float) -> list[list[float]]:
    """A square outline `half` from the centre to each side."""
    return [[half, half], [-half, half], [-half, -half], [half, -half]]


def draw_pyramid(p: EnemyParts) -> None:
    """The stepped pyramid: its tiers, each trimmed with neon, and the rock under it."""
    hull = p.hull
    neon = p.neon
    # P16-R06: the lowest tier is the living beast itself; the stone tiers grew on its back.
    temple_body(p)
    for i in range(len(TIERS.halves)):
        half = TIERS.halves[i]
        y = i * TIERS.height
        if i > 0:
            hull.box(
                [half * 2, TIERS.height, half * 2],
                STONE.base,
                Placement([0, y, 0]),
                STONE.light,
            )
        trim = TEMPLE_CYAN if i == 0 else TEMPLE_GOLD
        neon_band(
            neon,
            square(half),
            [y + TIERS.height - 1.4, y + TIERS.height - 0.6],
            [1.006, 1.006],
            trim,
        )
    p.flesh.lathe(ROOTS, 4, F.sinew, Placement(None, SQUARE), False)


def draw_stair(p: EnemyParts) -> None:
    """The grand stair, its walls and its cyan balustrades."""
    hull = p.hull
    neon = p.neon
    steps = STAIR.steps
    width = STAIR.width
    front = STAIR.front
    depth = STAIR.depth
    bottom = STAIR.bottom
    rise = (SUMMIT - bottom) / steps
    for i in range(steps):
        top = STONE.light if i == steps - 1 else STONE.base
        at: Vec3 = [0, bottom, front - depth * (i + 0.5)]
        hull.box([width, rise * (i + 1), depth], STONE.dark, Placement(at), top)
    low = front
    high = front - depth * steps
    for s in SIDES:
        x = s * (width / 2 + 1.2)
        bar(hull, [x, rise + bottom + 1, low], [x, SUMMIT + 2, high], [2.4, 3], STONE.base)
        bar(
            neon,
            [x, rise + bottom + 2.6, low],
            [x, SUMMIT + 3.6, high],
            [0.7, 0.6],
            TEMPLE_CYAN,
        )


def draw_sanctum(p: EnemyParts) -> None:
    """The sanctum (the core): its roofs, its crystal (rings, spirals), its door and twin
    cannons."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    w = SANCTUM.size[0]
    h = SANCTUM.size[1]
    d = SANCTUM.size[2]
    hull.box([w, h, d], STONE.base, Placement([0, SUMMIT, SANCTUM.z]), STONE.light)
    hull.box(
        [w - 6, 3, d - 6],
        STONE.base,
        Placement([0, SUMMIT + h, SANCTUM.z]),
        STONE.light,
    )
    hull.box([w - 14, 3, d - 12], STONE.gilt, Placement([0, SUMMIT + h + 3, SANCTUM.z]))
    neon_band(
        neon,
        square(w / 2),
        [SUMMIT + h - 1.4, SUMMIT + h - 0.6],
        [1, 1],
        TEMPLE_GOLD,
        Placement([0, 0, SANCTUM.z]),
    )
    roof = SUMMIT + h + 6
    for m in TEMPLE_CRYSTAL:
        crystal = boss_point(m[0], m[1], m[2])
        x = crystal[0]
        y = crystal[1]
        z = crystal[2]
        hull.cylinder(3.6, 2, 6, STONE.dark, Placement([x, roof, z]), 3)
        gem = [[2.4, roof + 2], [3.6, roof + 6], [0, y]]
        charge.lathe(gem, 6, WHITE, Placement([x, 0, z]))
        neon.ring(3.8, 0.6, 6, TEMPLE_CYAN, Placement([x, roof + 5.6, z]))
        muzzle(crystal, "ring")
    # The door, framed in cyan, between two pillars.
    door = SANCTUM.door
    hull.box([10, 8, 0.6], STONE.deep, Placement([0, SUMMIT, door + 0.1]))
    neon.box([12, 0.7, 0.5], TEMPLE_CYAN, Placement([0, SUMMIT + 8, door + 0.3]))
    for s in SIDES:
        neon.box([0.7, 8, 0.5], TEMPLE_CYAN, Placement([s * 5.6, SUMMIT, door + 0.3]))
        hull.box([3, h, 3], STONE.light, Placement([s * 13, SUMMIT, door + 1]))
    draw_cannons(p)


def draw_cannons(p: EnemyParts) -> None:
    """The twin cannons either side of the door (aimed shots, spreads, bursts, fans)."""
    guns = [boss_point(m[0], m[1], m[2]) for m in TEMPLE_GUNS]
    if len(guns) == 0:
        return
    gun = guns[0]
    x = gun[0]
    y = gun[1]
    z = gun[2]
    radius = 1.4
    # The charge light at a barrel's tip is `1.4 radius` long (see `barrels`).
    length = z - SANCTUM.door - radius * 1.4
    for s in SIDES:
        p.hull.box(
            [5, 5, 6],
            H.panel,
            Placement([s * x, y - 2.5, SANCTUM.door]),
            H.base,
        )
        p.neon.box([5.2, 0.5, 0.5], TEMPLE_GOLD, Placement([s * x, y + 1.6, SANCTUM.door + 3.1]))
    barrels(p, [0, y, SANCTUM.door], [2, abs(x) * 2], [radius, length])


def draw_braziers(p: EnemyParts) -> None:
    """Braziers on the summit's corners, flaring as the next attack charges."""
    hull = p.hull
    charge = p.charge
    at = TIERS.halves[len(TIERS.halves) - 1] or 34
    for x in SIDES:
        for z in SIDES:
            spot: Vec3 = [x * (at - 4), SUMMIT, z * (at - 4)]
            hull.cylinder(2.6, 2.4, 6, STONE.dark, Placement(spot), 3)
            charge.cylinder(2, 3, 6, WHITE, Placement([spot[0], SUMMIT + 2.4, spot[2]]), 0.3)


def sky_temple_core(p: EnemyParts) -> None:
    """The core of the Sky Temple: its pyramid, stair, sanctum, braziers and machinery."""
    draw_pyramid(p)
    draw_stair(p)
    draw_sanctum(p)
    draw_braziers(p)
    temple_machinery(p)
    temple_jungle(p)
    for key in OBELISKS.keys():  # noqa: SIM118 (Transcrypt: iterate keys() explicitly)
        xy = OBELISKS[key]
        socket(p.hull, boss_point(xy[0], xy[1], TIERS.height), 7, 0.6)
    beacon_at = TEMPLE_PARTS.beacon
    socket(p.hull, boss_point(beacon_at[0], beacon_at[1], SUMMIT), 7, 0.6)


def build_sky_temple(scene: Any) -> Any:
    """P09-R09: the Sky Temple, a flying stepped pyramid with four corner obelisks, gold and cyan
    neon: a sanctum on its summit, a beacon before it, a grand stair, the jungle's moss and vines
    over its stones, and the dark metal of a fortress under them (thrusters, buttresses)."""
    parts: dict[str, Any] = {}
    for key in OBELISKS.keys():  # noqa: SIM118 (Transcrypt: iterate keys() explicitly)
        parts[key] = obelisk
    parts["beacon"] = beacon
    return build_boss_model(
        SKY_TEMPLE,
        scene,
        TEMPLE_GOLD,
        {"core": sky_temple_core, "parts": parts},
    )
