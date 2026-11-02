# Copyright (c) 2026 Renaud Guillon
"""The material of the props' windows (D-210, GFX-BLDG-15).

The windows' atlas (`window_atlas.py`) uploaded once per scene, its light glowing by the time of day
as the other self-lit accents, its shape cut out of the quads so the walls show between the windows.
Needs a WebGL engine.

The atlas is the diffuse texture, not the emissive one: Babylon adds an emissive texture to the
emissive colour, so the dark windows would glow as much as the lit ones. As the diffuse texture
it multiplies the emissive colour (and the sunlight), so a dark window stays dark.
"""

from render.babylon import (
    babylon_class,
    babylon_constant,
    color3,
    color3_black,
    new_raw_texture,
    new_standard_material,
)
from render.scenery.scenery_kit import LIGHTS_Z_OFFSET
from render.scenery.window_atlas import kept_window_atlas

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


ANISOTROPY = 8


def _atlas_texture(scene: Any, atlas: Any) -> Any:
    """Return the atlas of `atlas` (its look) as a tiling, mipmapped texture."""
    texture_class = babylon_class("Texture")
    texture = new_raw_texture(
        kept_window_atlas(atlas),
        atlas.size,
        atlas.size,
        babylon_constant("TEXTUREFORMAT_RGBA"),
        scene,
        True,
        False,
        texture_class.TRILINEAR_SAMPLINGMODE,
    )
    texture.wrapU = texture_class.WRAP_ADDRESSMODE
    texture.wrapV = texture_class.WRAP_ADDRESSMODE
    texture.anisotropicFilteringLevel = ANISOTROPY
    texture.hasAlpha = True
    return texture


def add_window_material(materials: Any, scene: Any, look: Any) -> None:
    """Set `materials.windows` (the props' `PropMaterials`) for the scenery look `look`.

    If it has a windows' atlas (`look.props.windows`). The atlas' light is lit faintly by the sun
    (`atlas.glass`) and glows by the emissive colour, scaled as the other accents
    (`set_ground_lights`): off by day, on at night. A glow layer must draw the windows with this
    material (`glow_windows`).
    """
    atlas = look.props.windows
    if atlas == None:
        return
    texture = _atlas_texture(scene, atlas)
    material = new_standard_material("prop-windows", scene)
    material.diffuseTexture = texture
    # The alpha cuts the windows (and their halos) out of the quad.
    material.useAlphaFromDiffuseTexture = True
    material.diffuseColor = color3(atlas.glass[0], atlas.glass[1], atlas.glass[2])
    material.specularColor = color3_black()
    glow = look.props.lightIntensity
    material.emissiveColor = color3(glow, glow, glow)
    # Blended over their own wall only, which is always drawn: no need to sort or write depth.
    material.disableDepthWrite = True
    # Off their walls already (`WINDOW_OFFSET`), and pulled forward as the accents, for far walls.
    material.zOffset = LIGHTS_Z_OFFSET
    materials.windows = material


def glow_windows(layer: Any, mesh: Any) -> None:
    """Has the glow layer `layer` draw the windows' `mesh` with its own material: its own way.

    A glow layer would light the whole shape of every window, the dark ones too.
    """
    layer.referenceMeshToUseItsOwnMaterial(mesh)
