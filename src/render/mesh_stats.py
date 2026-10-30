"""Triangle counts of a model (ported from `render/mesh-stats.ts`)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import child_meshes, is_instance_of

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def count_triangles(root: Any) -> int:
    """Number of triangles drawn for `root` and all the meshes under it."""
    meshes = child_meshes(root, False)
    if is_instance_of(root, "AbstractMesh"):
        meshes.append(root)
    triangles = 0.0
    for mesh in meshes:
        indices = mesh.getTotalIndices()
        triangles = triangles + (indices if indices > 0 else mesh.getTotalVertices()) / 3
    return math.floor(triangles + 0.5)
