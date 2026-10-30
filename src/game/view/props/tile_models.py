"""The models made for the grid of tiles (Phase 15, P15-R07, R09), ported from
`props/tile-models.ts`: one per entry of `TILE_MODELS`, each built to fill its tiles less the
margin."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from game.config.tile_buildings import BUILDING_MARGIN, TILE, TILE_MODELS  # noqa: E402
from game.view.props.tile_city import (  # noqa: E402
    build_car_park,
    build_midrise,
    build_office,
    build_park,
    build_plaza,
    build_skyscraper,
    build_tower,
    build_yard,
)
from game.view.props.tile_homes import (  # noqa: E402
    build_adobe,
    build_barn,
    build_cottage,
    build_courtyard,
    build_farmhouse,
    build_flats,
    build_greenhouse,
    build_house,
    build_terrace,
    build_villa,
    build_workshop,
)
from game.view.props.tile_homesteads import build_homestead  # noqa: E402
from game.view.props.tile_kit import geometry_of, tile_kit  # noqa: E402
from game.view.props.tile_residences import build_residence  # noqa: E402
from game.view.props.tile_works import (  # noqa: E402
    build_containers,
    build_cooling_tower,
    build_depot,
    build_dock_crane,
    build_factory,
    build_flare,
    build_foundry,
    build_headframe,
    build_mine_works,
    build_oil_tanks,
    build_ore_silos,
    build_plant,
    build_pumpjack,
    build_radio,
    build_refinery,
    build_solar,
    build_tanks,
    build_warehouse,
    build_water_tower,
)
from render.scenery.scenery_look import PropGeometry  # noqa: E402


def make_builders() -> dict[str, Any]:
    """What each archetype of a model is built with."""
    return {
        "house": build_house,
        "villa": build_villa,
        "cottage": build_cottage,
        "terrace": build_terrace,
        "flats": build_flats,
        "residence": build_residence,
        "homestead": build_homestead,
        "workshop": build_workshop,
        "farmhouse": build_farmhouse,
        "greenhouse": build_greenhouse,
        "barn": build_barn,
        "adobe": build_adobe,
        "courtyard": build_courtyard,
        "waterTower": build_water_tower,
        "solar": build_solar,
        "radio": build_radio,
        "depot": build_depot,
        "headframe": build_headframe,
        "oreSilos": build_ore_silos,
        "mineWorks": build_mine_works,
        "pumpjack": build_pumpjack,
        "oilTanks": build_oil_tanks,
        "flare": build_flare,
        "refinery": build_refinery,
        "factory": build_factory,
        "warehouse": build_warehouse,
        "containers": build_containers,
        "coolingTower": build_cooling_tower,
        "tanks": build_tanks,
        "foundry": build_foundry,
        "plant": build_plant,
        "dockCrane": build_dock_crane,
        "midrise": build_midrise,
        "office": build_office,
        "tower": build_tower,
        "skyscraper": build_skyscraper,
        "carPark": build_car_park,
        "yard": build_yard,
        "plaza": build_plaza,
        "park": build_park,
    }


BUILDERS = make_builders()


def build_tile_model(model: Any) -> PropGeometry:
    """The geometry of `model`, filling its tiles less BUILDING_MARGIN each side."""
    w = model.tiles[0]
    d = model.tiles[1]
    k = tile_kit(
        w * TILE.size - 2 * BUILDING_MARGIN,
        d * TILE.size - 2 * BUILDING_MARGIN,
        TILE.size,
        model.seed,
    )
    BUILDERS[model.archetype](k)
    return geometry_of(k)


def tile_model_factory(model: Any) -> Any:
    """A model factory that builds `model` (a factory function: closures in loops break)."""

    def make() -> PropGeometry:
        return build_tile_model(model)

    return make


def make_tile_prop_models() -> dict[str, Any]:
    """The models made for the grid, keyed by id."""
    result: dict[str, Any] = {}
    for m in TILE_MODELS:
        result[m.id] = tile_model_factory(m)
    return result


TILE_PROP_MODELS = make_tile_prop_models()
