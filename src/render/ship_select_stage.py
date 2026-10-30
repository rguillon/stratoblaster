"""The 3D part of the ship select screen (P01-R06)

The ships stand side by side, rotating. The highlighted ship is scaled up, lit by its own key
light and sits on a neon ring; the others are smaller and only get the ambient light.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    camera_fov_mode_horizontal_fixed,
    child_meshes,
    color3,
    color3_black,
    create_torus,
    new_arc_rotate_camera,
    new_directional_light,
    new_hemispheric_light,
    new_standard_material,
    vector3,
    vector3_up,
)
from render.model_showcase import ModelShowcase, ShowcaseOptions

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

ModelFactory = Callable[[Any], Any]
__pragma__("noskip")


class StageCameraLook:
    """The stage camera: its angles, horizontal field of view, framing margin and target height."""

    def __init__(
        self,
        alpha: float,
        beta: float,
        horizontal_fov: float,
        framing_margin: float,
        target_y: float,
    ) -> None:
        self.alpha = alpha
        self.beta = beta
        self.horizontal_fov = horizontal_fov
        self.framing_margin = framing_margin
        self.target_y = target_y


class StageLightsLook:
    """The stage lights: ambient, the highlighted ship's key light, and the rim light."""

    def __init__(
        self,
        ambient_intensity: float,
        spot_intensity: float,
        spot_direction: list[float],
        rim_intensity: float,
        rim_direction: list[float],
    ) -> None:
        self.ambient_intensity = ambient_intensity
        self.spot_intensity = spot_intensity
        self.spot_direction = spot_direction
        self.rim_intensity = rim_intensity
        self.rim_direction = rim_direction


class StageRingLook:
    """The neon ring under the highlighted ship."""

    def __init__(self, diameter: float, thickness: float, y: float, color: list[float]) -> None:
        self.diameter = diameter
        self.thickness = thickness
        self.y = y
        self.color = color


class ShipSelectStageOptions(ShowcaseOptions):
    """Layout and look of a `ShipSelectStage`."""

    def __init__(  # noqa: PLR0913, PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        spacing: float,
        rotation_speed_rad_per_sec: float,
        highlight_scale: float,
        dim_scale: float,
        scale_ease_per_sec: float,
        camera: StageCameraLook,
        lights: StageLightsLook,
        ring: StageRingLook,
    ) -> None:
        super().__init__(spacing, rotation_speed_rad_per_sec)
        self.highlight_scale = highlight_scale
        self.dim_scale = dim_scale
        self.scale_ease_per_sec = scale_ease_per_sec
        self.camera = camera
        self.lights = lights
        self.ring = ring


def _vec(values: list[float]) -> Any:
    return vector3(values[0], values[1], values[2])


class ShipSelectStage:
    """The ship select stage: the showcase, its camera, its lights and the neon ring."""

    def __init__(
        self, scene: Any, factories: list[ModelFactory], options: ShipSelectStageOptions
    ) -> None:
        self.scene = scene
        self._options = options
        self._selected = 0
        self.showcase = ModelShowcase(scene, factories, options)
        self.camera = self._create_camera()
        lights = options.lights
        ambient = new_hemispheric_light("ship-select-ambient", vector3_up(), scene)
        ambient.intensity = lights.ambient_intensity
        rim = new_directional_light("ship-select-rim", _vec(lights.rim_direction), scene)
        rim.intensity = lights.rim_intensity
        # P13-R02: one light per ship, so highlighting another ship only turns lights on and off:
        # no mesh's lights change, and no shader is compiled again.
        self._spots: list[Any] = []
        for i in range(len(self.showcase.pivots)):
            spot = new_directional_light(
                "ship-select-spot-" + str(i),
                _vec(lights.spot_direction),
                scene,
            )
            spot.includedOnlyMeshes = child_meshes(self.showcase.pivots[i], False)
            spot.intensity = 0
            self._spots.append(spot)
        self.ring = self._create_ring()
        self.select(0)
        for pivot in self.showcase.pivots:
            pivot.scaling.setAll(self._target_scale(pivot))

    @property
    def spot(self) -> Any:
        """The key light of the highlighted ship."""
        spot = self._spots[self._selected] if self._selected < len(self._spots) else None
        if not spot:
            raise ValueError("The ship select stage has no ship")
        return spot

    @property
    def selected(self) -> int:
        """Index of the highlighted ship."""
        return self._selected

    def select(self, index: int) -> None:
        """Highlights ship `index` (clamped to the available ships)."""
        pivots = self.showcase.pivots
        self._selected = min(max(0, index), len(pivots) - 1)
        if self._selected >= len(pivots):
            return
        pivot = pivots[self._selected]
        for i in range(len(self._spots)):
            self._spots[i].intensity = (
                self._options.lights.spot_intensity if i == self._selected else 0
            )
        self.ring.position.x = pivot.position.x

    def update(self, dt_seconds: float) -> None:
        """Rotates the ships and eases their scales towards the highlight state."""
        self.showcase.update(dt_seconds)
        ease = 1 - math.exp(-self._options.scale_ease_per_sec * dt_seconds)
        for pivot in self.showcase.pivots:
            current = pivot.scaling.x
            pivot.scaling.setAll(current + (self._target_scale(pivot) - current) * ease)

    def _target_scale(self, pivot: Any) -> float:
        is_selected = self.showcase.pivots[self._selected] is pivot
        return self._options.highlight_scale if is_selected else self._options.dim_scale

    def _create_camera(self) -> Any:
        camera_look = self._options.camera
        horizontal_fov = camera_look.horizontal_fov
        radius = ((self.showcase.width / 2) * camera_look.framing_margin) / math.tan(
            horizontal_fov / 2
        )
        target = vector3(0, camera_look.target_y, 0)
        camera = new_arc_rotate_camera(
            "ship-select-camera",
            camera_look.alpha,
            camera_look.beta,
            radius,
            target,
            self.scene,
        )
        camera.fovMode = camera_fov_mode_horizontal_fixed()
        camera.fov = horizontal_fov
        return camera

    def _create_ring(self) -> Any:
        ring_look = self._options.ring
        ring = create_torus(
            "ship-select-ring",
            ring_look.diameter,
            ring_look.thickness,
            48,
            self.scene,
        )
        ring.position.y = ring_look.y
        mat = new_standard_material("ship-select-ring", self.scene)
        mat.emissiveColor = color3(ring_look.color[0], ring_look.color[1], ring_look.color[2])
        mat.diffuseColor = color3_black()
        mat.specularColor = color3_black()
        mat.disableLighting = True
        ring.material = mat
        return ring
