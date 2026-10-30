"""One model per prop kind of this game, keyed by its id (P04-R04), ported from
`props/prop-models.ts`. Phase 15: every model has a footprint of whole tiles (reviewer,
2026-10-28); those made for the grid already do."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from game.config.cars import CAR_IDS  # noqa: E402
from game.config.prop_ids import PROP_IDS  # noqa: E402
from game.config.prop_look import PROP_COLORS as C  # noqa: E402
from game.config.world_1.props import WORLD_1_PROP_IDS as W  # noqa: E402
from game.view.props.car_props import build_car  # noqa: E402
from game.view.props.desert_plants import build_cactus, build_dry_bush, build_palm_tree  # noqa: E402
from game.view.props.desert_props import build_beach_hut, build_desert_home  # noqa: E402
from game.view.props.farm_props import build_farmhouse, build_grain_silos, build_greenhouse  # noqa: E402
from game.view.props.green_tree_props import build_broadleaf_tree, build_bush, build_conifer  # noqa: E402
from game.view.props.home_props import build_cube_home, build_dome_home  # noqa: E402
from game.view.props.road_kit import ROAD_KIT_MODELS  # noqa: E402
from game.view.props.science_props import build_antenna_mast  # noqa: E402
from game.view.props.tile_fit import on_tiles  # noqa: E402
from game.view.props.tile_models import TILE_PROP_MODELS  # noqa: E402
from game.view.props.tree_props import build_dead_tree, build_forked_tree  # noqa: E402
from game.view.props.wind_turbine import build_wind_turbine  # noqa: E402


def merged(parts: list[Any]) -> dict[str, Any]:
    """The entries of `parts` in order, later ones replacing earlier ones (object spread)."""
    result: dict[str, Any] = {}
    for part in parts:
        for key in part.keys():  # noqa: SIM118 (Transcrypt: `for k in dict` is broken)
            result[key] = part[key]
    return result


def make_free_models() -> dict[str, Any]:
    """The hand-made models, before they are fitted to tiles."""
    return {
        PROP_IDS.antenna: build_antenna_mast,
        PROP_IDS.cubeHome: build_cube_home,
        PROP_IDS.domeHome: build_dome_home,
        PROP_IDS.deadTree: build_dead_tree,
        PROP_IDS.forkedTree: build_forked_tree,
        PROP_IDS.conifer: build_conifer,
        PROP_IDS.broadleaf: build_broadleaf_tree,
        PROP_IDS.bush: build_bush,
        # Phase 6: desert and coast homes, outposts and plants.
        W.desertHome: build_desert_home,
        W.beachHut: build_beach_hut,
        W.palm: build_palm_tree,
        W.dryBush: build_dry_bush,
        W.cactus: build_cactus,
        # Reviewer, 2026-10-26: the farms of World 1's green land.
        W.farmhouse: build_farmhouse,
        W.greenhouse: build_greenhouse,
        W.grainSilos: build_grain_silos,
        W.windTurbine: build_wind_turbine,
    }


def car_model(shape: str, paint: list[float]) -> Any:
    """A factory of one car model."""
    return lambda: build_car(shape, paint)


def make_car_models() -> dict[str, Any]:
    """The cars, at their own size: they drive in the lanes of the roads, not on tiles (D-162)."""
    return {
        CAR_IDS.red: car_model("sedan", C.containerRed),
        CAR_IDS.blue: car_model("sedan", C.containerBlue),
        CAR_IDS.white: car_model("sedan", C.white),
        CAR_IDS.grey: car_model("sedan", C.metal),
        CAR_IDS.van: car_model("van", C.white),
        CAR_IDS.truck: car_model("truck", C.containerGreen),
    }


def make_prop_models() -> dict[str, Any]:
    """One model per prop kind of this game, keyed by its id (P04-R04)."""
    return merged(
        [
            on_tiles(make_free_models()),
            make_car_models(),
            TILE_PROP_MODELS,
            # The road kit, for the `props/` page (no level places it: its streets are drawn).
            ROAD_KIT_MODELS,
        ]
    )


PROP_MODELS = make_prop_models()
