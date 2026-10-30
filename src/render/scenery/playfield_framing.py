"""Where the tilted camera stands relative to the playfield (P04-R05)

The playfield is a `screen`-sized rectangle on the flight plane: X across (centred on 0), Z along
the level from its bottom edge. The camera is tilted from straight down towards +Z.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.content.game_definition import LogicalScreen  # noqa: E402
from render.scenery.scenery_look import PlayfieldCameraLook  # noqa: E402

__pragma__("noskip")

DEG = math.pi / 180


class PlayfieldFraming:
    """Where the camera stands: `tilt` (radians), `half_fov` (half the vertical field of view,
    radians), `height` above the flight plane, `back` (camera Z relative to the playfield's bottom
    edge, negative: behind it) and `direction` (unit view direction (Y, Z); X is always 0)."""

    def __init__(
        self,
        tilt: float,
        half_fov: float,
        height: float,
        back: float,
        direction: tuple[float, float],
    ) -> None:
        self.tilt = tilt
        self.half_fov = half_fov
        self.height = height
        self.back = back
        self.direction = direction


class PlayfieldEyePoint:
    """Where the camera's eye is over the playfield: `x`, `y` and `height`."""

    def __init__(self, x: float, y: float, height: float) -> None:
        self.x = x
        self.y = y
        self.height = height


class GroundWindow:
    """The ground the camera can see, relative to the camera's Z: `z_near`, `z_far` and the
    half of the widest stretch of ground seen across X (`half_width`)."""

    def __init__(self, z_near: float, z_far: float, half_width: float) -> None:
        self.z_near = z_near
        self.z_far = z_far
        self.half_width = half_width


def frame_playfield(screen: LogicalScreen, look: PlayfieldCameraLook) -> PlayfieldFraming:
    """Frames a `screen`-sized playfield with a camera tilted by `look.tiltDeg`."""
    tilt = look.tiltDeg * DEG
    half_fov = (look.fovDeg * DEG) / 2
    if not (half_fov > 0) or tilt + half_fov >= math.pi / 2 or tilt - half_fov <= -math.pi / 2:
        raise ValueError("The camera must see the whole playfield below the horizon")
    height = screen.height / (math.tan(tilt + half_fov) - math.tan(tilt - half_fov))
    return PlayfieldFraming(
        tilt,
        half_fov,
        height,
        -height * math.tan(tilt - half_fov),
        (-math.cos(tilt), math.sin(tilt)),
    )


def playfield_eye(screen: LogicalScreen, framing: PlayfieldFraming) -> PlayfieldEyePoint:
    """Where the camera's eye is over a `screen`-sized playfield framed by `framing`: above the
    playfield's centre line, behind its bottom edge (enemy shots leave from the barrels it sees)."""
    return PlayfieldEyePoint(screen.width / 2, framing.back, framing.height)


def visible_ground(
    framing: PlayfieldFraming,
    aspect: float,
    camera_y: float,
    low: float,
    high: float,
) -> GroundWindow:
    """The ground the camera can see when the ground lies between heights `low` and `high`, for a
    screen of the given aspect ratio (width / height), with the camera `camera_y` high."""
    bottom_ray = math.tan(framing.tilt - framing.half_fov)
    top_ray = framing.tilt + framing.half_fov
    near_heights = [max(0, camera_y - high) * bottom_ray, max(0, camera_y - low) * bottom_ray]
    deepest = max(0, camera_y - low)
    # The far top corners: range along the top ray, then depth along the view axis.
    depth = (deepest / math.cos(top_ray)) * math.cos(framing.half_fov)
    return GroundWindow(
        min(near_heights[0], near_heights[1]),
        deepest * math.tan(top_ray),
        depth * math.tan(framing.half_fov) * aspect,
    )


def visible_half_width(framing: PlayfieldFraming, aspect: float, y: float) -> float:
    """Half of the playfield width seen on screen at height `y` of the playfield (logical pixels
    from its bottom edge), for a screen of the given aspect ratio (width / height). With the tilted
    camera, less of the playfield is seen at the bottom than at the top."""
    dy = framing.direction[0]
    dz = framing.direction[1]
    # Depth of the point (0, flight plane, y) along the view axis, from the camera.
    depth = -framing.height * dy + (y - framing.back) * dz
    return depth * math.tan(framing.half_fov) * aspect
