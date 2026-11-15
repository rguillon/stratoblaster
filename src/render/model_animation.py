# Copyright (c) 2026 Renaud Guillon
"""Per-frame animations attached to the nodes of a model (GFX-ART-11).

A `ModelAnimation` is a function of the elapsed seconds. It is kept per node in a JavaScript
`WeakMap`, so it is dropped with the node.
"""

from render.babylon import descendants, new_weak_map, weak_map_get, weak_map_set

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Any

from render.handles import WeakMap

ModelAnimation = Callable[[float], None]
# __pragma__ ("noskip")


ANIMATIONS: WeakMap[list[ModelAnimation]] = new_weak_map()
# D-411: by model root, the nodes under it with animations, found once and kept until an
# animation is added anywhere (`_added` counts them): looking through every node of every model on
# every frame for them cost the frames of busy levels.
_ANIMATED: WeakMap[list[Any]] = new_weak_map()
_added = [0]
# What drives a model's animations from outside, by node: name to number (the ship's sideways
# speed, D-359).
INPUTS: WeakMap[dict[str, float]] = new_weak_map()
# The ship's sideways speed as a share of its top speed, -1 to 1, positive towards the model's +X.
SIDEWAYS = "sideways"


def add_model_animation(node: Any, animation: Any) -> None:
    """Attaches a per-frame animation to a node of a model (reactor flames, blinking lights...).

    It runs whenever the model is stepped with `step_model_animations` and is dropped with the node.
    """
    current = weak_map_get(ANIMATIONS, node)
    if current is None:
        weak_map_set(ANIMATIONS, node, [animation])
    else:
        current.append(animation)
    _added[0] += 1


def step_model_animations(root: Any, dt_seconds: float) -> None:
    """Run the animations attached to `root` and to all its descendants."""
    for animations in _animated_under(root):
        for animation in animations:
            animation(dt_seconds)


def _animated_under(root: Any) -> list[list[ModelAnimation]]:
    """Return the animations of `root` and of the nodes under it, node by node (D-411), found once.

    The list is kept with the count of animations added when it was made, and made again once any
    animation was added since (a model built or changed).
    """
    if _ANIMATED is None:
        # CPython (unit tests): no WeakMap to keep the list in.
        return _find_animated(root)
    known = weak_map_get(_ANIMATED, root)
    if known is not None and known[0] == _added[0]:
        cached: list[list[ModelAnimation]] = known[1]
        return cached
    animated = _find_animated(root)
    weak_map_set(_ANIMATED, root, [_added[0], animated])
    return animated


def _find_animated(root: Any) -> list[list[ModelAnimation]]:
    """Return the animations of `root` and of the nodes under it that have some, in tree order."""
    nodes = [root]
    nodes.extend(descendants(root, False))
    found: list[list[ModelAnimation]] = []
    for node in nodes:
        animations = weak_map_get(ANIMATIONS, node)
        if animations is not None:
            found.append(animations)
    return found


def set_model_input(node: Any, name: str, value: float) -> None:
    """Set an input `name` of the model under `node` (or of the node itself), for its animations.

    The game sets it on the node it moves the model by; the model's animations read it with
    `model_input` from their own node, below it.
    """
    inputs = weak_map_get(INPUTS, node)
    if inputs is None:
        inputs = {}
        weak_map_set(INPUTS, node, inputs)
    inputs[name] = value


def model_input(node: Any, name: str, default: float) -> float:
    """Return the input `name` set on `node` or the nearest of its ancestors; `default` if none."""
    current = node
    while current:
        inputs = weak_map_get(INPUTS, current)
        if inputs is not None and name in inputs:
            return inputs[name]
        current = current.parent
    return default
