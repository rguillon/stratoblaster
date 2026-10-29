"""The node the ground hangs from (P04-R05), ported from `render/scenery/ground-root.ts`: drawn
`scale` times as big as it is, as if flying lower (`PlayfieldCameraLook.groundScale`).
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    new_transform_node,
    scene_meshes,
    scene_transform_nodes,
    scene_unique_id,
)
from render.node_adopter import newer
from render.scenery.playfield_framing import GroundWindow, PlayfieldFraming, visible_ground
from render.scenery.scenery_kit import GroundTransform
from render.scenery.stage_parts import lowest_ground

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

__pragma__("noskip")


class GroundRoot:
    """The node the ground hangs from, drawn `scale` times as big as it is, as if flying lower
    (`PlayfieldCameraLook.groundScale`). As the view moves `distance` along the level, the node is
    moved so the ground point under the view is still `distance` in: the level covers the same
    ground a second, which passes `scale` times as fast."""

    def __init__(self, scene: Any, scale: float) -> None:
        self.scene = scene
        self.scale = scale
        self.node = new_transform_node("ground-root", scene)
        self.node.scaling.setAll(scale)

    def adopt(self, create: Callable[[], Any]) -> Any:
        """Runs `create`, then hangs what it made from the ground (unless it has a parent)."""
        before = scene_unique_id(self.scene)
        try:
            return create()
        finally:
            for node in newer(scene_transform_nodes(self.scene), before):
                self._hang(node)
            for mesh in newer(scene_meshes(self.scene), before):
                self._hang(mesh)

    def move_to(self, distance: float) -> None:
        """Moves the ground for the view `distance` along the level."""
        self.node.position.z = (1 - self.scale) * distance

    def to_ground(self, z: float) -> float:
        """The ground Z drawn at world Z `z`."""
        offset: float = self.node.position.z
        return (z - offset) / self.scale

    def to_world(self, z: float) -> float:
        """The world Z where ground Z `z` is drawn."""
        offset: float = self.node.position.z
        return z * self.scale + offset

    @property
    def transform(self) -> GroundTransform:
        """What the terrain's material needs to know (`SceneryKitFrame.ground`)."""
        return GroundTransform(self.scale, self.node.position.z)

    def _hang(self, node: Any) -> None:
        if node.parent is None and node is not self.node:
            node.parent = self.node


def ground_window_of(options: Any, framing: PlayfieldFraming, scale: float) -> GroundWindow:
    """The ground the camera sees over a level (relative to the camera's ground Z, in ground
    units) when the ground is drawn `scale` times as big. `options` has `screen`, `camera` and
    `level`."""
    screen = options.screen
    camera = options.camera
    world = visible_ground(
        framing,
        screen.width / screen.height,
        camera.flight_altitude + framing.height,
        lowest_ground(options.level) * scale,
        camera.flight_altitude,
    )
    return GroundWindow(world.z_near / scale, world.z_far / scale, world.half_width / scale)
