"""Vertex data of the terrain grid (P04-R01, ENG-19)

Ground cover is stored in the terrain's vertex colours: red = 1 - lush x SURFACE_SCALE,
green = 1 - sandy x SURFACE_SCALE, blue = 1 - paved x SURFACE_SCALE. The arrays are typed
(Float32, Uint32), so the values round the same way.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import float32_array, uint32_array

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any, Protocol  # noqa: E402


class HeightSource(Protocol):
    """Anything that gives a ground height at (x, z), e.g. a `HeightField`. `surface(z)` gives the
    ground cover at `z` (optional)."""

    def height(self, x: float, z: float) -> float: ...


__pragma__("noskip")

# Ground cover is stored in the vertex colours with this scale (see the module docstring).
SURFACE_SCALE = 0.5


class TerrainGrid:
    """A rectangular grid of ground, `columns` x `rows` cells of `cell` world units, from
    (`x_min`, `z_min`)."""

    def __init__(self, x_min: float, z_min: float, columns: int, rows: int, cell: float) -> None:
        self.x_min = x_min
        self.z_min = z_min
        self.columns = columns
        self.rows = rows
        self.cell = cell


class TerrainGeometry:
    """Vertex data of a terrain grid, ready for a mesh: `positions`, `normals` and `colors`
    (RGBA per vertex, with the ground cover)."""

    def __init__(self, positions: Any, normals: Any, colors: Any) -> None:
        self.positions = positions
        self.normals = normals
        self.colors = colors


def _hypot3(a: float, b: float, c: float) -> float:
    """`Math.hypot(a, b, c)`: JavaScript's rounding."""
    __pragma__("js", "{}", "return Math.hypot(a, b, c);")
    return 0


def build_terrain_geometry(source: Any, grid: TerrainGrid) -> TerrainGeometry:
    """Samples the ground on a grid and computes smooth normals from the neighbouring heights (one
    extra ring of samples around the grid, so neighbouring chunks get the same normals on their
    shared edge and the seam does not show)."""
    x_min = grid.x_min
    z_min = grid.z_min
    columns = grid.columns
    rows = grid.rows
    cell = grid.cell
    width = columns + 3
    heights = float32_array(width * (rows + 3))
    for r in range(-1, rows + 2):
        for c in range(-1, columns + 2):
            heights[(r + 1) * width + c + 1] = source.height(x_min + c * cell, z_min + r * cell)

    def at(c: int, r: int) -> float:
        value: float = heights[(r + 1) * width + c + 1]
        return value

    count = (columns + 1) * (rows + 1)
    positions = float32_array(count * 3)
    normals = float32_array(count * 3)
    colors = float32_array(count * 4)
    v = 0
    for r in range(0, rows + 1):
        cover = source.surface(z_min + r * cell) if hasattr(source, "surface") else None
        lush = cover.lush if cover is not None else 0
        paved = cover.paved if cover is not None else 0
        sandy = cover.sandy if (cover is not None and hasattr(cover, "sandy")) else 0
        color = [
            1 - lush * SURFACE_SCALE,
            1 - sandy * SURFACE_SCALE,
            1 - paved * SURFACE_SCALE,
            1,
        ]
        for c in range(0, columns + 1):
            colors.set(color, (r * (columns + 1) + c) * 4)
        for c in range(0, columns + 1):
            nx = at(c - 1, r) - at(c + 1, r)
            nz = at(c, r - 1) - at(c, r + 1)
            ny = 2 * cell
            length = _hypot3(nx, ny, nz)
            positions.set([x_min + c * cell, at(c, r), z_min + r * cell], v)
            normals.set([nx / length, ny / length, nz / length], v)
            v += 3
    return TerrainGeometry(positions, normals, colors)


def build_grid_indices(columns: int, rows: int) -> Any:
    """Triangle indices of a `columns` x `rows` grid (row-major vertices), front faces up."""
    indices = uint32_array(columns * rows * 6)
    i = 0
    for r in range(0, rows):
        for c in range(0, columns):
            a = r * (columns + 1) + c
            b = a + columns + 1
            # Babylon front faces have the normal (c - a) x (b - a): here +Y.
            indices.set([a, a + 1, b, a + 1, b + 1, b], i)
            i += 6
    return indices
