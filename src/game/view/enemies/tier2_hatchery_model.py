# Copyright (c) 2026 Renaud Guillon
"""ENM-HATCHERY-01: the Hatchery, Cyber-Organic (ENM-35), a tier 2 kind.

A big flight deck: a wide metal deck over two swollen flesh hulls, an armoured bow and stern, and
three launch bays sunk in the deck, each closed by two sliding doors over a Wasp waiting on its
lift. Everything lies below the playfield's plane, where the Wasps fly, so a Wasp taking off flies
over the ship. Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.enemy_hatchery import HATCHERY_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import LOBE_SECTION, SIDES
from game.view.enemies.veteran_small_models import docked_wasp
from render.geometry.organic import SegmentedBody, segmented_body
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2

# ENM-HATCHERY-01: the deck's top (just under the Wasps' plane, Y = 0), its bottom, how far out it
# reaches and how far along (Z).
DECK_TOP = -1
DECK_BOTTOM = -3
DECK_HALF = 18
DECK_LENGTH = 31
# A side hull under the deck's edge, and the armour plates along it (`[z, half width, half
# length]`), out past the deck.
HULL_X = 20
HATCHERY_HULL = SegmentedBody(-36, 34, 3, 8, -12, -2.2)
PLATE_X = 23
HATCHERY_PLATES = [[-20, 3.6, 6], [20, 3.6, 6]]  # type: list[list[float]]
# A side gun turret, between the plates: its fixed pedestal and its turning dome (lathe profiles),
# its barrel's length and radius. Its pivot and barrel tip are the config's (`turrets`).
TURRET_BASE = [[4.4, -3.2], [4.4, -1.4], [3.8, -0.9], [0, -0.9]]  # type: list[list[float]]
TURRET_DOME = [[3.6, -0.9], [3.4, 0.5], [2.4, 1.5], [0, 1.8]]  # type: list[list[float]]
TURRET_BARREL = [5.6, 0.7]  # type: list[float]
PLATE_HEIGHTS = [-3.4, -2.4, -1.2]  # type: list[float]
# The bow and the stern (right halves mirrored), and their heights.
HATCHERY_BOW = [[-DECK_HALF, 31], [DECK_HALF, 31], [12, 39], [-12, 39]]  # type: list[list[float]]
HATCHERY_STERN = [[-DECK_HALF, -31], [DECK_HALF, -31], [12, -38], [-12, -38]]  # type: list[list[float]]
END_HEIGHTS = [-4, -2.5, -1.1]  # type: list[float]
# ENM-HATCHERY-02: a bay's half size (a square well), its floor, and its doors (their thickness,
# and how far they sink as they slide open under the deck, per unit they slide).
BAY = 8.5
BAY_FLOOR = -5.4
DOOR = [-1.45, -1.05]  # type: list[float]
DOOR_SINK = 0.12
# Where a Wasp waits on its lift at the bottom of the well (its centre's height), raised to Y = 0
# for its take-off.
LIFT_LOW = -4.4


def rect(x0: float, x1: float, z0: float, z1: float) -> list[list[float]]:
    """Return a rectangle outline (`[x, z]`) between `x0`, `x1` and `z0`, `z1`."""
    return [[x0, z0], [x1, z0], [x1, z1], [x0, z1]]


def deck_pieces(bays: list[float]) -> list[list[list[float]]]:
    """Return the deck cut round the bays at `bays` (Z): its side strips and the strips between."""
    pieces = [rect(BAY, DECK_HALF, -DECK_LENGTH, DECK_LENGTH)]
    pieces.append(rect(-DECK_HALF, -BAY, -DECK_LENGTH, DECK_LENGTH))
    z: float = -DECK_LENGTH
    for c in sorted(bays):
        if c - BAY > z:
            pieces.append(rect(-BAY, BAY, z, c - BAY))
        z = c + BAY
    if z < DECK_LENGTH:
        pieces.append(rect(-BAY, BAY, z, DECK_LENGTH))
    return pieces


def well(p: Any, c: float) -> None:
    """Add a bay's well at `c` (Z) under the deck: its dark walls and floor, lit edges on the deck.

    The edges glow as the next launch nears (ENM-HATCHERY-03).
    """
    walls = [
        rect(-BAY - 0.3, -BAY, c - BAY, c + BAY),
        rect(BAY, BAY + 0.3, c - BAY, c + BAY),
        rect(-BAY, BAY, c - BAY - 0.3, c - BAY),
        rect(-BAY, BAY, c + BAY, c + BAY + 0.3),
    ]
    for wall in walls:
        p.hull.slab(wall, [BAY_FLOOR, DECK_TOP - 0.02], H.dark)
    p.hull.slab(rect(-BAY, BAY, c - BAY, c + BAY), [BAY_FLOOR - 0.3, BAY_FLOOR], H.dark)
    for s in SIDES:
        x0 = s * (BAY + 0.4)
        x1 = s * (BAY + 1)
        p.charge.slab(rect(min(x0, x1), max(x0, x1), c - BAY, c + BAY), [DECK_TOP, -0.95], WHITE)


def door_draw(s: float, c: float) -> Any:
    """Return what the half door on side `s` of the bay at `c` draws (factory: no loop closure)."""

    def draw(piece: Any) -> None:
        x0 = min(0, s * BAY)
        x1 = max(0, s * BAY)
        piece.hull.slab(rect(x0, x1, c - BAY, c + BAY), DOOR, H.panel, None, H.base)
        # A lime stripe along the edge where the two halves meet.
        sx0 = min(s * 0.3, s * 1)
        sx1 = max(s * 0.3, s * 1)
        piece.neon.slab(
            rect(sx0, sx1, c - BAY + 1, c + BAY - 1), [DOOR[1], DOOR[1] + 0.05], N.hatchery
        )

    return draw


def wasp_draw(c: float) -> Any:
    """Return what the Wasp waiting on the lift of the bay at `c` draws (factory)."""

    def draw(piece: Any) -> None:
        docked_wasp(piece, [0, LIFT_LOW, c])

    return draw


def bay(p: Any, c: float, k: int, bays: int) -> None:
    """ENM-HATCHERY-02: a launch bay sunk in the deck at `c` (Z): number `k` of `bays`.

    Its well, its two doors (`Enemy.tracks[k]`: how open, sliding apart under the deck) and the
    Wasp on its lift (`Enemy.tracks[bays + k]`: how far risen to the deck, hidden while empty).
    """
    well(p, c)
    for s in SIDES:
        pivot = [s * BAY / 2, (DOOR[0] + DOOR[1]) / 2, c]
        p.slide(pivot, [s, 0], BAY + 0.1, k, door_draw(s, c), False, None, "track", -DOOR_SINK)
    lift = [0, LIFT_LOW, c]
    p.slide(lift, [0, 0], -LIFT_LOW, bays + k, wasp_draw(c), False, None, "track", 1)


def scaled(profile: list[list[float]], size: list[float]) -> list[list[float]]:
    """Return a lathe profile scaled by `size[0]`, then lifted by `size[1]`."""
    return [[q[0] * size[0], q[1] * size[0] + size[1]] for q in profile]


def dome_draw(centre: list[float], height: float, size: list[float]) -> Any:
    """Return what a turret's turning dome at `centre` draws (factory): its gun's housing too.

    Its gun at `height`; `size` is its scale and lift (see `turret`).
    """
    k = size[0]

    def draw(piece: Any) -> None:
        piece.hull.lathe(scaled(TURRET_DOME, size), 8, H.panel, Placement(centre))
        housing = Placement([centre[0], height, centre[2] + 2.4 * k], 0, QUARTER)
        piece.hull.cylinder(1.1 * k, 2.2 * k, 6, H.dark, housing, 0.5 * k)

    return draw


def barrel_draw(base: list[float], end: list[float], k: float) -> Any:
    """Return what a turret's barrel from `base` to its charge light at `end` draws (factory).

    `k` times as big as the Hatchery's.
    """
    length = TURRET_BARREL[0] * k
    radius = TURRET_BARREL[1] * k

    def draw(piece: Any) -> None:
        place = Placement(base, 0, QUARTER)
        piece.hull.cylinder(radius, length, 6, H.dark, place, radius * 0.82)
        piece.neon.cylinder(radius * 1.1, 0.8 * k, 5, WHITE, Placement(end, 0, QUARTER))

    return draw


def turret(
    p: Any, k: int, guns: Any, size: list[float] | None = None, pedestal: bool = True
) -> None:
    """Add gun turret number `k` of `guns` (a carrier's `turrets` config).

    A fixed pedestal, a dome and a barrel turning with it. The dome and the barrel turn with the
    enemy's `turrets[k]`; the barrel recoils with its `barrels[k]` (WPN-02, WPN-03). `size` is how
    many times as big as the Hatchery's it is and how high it stands (`[scale, lift]`; `[1, 0]`
    when None); the config's barrel height and length must match it. Without `pedestal`, its dome
    stands on the hull with no pedestal under it (one sunk in the hull would not show).
    """
    if size is None:
        size = [1, 0]
    scale = size[0]
    pivot = guns.pivots[k]
    # The config's X is right of the screen, the model's +X its left; its Y up, the model's Z down.
    centre = [-pivot[0], 0, -pivot[1]]
    if pedestal:
        p.hull.lathe(scaled(TURRET_BASE, size), 8, H.base, Placement(centre))
    dome = dome_draw(centre, guns.height, size)
    p.slide(centre, [0, -1], 0, k, dome, True, centre, "barrel", 0, k)
    tip = [centre[0], guns.height, centre[2] + guns.barrel]
    end = [tip[0], tip[1], tip[2] - 0.8 * scale]
    length = TURRET_BARREL[0] * scale
    base = [end[0], end[1], end[2] - length]
    recoil = length * ENEMY_LOOK.barrelRecoil
    barrel = barrel_draw(base, end, scale)
    p.slide(base, [0, -1], recoil, k, barrel, True, centre, "barrel", 0, k)
    p.muzzle(tip, "gun")


def build_hatchery(scene: Any) -> Any:
    """ENM-HATCHERY-01: a flight deck, the carrier of tier 2.

    A wide metal deck over two swollen flesh hulls under metal armour plates with lime neon bands,
    an armoured bow and stern; three launch bays sunk in the deck in a row, each closed by two
    sliding doors over a Wasp on its lift, their edges glowing as the next launch nears
    (ENM-HATCHERY-02, ENM-HATCHERY-03); a gun turret on each hull, turning to the player; a reactor
    at the tail of each hull (ENM-HATCHERY-04); lime neon (ENM-HATCHERY-04). It all lies under the
    Wasps' plane: they take off over it.
    """
    # The bays, from the config's (X right of the screen, Y up it): the model's Z is down the
    # screen (the bays sit on the centre line).
    bays = [-entry[1] for entry in HATCHERY_CONFIG.bays]

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        for s in SIDES:
            segmented_body(
                flesh, HATCHERY_HULL, F.graphite, Placement([s * HULL_X, 0, 0]), LOBE_SECTION
            )
            for plate in HATCHERY_PLATES:
                z = plate[0]
                w = plate[1]
                half = plate[2]
                x = s * PLATE_X
                outline = [
                    [x - w * 0.7, z - half],
                    [x + w * 0.7, z - half],
                    [x + w, z],
                    [x + w * 0.7, z + half],
                    [x - w * 0.7, z + half],
                    [x - w, z],
                ]
                hull.bevel_slab(outline, PLATE_HEIGHTS, [0.3, 0.8], H.base, None, H.panel)
                band = Placement([x, PLATE_HEIGHTS[2] - 0.15, z])
                neon.box([0.6, 0.2, half * 1.4], N.hatchery, band)
            p.reactor([s * HULL_X, -6, -36.5], 2.6)
        for piece in deck_pieces(bays):
            hull.bevel_slab(
                piece, [DECK_BOTTOM, DECK_TOP - 0.4, DECK_TOP], [0.2, 0.1], H.base, None, H.panel
            )
        for end in [HATCHERY_BOW, HATCHERY_STERN]:
            hull.bevel_slab(end, END_HEIGHTS, [0.4, 1.2], H.base, None, H.panel)
        for k in range(len(bays)):
            bay(p, bays[k], k, len(bays))
        for k in range(len(HATCHERY_CONFIG.turrets.pivots)):
            turret(p, k, HATCHERY_CONFIG.turrets)

    return build_enemy_model("hatchery", scene, N.hatchery, draw)
