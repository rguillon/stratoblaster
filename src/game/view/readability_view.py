"""Readability of the playfield (P14): the player ships' outlines, the
toning of the scenery under them, and the shot renderers' glow
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.readability import READABILITY as LOOK
from game.config.record import record
from render.babylon import babylon_constant
from render.outline import outline_model

__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

Scene = Any  # noqa: E402


__pragma__("noskip")

# Colours that are not darkened: tint factors, and lava, which glows by itself.
KEEP = ["tints", "lava"]


def _is_array(value: Any) -> bool:
    """`Array.isArray(value)`."""
    __pragma__("js", "{}", "return Array.isArray(value);")
    return False


def _is_number_triple(value: Any) -> bool:
    """True for a 3-element array of numbers (an RGB colour)."""
    __pragma__(
        "js", "{}", "return value.length === 3 && value.every((v) => typeof v === 'number');"
    )
    return False


def _is_object(value: Any) -> bool:
    """`typeof value === 'object' && value !== null`."""
    __pragma__("js", "{}", "return typeof value === 'object' && value !== null;")
    return False


def _entries(value: Any) -> list[Any]:
    """`Object.entries(value)`: a list of `[key, value]` pairs."""
    __pragma__("js", "{}", "return Object.entries(value);")
    return []


def _from_entries(pairs: list[Any]) -> Any:
    """`Object.fromEntries(pairs)`."""
    __pragma__("js", "{}", "return Object.fromEntries(pairs);")
    return None


def _copy_object(value: Any) -> Any:
    """A shallow copy of a plain object (`{...value}`)."""
    __pragma__("skip")
    return record(dict(value))
    __pragma__("noskip")
    __pragma__("js", "{}", "return Object.assign({}, value);")
    return None


def _range_scale(value: Any, k: float, skip: list[str]) -> Any:
    """`value` with every colour (3 numbers) in it times `k`, but under the `skip` keys."""
    if _is_array(value):
        if _is_number_triple(value):
            return [v * k for v in value]
        return [_range_scale(v, k, skip) for v in value]
    if not _is_object(value):
        return value
    return _from_entries(
        [[key, v if key in skip else _range_scale(v, k, skip)] for key, v in _entries(value)]
    )


def _outlined(build: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """A model factory that outlines what `build` makes in the player colour (P14-R03)."""

    def outlined(scene: Scene) -> Any:
        root = build(scene)
        outline_model(root, LOOK.playerOutline.color)
        return root

    return outlined


def _toned_shot(create: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """A shot renderer factory whose additive materials are capped at `playerShotMaxOpacity`."""

    def toned_shot(scene: Scene) -> Any:
        before = scene.materials.slice()
        renderer = create(scene)
        for material in scene.materials:
            if material not in before and material.alphaMode == babylon_constant("ALPHA_ADD"):
                material.alpha = min(material.alpha, LOOK.playerShotMaxOpacity)
        return renderer

    return toned_shot


def outlined_ships(models: dict[str, Any]) -> dict[str, Any]:
    """The player ship models, each with a rim glow in the player colour (P14-R03)."""
    return {ship_id: _outlined(build) for ship_id, build in models.items()}


def toned(look: Any, tone: float) -> Any:
    """P14-R01: `look` with its ground, shores, water and roads darkened to `tone` (0..1) of their
    colours, and its props, haze and clouds by the engine (`SceneryLook.tone`), so the ships and
    shots stand out over them. The props' self-lit accents keep their brightness."""
    result = _copy_object(look)
    result.terrain = _range_scale(look.terrain, tone, KEEP)
    result.sea = _range_scale(look.sea, tone, KEEP)
    result.roads = _range_scale(look.roads, tone, KEEP)
    result.tone = tone
    return result


def all_toned(looks: dict[str, Any], tone: float) -> dict[str, Any]:
    """`looks`, each `toned` to `tone`."""
    return {look_id: toned(look, tone) for look_id, look in looks.items()}


def toned_shots(renderers: dict[str, Any]) -> dict[str, Any]:
    """P14-R06: the shot renderers, their glows (added on) toned down to `playerShotMaxOpacity`,
    so they never hide the enemy bullets."""
    return {shot_id: _toned_shot(create) for shot_id, create in renderers.items()}
