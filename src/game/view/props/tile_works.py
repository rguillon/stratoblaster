"""The works made for the grid of tiles (Phase 15, P15-R09): outposts, mines, oil, refineries,
factories, warehouses, docks and the foundries of heavy industry See `tile_kit.py`."""

import math

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from game.view.props.tile_kit import (
    TileKit,
    any_of,
    front_lights,
    gable,
    js_round,
    lamp,
    plot,
    r,
    windows,
)
from render.geometry.solids import Placement

SHEDS = [C.corrugated, C.metal, C.concrete, C.rust]
CONTAINERS = [C.containerBlue, C.containerGreen, C.containerRed, C.rust]


def cylinders(k: TileKit, radius: float, height: list[float], color: list[float]) -> None:
    """Rows of cylinders (tanks, silos) over the plot, `per` tiles apart."""
    nx = max(1, math.floor(k.w / (2 * radius + 1.5)))
    nz = max(1, math.floor(k.d / (2 * radius + 1.5)))
    for i in range(nx):
        for j in range(nz):
            x = -k.w / 2 + (k.w / nx) * (i + 0.5)
            z = -k.d / 2 + (k.d / nz) * (j + 0.5)
            h = r(k, height)
            k.s.cylinder(radius, h, 10, color, Placement([x, 0, z], 0, 0, 0))
            k.s.cylinder(radius, 0.8, 10, C.metalDark, Placement([x, h, z], 0, 0, 0), radius * 0.6)
            k.lights.ring(radius + 0.05, 0.25, 10, L.red, Placement([x, h * 0.7, z], 0, 0, 0))


def chimney(k: TileKit, x: float, z: float, h: float, radius: float = 0.9) -> None:
    """A chimney `h` high at (x, z), a glowing ring near its top."""
    k.s.cylinder(radius, h, 8, C.concreteDark, Placement([x, 0, z], 0, 0, 0), radius * 0.75)
    k.lights.ring(radius * 0.8, 0.5, 8, L.red, Placement([x, h - 1.2, z], 0, 0, 0))


def build_water_tower(k: TileKit) -> None:
    """A water tower on four legs, a cyan ring of light under the tank."""
    plot(k, C.sand)
    for x, z in [[-2, -2], [2, -2], [-2, 2], [2, 2]]:
        k.s.box([0.4, 8, 0.4], C.metalDark, Placement([x, 0, z], 0, 0, 0))
    k.s.cylinder(3, 3.5, 10, C.silver, Placement([0, 8, 0], 0, 0, 0), 2.6)
    k.lights.ring(3.05, 0.3, 10, L.cyan, Placement([0, 9.5, 0], 0, 0, 0))


def build_solar(k: TileKit) -> None:
    """A solar farm: rows of tilted panels on sand."""
    plot(k, C.sand)
    rows = max(2, js_round(k.d / 3))
    for i in range(rows):
        k.s.box(
            [k.w - 1, 0.3, 1.6],
            C.solar,
            Placement([0, 0.8, -k.d / 2 + (k.d / rows) * (i + 0.5)], 0, 0.3, 0),
        )
    lamp(k, k.w / 2 - 0.5, -k.d / 2 + 0.5)


def build_radio(k: TileKit) -> None:
    """A radio station: a low hut and a tall mast with a red light."""
    plot(k, C.sand)
    k.s.box([4, 3, 3], C.concrete, Placement([-1.5, 0, -2], 0, 0, 0), C.roof)
    k.s.cylinder(0.4, 14, 4, C.metal, Placement([2, 0, 1.5], 0, 0, 0), 0.1)
    k.lights.box([0.5, 0.5, 0.5], L.red, Placement([2, 14, 1.5], 0, 0, 0))
    k.lights.box([2.5, 0.4, 0.2], L.window, Placement([-1.5, 1.2, -3.6], 0, 0, 0))


def build_depot(k: TileKit) -> None:
    """A depot: a shed and two silos on sand."""
    plot(k, C.sand)
    k.s.box(
        [k.w * 0.6, 5, k.d * 0.5],
        any_of(k, SHEDS),
        Placement([-k.w * 0.15, 0, -k.d * 0.15], 0, 0, 0),
    )
    gable(k, [k.w * 0.6, k.d * 0.5], 5, 1.5, C.roof, [-k.w * 0.15, -k.d * 0.15])
    cylinders_at(k, [k.w * 0.3, k.d * 0.25], 1.6, 4)
    front_lights(k, k.w * 0.6, -k.d * 0.4, 4.5, L.yellowDim)


def cylinders_at(k: TileKit, at: list[float], radius: float, h: float) -> None:
    """A single silo of `radius` and height `h` at (x, z)."""
    k.s.cylinder(radius, h, 8, C.silver, Placement([at[0], 0, at[1]], 0, 0, 0))


def build_headframe(k: TileKit) -> None:
    """A mine headframe: four legs and a sheave wheel over a shed."""
    plot(k, C.ore)
    h = r(k, [14, 20])
    for x, z in [[-2, -2], [2, -2], [-2, 2], [2, 2]]:
        k.s.box([0.6, h, 0.6], C.mineYellow, Placement([x * 0.8, 0, z * 0.8 - k.d * 0.15], 0, 0, 0))
    k.s.cylinder(2, 0.8, 10, C.metalDark, Placement([0, h, -k.d * 0.15], 0, math.pi / 2, 0))
    k.s.box(
        [k.w * 0.5, 6, k.d * 0.3], any_of(k, SHEDS), Placement([0, 0, k.d * 0.3], 0, 0, 0), C.roof
    )
    k.lights.box([0.5, 0.5, 0.5], L.red, Placement([0, h + 1.5, -k.d * 0.15], 0, 0, 0))
    windows(k, [k.w * 0.5, k.d * 0.3], [1, 5], L.windowDim, [0, k.d * 0.3])


def build_ore_silos(k: TileKit) -> None:
    """Rows of ore silos."""
    plot(k, C.ore)
    cylinders(k, min(k.w, k.d) / 2 - 1, [8, 12], C.metal)


def build_mine_works(k: TileKit) -> None:
    """Mine works: a corrugated hall, a conveyor, a chimney."""
    plot(k, C.ore)
    k.s.box(
        [k.w * 0.55, 9, k.d * 0.5],
        C.corrugated,
        Placement([-k.w * 0.2, 0, -k.d * 0.2], 0, 0, 0),
        C.roof,
    )
    k.s.box([1.4, 1.4, k.d * 0.7], C.mineYellow, Placement([k.w * 0.15, 5, k.d * 0.05], 0, -0.3, 0))
    k.s.lathe(
        [
            [k.w * 0.18, 0],
            [0, k.w * 0.2],
        ],
        7,
        C.ore,
        Placement([k.w * 0.3, 0, k.d * 0.28], 0, 0, 0),
    )
    chimney(k, -k.w * 0.35, k.d * 0.3, 14)
    windows(k, [k.w * 0.55, k.d * 0.5], [1, 8], L.windowDim, [-k.w * 0.2, -k.d * 0.2])


def build_pumpjack(k: TileKit) -> None:
    """Pumpjacks in a row on sand."""
    plot(k, C.sand)
    n = max(1, js_round(k.d / 10))
    for i in range(n):
        z = -k.d / 2 + (k.d / n) * (i + 0.5)
        k.s.box([2.5, 1, 5], C.concreteDark, Placement([0, 0, z], 0, 0, 0))
        k.s.box([0.6, 4, 0.6], C.metalDark, Placement([0, 1, z], 0, 0, 0))
        k.s.box([0.7, 0.7, 6.5], C.mineYellow, Placement([0, 4.5, z], 0, 0.2, 0))
        k.s.box([1.4, 2, 0.8], C.metalDark, Placement([0, 4.3, z - 3.2], 0, 0.2, 0))
        k.lights.box([0.3, 0.3, 0.3], L.red, Placement([0, 5.6, z + 2.6], 0, 0, 0))


def build_oil_tanks(k: TileKit) -> None:
    """Rows of white oil tanks."""
    plot(k, C.sand)
    cylinders(k, min(4, min(k.w, k.d) / 2 - 0.8), [4, 6], C.white)


def build_flare(k: TileKit) -> None:
    """A gas flare: a stack with a molten tip, a small block beside it."""
    plot(k, C.concreteDark)
    k.s.cylinder(0.7, 16, 6, C.metal, Placement([0, 0, 0], 0, 0, 0), 0.5)
    k.lights.lathe(
        [
            [0.6, 16],
            [1, 17.5],
            [0, 19.5],
        ],
        6,
        L.molten,
    )
    k.s.box([3, 2, 2], C.metalDark, Placement([-2.5, 0, -2.5], 0, 0, 0))


def build_tanks(k: TileKit) -> None:
    """Rows of tanks in white, silver or grey."""
    plot(k, C.concreteDark)
    cylinders(
        k,
        min(5, min(k.w, k.d) / 2 - 0.8),
        [5, 8],
        any_of(k, [C.white, C.silver, C.metal]),
    )


def build_refinery(k: TileKit) -> None:
    """A refinery: columns, pipe racks and a block of plant."""
    plot(k, C.concreteDark)
    n = max(2, js_round((k.w * k.d) / 120))
    for _i in range(n):
        x = r(k, [-k.w / 2 + 2, k.w / 2 - 2])
        z = r(k, [-k.d / 2 + 2, k.d / 2 - 2])
        h = r(k, [12, 22])
        k.s.cylinder(1.4, h, 8, C.silver, Placement([x, 0, z], 0, 0, 0))
        k.lights.ring(1.45, 0.3, 8, L.yellow, Placement([x, h * 0.6, z], 0, 0, 0))
    k.s.box([k.w - 2, 1, 1], C.metal, Placement([0, 6, 0], 0, 0, 0))
    k.s.box([1, 1, k.d - 2], C.metal, Placement([0, 6, 0], 0, 0, 0))
    k.s.box(
        [k.w * 0.4, 4, k.d * 0.25],
        C.concrete,
        Placement([-k.w * 0.25, 0, -k.d * 0.33], 0, 0, 0),
        C.roof,
    )


def build_factory(k: TileKit) -> None:
    """A factory: a saw-tooth hall, chimneys and lit windows."""
    plot(k, C.concreteDark)
    w = k.w - 1
    d = k.d * 0.75
    z = (k.d - d) / 2 - 0.5
    h = r(k, [8, 12])
    k.s.box([w, h, d], any_of(k, SHEDS), Placement([0, 0, z], 0, 0, 0))
    teeth = max(2, js_round(d / 6))
    for i in range(teeth):
        gable(k, [w, d / teeth], h, 2.2, C.roof, [0, z - d / 2 + (d / teeth) * (i + 0.5)])
    for i in range(max(1, js_round(k.w / 12))):
        chimney(k, -w / 2 + 2 + i * 6, z + d / 2 - 2, h + r(k, [10, 16]))
    windows(k, [w, d], [1.5, h - 1], L.windowDim, [0, z], 3.5)
    front_lights(k, w, z - d / 2, h - 1.5, any_of(k, [L.pink, L.cyan]))


def build_warehouse(k: TileKit) -> None:
    """A warehouse: a long hall with loading doors."""
    plot(k, C.concreteDark)
    w = k.w - 1
    d = k.d - 3
    h = r(k, [6, 9])
    k.s.box([w, h, d], any_of(k, SHEDS), Placement([0, 0, 1], 0, 0, 0))
    gable(k, [w, d], h, 1.5, C.roof, [0, 1], d > w)
    doors = max(1, js_round(w / 5))
    for i in range(doors):
        k.lights.box(
            [2.5, 3, 0.2],
            L.yellowDim,
            Placement([-w / 2 + (w / doors) * (i + 0.5), 0, 1 - d / 2 - 0.1], 0, 0, 0),
        )


def build_containers(k: TileKit) -> None:
    """A container yard: stacks of containers in a grid, a lamp."""
    plot(k, C.concreteDark)
    cols = max(1, math.floor(k.w / 3.5))
    rows = max(1, math.floor(k.d / 7))
    for i in range(cols):
        for j in range(rows):
            stack = 1 + math.floor(k.random() * 2)
            for n in range(stack):
                x = -k.w / 2 + (k.w / cols) * (i + 0.5)
                z = -k.d / 2 + (k.d / rows) * (j + 0.5)
                k.s.box([2.4, 2.5, 6], any_of(k, CONTAINERS), Placement([x, n * 2.5, z], 0, 0, 0))
    lamp(k, -k.w / 2 + 0.3, -k.d / 2 + 0.3, 8)


def build_cooling_tower(k: TileKit) -> None:
    """A hyperbolic cooling tower, a red ring at its throat, a service block."""
    plot(k, C.concreteDark)
    rad = min(k.w, k.d) * 0.36
    k.s.lathe(
        [
            [rad, 0],
            [rad * 0.72, rad * 1.6],
            [rad * 0.78, rad * 2.2],
        ],
        14,
        C.concrete,
    )
    k.lights.ring(rad * 0.74, 0.5, 14, L.red, Placement([0, rad * 2.1, 0], 0, 0, 0))
    k.s.box([k.w * 0.25, 4, k.d * 0.2], C.metal, Placement([k.w * 0.33, 0, -k.d * 0.36], 0, 0, 0))


def build_foundry(k: TileKit) -> None:
    """A foundry: a tall hall with molten furnace mouths and tall stacks."""
    plot(k, C.rustDark)
    w = k.w - 2
    d = k.d * 0.6
    h = r(k, [14, 20])
    k.s.box(
        [w, h, d],
        any_of(k, [C.rust, C.metalDark, C.corrugated]),
        Placement([0, 0, -k.d * 0.15], 0, 0, 0),
    )
    gable(k, [w, d], h, 4, C.metalDark, [0, -k.d * 0.15])
    mouths = max(2, js_round(w / 8))
    for i in range(mouths):
        x = -w / 2 + (w / mouths) * (i + 0.5)
        k.lights.box(
            [3, 4, 0.3], L.molten, Placement([x, 0.5, -k.d * 0.15 - d / 2 - 0.15], 0, 0, 0)
        )
        chimney(k, x, k.d * 0.3, h + r(k, [14, 22]), 1.2)
    k.s.box([w, 1.2, 1.2], C.metal, Placement([0, h * 0.7, k.d * 0.3], 0, 0, 0))


def build_plant(k: TileKit) -> None:
    """A power plant: a hall, a cooling tower, silos and a tall stack."""
    plot(k, C.concreteDark)
    k.s.box(
        [k.w * 0.5, 16, k.d * 0.45],
        C.metalDark,
        Placement([-k.w * 0.22, 0, -k.d * 0.25], 0, 0, 0),
        C.roof,
    )
    windows(k, [k.w * 0.5, k.d * 0.45], [2, 15], L.windowDim, [-k.w * 0.22, -k.d * 0.25], 4)
    rad = min(k.w, k.d) * 0.16
    k.s.lathe(
        [
            [rad, 0],
            [rad * 0.72, rad * 1.6],
            [rad * 0.8, rad * 2.2],
        ],
        12,
        C.concrete,
        Placement([k.w * 0.25, 0, -k.d * 0.25], 0, 0, 0),
    )
    for i in range(3):
        k.s.cylinder(
            2.2, 9, 10, C.silver, Placement([-k.w / 2 + 3 + i * 5.5, 0, k.d * 0.28], 0, 0, 0)
        )
    chimney(k, k.w * 0.3, k.d * 0.3, 34, 1.4)
    k.s.box([k.w - 2, 1, 1], C.rust, Placement([0, 7, k.d * 0.05], 0, 0, 0))


def build_dock_crane(k: TileKit) -> None:
    """A dock crane: two gantry legs a side and a beam across the top."""
    plot(k, C.concreteDark)
    long = max(k.w, k.d)
    along_z = k.d > k.w
    for a in [-long / 3, long / 3]:
        x = 0 if along_z else a
        z = a if along_z else 0
        k.s.box([1, 14, 1], C.signalOrange, Placement([x - 2, 0, z], 0, 0, 0))
        k.s.box([1, 14, 1], C.signalOrange, Placement([x + 2, 0, z], 0, 0, 0))
    beam = [5, 1.5, long - 1] if along_z else [long - 1, 1.5, 5]
    k.s.box(beam, C.signalOrange, Placement([0, 14, 0], 0, 0, 0))
    k.s.box([2, 2, 3], C.metalDark, Placement([0, 15.5, 0], 0, 0, 0))
    k.lights.box([0.4, 0.4, 0.4], L.red, Placement([0, 17.6, 0], 0, 0, 0))
