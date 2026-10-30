"""Rim glow round the silhouette of playfield meshes (phase 14).

A mesh asks for a rim glow by its `metadata.outline` colour (`set_outline`); an `OutlineLayer`
draws it: each such mesh is drawn a second time, a little fatter, in its rim colour, behind
itself.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    babylon_constant,
    child_meshes,
    color3,
    is_instance_of,
    metadata_field,
    object_with_field,
)

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

Rgb = list[float]
__pragma__("noskip")


def set_outline(mesh: Any, color: Rgb) -> None:
    """Asks for a rim glow of `color` round `mesh`'s silhouette, drawn by an `OutlineLayer`
    wherever the mesh is shown. Keeps the mesh's other metadata."""
    mesh.metadata = object_with_field(mesh.metadata, "outline", color)


def outline_of(mesh: Any) -> Rgb | None:
    """The rim glow `mesh` asks for, if any."""
    color: Rgb | None = metadata_field(mesh.metadata, "outline")
    return color


def _is_solid(mesh: Any) -> bool:
    """Whether `mesh` is solid: not added on nor see-through (glows and flames get no rim)."""
    material = mesh.material
    if not material or mesh.hasVertexAlpha:
        return False
    solid: bool = material.alpha >= 1 and material.alphaMode != babylon_constant("ALPHA_ADD")
    return solid


def outline_model(root: Any, color: Rgb) -> None:
    """Asks for a rim glow of `color` round every solid mesh of the model under `root`."""
    for mesh in child_meshes(root, False):
        if _is_solid(mesh):
            set_outline(mesh, color)


class OutlineLook:
    """How the rim glows look: width in world units (logical pixels on the playfield), and
    strength."""

    def __init__(self, width: float, intensity: float) -> None:
        self.width = width
        self.intensity = intensity


class OutlineLayer:
    """Draws a thin rim round the silhouette of the meshes that ask for one (phase 14). No
    screen-wide pass: one more draw per mesh."""

    def __init__(self, look: OutlineLook) -> None:
        self._look = look

    def add(self, mesh: Any) -> bool:
        """Gives `mesh` its rim if it asks for one. Returns whether it did."""
        color = outline_of(mesh)
        if color is None or not is_instance_of(mesh, "Mesh"):
            return False
        # The rim is pushed out in the mesh's own space: undo its scale, so it is as wide on all.
        mesh.computeWorldMatrix(True)
        scale = abs(mesh.absoluteScaling.x) or 1
        mesh.renderOutline = True
        mesh.outlineColor = color3(color[0], color[1], color[2]).scale(self._look.intensity)
        mesh.outlineWidth = self._look.width / scale
        return True


def compile_outlines(meshes: Any) -> None:
    """Makes the rim shaders of the outlined `meshes` (P13-R04): Babylon creates each one, and
    starts compiling it, when it is first asked if it is ready. Done before play, the first ship or
    enemy with a rim does not stall the frame it appears in."""
    for mesh in meshes:
        if mesh.renderOutline:
            renderer = mesh.getScene().getOutlineRenderer()
            for sub in mesh.subMeshes:
                renderer.isReady(sub, False)


def outlines_ready(meshes: Any) -> bool:
    """Whether the rim shaders of the outlined `meshes` are compiled (see `compile_outlines`)."""
    for mesh in meshes:
        if mesh.renderOutline:
            renderer = mesh.getScene().getOutlineRenderer()
            for sub in mesh.subMeshes:
                if not renderer.isReady(sub, False):
                    return False
    return True
