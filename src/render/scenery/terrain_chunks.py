"""The terrain as a row of chunks along Z (P04-R01, ENG-19), ported from
`render/scenery/terrain-chunks.ts`: only the chunks under the camera exist, and the meshes of
chunks that scroll out of view are reused for new ones.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    apply_vertex_data_updatable,
    new_mesh,
    new_vertex_data,
    set_enabled,
    update_vertices_data,
    vertex_buffer_kind,
)
from render.scenery.terrain_geometry import (
    TerrainGrid,
    build_grid_indices,
    build_terrain_geometry,
)

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

__pragma__("noskip")


class TerrainChunkOptions:
    """Size of the terrain chunks: `length` along Z, the grid `cell` size, and the chunks span X
    from `x_min` over `columns` cells."""

    def __init__(self, length: float, cell: float, x_min: float, columns: int) -> None:
        # `length_`: Transcrypt cannot assign an attribute named `length`.
        self.length_ = length
        self.cell = cell
        self.x_min = x_min
        self.columns = columns


class ChunkSpan:
    """Index and Z range of one chunk."""

    def __init__(self, index: int, z_min: float, z_max: float) -> None:
        self.index = index
        self.z_min = z_min
        self.z_max = z_max


class ChunkChanges:
    """What `TerrainChunks.cover` changed: the `added` spans and the `removed` indices."""

    def __init__(self, added: list[ChunkSpan], removed: list[int]) -> None:
        self.added = added
        self.removed = removed


def _empty_map() -> Any:
    """An empty JavaScript `Map` (insertion order, as the TypeScript one)."""
    __pragma__("js", "{}", "return new Map();")
    return None


class TerrainChunks:
    """The terrain as a row of chunks along Z (P04-R01): only the chunks under the camera exist,
    and the meshes of chunks that scroll out of view are reused for new ones (ENG-19).

    The live chunks are kept in a JavaScript `Map` (insertion order), as the TypeScript one."""

    def __init__(
        self,
        scene: Any,
        material: Any,
        options: TerrainChunkOptions,
        source: Any,
        on_mesh: Callable[[Any], None] | None = None,
    ) -> None:
        """`on_mesh` is called once for each new mesh (e.g. to make it cast shadows)."""
        self.scene = scene
        self.material = material
        self.options = options
        self.source = source
        self.on_mesh = on_mesh
        self._live: Any = _empty_map()
        self._free: list[Any] = []
        self._created = 0
        self._rows = max(1, math.floor(options.length_ / options.cell + 0.5))
        self._indices = build_grid_indices(options.columns, self._rows)

    @property
    def count(self) -> int:
        """Number of chunks in the scene."""
        return _map_size(self._live)

    @property
    def meshes(self) -> Any:
        """The chunk meshes in use, by chunk index."""
        return self._live

    def span(self, index: int) -> ChunkSpan:
        """Index and Z range of chunk `index`."""
        z_min = index * self.options.length_
        return ChunkSpan(index, z_min, z_min + self.options.length_)

    def cover(self, z_min: float, z_max: float) -> ChunkChanges:
        """Keeps exactly the chunks that overlap [z_min, z_max]."""
        first = math.floor(z_min / self.options.length_)
        last = math.floor(z_max / self.options.length_)
        removed: list[int] = []
        for index in _map_keys(self._live):
            if index < first or index > last:
                mesh = _map_get(self._live, index)
                set_enabled(mesh, False)
                self._free.append(mesh)
                _map_delete(self._live, index)
                removed.append(index)
        added: list[ChunkSpan] = []
        for index in range(first, last + 1):
            if not _map_has(self._live, index):
                mesh = self._free.pop() if len(self._free) > 0 else self._new_mesh()
                _map_set(self._live, index, self._fill(mesh, index))
                added.append(self.span(index))
        return ChunkChanges(added, removed)

    def rebuild(self, source: Any) -> None:
        """Rebuilds every chunk from a new height source (e.g. a new seed)."""
        self.source = source
        for index in _map_keys(self._live):
            self._fill(_map_get(self._live, index), index)

    def _grid(self, index: int) -> TerrainGrid:
        options = self.options
        return TerrainGrid(
            options.x_min,
            self.span(index).z_min,
            options.columns,
            self._rows,
            options.cell,
        )

    def _new_mesh(self) -> Any:
        mesh = new_mesh("terrain-chunk-" + str(self._created), self.scene)
        self._created += 1
        geometry = build_terrain_geometry(self.source, self._grid(0))
        data = new_vertex_data()
        data.positions = geometry.positions
        data.normals = geometry.normals
        data.colors = geometry.colors
        data.indices = self._indices
        apply_vertex_data_updatable(data, mesh)
        mesh.material = self.material
        mesh.isPickable = False
        mesh.receiveShadows = True
        if self.on_mesh is not None:
            self.on_mesh(mesh)
        return mesh

    def _fill(self, mesh: Any, index: int) -> Any:
        geometry = build_terrain_geometry(self.source, self._grid(index))
        update_vertices_data(mesh, vertex_buffer_kind("PositionKind"), geometry.positions)
        update_vertices_data(mesh, vertex_buffer_kind("NormalKind"), geometry.normals)
        update_vertices_data(mesh, vertex_buffer_kind("ColorKind"), geometry.colors)
        mesh.refreshBoundingInfo()
        set_enabled(mesh, True)
        return mesh


def _map_size(cache: Any) -> int:
    __pragma__("js", "{}", "return cache.size;")
    return 0


def _map_keys(cache: Any) -> list[Any]:
    """The keys of a JavaScript `Map`, as a list (a copy: safe to change the map while looping)."""
    __pragma__("js", "{}", "return Array.from(cache.keys());")
    return []


def _map_get(cache: Any, key: Any) -> Any:
    __pragma__("js", "{}", "return cache.get(key);")
    return None


def _map_has(cache: Any, key: Any) -> bool:
    __pragma__("js", "{}", "return cache.has(key);")
    return False


def _map_set(cache: Any, key: Any, value: Any) -> None:
    __pragma__("js", "{}", "cache.set(key, value);")


def _map_delete(cache: Any, key: Any) -> None:
    __pragma__("js", "{}", "cache.delete(key);")
