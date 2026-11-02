# Copyright (c) 2026 Renaud Guillon
"""One model per prop kind of this game, keyed by its id (GFX-PROP-02).

The cars, the buildings and lots of the grid of tiles, the trees (D-212) and the road kit. D-207:
the hand-made homes, huts, masts, farms and plants are gone.
"""

from game.config.cars import CAR_IDS
from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from game.view.props.car_props import build_car
from game.view.props.crag_props import CRAG_MODELS, MESA_MODELS
from game.view.props.road_kit import ROAD_KIT_MODELS
from game.view.props.tile_models import TILE_PROP_MODELS
from game.view.props.tree_props import TREE_MODELS

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def merged(parts: list[Any]) -> dict[str, Any]:
    """Return the entries of `parts` in order, later ones replacing earlier ones (object spread)."""
    result: dict[str, Any] = {}
    for part in parts:
        for key in part.keys():
            result[key] = part[key]
    return result


def car_model(shape: str, paint: list[float], accent: list[float]) -> Any:
    """Return a factory of one car model, its neon `accent` (D-211)."""
    return lambda: build_car(shape, paint, accent)


def make_car_models() -> dict[str, Any]:
    """Return the cars, at their own size: they drive in road lanes, not on tiles (D-162).

    D-213: each kind has its own body.
    """
    return {
        CAR_IDS.red: car_model("racer", C.containerRed, L.cyan),
        CAR_IDS.blue: car_model("sedan", C.containerBlue, L.pink),
        CAR_IDS.white: car_model("pod", C.white, L.cyan),
        CAR_IDS.grey: car_model("cruiser", C.metal, L.violet),
        CAR_IDS.van: car_model("van", C.white, L.pink),
        CAR_IDS.truck: car_model("truck", C.containerGreen, L.yellow),
        CAR_IDS.bus: car_model("bus", C.carOrange, L.cyan),
        CAR_IDS.tanker: car_model("tanker", C.carTeal, L.molten),
    }


def make_prop_models() -> dict[str, Any]:
    """One model per prop kind of this game, keyed by its id.

    Only the kinds some level places, the road kit apart (GFX-PROP-03).
    """
    return merged([
        make_car_models(),
        TILE_PROP_MODELS,
        # D-212: the trees of the green land.
        TREE_MODELS,
        # GFX-PROP-19: the blocks of stone of the cliff faces.
        CRAG_MODELS,
        MESA_MODELS,
        # The road kit, for the `props/` page (no level places it: its streets are drawn).
        ROAD_KIT_MODELS,
    ])


PROP_MODELS = make_prop_models()
