"""Disabled template meshes for shots (P03), ported from `shots/shot-meshes.ts`.

Clones of a template share its geometry; the renderers show or hide them through `NodePool`.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from render.babylon import (  # noqa: E402
    apply_vertex_data,
    babylon_constant,
    color3,
    color3_black,
    new_mesh,
    new_standard_material,
    vertex_data_of,
)

# Vertex colours are RGBA: every fourth component is the alpha.
RGBA = 4
ALPHA_SLOT = 3


def _vertex_colour(colour: float, index: int, alphas: list[float]) -> float:
    """Vertex colour component `index`; alpha components (every fourth) take `alphas`."""
    if index % RGBA != ALPHA_SLOT:
        return colour
    alpha = alphas[index // RGBA]
    # `??`: an alpha that is missing (undefined) keeps the colour's own value.
    return colour if alpha == None else alpha  # noqa: E711


def additive_template(name: str, geo: Any, scene: Any, on_top: bool = False) -> Any:
    """A disabled template mesh showing its vertex colours, unlit, added onto what is behind it
    (black is transparent), without writing depth. Clones of it share its geometry. `on_top`
    draws it over everything, models included (phase 8 review: a laser leaving a lens set into a
    raised hull is seen leaving the lens, not from under the hull).
    """
    mesh = new_mesh(name, scene)
    data = vertex_data_of(geo.positions, geo.indices, None, geo.colors)
    apply_vertex_data(data, mesh)
    material = new_standard_material(name, scene)
    material.emissiveColor = color3(1, 1, 1)
    material.diffuseColor = color3_black()
    material.specularColor = color3_black()
    material.disableLighting = True
    material.backFaceCulling = False
    material.alphaMode = babylon_constant("ALPHA_ADD")
    # Below 1, so the material goes through the blended pass.
    material.alpha = 0.999
    material.disableDepthWrite = True
    if on_top:
        material.depthFunction = babylon_constant("ALWAYS")
    mesh.material = material
    mesh.isPickable = False
    mesh.setEnabled(False)
    return mesh


def blended_template(name: str, geo: Any, alphas: list[float], scene: Any) -> Any:
    """A disabled template mesh of colours that hide what is behind them as much as their vertex
    alpha says (phase 8 review): unlit, blended, without writing depth. Unlike an additive glow,
    its colours stay as they are over bright ground (snow) instead of washing out to white.
    """
    mesh = new_mesh(name, scene)
    colors = [_vertex_colour(c, i, alphas) for i, c in enumerate(geo.colors)]
    data = vertex_data_of(geo.positions, geo.indices, None, colors)
    apply_vertex_data(data, mesh)
    mesh.hasVertexAlpha = True
    material = new_standard_material(name, scene)
    material.emissiveColor = color3(1, 1, 1)
    material.diffuseColor = color3_black()
    material.specularColor = color3_black()
    material.disableLighting = True
    material.backFaceCulling = False
    material.disableDepthWrite = True
    mesh.material = material
    mesh.isPickable = False
    mesh.setEnabled(False)
    return mesh
