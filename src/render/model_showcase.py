"""Models shown side by side, each one spinning ()."""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import new_transform_node
from render.model_animation import step_model_animations

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

ModelFactory = Callable[[Any], Any]
__pragma__("noskip")


class ShowcaseOptions:
    """Layout and animation settings of a `ModelShowcase`.

    `spacing` is the distance between the centres of two neighbouring models, in world units.
    """

    def __init__(self, spacing: float, rotation_speed_rad_per_sec: float) -> None:
        self.spacing = spacing
        self.rotation_speed_rad_per_sec = rotation_speed_rad_per_sec


class ModelShowcase:
    """Shows models side by side along X, each one spinning around its vertical axis. Model
    animations (`add_model_animation`) are stepped with the rotation."""

    def __init__(self, scene: Any, factories: list[ModelFactory], options: ShowcaseOptions) -> None:
        self._rotation_speed = options.rotation_speed_rad_per_sec
        # Distance from the leftmost to the rightmost model edge slot, in world units.
        self.width = len(factories) * options.spacing
        offset = ((len(factories) - 1) * options.spacing) / 2
        # One pivot per model, left to right; each model is the only child of its pivot.
        self.pivots: list[Any] = []
        for i in range(len(factories)):
            pivot = new_transform_node("showcase-pivot-" + str(i), scene)
            pivot.position.x = i * options.spacing - offset
            factories[i](scene).parent = pivot
            self.pivots.append(pivot)

    def update(self, dt_seconds: float) -> None:
        """Advances the rotation and the model animations by `dt_seconds`."""
        for pivot in self.pivots:
            pivot.rotation.y = pivot.rotation.y + self._rotation_speed * dt_seconds
            step_model_animations(pivot, dt_seconds)

    def dispose(self) -> None:
        for pivot in self.pivots:
            pivot.dispose()
