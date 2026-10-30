"""A neutral scenery look for the tests of `render/scenery/`: every field is set to a plain value,
so a test changes only the fields it is about. The records are the classes of
`render/scenery/scenery_look.py`, built positionally as the game's own configs build them."""

from typing import Any

from render.scenery.road_geometry import RoadLook, RoadOpacity
from render.scenery.scenery_look import (
    AmbientLook,
    CloudLayerLook,
    GlowLook,
    Jitter,
    PropsLook,
    SceneryFog,
    SceneryLook,
    SceneryLookSky,
    SeaLook,
    SeaNormalMap,
    ShadowLook,
    ShoreFoam,
    ShoreLook,
    SunLook,
    TerrainLook,
    TextureLook,
)

GREY = (0.5, 0.5, 0.5)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)


def texture(**overrides: Any) -> TextureLook:
    values: dict[str, Any] = {
        "colors": (BLACK, GREY, WHITE),
        "frequency": 4,
        "octaves": 2,
        "speckle": 0,
        "speckle_color": GREY,
        "strata": 0,
    }
    values.update(overrides)
    return TextureLook(**values)


def make_look(**overrides: Any) -> SceneryLook:
    """A scenery look with plain values. Pass any field of `SceneryLook` to replace it."""
    foam = ShoreFoam(WHITE, 1, 4, 1, 2)
    shore = ShoreLook(GREY, 2, GREY, BLACK, 10, foam)
    terrain = TerrainLook(
        64,
        32,
        texture(),
        texture(),
        texture(),
        texture(),
        texture(),
        texture(),
        texture(),
        0,
        20,
        2,
        (0.5, 1),
        Jitter(0, 0),
        16,
        (WHITE, GREY),
        8,
        shore,
        0.2,
    )
    sea = SeaLook(GREY, 0.8, 0.1, 0.5, SeaNormalMap(64, 4, 2, 0.3), 16, (0.1, 0.1))
    values: dict[str, Any] = {
        "sky": SceneryLookSky(GREY, [], 1),
        "fog": SceneryFog(100, 400),
        "sun": SunLook(45, 0, WHITE, 1, ShadowLook(256, 100, 0.001, 0.01, 0.5)),
        "ambient": AmbientLook(GREY, BLACK, 0.5),
        "terrain": terrain,
        "sea": sea,
        "clouds": [],
        "roads": RoadLook(GREY, GREY, RoadOpacity(1, 0.8), 1, 0.5, None, 0, 0.1, None),
        "props": PropsLook(0.3, 1),
        "glow": GlowLook(1, 8),
    }
    values.update(overrides)
    return SceneryLook(
        values["sky"],
        values["fog"],
        values["sun"],
        values["ambient"],
        values["terrain"],
        values["sea"],
        values["clouds"],
        values["roads"],
        values["props"],
        values["glow"],
        values.get("atmosphere"),
        values.get("shot_style"),
        values.get("tone"),
    )


def cloud(**overrides: Any) -> CloudLayerLook:
    values: dict[str, Any] = {
        "altitude": 100,
        "coverage": 0.5,
        "opacity": 0.5,
        "tile_size": 64,
        "drift": (0, 0),
        "softness": 0.5,
        "color": WHITE,
        "shade": GREY,
    }
    values.update(overrides)
    return CloudLayerLook(**values)
