"""The road pieces of the `props/` page (phase 15), ported from `app/prop-viewer-roads.ts`: drawn
as in the levels, one textured surface per piece, its markings from the road atlas."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from render.babylon import (  # noqa: E402
    apply_vertex_data,
    babylon_constant,
    color3_black,
    compute_normals,
    new_mesh,
    new_raw_texture,
    new_standard_material,
    new_vertex_data,
    texture_trilinear_sampling_mode,
    update_raw_texture,
)
from render.scenery.road_atlas import ATLAS_SIZE, RoadAtlas  # noqa: E402
from render.scenery.road_surface import build_road_surfaces  # noqa: E402

_ALL_Z = float("-Infinity")
_ALL_Z_MAX = float("Infinity")


def _flat(_x: float, _z: float) -> float:
    """The ground of the props page: flat."""
    return 0


class ViewerRoads:
    """Builds meshes of road pieces on flat ground, from one atlas and one material."""

    def __init__(self, scene: Any, tile: Any, look: Any) -> None:
        self._scene = scene
        self._tile = tile
        self._look = look
        self._atlas = RoadAtlas(tile, look)
        self._texture = new_raw_texture(
            self._atlas.data,
            ATLAS_SIZE,
            ATLAS_SIZE,
            babylon_constant("TEXTUREFORMAT_RGBA"),
            scene,
            True,
            False,
            texture_trilinear_sampling_mode(),
        )
        self._texture.anisotropicFilteringLevel = 8
        self._material = new_standard_material("props-roads", scene)
        self._material.diffuseTexture = self._texture
        self._material.specularColor = color3_black()

    def mesh(self, name: str, pieces: list[Any]) -> Any:
        """A mesh of `pieces`, or None when there are none."""
        surfaces, _layered = build_road_surfaces(
            pieces, self._tile, self._look, self._atlas, _flat, _ALL_Z, _ALL_Z_MAX
        )
        if self._atlas.dirty:
            update_raw_texture(self._texture, self._atlas.data)
            self._atlas.dirty = False
        if len(surfaces.indices) == 0:
            return None
        mesh = new_mesh(name, self._scene)
        data = new_vertex_data()
        data.positions = surfaces.positions
        data.indices = surfaces.indices
        data.uvs = surfaces.uvs
        data.normals = compute_normals(surfaces.positions, surfaces.indices)
        apply_vertex_data(data, mesh)
        mesh.material = self._material
        return mesh
