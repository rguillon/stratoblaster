"""The material of the props' windows (D-210): the windows' atlas (`window_atlas.py`) uploaded once
per scene, its light glowing by the time of day as the other self-lit accents, its shape cut out
of the quads so the walls show between the windows. Needs a WebGL engine.
"""

from org.transcrypt.stubs.browser import __pragma__

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

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

ANISOTROPY = 8


def _atlas_texture(scene: Any, atlas: Any) -> Any:  # noqa: ANN401
    """The atlas of `atlas` (its look) as a tiling, mipmapped texture."""
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


def add_window_material(materials: Any, scene: Any, look: Any) -> None:  # noqa: ANN401
    """Sets `materials.windows` (the props' `PropMaterials`) for the scenery look `look`, if it
    has a windows' atlas (`look.props.windows`). Lit by the sun as dark glass (`atlas.glass`); the
    atlas' light is emissive, scaled as the other accents (`set_ground_lights`), so it glows at
    night, in the glow layer too, and is off by day."""
    atlas = look.props.windows
    if atlas == None:  # noqa: E711 (absent: undefined)
        return
    texture = _atlas_texture(scene, atlas)
    material = new_standard_material("prop-windows", scene)
    material.diffuseColor = color3(atlas.glass[0], atlas.glass[1], atlas.glass[2])
    material.specularColor = color3_black()
    glow = look.props.lightIntensity
    material.emissiveColor = color3(glow, glow, glow)
    material.emissiveTexture = texture
    # The alpha cuts the windows (and their halos) out of the quad.
    material.opacityTexture = texture
    # Blended over their own wall only, which is always drawn: no need to sort or write depth.
    material.disableDepthWrite = True
    # Off their walls already (`WINDOW_OFFSET`), and pulled forward as the accents, for far walls.
    material.zOffset = LIGHTS_Z_OFFSET
    materials.windows = material
