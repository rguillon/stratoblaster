"""Per-frame animations attached to the nodes of a model ().

A `ModelAnimation` is a function of the elapsed seconds. It is kept per node in a JavaScript
`WeakMap`, so it is dropped with the node.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import descendants, new_weak_map, weak_map_get, weak_map_set

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

ModelAnimation = Callable[[float], None]
__pragma__("noskip")

ANIMATIONS = new_weak_map()


def add_model_animation(node: Any, animation: Any) -> None:
    """Attaches a per-frame animation to a node of a model (reactor flames, blinking lights...).

    It runs whenever the model is stepped with `step_model_animations` and is dropped with the
    node.
    """
    current = weak_map_get(ANIMATIONS, node)
    if current is None:
        weak_map_set(ANIMATIONS, node, [animation])
    else:
        current.append(animation)


def step_model_animations(root: Any, dt_seconds: float) -> None:
    """Runs the animations attached to `root` and to all its descendants."""
    nodes = [root]
    for node in descendants(root, False):
        nodes.append(node)
    for node in nodes:
        animations = weak_map_get(ANIMATIONS, node)
        if animations is not None:
            for animation in animations:
                animation(dt_seconds)
