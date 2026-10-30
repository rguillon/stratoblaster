"""One model per prop kind of this game, keyed by its id (P04-R04): the cars, the buildings and lots
of the grid of tiles, the trees (D-212) and the road kit. D-207: the hand-made homes, huts, masts,
farms and plants are gone."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from game.config.cars import CAR_IDS  # noqa: E402
from game.config.prop_look import PROP_COLORS as C  # noqa: E402
from game.config.prop_look import PROP_LIGHTS as L  # noqa: E402
from game.view.props.car_props import build_car  # noqa: E402
from game.view.props.road_kit import ROAD_KIT_MODELS  # noqa: E402
from game.view.props.tile_models import TILE_PROP_MODELS  # noqa: E402
from game.view.props.tree_props import TREE_MODELS  # noqa: E402


def merged(parts: list[Any]) -> dict[str, Any]:
    """The entries of `parts` in order, later ones replacing earlier ones (object spread)."""
    result: dict[str, Any] = {}
    for part in parts:
        for key in part.keys():  # noqa: SIM118 (Transcrypt: `for k in dict` is broken)
            result[key] = part[key]
    return result


def car_model(shape: str, paint: list[float], accent: list[float]) -> Any:
    """A factory of one car model, its neon `accent` (D-211)."""
    return lambda: build_car(shape, paint, accent)


def make_car_models() -> dict[str, Any]:
    """The cars, at their own size: they drive in the lanes of the roads, not on tiles (D-162)."""
    return {
        CAR_IDS.red: car_model("sedan", C.containerRed, L.cyan),
        CAR_IDS.blue: car_model("sedan", C.containerBlue, L.pink),
        CAR_IDS.white: car_model("sedan", C.white, L.cyan),
        CAR_IDS.grey: car_model("sedan", C.metal, L.violet),
        CAR_IDS.van: car_model("van", C.white, L.pink),
        CAR_IDS.truck: car_model("truck", C.containerGreen, L.yellow),
    }


def make_prop_models() -> dict[str, Any]:
    """One model per prop kind of this game, keyed by its id (P04-R04)."""
    return merged(
        [
            make_car_models(),
            TILE_PROP_MODELS,
            # D-212: the trees of the green land.
            TREE_MODELS,
            # The road kit, for the `props/` page (no level places it: its streets are drawn).
            ROAD_KIT_MODELS,
        ]
    )


PROP_MODELS = make_prop_models()
