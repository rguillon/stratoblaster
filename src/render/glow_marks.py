# Copyright (c) 2026 Renaud Guillon
"""Marks a mesh that glow layers draw as it is: with its own material and colours (D-428).

A glow layer draws a mesh in its emissive colour alone. A mesh whose instances each have their own
colour and opacity (the flames) would glow white: marked, the layer that takes it draws it with its
own material instead.
"""

from render.babylon import metadata_field, object_with_field

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")

GLOWS_AS_DRAWN = "glowsAsDrawn"


def mark_glows_as_drawn(mesh: Any) -> None:
    """Mark `mesh`, keeping its other metadata."""
    mesh.metadata = object_with_field(mesh.metadata, GLOWS_AS_DRAWN, True)


def glows_as_drawn(mesh: Any) -> bool:
    """Whether `mesh` is marked."""
    return metadata_field(mesh.metadata, GLOWS_AS_DRAWN) is True
