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


def step_model_animations(root: Any, dt_seconds: float) -> None:
    """Run the animations attached to `root` and to all its descendants."""
    nodes = [root]
    nodes.extend(descendants(root, False))
    for node in nodes:
        animations = weak_map_get(ANIMATIONS, node)
        if animations is not None:
            for animation in animations:
                animation(dt_seconds)


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
