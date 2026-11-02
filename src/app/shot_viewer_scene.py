# Copyright (c) 2026 Renaud Guillon
"""The player ship lying on the playfield, as the game and the dev viewer show it."""

import math

from render.babylon import (
    child_meshes,
    descendants,
    dispose_node,
    is_instance_of,
    new_transform_node,
)
from render.model_animation import step_model_animations

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


class PlayfieldShip:
    """A player ship lying on the playfield, nose up (+Y), top towards the camera.

    As in the game, and in the ships viewer (DEV-MENU-12).
    """

    def __init__(self, scene: Any, scale: float, x: float, y: float) -> None:
        self.scene = scene
        self.scale = scale
        self.pivot = new_transform_node("playfield-ship", scene)
        self.pivot.position.set(x, y, 0)
        self._model: Any = None

    def show(self, factory: Any) -> float:
        """Replace the ship model and return the height (Y) of its nose tip on the playfield.

        That is where the muzzle is (GFX-SHOT-05).
        """
        if self._model is not None:
            dispose_node(self._model)
        # Models face +Z with +Y up: a holder turns the nose to +Y and the top to -Z (the camera).
        holder = new_transform_node("playfield-ship-model", self.scene)
        holder.parent = self.pivot
        holder.rotation.x = -math.pi / 2
        holder.scaling.setAll(self.scale)
        factory(self.scene).parent = holder
        self._model = holder
        return self._nose_y(holder)

    def _nose_y(self, holder: Any) -> float:
        """Highest point of the model's meshes, i.e. its nose tip (the pivot when it has none)."""
        nodes = [self.pivot, holder]
        nodes.extend(descendants(holder, False))
        # Parents come before their children, so each world matrix uses an up-to-date parent.
        for node in nodes:
            if is_instance_of(node, "TransformNode"):
                node.computeWorldMatrix(True)
        top: float = self.pivot.position.y
        for mesh in child_meshes(holder, False):
            if mesh.getTotalVertices() > 0:
                top = max(top, mesh.getBoundingInfo().boundingBox.maximumWorld.y)
        return top

    def update(self, dt: float) -> None:
        """Advances the model's animation by `dt` and refreshes the view."""
        if self._model is not None:
            step_model_animations(self._model, dt)
