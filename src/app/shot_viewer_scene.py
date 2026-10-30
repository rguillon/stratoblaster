"""The playfield scene of the shot and enemy viewers:
an orthographic camera looking straight down on the playfield, and the player ship lying on it.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from config.shot_viewer import SHOT_VIEWER_CONFIG as CFG
from render.babylon import (
    babylon_class,
    child_meshes,
    color4,
    descendants,
    dispose_node,
    is_instance_of,
    new_directional_light,
    new_free_camera,
    new_hemispheric_light,
    new_scene,
    new_transform_node,
    vector3,
)
from render.model_animation import step_model_animations

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

CAMERA_DISTANCE = 500


def create_playfield_scene(engine: Any, screen: Any) -> Any:
    """A scene looking straight down on a `screen`-sized playfield: an orthographic camera shows
    X in [0, width] and Y in [0, height] (one unit per logical pixel), from -Z.
    """
    scene = new_scene(engine)
    clear = CFG.clear_color
    scene.clearColor = color4(clear[0], clear[1], clear[2], clear[3])
    width = screen.width
    height = screen.height
    camera = new_free_camera(
        "playfield-camera",
        vector3(width / 2, height / 2, -CAMERA_DISTANCE),
        scene,
    )
    camera.setTarget(vector3(width / 2, height / 2, 0))
    camera.mode = babylon_class("Camera").ORTHOGRAPHIC_CAMERA
    camera.orthoLeft = -width / 2
    camera.orthoRight = width / 2
    camera.orthoBottom = -height / 2
    camera.orthoTop = height / 2
    camera.minZ = 1
    camera.maxZ = CAMERA_DISTANCE * 2
    ambient = new_hemispheric_light("playfield-ambient", vector3(0, 0, -1), scene)
    ambient.intensity = CFG.lights.ambient_intensity
    key_direction = CFG.lights.key_direction
    key = new_directional_light(
        "playfield-key",
        vector3(key_direction[0], key_direction[1], key_direction[2]),
        scene,
    )
    key.intensity = CFG.lights.key_intensity
    return scene


class PlayfieldShip:
    """A player ship lying on the playfield, nose up (+Y), top towards the camera."""

    def __init__(self, scene: Any, scale: float, x: float, y: float) -> None:
        self.scene = scene
        self.scale = scale
        self.pivot = new_transform_node("playfield-ship", scene)
        self.pivot.position.set(x, y, 0)
        self._model: Any = None

    def show(self, factory: Any) -> float:
        """Replaces the ship model and returns the height (Y) of its nose tip on the playfield."""
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
        if self._model is not None:
            step_model_animations(self._model, dt)
