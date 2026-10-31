"""Unit tests of `src/render/scenery/terrain_geometry.py`."""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import patch_babylon
from helpers.render_geometry import babylon_normal, triangles

from core.scenery.ground_fit import SampledGround
from render.scenery import terrain_geometry
from render.scenery.terrain_geometry import (
    SURFACE_SCALE,
    TerrainGrid,
    build_grid_indices,
    build_terrain_geometry,
)


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, terrain_geometry)


class Slope:
    """Ground that rises by `rise` per unit of X, and has a given cover."""

    def __init__(self, rise: float = 0.0, cover: Any = None) -> None:
        self.rise = rise
        self.cover = cover

    def height(self, x: float, z: float) -> float:
        return self.rise * x

    def surface(self, z: float) -> Any:
        return self.cover


def test_a_flat_grid_has_a_vertex_per_corner_and_straight_up_normals() -> None:
    geo = build_terrain_geometry(Slope(), TerrainGrid(0, 0, 2, 3, 1))
    assert len(geo.positions) == (2 + 1) * (3 + 1) * 3
    assert len(geo.normals) == len(geo.positions)
    assert len(geo.colors) == (2 + 1) * (3 + 1) * 4
    for i in range(0, len(geo.normals), 3):
        assert geo.normals[i : i + 3] == pytest.approx([0, 1, 0])


def test_vertices_sit_on_the_grid_at_the_sampled_height() -> None:
    geo = build_terrain_geometry(Slope(rise=2), TerrainGrid(10, 5, 2, 1, 4))
    # The first row: x = 10, 14, 18 at heights 2x.
    assert geo.positions[0:3] == pytest.approx([10, 20, 5])
    assert geo.positions[3:6] == pytest.approx([14, 28, 5])
    assert geo.positions[6:9] == pytest.approx([18, 36, 5])


def test_the_normal_of_a_slope_tilts_against_it() -> None:
    geo = build_terrain_geometry(Slope(rise=1), TerrainGrid(0, 0, 2, 1, 1))
    nx, ny, nz = geo.normals[3:6]
    assert nx < 0 and ny > 0
    assert nz == pytest.approx(0)
    assert nx**2 + ny**2 + nz**2 == pytest.approx(1)


def test_the_ground_cover_goes_into_the_vertex_colours() -> None:
    cover = SimpleNamespace(lush=1, sandy=0.5, paved=0)
    geo = build_terrain_geometry(Slope(cover=cover), TerrainGrid(0, 0, 1, 1, 1))
    assert geo.colors[0:4] == pytest.approx([1 - 1 * SURFACE_SCALE, 1 - 0.5 * SURFACE_SCALE, 1, 1])


def test_a_source_without_cover_is_bare_ground() -> None:
    class Bare:
        def height(self, x: float, z: float) -> float:
            return 0

    geo = build_terrain_geometry(Bare(), TerrainGrid(0, 0, 1, 1, 1))
    assert geo.colors[0:4] == [1, 1, 1, 1]


def test_grid_triangles_face_up() -> None:
    indices = build_grid_indices(2, 2)
    assert len(indices) == 2 * 2 * 6
    flat = list(range(9))  # Only the corner positions matter for the orientation.
    positions = [0.0] * (9 * 3)
    for i in range(9):
        x, z = i % 3, i // 3
        positions[i * 3 : i * 3 + 3] = [x, 0, z]
    for tri in triangles(positions, list(indices)):
        assert babylon_normal(tri)[1] > 0
    assert flat[-1] == 8


class Bumps:
    """Ground that no plane fits: a sum of sines."""

    def height(self, x: float, z: float) -> float:
        return 10 * math.sin(x * 0.37) + 7 * math.cos(z * 0.23) + 0.05 * x * z


def _height_on(tris: list[Any], x: float, z: float) -> float:
    """The height of the triangles (seen from above) over (`x`, `z`)."""
    for a, b, c in tris:
        den = (b[2] - c[2]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[2] - c[2])
        wa = ((b[2] - c[2]) * (x - c[0]) + (c[0] - b[0]) * (z - c[2])) / den
        wb = ((c[2] - a[2]) * (x - c[0]) + (a[0] - c[0]) * (z - c[2])) / den
        wc = 1 - wa - wb
        if min(wa, wb, wc) >= -1e-9:
            return float(wa * a[1] + wb * b[1] + wc * c[1])
    raise AssertionError("no triangle over (" + str(x) + ", " + str(z) + ")")


def test_d212_the_trees_stand_on_the_mesh_drawn() -> None:
    # The terrain of a chunk on the multiples of 8, and the ground a tree cell samples there (cell
    # 50 less the margin of 8, as `PropPlacer._trees` asks): off the grid, with the mesh's cell.
    cell = 8
    field = Bumps()
    grid = TerrainGrid(-80, -96, 30, 30, cell)
    geo = build_terrain_geometry(field, grid)
    tris = triangles(list(geo.positions), list(build_grid_indices(grid.columns, grid.rows)))
    ground = SampledGround(field, 42.0, -58.0, 66.0, cell)
    for k in range(60):
        x = 42.0 + k * 1.09
        z = -58.0 + ((k * 7) % 60) * 1.07
        assert ground.height(x, z) == pytest.approx(_height_on(tris, x, z))
