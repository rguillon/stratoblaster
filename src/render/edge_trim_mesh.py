"""Self-lit edge trim on a model's meshes (replaces the rim outline of the ships, GFX-TRIM-01,
read as a built-in rim light).

A mesh asks for a trim by its `metadata.trim` colour (`set_trim`, or `request_trim` for every solid
mesh of a model); once the whole model is built, `add_edge_trim` gives each such mesh a child mesh:
glowing ribbons along the edges the model shows from above (`render/geometry/edge_trim.py`). The
trim is part of the model: it moves, blinks and hides with its mesh (GFX-TRIM-04).
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
from typing import Any  # noqa: E402 (after the Transcrypt skip block, ENG-153)

Rgb = list[float]
__pragma__("noskip")

# The trim materials of each scene, by colour.
_MATERIALS = new_weak_map()


def set_trim(mesh: Any, color: Rgb) -> None:
    """Asks for a trim of `color` along `mesh`'s silhouette (e.g. an enemy's, in its colour:
    ENM-47). Keeps the mesh's other metadata."""
    mesh.metadata = object_with_field(mesh.metadata, "trim", color)


def trim_of(mesh: Any) -> Rgb | None:
    """The trim colour `mesh` asks for, if any."""
    color: Rgb | None = metadata_field(mesh.metadata, "trim")
    return color


def clear_trim(root: Any) -> None:
    """Takes back the trim requests of every mesh under `root` (e.g. a burnt stump,
    GFX-TRIM-09)."""
    for mesh in child_meshes(root, False):
        if trim_of(mesh) is not None:
            mesh.metadata = object_with_field(mesh.metadata, "trim", None)


def set_trim_group(node: Any) -> None:
    """Makes the model under `node` a trim group of its own: its meshes are trimmed along their own
    silhouette, as if the rest of the model were not there (e.g. a boss's destroyable part, which
    must show as one wherever it sits on the hull, GFX-TRIM-08)."""
    node.metadata = object_with_field(node.metadata, "trimGroup", True)


def _group_of(mesh: Any, root: Any) -> Any:
    """The trim group `mesh` belongs to: its nearest ancestor below `root` made one, else `root`."""
    node = mesh.parent
    while node is not None and node is not root:
        if metadata_field(node.metadata, "trimGroup") is True:
            return node
        node = node.parent
    return root


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
    """The scene's unlit, two-sided material of `color`, made on first use (GFX-TRIM-07)."""
    by_color = weak_map_get(_MATERIALS, scene)
    if by_color == None:  # noqa: E711 (absent value is undefined in the browser, ENG-161)
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
    asking for one in a trim group (see `set_trim_group`) hide each other's inner edges. Returns
    the trim meshes made."""
    meshes = [mesh for mesh in child_meshes(root, False) if trim_of(mesh) is not None]
    if len(meshes) == 0:
        return []
    to_root = inverse(world_matrix(root))
    # The meshes of each trim group, the model's own (root) first.
    groups: list[Any] = []
    members: list[list[int]] = []
    for k, mesh in enumerate(meshes):
        group = _group_of(mesh, root)
        found = -1
        for g in range(len(groups)):
            if groups[g] is group:
                found = g
        if found < 0:
            groups.append(group)
            members.append([])
            found = len(groups) - 1
        members[found].append(k)
    geos: list[Any] = [None for _ in meshes]
    for indices in members:
        shapes = [
            TrimShape(
                mesh_positions(meshes[k]),
                mesh_indices(meshes[k]),
                multiply(world_matrix(meshes[k]), to_root),
            )
            for k in indices
        ]
        trims = trim_model(shapes, options)
        for j, k in enumerate(indices):
            geos[k] = trims[j]
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
