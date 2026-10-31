"""Self-lit edge trim on a model's meshes (replaces the rim outline of the ships, P14-R03 / R04 read
as a built-in rim light).

A mesh asks for a trim by its `metadata.trim` colour (`set_trim`, or `request_trim` for every solid
mesh of a model); once the whole model is built, `add_edge_trim` gives each such mesh a child mesh:
glowing ribbons along the edges the model shows from above (`render/geometry/edge_trim.py`). The
trim is part of the model: it moves, blinks and hides with its mesh.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    apply_vertex_data,
    babylon_constant,
    child_meshes,
    color3,
    compute_normals,
    mesh_indices,
    mesh_positions,
    metadata_field,
    new_mesh,
    new_standard_material,
    new_weak_map,
    node_name,
    object_with_field,
    vertex_data_of,
    weak_map_get,
    weak_map_set,
    world_matrix,
)
from render.geometry.edge_trim import TrimOptions, TrimShape, inverse, multiply, trim_model

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

Rgb = list[float]
__pragma__("noskip")

# The trim materials of each scene, by colour.
_MATERIALS = new_weak_map()


def set_trim(mesh: Any, color: Rgb) -> None:
    """Asks for a trim of `color` along `mesh`'s silhouette. Keeps the mesh's other metadata."""
    mesh.metadata = object_with_field(mesh.metadata, "trim", color)


def trim_of(mesh: Any) -> Rgb | None:
    """The trim colour `mesh` asks for, if any."""
    color: Rgb | None = metadata_field(mesh.metadata, "trim")
    return color


def clear_trim(root: Any) -> None:
    """Takes back the trim requests of every mesh under `root` (e.g. a burnt stump)."""
    for mesh in child_meshes(root, False):
        if trim_of(mesh) is not None:
            mesh.metadata = object_with_field(mesh.metadata, "trim", None)


def is_solid(mesh: Any) -> bool:
    """Whether `mesh` is solid: not added on nor see-through (glows and flames get no trim)."""
    material = mesh.material
    if not material or mesh.hasVertexAlpha:
        return False
    solid: bool = material.alpha >= 1 and material.alphaMode != babylon_constant("ALPHA_ADD")
    return solid


def request_trim(root: Any, color: Rgb) -> None:
    """Asks for a trim of `color` on every solid mesh of the model under `root`."""
    for mesh in child_meshes(root, False):
        if is_solid(mesh):
            set_trim(mesh, color)


def _material(scene: Any, color: Rgb) -> Any:
    """The scene's unlit, two-sided material of `color`, made on first use."""
    by_color = weak_map_get(_MATERIALS, scene)
    if by_color == None:  # noqa: E711
        by_color = {}
        weak_map_set(_MATERIALS, scene, by_color)
    key = str(color[0]) + "," + str(color[1]) + "," + str(color[2])
    if key not in by_color:
        mat = new_standard_material("edge-trim-" + key, scene)
        mat.disableLighting = True
        mat.emissiveColor = color3(color[0], color[1], color[2])
        mat.backFaceCulling = False
        by_color[key] = mat
    return by_color[key]


def add_edge_trim(root: Any, options: TrimOptions) -> list[Any]:
    """Gives each mesh under `root` that asks for a trim its trim mesh, as a child; the meshes
    asking for one hide each other's inner edges. Returns the trim meshes made."""
    meshes = [mesh for mesh in child_meshes(root, False) if trim_of(mesh) is not None]
    if len(meshes) == 0:
        return []
    to_root = inverse(world_matrix(root))
    shapes = [
        TrimShape(mesh_positions(mesh), mesh_indices(mesh), multiply(world_matrix(mesh), to_root))
        for mesh in meshes
    ]
    geos = trim_model(shapes, options)
    made: list[Any] = []
    for k, mesh in enumerate(meshes):
        geo = geos[k]
        if len(geo.indices) == 0:
            continue
        scene = mesh.getScene()
        trim = new_mesh(node_name(mesh) + "-trim", scene)
        normals = compute_normals(geo.positions, geo.indices)
        apply_vertex_data(vertex_data_of(geo.positions, geo.indices, normals, geo.colors), trim)
        color: Rgb = trim_of(mesh) or []
        trim.material = _material(scene, color)
        trim.isPickable = False
        # A light: the haze of the level (fog) does not dim it, as it did not dim the rim.
        trim.applyFog = False
        trim.parent = mesh
        made.append(trim)
    return made
