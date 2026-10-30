"""Road ribbons of the terrain chunks in view, one mesh per chunk (P04-R07). See-through meshes are
drawn by increasing `alphaIndex`: a field of paths with a lower one than the field of roads keeps
the roads on top where they meet.

Ported from `render/scenery/road-field.ts`. A chunk span is a `(z_min, z_max)` pair.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    apply_vertex_data,
    compute_normals,
    dispose_node,
    new_mesh,
    new_vertex_data,
    node_name,
    raw_rgba_texture,
    texture_trilinear_sampling_mode,
    update_raw_texture,
)
from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery.road_atlas import ATLAS_SIZE
from render.scenery.road_chunks import RoadChunk
from render.scenery.road_geometry import RoadLook, build_road_geometry

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Any  # noqa: E402

from core.scenery.road_types import Road  # noqa: E402
from core.scenery.scenery_level import TileRules  # noqa: E402
from render.scenery.terrain_geometry import HeightSource  # noqa: E402

__pragma__("noskip")

# Depth offset of the opaque middles of the streets: pulled towards the camera less than the
# see-through ribbons and lane markings (-2), which stay on top of them.
STREET_Z_OFFSET = -1

# Draw order of the see-through road ribbons: before the sea (0) and the clouds.
DRAW_ORDER_PATHS = -2
DRAW_ORDER_ROADS = -1

# Keys of the lists and functions that hold their cached results (a WeakMap keyed by the list).
_SPLIT_SLOT = "render_road_split"
_WINDING_SLOT = "render_road_winding"


def _slot_get(owner: Any, slot: str) -> Any:
    """The value kept on `owner` under `slot`, or undefined (a WeakMap entry keyed by the list)."""
    __pragma__("js", "{}", "return owner[slot];")
    return None


def _slot_set(owner: Any, slot: str, value: Any) -> None:
    __pragma__("js", "{}", "owner[slot] = value;")


class RoadField:
    """Road ribbons of one kind, one mesh per terrain chunk (by chunk index, in insertion
    order)."""

    def __init__(
        self,
        scene: Any,
        material: Any,
        name: str,
        alpha_index: int,
        see_through: bool = True,
    ) -> None:
        """`alpha_index`: draw order among the see-through meshes (the sea is 0, clouds above).
        `see_through`: whether the ribbons fade with their vertex alpha (else they are drawn
        opaque)."""
        self._scene = scene
        self._material = material
        self._name = name
        self._alpha_index = alpha_index
        self._see_through = see_through
        self._indices: list[int] = []
        self._meshes: list[Any] = []

    @property
    def count(self) -> int:
        """Number of chunks with roads."""
        return len(self._meshes)

    def _position(self, index: int) -> int:
        for i in range(len(self._indices)):
            if self._indices[i] == index:
                return i
        return -1

    def mesh(self, index: int) -> Any:
        """The mesh of chunk `index`, if it has one."""
        i = self._position(index)
        return self._meshes[i] if i >= 0 else None

    def set_chunk(self, index: int, geometry: ColoredGeometry) -> None:
        """Makes (or replaces) the mesh of chunk `index` from `geometry`."""
        self.remove_chunk(index)
        if len(geometry.indices) == 0:
            return
        mesh = new_mesh(self._name + "-" + str(index), self._scene)
        data = new_vertex_data()
        data.positions = geometry.positions
        data.indices = geometry.indices
        data.colors = geometry.colors
        if hasattr(geometry, "uvs"):
            data.uvs = geometry.uvs
        normals = compute_normals(geometry.positions, geometry.indices)
        data.normals = normals
        apply_vertex_data(data, mesh)
        mesh.material = self._material
        mesh.isPickable = False
        mesh.receiveShadows = True
        # The roads fade into the ground with their vertex alpha.
        mesh.hasVertexAlpha = self._see_through
        mesh.alphaIndex = self._alpha_index
        self._indices.append(index)
        self._meshes.append(mesh)

    def remove_chunk(self, index: int) -> None:
        i = self._position(index)
        if i >= 0:
            dispose_node(self._meshes[i])
            self._indices.pop(i)
            self._meshes.pop(i)

    def clear(self) -> None:
        for index in list(self._indices):
            self.remove_chunk(index)


class SplitRoads:
    """The paths and the other roads of a list of roads, and whether all are streets."""

    def __init__(self, paths: list[Road], roads: list[Road], streets_only: bool) -> None:
        self.paths = paths
        self.roads = roads
        self.streets_only = streets_only


def _split_roads(roads: Sequence[Road]) -> SplitRoads:
    """The roads split once per list (P13-R04)."""
    split = _slot_get(roads, _SPLIT_SLOT)
    if not split:
        paths = [r for r in roads if r.kind == "cross"]
        others = [r for r in roads if r.kind != "cross"]
        streets_only = True
        for r in roads:
            if r.kind != "street":
                streets_only = False
        split = SplitRoads(paths, others, streets_only)
        _slot_set(roads, _SPLIT_SLOT, split)
    result: SplitRoads = split
    return result


def _opaque_of(material: Any) -> Any:
    """The road material, opaque: written in depth, so the terrain under it is not shaded."""
    cloned = material.clone(node_name(material) + "-opaque")
    opaque = cloned if cloned else material
    opaque.disableDepthWrite = False
    opaque.zOffset = STREET_Z_OFFSET
    return opaque


class RoadLayers:
    """The ribbons of the paths and of the main roads, in two fields: the paths are drawn first, so
    the roads stay on top where they meet (phase 4 review). Where all the roads are streets, the
    even middles of the streets are a third field, drawn opaque before the see-through ones and
    hiding the terrain under them (reviewer, 2026-10-28); their soft edges and markings stay in the
    roads' field, drawn over them. Elsewhere a street drawn before a road or a path would end up
    under it.

    Phase 15 (experiment): the street pieces are textured surfaces, one atlas per road look, and
    `show_tile_grid` draws the grid of tiles over the districts."""

    def __init__(self, scene: Any, material: Any) -> None:
        self._scene = scene
        self._material = material
        self._paths = RoadField(scene, material, "paths", DRAW_ORDER_PATHS)
        self._roads = RoadField(scene, material, "roads", DRAW_ORDER_ROADS)
        self._streets = RoadField(scene, _opaque_of(material), "streets", 0, False)
        self._surface_material = _opaque_of(material)
        self._surfaces = RoadField(scene, self._surface_material, "street-surfaces", 0, False)
        self._grid: RoadField | None = None
        self._atlas_texture: Any = None

    def _show_atlas(self, pixels: Any) -> None:
        """The road atlas's pixels on the surfaces' texture: made once, then updated."""
        if self._atlas_texture is None:
            texture = raw_rgba_texture(
                pixels,
                ATLAS_SIZE,
                self._scene,
                True,
                False,
                texture_trilinear_sampling_mode(),
            )
            texture.anisotropicFilteringLevel = 8
            self._atlas_texture = texture
            self._surface_material.diffuseTexture = texture
        else:
            update_raw_texture(self._atlas_texture, pixels)

    @property
    def count(self) -> int:
        """Number of chunks with road ribbons."""
        return max(self._roads.count, self._paths.count)

    def streets_of(self, index: int) -> Any:
        """The opaque middles of the streets of a chunk, if drawn apart."""
        return self._streets.mesh(index)

    def set_chunk(
        self,
        index: int,
        roads: list[Road],
        ground: HeightSource,
        span: tuple[float, float],
        look: RoadLook,
        tiles: TileRules | None = None,
    ) -> None:
        """Ribbons of the segments of `roads` that start in the chunk's Z range (`span`); with
        `tiles` (phase 15), the streets are road pieces on the grid instead, opaque."""
        if tiles is not None and look.tiles is not None:
            self._set_tile_ribbons(index, roads, ground, span, look)
            return
        split = _split_roads(roads)
        z_min, z_max = span
        self._paths.set_chunk(index, build_road_geometry(split.paths, ground, z_min, z_max, look))
        # Main roads and streets, the middles of the streets apart if they are all there is.
        middles = ColoredGeometry() if split.streets_only else None
        self._roads.set_chunk(
            index, build_road_geometry(split.roads, ground, z_min, z_max, look, middles)
        )
        if middles is not None:
            self._streets.set_chunk(index, middles)
        else:
            self._streets.remove_chunk(index)

    def _set_tile_ribbons(
        self,
        index: int,
        roads: list[Road],
        ground: HeightSource,
        span: tuple[float, float],
        look: RoadLook,
    ) -> None:
        """The paths and the other roads of a chunk (the tile path's ribbons); its street surfaces
        come with `set_tile_chunk`."""
        split = _split_roads(roads)
        others = _slot_get(roads, _WINDING_SLOT)
        if not others:
            others = [r for r in split.roads if r.kind != "street"]
        _slot_set(roads, _WINDING_SLOT, others)
        z_min, z_max = span
        self._paths.set_chunk(index, build_road_geometry(split.paths, ground, z_min, z_max, look))
        self._roads.set_chunk(index, build_road_geometry(others, ground, z_min, z_max, look))

    def set_tile_chunk(self, index: int, chunk: RoadChunk) -> None:
        """The street surfaces of a chunk, made by `road_chunks` (in the worker or here)."""
        if chunk.atlas is not None:
            self._show_atlas(chunk.atlas)
        self._surfaces.set_chunk(index, chunk.surfaces)
        self._streets.set_chunk(index, chunk.layered)
        if self._grid is not None and chunk.grid is not None:
            self._grid.set_chunk(index, chunk.grid)

    def show_tile_grid(self) -> None:
        """Phase 15 (P15-R10, `tiles=1`): draws the grid of tiles over the districts from now on."""
        if self._grid is None:
            self._grid = RoadField(self._scene, self._grid_material(), "tile-grid", 0, False)

    def _grid_material(self) -> Any:
        material = self._material.clone("tile-grid")
        if not material:
            material = self._material
        material.disableDepthWrite = False
        material.zOffset = -3
        return material

    def remove_chunk(self, index: int) -> None:
        if self._grid is not None:
            self._grid.remove_chunk(index)
        self._surfaces.remove_chunk(index)
        self._paths.remove_chunk(index)
        self._roads.remove_chunk(index)
        self._streets.remove_chunk(index)

    def clear(self) -> None:
        if self._grid is not None:
            self._grid.clear()
        self._surfaces.clear()
        self._paths.clear()
        self._roads.clear()
        self._streets.clear()
