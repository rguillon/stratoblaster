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
