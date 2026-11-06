# Copyright (c) 2026 Renaud Guillon
"""ENM-35: the pieces the basic kinds share.

Grafted gun barrels, a pair of fluttering membrane wings, sinews and eyes. Logical pixels, nose +Z,
Y up.
"""

import math

from game.config.enemy_look import ENEMY_LOOK
from game.config.record import concat
from game.view.enemies.enemy_shapes import SIDES, decal
from game.view.enemies.organic_parts import opt
from render.geometry.organic import curve, tendril, vein
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[float]
type Rgb = list[float]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2


def gun_barrel(parts: Any, at: Vec3, length: float, yaw: float = 0) -> None:
    """Add a small gun barrel grafted on (ENM-36: metal), from `at` along `yaw` (0: to the nose).

    It is `length` long, with a charge light at its muzzle (phase 7 review), marked there.
    """

    def along(d: float) -> list[float]:
        return [at[0] + math.sin(yaw) * d, at[1], at[2] + math.cos(yaw) * d]

    parts.hull.cylinder(
        0.55, length, 5, H.dark, Placement([at[0], at[1], at[2]], yaw, QUARTER), 0.45
    )
    parts.charge.cylinder(0.6, 0.8, 5, WHITE, Placement(along(length), yaw, QUARTER))
    parts.muzzle(along(length + 0.8), "gun")


def config_barrels(
    parts: Any,
    muzzles: Any,
    length: float,
    radius: float = 0.55,
    swivel: bool = False,
    centre: Any = None,
    lit: bool = True,
    housing: bool = True,
) -> None:
    """Add a recoiling barrel at each of an enemy's config `muzzles`, in their order (WPN-03).

    Swivelling ones turn about `centre` (model space) when given, each about its root otherwise.
    Unlit ones have no charge light at their tips and no edge trim (see `model_barrel`). Without
    `housing`, a barrel sunk in the hull has no housing round its root (it would not show).
    """
    for i, m in enumerate(muzzles):
        angle = m[3] if len(m) > 3 else 0
        tip = [-m[0], m[2], -m[1]]
        model_barrel(
            parts, tip, math.radians(angle), length, i, radius, swivel, centre, lit, housing
        )


def recoil_barrel(
    parts: Any,
    tip: Vec3,
    angle_deg: float,
    length: float,
    index: int,
    radius: float = 0.55,
    swivel: bool = False,
    centre: Any = None,
) -> None:
    """Add barrel number `index` of the enemy's guns, which recoils when it fires (WPN-03).

    `tip` is its muzzle as the config gives it, reordered to model space (`[x, height, -y]`) and
    `angle_deg` the way it points (from the nose, positive to the right). The config's X is right
    of an enemy facing down the screen, which is the model's left (turning the model to face down
    turns its +X to the screen's left), so the barrel is drawn mirrored: the one the simulation
    fires from is the one that is drawn firing. A
    fixed housing holds a barrel `length` long that slides back along its axis, with a charge light
    at its tip (the muzzle marked there, ENM-21).
    """
    model_barrel(
        parts,
        [-tip[0], tip[1], tip[2]],
        math.radians(angle_deg),
        length,
        index,
        radius,
        swivel,
        centre,
    )


def model_barrel(
    parts: Any,
    muzzle_at: Vec3,
    yaw: float,
    length: float,
    index: int,
    radius: float = 0.55,
    swivel: bool = False,
    centre: Any = None,
    lit: bool = True,
    housing: bool = True,
    trim: bool = True,
    sides: int = 5,
) -> None:
    """Add barrel number `index`, which recoils, with its tip at `muzzle_at` (model space).

    It points `yaw` radians from the nose (the model's own, no mirroring). A `lit` barrel has a
    charge light at its tip and an edge trim; an unlit one has neither: no glow at all. Without
    `housing`, it has no housing round its root (sunk in the hull, it would not show). Without
    `trim`, the barrel and its housing have no edge trim (its charge light stays when `lit`). A big
    barrel may be rounder: `sides` facets.
    """
    metal_of = trim and lit
    sx, sz = math.sin(yaw), math.cos(yaw)
    tip = muzzle_at
    end = [tip[0] - sx * 0.8, tip[1], tip[2] - sz * 0.8]
    base = [end[0] - sx * length, end[1], end[2] - sz * length]
    # The housing the barrel slides out of, fixed on the body. A swivelling barrel has none: it
    # turns on its turret, and a fixed housing would be left pointing ahead.
    if housing and not swivel:
        (parts.hull if metal_of else parts.bare).cylinder(
            radius * 1.45,
            length * 0.45,
            sides + 1,
            H.dark,
            Placement([base[0], base[1], base[2]], yaw, QUARTER),
            0.45,
        )

    def draw(piece: Any) -> None:
        (piece.hull if metal_of else piece.bare).cylinder(
            radius,
            length,
            sides,
            H.dark,
            Placement([base[0], base[1], base[2]], yaw, QUARTER),
            radius * 0.82,
        )
        if lit:
            piece.neon.cylinder(radius * 1.1, 0.8, sides, WHITE, Placement(end, yaw, QUARTER))

    parts.slide(base, [-sx, -sz], length * ENEMY_LOOK.barrelRecoil, index, draw, swivel, centre)
    parts.muzzle(muzzle_at, "gun")


def mirror(outline: Any, s: float) -> list[list[float]]:
    """Return the outline mirrored by `s` across (x times `s`)."""
    return [[s * p[0], p[1]] for p in outline]


def wing_draw(
    r: list[float], ts: list[list[float]], y: float, strut: float, lights: Any, glow: Rgb, s: int
) -> Any:
    """Return what a membrane wing draws in its model space (factory: no loop closure)."""

    def draw(w: Any) -> None:
        w.flesh.slab(concat([r], ts), [y - 0.25, y + 0.25], F.membrane)
        for t in ts:
            path = curve([r[0], y, r[1]], [t[0], y, t[1]], [0, 0.6, 0], 2)
            tendril(w.flesh, path, [strut, 0], 3, F.bone)
        tip = ts[0] if len(ts) > 0 else r
        mid = [(r[0] + tip[0]) / 2, y + 0.5, (r[1] + tip[1]) / 2]
        for light in lights if lights != None else []:
            decal(w.neon, mirror(light, s), y + 0.3, glow)
        if lights == None:
            vein(w.vein, [[r[0], y + 0.5, r[1]], mid], 0.5, glow)

    return draw


def wing_pair(parts: Any, shape: Any, glow: Rgb) -> None:
    """GFX-ART-13, ENM-42: a pair of membrane wings, each fluttering from its root (unless fixed).

    A `membrane` skin spread from the root to its tips, a lean `bone` strut out to each tip, and
    either a steady neon light on it or a vein along its leading strut.
    """
    root = shape["root"]
    tips = shape["tips"]
    y = shape["y"]
    strut = shape["strut"]
    lights = opt(shape, "lights", None)
    # A `fixed` pair is drawn on the body: it does not flutter.
    fixed = opt(shape, "fixed", False)
    for s in SIDES:
        r = [s * root[0], root[1]]
        ts = mirror(tips, s)
        draw = wing_draw(r, ts, y, strut, lights, glow, s)
        if fixed:
            draw(parts)
            continue
        span = max([abs(p[0] - root[0]) for p in tips])
        parts.flap([r[0], y, r[1]], s, span, draw)


def sinew(parts: Any, start: Vec3, end: Vec3, bow: Vec3, radius: float) -> None:
    """Add a sinew from `start` to `end`, bowed by `bow`: three facets, thinning out."""
    tendril(parts.flesh, curve(start, end, bow, 2), [radius, radius * 0.5], 3, F.sinew)


def eye_pair(parts: Any, at: Vec3, gap: float, size: float, glow: Rgb) -> None:
    """Add a pair of small glowing eyes, `gap` apart across `at` (ENM-37: lit as veins).

    Each is 8 triangles.
    """
    bead = [[0, -size * 0.5], [size, 0], [0, size * 0.5]]
    for s in SIDES:
        parts.vein.lathe(bead, 4, glow, Placement([at[0] + s * gap, at[1], at[2]]))
