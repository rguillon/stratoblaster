"""The homes of the residential districts (Phase 15, reviewer 2026-10-28: "gather the terraces
and suburbs into the same category, remove the green, make it more diverse, this is the future, no
need for tile roofs"), ported from `props/tile-residences.ts`: flat or metal roofed, on paved
plots. Each model takes the silhouette its seed names, so a group's models all differ: cantilevered
slabs, pods, a row of modules under solar panels, stepped terraces, a house on stilts and a wedge
under a sloping metal roof."""

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from game.view.props.tile_kit import (
    NEON,
    TileKit,
    any_of,
    js_remainder,
    js_round,
    plot,
    r,
    windows,
)
from render.geometry.solids import Placement

SHELLS = [C.white, C.silver, C.panel, C.concrete]
GLASS = [C.glassBlue, C.glassDark, C.glass]
DECKS = [C.concrete, C.concreteDark, C.metalDark]


def deck(k: TileKit) -> None:
    """The paved plot, a lit strip along the path to the door at the front."""
    plot(k, any_of(k, DECKS))
    k.lights.box(
        [0.3, 0.05, k.d * 0.3], any_of(k, NEON), Placement([k.w * 0.3, 0.2, -k.d * 0.3], 0, 0, 0)
    )


def cantilever(k: TileKit) -> None:
    """Two slabs, the upper one turned across the lower and overhanging it, lit underneath."""
    w = k.w * 0.7
    d = k.d * 0.55
    shell = any_of(k, SHELLS)
    k.s.box([w, 3.5, d], shell, Placement([-k.w * 0.1, 0, -k.d * 0.1], 0, 0, 0), C.metalDark)
    k.s.box([w * 0.75, 0.6, d * 1.4], any_of(k, GLASS), Placement([k.w * 0.05, 3.5, 0], 0, 0, 0))
    k.s.box([w * 0.8, 3, d * 1.5], shell, Placement([k.w * 0.08, 4.1, 0], 0, 0, 0), C.metalDark)
    k.lights.box(
        [w * 0.7, 0.15, 0.3], any_of(k, NEON), Placement([k.w * 0.08, 4, -d * 0.75], 0, 0, 0)
    )
    windows(k, [w * 0.8, d * 1.5], [4.6, 6.6], L.window, [k.w * 0.08, 0], 2.5)


def pods(k: TileKit) -> None:
    """One or two round pods under domes, a ring of light round each."""
    long = max(k.w, k.d) > min(k.w, k.d) * 1.5
    radius = min(k.w, k.d) * 0.38
    shell = any_of(k, SHELLS)
    light = any_of(k, NEON)
    if long:
        if k.w > k.d:
            spots = [[-k.w * 0.25, 0], [k.w * 0.25, 0]]
        else:
            spots = [[0, -k.d * 0.25], [0, k.d * 0.25]]
    else:
        spots = [[0, 0]]
    for i, spot in enumerate(spots):
        x = spot[0]
        z = spot[1]
        h = 3 + i * 1.5
        k.s.cylinder(radius, h, 12, shell, Placement([x, 0, z], 0, 0, 0))
        k.s.lathe(
            [
                [radius, h],
                [radius * 0.8, h + radius * 0.45],
                [0, h + radius * 0.65],
            ],
            12,
            any_of(k, GLASS),
            Placement([x, 0, z], 0, 0, 0),
        )
        k.lights.ring(radius + 0.1, 0.25, 12, light, Placement([x, h - 0.6, z], 0, 0, 0))


def modules(k: TileKit) -> None:
    """A row of modules of different heights along the long side, solar panels tilted on top."""
    along_z = k.d > k.w
    length = k.d if along_z else k.w
    depth = k.w if along_z else k.d
    n = max(2, js_round(length / 5))
    each = length / n
    for i in range(n):
        a = -length / 2 + each * (i + 0.5)
        h = r(k, [4, 7.5])
        x = 0 if along_z else a
        z = a if along_z else 0
        bw = depth * 0.7 if along_z else each - 0.6
        bd = each - 0.6 if along_z else depth * 0.7
        k.s.box([bw, h, bd], any_of(k, SHELLS), Placement([x, 0, z], 0, 0, 0), C.metalDark)
        tilt = (
            Placement([x, h + 0.5, z], 0, 0, 0.35)
            if along_z
            else Placement([x, h + 0.5, z], 0, -0.35, 0)
        )
        k.s.box([bw * 0.8, 0.12, bd * 0.8], C.solar, tilt)
        color = L.window if i % 2 == 0 else any_of(k, NEON)
        windows(k, [bw, bd], [1, h - 0.8], color, [x, z], 2.4)


def stepped(k: TileKit) -> None:
    """Terraces stepping back and up, a lit band along each step's edge."""
    steps = 3
    light = any_of(k, NEON)
    shell = any_of(k, SHELLS)
    for i in range(steps):
        w = k.w * (0.85 - i * 0.2)
        d = k.d * (0.8 - i * 0.18)
        z = i * k.d * 0.08
        k.s.box([w, 2.8, d], shell, Placement([0, i * 2.8, z], 0, 0, 0), C.concreteDark)
        k.lights.box(
            [w * 0.9, 0.15, 0.2], light, Placement([0, (i + 1) * 2.8, z - d / 2 - 0.1], 0, 0, 0)
        )
        k.s.box(
            [w * 0.9, 1.4, 0.2],
            any_of(k, GLASS),
            Placement([0, i * 2.8 + 0.8, z - d / 2 - 0.05], 0, 0, 0),
        )


def stilts(k: TileKit) -> None:
    """A glass-fronted box raised on thin legs, a car port under it."""
    w = k.w * 0.8
    d = k.d * 0.6
    lift = 3
    for sx, sz in [[-1, -1], [1, -1], [-1, 1], [1, 1]]:
        k.s.box(
            [0.35, lift, 0.35], C.metal, Placement([(sx * w) / 2.3, 0, (sz * d) / 2.3], 0, 0, 0)
        )
    k.s.box([w, 3.5, d], any_of(k, SHELLS), Placement([0, lift, 0], 0, 0, 0), C.metalDark)
    k.s.box(
        [w * 0.85, 2.4, 0.2], any_of(k, GLASS), Placement([0, lift + 0.5, -d / 2 - 0.05], 0, 0, 0)
    )
    k.lights.box(
        [w * 0.8, 0.12, 0.12], L.window, Placement([0, lift + 2.95, -d / 2 - 0.15], 0, 0, 0)
    )
    k.s.box(
        [2, 1.1, 3.6],
        any_of(k, [C.containerRed, C.containerBlue, C.silver]),
        Placement([w * 0.15, 0, 0], 0, 0, 0),
    )
    k.lights.box([w * 0.6, 0.1, d * 0.6], any_of(k, NEON), Placement([0, lift - 0.15, 0], 0, 0, 0))


def wedge(k: TileKit) -> None:
    """A wedge: a block under one metal roof sloping from the back down to the front, glazed end."""
    w = k.w * 0.8
    d = k.d * 0.7
    low = 3
    high = r(k, [6, 8])
    shell = any_of(k, SHELLS)
    k.s.box([w, low, d], shell)
    roof = C.metalDark
    x0 = -w / 2
    x1 = w / 2
    z0 = -d / 2
    z1 = d / 2
    k.s.face(
        [
            [x0, low, z0],
            [x0, high, z1],
            [x1, high, z1],
            [x1, low, z0],
        ],
        roof,
    )
    k.s.face(
        [
            [x0, low, z1],
            [x0, high, z1],
            [x0, low, z0],
        ],
        shell,
    )
    k.s.face(
        [
            [x1, low, z0],
            [x1, high, z1],
            [x1, low, z1],
        ],
        shell,
    )
    k.s.box([w, high - low, 0.2], any_of(k, GLASS), Placement([0, low, z1 - 0.1], 0, 0, 0))
    k.lights.box(
        [w * 0.9, 0.2, 0.2], any_of(k, NEON), Placement([0, low - 0.1, z0 - 0.15], 0, 0, 0)
    )
    windows(k, [w, d], [1, low - 0.5], L.window, [0, 0], 2.5)


SILHOUETTES = [cantilever, pods, modules, stepped, stilts, wedge]

# Number of silhouettes: seeds 1 to this give different homes.
RESIDENCE_COUNT = len(SILHOUETTES)


def build_residence(k: TileKit) -> None:
    """A home of the residential districts, of the silhouette its seed names, on a paved plot."""
    deck(k)
    index = js_remainder(k.seed - 1, len(SILHOUETTES))
    build = SILHOUETTES[index] if 0 <= index < len(SILHOUETTES) else cantilever
    build(k)
