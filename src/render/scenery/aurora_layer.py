"""The aurora of a scenery stage (P08-R04, 2-5 at night): slow green and violet curtains over the
scene, on a sheet high above the ground.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import create_ground, set_enabled
from render.scenery.cloud_layers import BELOW_CLOUDS_GROUP

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any, Protocol  # noqa: E402

__pragma__("noskip")

# Draw order: after the clouds and the weather.
AURORA_ALPHA_INDEX = 5


class AuroraFrame:
    """What the aurora shows on one frame."""

    def __init__(self, time: float, strength: float, camera_position: Any, fog: Any) -> None:
        self.time = time
        self.strength = strength
        self.camera_position = camera_position
        self.fog = fog


__pragma__("skip")


class AuroraMaterial(Protocol):
    """The aurora's material, driven frame by frame."""

    material: Any

    def set(self, frame: AuroraFrame) -> None: ...


__pragma__("noskip")


class AuroraLayer:
    """An aurora (P08-R04): slow green and violet curtains added over the scene from a sheet high
    above the ground, faint near the camera and strongest in the far haze at the top of the
    screen. Shown only while the atmosphere has one; it never flashes."""

    def __init__(self, scene: Any, material: Any, placement: tuple[Any, float, float]) -> None:
        """`material` is an `AuroraMaterial`; `placement` is `(seen, altitude, margin)`."""
        seen, altitude, margin = placement
        self.mesh = create_ground(
            "aurora",
            2 * (seen.half_width + margin),
            seen.z_far - seen.z_near + 2 * margin,
            1,
            scene,
        )
        self.mesh.position.y = altitude
        self.mesh.material = material.material
        self.mesh.isPickable = False
        self.mesh.renderingGroupId = BELOW_CLOUDS_GROUP + 1
        self.mesh.alphaIndex = AURORA_ALPHA_INDEX
        set_enabled(self.mesh, False)
        self._material = material
        self._middle = (seen.z_near + seen.z_far) / 2

    def update(self, atmosphere: Any, time: float, camera_position: Any) -> None:
        """Follows the camera and shows the aurora of `atmosphere`, if any."""
        strength = atmosphere.aurora
        set_enabled(self.mesh, strength > 0)
        if strength <= 0:
            return
        self.mesh.position.z = camera_position.z + self._middle
        self._material.set(AuroraFrame(time, strength, camera_position, atmosphere.fog))
