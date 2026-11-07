# Copyright (c) 2026 Renaud Guillon
"""FB-CATHEDRAL-ENGINE-03, FB-CATHEDRAL-ENGINE-05: the Cathedral Engine's parts and its armour.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera; a playfield point
`(x, y)` is model `(-x, -y)`. Its spires, its organ-pipe banks and its rose window (their gun
mounts are drawn by `build_boss_model`, BOSS-58), the roofs it sheds as it transforms and the hatch
over its lantern rotor.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.cathedral_engine import (
    AISLE,
    AISLE_ROOF_HEIGHTS,
    BELFRY_TOP,
    BELL_AT,
    CHOIR_AISLE,
    CHOIR_VESSEL,
    CONSOLE_TOP,
    HATCH_RADIUS,
    LANTERN_AT,
    NEEDLE_AT,
    ROSE_TOP,
    SPIRE_AT,
    VAULT_HEIGHTS,
    VESSEL,
    VESSEL_TOP,
)
from game.view.bosses.final_boss_shapes import strip
from game.view.bosses.mini_boss_greebles import seam
from game.view.bosses.mini_boss_shapes import offset, sign_of
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


V = BOSS_LOOK.neon["cathedral-engine"]
# Its stained glass: dark, smoked panes (BOSS-50 greys the violet out of its body shades).
GLASS = [0.06, 0.055, 0.075]
SLATE = [0.075, 0.075, 0.085]
# The tower tops the spires stand on, and the transept's deck the organ banks stand on.
TOWER_TOP = 12
TRANSEPT_DECK = 12
# The crossing tower's top, the rose window lies on.
CROSSING_TOP = 14


def prism(builder: Any, profile: list[Any], zs: list[Any], color: Any, yaw: float = 0) -> None:
    """Add a prism: the convex `profile` (`[x, y]` corners) extruded along Z, `zs[0]` to `zs[1]`.

    Turned by `yaw` about the vertical (pi / 2 lays it along X). Roofs and gables.
    """
    area = 0.0
    n = len(profile)
    for i in range(n):
        a = profile[i]
        b = profile[(i + 1) % n]
        area += a[0] * b[1] - b[0] * a[1]
    ring = profile if area > 0 else [profile[n - 1 - i] for i in range(n)]
    z0 = zs[0]
    z1 = zs[1]
    place = Placement([0, 0, 0], yaw)
    builder.face([[q[0], q[1], z1] for q in ring], color, place)
    builder.face([[ring[n - 1 - i][0], ring[n - 1 - i][1], z0] for i in range(n)], color, place)
    for i in range(n):
        a = ring[i]
        b = ring[(i + 1) % n]
        builder.face(
            [[a[0], a[1], z0], [b[0], b[1], z0], [b[0], b[1], z1], [a[0], a[1], z1]], color, place
        )


def model_zs(ys: list[Any]) -> list[Any]:
    """Return a playfield span `[y0, y1]` (Y up the screen) as a model span along Z, low to high."""
    return [-ys[1], -ys[0]]


def _shift(at: Vec3, config: list[Any], spot: list[Any], y: float) -> Vec3:
    """Return the model point of the playfield point `config`, from a part's model point `at`.

    `spot` is the part's own playfield point (`at`'s): it keeps the side of `at`'s X.
    """
    s = sign_of(-at[0]) if at[0] != 0 else 1
    return [at[0] - s * (abs(config[0]) - abs(spot[0])), y, at[2] - (config[1] - spot[1])]


def spire(p: Any, at: Vec3) -> None:
    """Add a spire (FB-CATHEDRAL-ENGINE-03): a belfry on its tower, a tall needle behind it.

    An octagonal belfry with violet louvres, a pinnacle on each corner, the bell gun's seat at its
    front (its mount, BOSS-58) and an octagonal needle rising behind, ringed with light.
    """
    p.hull.cylinder(
        8,
        BELFRY_TOP - TOWER_TOP,
        8,
        M.panel,
        Placement(offset(at, 0, TOWER_TOP, 0), math.pi / 8),
        7.4,
    )
    p.neon.ring(8.05, 0.5, 8, V, Placement(offset(at, 0, TOWER_TOP + 1.2, 0), math.pi / 8))
    bell = _shift(at, BELL_AT, SPIRE_AT, BELFRY_TOP - 0.1)
    p.hull.cylinder(4.2, 0.5, 8, M.dark, Placement(bell, math.pi / 8))
    needle = _shift(at, NEEDLE_AT, SPIRE_AT, BELFRY_TOP)
    p.hull.cylinder(4.4, 4, 8, M.base, Placement(needle, math.pi / 8), 3.8)
    p.hull.cylinder(3.8, 18, 8, SLATE, Placement(offset(needle, 0, 4, 0), math.pi / 8), 0.3)
    for k in range(3):
        h = 6 + k * 5
        r = 3.8 - (3.5 * (h - 4)) / 18
        p.neon.ring(r + 0.15, 0.5, 8, V, Placement(offset(needle, 0, h, 0), math.pi / 8))
    p.neon.box([0.9, 1.4, 0.9], V, Placement(offset(needle, 0, 22, 0)))
    for dx in [-5.6, 5.6]:
        for dz in [-5.6, 5.6]:
            corner = offset(at, dx, BELFRY_TOP - 0.5, dz)
            p.hull.cylinder(1.3, 6, 4, SLATE, Placement(corner, math.pi / 4), 0.1)
            p.neon.box([0.6, 0.6, 0.6], V, Placement(offset(corner, 0, 3, 0)))


def organ(p: Any, at: Vec3) -> None:
    """Add an organ-pipe bank (FB-CATHEDRAL-ENGINE-03): a console and its pipes on the transept.

    A dark console on the transept's deck, its rotor on top (its mount, BOSS-58), and a façade of
    pipes in a half ring round its outer side, the tallest in the middle, each with a violet mouth
    and a dark lip.
    """
    s = sign_of(at[0])
    p.hull.bevel_slab(
        [[-8, -9], [8, -9], [9, -6], [9, 6], [8, 9], [-8, 9], [-9, 6], [-9, -6]],
        [TRANSEPT_DECK - 0.4, CONSOLE_TOP - 1, CONSOLE_TOP],
        [0, 1],
        M.panel,
        Placement(at),
        M.base,
    )
    p.hull.cylinder(5.8, 0.5, 10, M.dark, Placement(offset(at, 0, CONSOLE_TOP - 0.1, 0)))
    p.neon.ring(6.2, 0.4, 10, V, Placement(offset(at, 0, CONSOLE_TOP - 0.7, 0)))
    pipes = 9
    for k in range(pipes):
        a = math.pi * (k + 0.5) / pipes
        middle = 1 - abs(k - (pipes - 1) / 2) / ((pipes - 1) / 2)
        tall = 5 + 9 * middle
        r = 1.15 + 0.35 * middle
        foot = offset(at, s * 10.5 * math.sin(a), CONSOLE_TOP - 1, 10.5 * math.cos(a))
        p.hull.cylinder(r, tall, 6, SLATE, Placement(foot))
        p.neon.ring(r + 0.1, 0.6, 6, V, Placement(offset(foot, 0, tall * 0.3, 0)))
        p.hull.cylinder(r + 0.15, 0.5, 6, M.dark, Placement(offset(foot, 0, tall - 0.5, 0)))
    # The wind chest under the pipes and the conduits feeding it from the console.
    p.hull.box([3, 2, 20], M.base, Placement(offset(at, s * 11, CONSOLE_TOP - 1.4, 0)))
    for dz in [-4, 4]:
        p.hull.cylinder(
            0.7,
            4,
            6,
            M.dark,
            Placement(offset(at, s * 7.5, CONSOLE_TOP - 1.2, dz), s * math.pi / 2, math.pi / 2),
        )


# The rose window's tracery: its rings' radii and its spokes.
ROSE_RINGS = [14, 9.5, 5.5]
ROSE_SPOKES = 12


def rose(p: Any, at: Vec3) -> None:
    """Add the rose window (FB-CATHEDRAL-ENGINE-03): a great round window over the crossing.

    A dark metal rim round smoked glass panes, violet tracery of rings and spokes, a petal of pale
    glass in each light that brightens as it charges, and the laser's hub at its centre (its mount,
    BOSS-58).
    """
    base = CROSSING_TOP - 0.4
    p.hull.cylinder(15, 1.6, 24, M.panel, Placement(offset(at, 0, base, 0)))
    p.hull.ring(15.05, 2.4, 24, M.base, Placement(offset(at, 0, base, 0)))
    p.flesh.cylinder(13.6, 0.4, 24, GLASS, Placement(offset(at, 0, base + 1.6, 0)))
    for r in ROSE_RINGS:
        p.neon.ring(r, 0.5, 24, V, Placement(offset(at, 0, base + 1.8, 0)))
    for k in range(ROSE_SPOKES):
        a = 2 * math.pi * k / ROSE_SPOKES
        mid = offset(at, 9.75 * math.sin(a), base + 1.9, 9.75 * math.cos(a))
        p.neon.box([0.5, 0.4, 8.5], V, Placement(mid, a))
        inner = offset(at, 7.5 * math.sin(a), base + 1.8, 7.5 * math.cos(a))
        p.neon.box([0.4, 0.4, 3.8], V, Placement(inner, a))
        b = a + math.pi / ROSE_SPOKES
        petal = offset(at, 11.8 * math.sin(b), base + 1.85, 11.8 * math.cos(b))
        p.charge.cylinder(1.4, 0.3, 6, [0.85, 0.8, 1], Placement(petal, b))
    p.hull.cylinder(
        5,
        ROSE_TOP - base - 1.6,
        8,
        M.base,
        Placement(offset(at, 0, base + 1.6, 0), math.pi / 8),
        4.2,
    )
    p.neon.ring(5.05, 0.5, 8, V, Placement(offset(at, 0, base + 2.6, 0), math.pi / 8))


def _lean_to(p: Any, xs: list[Any], ys: list[Any]) -> None:
    """Add a pair of lean-to roofs over the aisles between `xs` (inner, outer), along `ys`.

    Their slates from the high wall's foot down to the outer eaves, ribs across them, a violet line
    along their eaves.
    """
    low = AISLE_ROOF_HEIGHTS[0]
    high = AISLE_ROOF_HEIGHTS[1]
    zs = model_zs(ys)
    for s in SIDES:
        inner = s * xs[0]
        outer = s * xs[1]
        prism(p.hull, [[inner, low], [outer, low], [outer, low + 2.2], [inner, high]], zs, SLATE)
        z = zs[0] + 4
        while z < zs[1] - 2:
            rib = [(inner + outer) / 2, (low + 2.2 + high) / 2 + 0.1, z]
            p.hull.box(
                [abs(outer - inner) + 0.6, 0.6, 0.9],
                M.base,
                Placement(rib, 0, 0, -s * math.atan2(high - low - 2.2, abs(outer - inner))),
            )
            z += 6
        strip(
            p.neon,
            [outer - s * 0.4, zs[0] + 1],
            [outer - s * 0.4, zs[1] - 1],
            0.5,
            [low + 1.6, low + 2.4],
            V,
        )


def draw_aisles(p: Any) -> None:
    """Draw the nave's aisle roofs (FB-CATHEDRAL-ENGINE-05): shed at the first transformation."""
    _lean_to(p, [VESSEL, AISLE], [-56, -18])


def draw_choir_aisles(p: Any) -> None:
    """Draw the choir's aisle roofs (FB-CATHEDRAL-ENGINE-05): shed at the second transformation."""
    _lean_to(p, [CHOIR_VESSEL, CHOIR_AISLE], [18, 46])


def draw_vault(p: Any) -> None:
    """Draw the nave's high vault (FB-CATHEDRAL-ENGINE-05): a steep gabled roof over the nave.

    Its slates, ribs across it and a violet line along its ridge; shed at the second
    transformation.
    """
    low = VAULT_HEIGHTS[0]
    ridge = VAULT_HEIGHTS[1]
    zs = model_zs([-56, -18])
    w = VESSEL
    prism(p.hull, [[-w, low], [w, low], [w, low + 3], [0, ridge], [-w, low + 3]], zs, SLATE)
    strip(p.neon, [0, zs[0] + 1], [0, zs[1] - 1], 0.7, [ridge - 0.5, ridge + 0.2], V)
    z = zs[0] + 3
    while z < zs[1] - 2:
        for s in SIDES:
            seam(
                p.hull,
                [s * 0.6, z],
                [s * (w - 0.5), z],
                [low + 3 + (ridge - low - 3) * 0.5 - 0.3, 0.7, 0.4],
                M.base,
            )
        z += 5


def draw_hatch(p: Any) -> None:
    """Draw the hatch over the lantern rotor (BOSS-58): a domed octagonal cap, a seam of light."""
    at: Vec3 = [-LANTERN_AT[0], VESSEL_TOP, -LANTERN_AT[1]]
    r = HATCH_RADIUS
    p.hull.cylinder(r, 1.6, 8, M.panel, Placement(at, math.pi / 8), r - 0.8)
    p.hull.cylinder(r - 2.6, 1.2, 8, SLATE, Placement(offset(at, 0, 1.6, 0), math.pi / 8), 1)
    p.neon.ring(r - 0.3, 0.25, 8, V, Placement(offset(at, 0, 1.1, 0), math.pi / 8))


def draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at: Vec3 = [-LANTERN_AT[0], VESSEL_TOP, -LANTERN_AT[1]]
    p.hull.ring(HATCH_RADIUS - 0.4, 0.9, 16, M.base, Placement(at))
    p.neon.ring(HATCH_RADIUS - 0.4, 0.3, 16, V, Placement(offset(at, 0, 0.9, 0)))
