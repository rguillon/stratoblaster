"""Cloud layers of a scenery stage (P04-R03, P08-R04): planes under the flight altitude that follow
the camera and drift, each with its own material.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import create_ground, set_enabled
from render.scenery.scenery_kit import CloudState, FogState

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Group of all but the clouds, drawn next: a glow composed after it stays under them.
BELOW_CLOUDS_GROUP = 0
# Group of what flies above the clouds (the ships), drawn last and keeping the depth: neither the
# clouds nor a glow composed after the ground draw over it (phase 4 review).
ABOVE_CLOUDS_GROUP = BELOW_CLOUDS_GROUP + 2


class CloudLayerState:
    """A cloud layer's live settings (P04-R03)."""

    def __init__(self, enabled: bool, coverage: float, opacity: float) -> None:
        self.enabled = enabled
        self.coverage = coverage
        self.opacity = opacity


class CloudLayer:
    """One cloud layer: its look, the Z of the middle of what the camera sees at its altitude,
    its mesh, its material and its live state."""

    def __init__(
        self, look: Any, middle: float, mesh: Any, material: Any, state: CloudLayerState
    ) -> None:
        self.look = look
        self.middle = middle
        self.mesh = mesh
        self.material = material
        self.state = state


def build_cloud_layer(
    scene: Any, look: Any, material: Any, index: int, placement: tuple[Any, float, float]
) -> CloudLayer:
    """Cloud layer number `index` (P04-R03): a plane at `altitude` covering what the camera sees
    there (`seen`) and `margin` more, drawn after everything else. `placement` is
    `(seen, altitude, margin)`."""
    seen, altitude, margin = placement
    mesh = create_ground(
        "cloud-layer-" + str(index),
        2 * (seen.half_width + margin),
        seen.z_far - seen.z_near + 2 * margin,
        1,
        scene,
    )
    mesh.position.y = altitude
    mesh.material = material.material
    mesh.isPickable = False
    mesh.renderingGroupId = BELOW_CLOUDS_GROUP + 1
    # Lower layers are drawn first, after the sea.
    mesh.alphaIndex = index + 1
    return CloudLayer(
        look,
        (seen.z_near + seen.z_far) / 2,
        mesh,
        material,
        CloudLayerState(True, look.coverage, look.opacity),
    )


def update_cloud_layer(
    layer: CloudLayer, camera_time: tuple[float, float], frame: tuple[Any, Any, bool]
) -> None:
    """Follows the camera at `camera_time[0]`, drifts with `camera_time[1]`, and takes the colours
    of `cover` and the haze of `atmosphere` (P08-R04); its coverage and opacity too when `follow`
    (a level whose look changes), otherwise they stay as set on its state (set by code).
    `frame` is `(atmosphere, cover, follow)`; `cover` may be missing (None)."""
    camera_z, time = camera_time
    atmosphere, cover, follow = frame
    look = layer.look
    mesh = layer.mesh
    material = layer.material
    state = layer.state
    if follow and cover:
        state.coverage = cover.coverage
        state.opacity = cover.opacity
    mesh.position.z = camera_z + layer.middle
    visible = state.enabled and state.coverage > 0 and state.opacity > 0
    set_enabled(mesh, visible)
    color = cover.color if cover else look.color
    shade = cover.shade if cover else look.shade
    fog = FogState(atmosphere.sky.haze, atmosphere.fog.start, atmosphere.fog.end)
    material.set(
        CloudState(
            state.coverage,
            state.opacity,
            color,
            shade,
            fog,
            look.drift[0] * time,
            look.drift[1] * time,
        )
    )
