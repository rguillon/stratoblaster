"""The city made for the grid of tiles (Phase 15, P15-R09): mid-rise blocks, offices, towers and
skyscrapers, and the lots (car parks, yards, plazas, parks), ported from `props/tile-city.ts`.
See `tile_kit.py`."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.props.tile_kit import Rgb  # noqa: E402

__pragma__("noskip")

from game.config.prop_look import PROP_COLORS as C  # noqa: E402
from game.view.props.city_lots import LotKit  # noqa: E402
from game.view.props.tile_kit import (  # noqa: E402
    NEON,
    NEON_DIM,
    TileKit,
    any_of,
    js_round,
    lamp,
    plot,
    r,
    tree,
)
from game.view.props.tile_towers import city_building  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

FACADES = [C.glassBlue, C.glassDark, C.glassGreen, C.concrete, C.white]
ROOFS = [C.roof, C.metal, C.metalDark]


def lot_kit(k: TileKit, facades: list[Rgb], lights: list[Rgb], faces: bool = False) -> LotKit:
    """The lot colours of a city building: a facade, its windows and a roof, picked at random."""
    return LotKit(
        k.s,
        k.lights,
        any_of(k, facades),
        any_of(k, lights),
        any_of(k, ROOFS),
        k.random,
        faces,
    )


def city(k: TileKit, height: list[float], facades: list[Rgb], asymmetric: bool = False) -> None:
    """A city building of the silhouette its seed names (see `tile_towers.py`); `asymmetric`,
    each face lit its own way, an annex and a fin on one side (reviewer, 2026-10-28)."""
    city_building(k, lot_kit(k, facades, NEON_DIM, asymmetric), height, asymmetric)


def build_midrise(k: TileKit) -> None:
    city(k, [16, 28], [C.brick, C.concrete, C.white, C.farmWall])


def build_office(k: TileKit) -> None:
    city(k, [26, 42], FACADES, True)


def build_tower(k: TileKit) -> None:
    city(k, [44, 66], FACADES, True)


def build_skyscraper(k: TileKit) -> None:
    city(k, [70, 110], [C.glassBlue, C.glassDark, C.glassGreen], True)


def build_car_park(k: TileKit) -> None:
    plot(k, C.metalDark)
    rows = max(1, js_round(k.d / 6))
    for j in range(rows):
        z = -k.d / 2 + (k.d / rows) * (j + 0.5)
        x = -k.w / 2 + 1
        while x < k.w / 2 - 3:
            k.s.box([0.15, 0.05, 4], C.white, Placement([x, 0.2, z], 0, 0, 0))
            if k.random() < 0.5:  # noqa: PLR2004 (a geometry constant)
                k.s.box(
                    [1.6, 1.2, 3.6],
                    any_of(k, [C.containerRed, C.containerBlue, C.white]),
                    Placement([x + 1.5, 0.2, z], 0, 0, 0),
                )
            x += 3
    lamp(k, -k.w / 2 + 0.5, -k.d / 2 + 0.5)


def build_yard(k: TileKit) -> None:
    plot(k, C.concrete)
    for _i in range(4):
        size = [1.6, 1.2 + k.random(), 1.6]
        color = any_of(k, [C.wood, C.rust, C.containerGreen])
        at = [r(k, [-k.w / 2 + 1, k.w / 2 - 1]), 0.2, r(k, [-k.d / 2 + 1, k.d / 2 - 1])]
        k.s.box(size, color, Placement(at, 0, 0, 0))
    lamp(k, k.w / 2 - 0.5, -k.d / 2 + 0.5)


def build_plaza(k: TileKit) -> None:
    plot(k, C.paving)
    k.s.cylinder(3, 0.8, 10, C.concreteDark, Placement([0, 0.2, 0], 0, 0, 0))
    k.lights.ring(2.6, 0.3, 10, any_of(k, NEON), Placement([0, 1, 0], 0, 0, 0))
    for x, z in [[-1, -1], [1, -1], [-1, 1], [1, 1]]:
        tree(k, (x * k.w) / 3, (z * k.d) / 3, 3)


def build_park(k: TileKit) -> None:
    plot(k, C.leaf)
    k.s.box([1.2, 0.05, k.d - 1], C.paving, Placement([0, 0.2, 0], 0.4, 0, 0))
    lamp(k, k.w / 2 - 0.5, -k.d / 2 + 0.5)
    n = max(2, js_round((k.w * k.d) / 40))
    for _i in range(n):
        x = r(k, [-k.w / 2 + 2.5, k.w / 2 - 2.5])
        z = r(k, [-k.d / 2 + 2.5, k.d / 2 - 2.5])
        tree(k, x, z, r(k, [3, 4]))
