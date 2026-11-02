# Copyright (c) 2026 Renaud Guillon
"""Rim glow round the silhouette of playfield meshes (phase 14).

It is now only on the enemy missiles (GFX-SHOT-15); the ships, enemies and bosses have a glowing
edge trim in their geometry instead (`render/edge_trim_mesh.py`).

A mesh asks for a rim glow by its `metadata.outline` colour (`set_outline`); an `OutlineLayer` draws
it: each such mesh is drawn a second time, a little fatter, in its rim colour, behind itself.
"""

from render.babylon import (
    color3,
    is_instance_of,
    metadata_field,
    object_with_field,
)

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

Rgb = list[float]
# __pragma__ ("noskip")


def set_outline(mesh: Any, color: Rgb) -> None:
    """Asks for a rim glow of `color` round `mesh`'s silhouette.

    It is drawn by an `OutlineLayer` wherever the mesh is shown.

    Keeps the mesh's other metadata.
    """
    mesh.metadata = object_with_field(mesh.metadata, "outline", color)


def outline_of(mesh: Any) -> Rgb | None:
    """Return the rim glow `mesh` asks for, if any."""
    color: Rgb | None = metadata_field(mesh.metadata, "outline")
    return color


class OutlineLook:
    """How the rim glows look: width in world units (logical pixels on the playfield), strength."""

    def __init__(self, width: float, intensity: float) -> None:
        self.width = width
        self.intensity = intensity


class OutlineLayer:
    """Draws a thin rim round the silhouette of the meshes that ask for one (phase 14).

    No screen-wide pass: one more draw per mesh.
    """

    def __init__(self, look: OutlineLook) -> None:
        self._look = look

    def add(self, mesh: Any) -> bool:
        """Give `mesh` its rim if it asks for one.

        Returns whether it did.
        """
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
    """Make the rim shaders of the outlined `meshes` (PERF-20).

    Babylon creates each one, and starts compiling it, when it is first asked if it is ready.

    Done before play, the first ship or enemy with a rim does not stall the frame it appears in.
    """
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
