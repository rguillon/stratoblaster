"""Imposters (D-211): models drawn as a picture of themselves, baked once into an atlas, one frame
per heading, as the tilted playfield camera sees them. Pure: the atlas' layout, the geometry the
pictures are baked from and the quads that show them. The bake itself needs WebGL
(`imposter_bake_visual.py`).

The camera looks down the playfield at `tilt` from straight down, towards +Z, never turning: so a
model's picture only depends on its heading. Frame `i` of a kind shows it turned `i / headings` of a
turn (as `PropPlacement.rotation`). In the atlas each kind has a row, each heading a column; row 0
is at the top.

The look (`ImposterLook`, a config record) has `headings` (frames per kind), `framePx` (pixels
across a frame), `frameSize` (model units across a frame) and `centre` (the height, in model units,
of the point at the middle of each frame) and `ambient` (how bright the faces turned from the bake's
light are, 0..1: D-212).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.gradient_shapes import ColoredGeometry
from render.geometry.textured import QuadBuilder, TexturedGeometry
from render.geometry.vec3 import plus

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# How the bake shades the models (their colours are drawn unlit): towards this light, from the
# look's `ambient` (D-212).
BAKE_LIGHT = [-0.35, 0.85, -0.4]
# How high the bottom of an imposter's quad stays over the ground.
QUAD_CLEARANCE = 0.05


def atlas_rows(kinds: int) -> int:
    """The rows of the atlas of `kinds` kinds: a power of two, so its texture is too."""
    rows = 1
    while rows < kinds:
        rows *= 2
    return rows


def atlas_size(look: Any, kinds: int) -> list[int]:  # noqa: ANN401 (a config record)
    """The atlas' `[width, height]` in pixels."""
    px: int = look.framePx
    headings: int = look.headings
    return [headings * px, atlas_rows(kinds) * px]


def frame_of(rotation: float, headings: int) -> int:
    """The frame (0..headings-1) nearest to the heading `rotation` (radians)."""
    turns = rotation / (math.pi * 2)
    i = math.floor((turns - math.floor(turns)) * headings + 0.5)
    return 0 if i >= headings else i


def frame_uv(look: Any, kinds: int, kind: int, frame: int) -> list[float]:  # noqa: ANN401
    """The `[u0, v0, u1, v1]` of frame `frame` of kind `kind` (V up: row 0 at the top)."""
    headings: int = look.headings
    rows = atlas_rows(kinds)
    return [frame / headings, 1 - (kind + 1) / rows, (frame + 1) / headings, 1 - kind / rows]


def view_axes(tilt: float) -> list[list[float]]:
    """The camera's `[right, up, towards]` unit vectors: across the screen, up it, and from the
    ground towards the camera."""
    return [
        [1, 0, 0],
        [0, math.sin(tilt), math.cos(tilt)],
        [0, math.cos(tilt), -math.sin(tilt)],
    ]


def frame_centre(look: Any, kinds: int, at: list[int], tilt: float) -> list[float]:  # noqa: ANN401
    """Where, round the origin of the bake, frame `at[1]` of kind `at[0]` is centred: the frames
    side by side in the camera's plane, as in the atlas."""
    axes = view_axes(tilt)
    size: float = look.frameSize
    headings: int = look.headings
    rows = atlas_rows(kinds)
    across = (at[1] + 0.5 - headings / 2) * size
    up = (rows / 2 - at[0] - 0.5) * size
    return plus(plus([0, 0, 0], axes[0], across), axes[1], up)


def _shade(normal: list[float], ambient: float) -> float:
    """How bright a face of `normal` is baked (towards BAKE_LIGHT, from `ambient`)."""
    lx = BAKE_LIGHT[0]
    ly = BAKE_LIGHT[1]
    lz = BAKE_LIGHT[2]
    length = math.sqrt(lx * lx + ly * ly + lz * lz)
    n = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
    if n == 0:
        return 1
    dot = (normal[0] * lx + normal[1] * ly + normal[2] * lz) / (length * n)
    return ambient + (1 - ambient) * max(0, dot)


def _face_normal(p: list[float], i: int, j: int, k: int) -> list[float]:
    """The normal of the triangle `i, j, k` of positions `p`, as Babylon's front face sees it."""
    ax = p[j * 3] - p[i * 3]
    ay = p[j * 3 + 1] - p[i * 3 + 1]
    az = p[j * 3 + 2] - p[i * 3 + 2]
    bx = p[k * 3] - p[i * 3]
    by = p[k * 3 + 1] - p[i * 3 + 1]
    bz = p[k * 3 + 2] - p[i * 3 + 2]
    # Babylon's front faces have the normal (c - a) × (b - a), that is (b - a) × (c - a) negated:
    # with u = b - a and v = c - a, the normal is v × u.
    return [by * az - bz * ay, bz * ax - bx * az, bx * ay - by * ax]


def add_baked(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    out: ColoredGeometry,
    model: ColoredGeometry,
    yaw: float,
    centre: list[float],
    look: Any,  # noqa: ANN401
) -> None:
    """Adds `model` to `out`, turned `yaw` round Y and moved so its point at height
    `look.centre` lies at `centre`, its colours shaded by the bake's light (each face has its own
    vertices: `SolidBuilder`'s flat shading)."""
    c = math.cos(yaw)
    s = math.sin(yaw)
    base = len(out.positions) // 3
    positions = model.positions
    count = len(positions) // 3
    turned: list[float] = []
    for v in range(count):
        x = positions[v * 3]
        z = positions[v * 3 + 2]
        # The yaw of `Placement` and of the instances (`RotationYawPitchRoll`).
        turned.extend(
            [
                centre[0] + x * c + z * s,
                centre[1] + positions[v * 3 + 1] - look.centre,
                centre[2] - x * s + z * c,
            ]
        )
    # A loop: Transcrypt has no list repetition (`[1.0] * count`).
    shades: list[float] = [1.0 for _ in range(count)]
    indices = model.indices
    ambient: float = look.ambient
    for t in range(0, len(indices), 3):
        shade = _shade(_face_normal(turned, indices[t], indices[t + 1], indices[t + 2]), ambient)
        for k in range(3):
            shades[indices[t + k]] = shade
    out.positions.extend(turned)
    colors = model.colors
    for v in range(count):
        f = shades[v]
        out.colors.extend([colors[v * 4] * f, colors[v * 4 + 1] * f, colors[v * 4 + 2] * f, 1])
    for i in indices:
        out.indices.append(base + i)


def bake_geometry(models: list[ColoredGeometry], look: Any, tilt: float) -> ColoredGeometry:  # noqa: ANN401
    """Every frame of every model (`models`, by kind) side by side round the origin, as the bake
    camera draws them into the atlas."""
    out = ColoredGeometry()
    headings: int = look.headings
    for k in range(len(models)):
        for i in range(headings):
            centre = frame_centre(look, len(models), [k, i], tilt)
            add_baked(out, models[k], (i / headings) * math.pi * 2, centre, look)
    return out


def quad_lift(look: Any, tilt: float) -> float:  # noqa: ANN401 (a config record)
    """How far towards the camera a quad is moved (model units), so its bottom stays over the
    ground: on the line of sight, which does not move it on screen."""
    half: float = look.frameSize / 2
    centre: float = look.centre
    low = centre - half * math.sin(tilt)
    if low >= QUAD_CLEARANCE:
        return 0
    return (QUAD_CLEARANCE - low) / math.cos(tilt)


def imposter_quad(look: Any, tilt: float, uv: list[float]) -> TexturedGeometry:  # noqa: ANN401
    """The quad that shows the frame at `uv`, in model units round a model standing at the
    origin: facing the camera, through the frame's centre point, moved towards the camera by
    `quad_lift`."""
    axes = view_axes(tilt)
    right = axes[0]
    up = axes[1]
    middle = plus([0, look.centre, 0], axes[2], quad_lift(look, tilt))
    half: float = look.frameSize / 2
    low = plus(middle, up, -half)
    high = plus(middle, up, half)
    quads = QuadBuilder()
    # The corners run clockwise in Babylon's convention (`QuadBuilder` assumes the other way), so
    # the quad's triangles are turned round: their front faces then look at the camera.
    quads.quad(
        [
            plus(low, right, half),
            plus(high, right, half),
            plus(high, right, -half),
            plus(low, right, -half),
        ],
        uv,
        [1, 1, 1],
    )
    indices = quads.geometry.indices
    for t in range(0, len(indices), 3):
        swap = indices[t + 1]
        indices[t + 1] = indices[t + 2]
        indices[t + 2] = swap
    return quads.geometry
