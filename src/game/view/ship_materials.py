# Copyright (c) 2026 Renaud Guillon
"""Materials shared by all the player ships of a scene (GFX-SHIP-04, GFX-ART-04).

Shiny grey/blue metals and blue lights.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.readability import READABILITY
from game.config.ship_look import SHIP_LOOK
from render.babylon import color3, color3_black, new_pbr_material, new_standard_material

# isort: split
# __pragma__ ("skip")
from typing import Any

Scene = Any
# __pragma__ ("noskip")

# The scene's materials, by scene.
__pragma__("js", "{}", "const SHIP_MATERIALS_CACHE = new WeakMap();")


class ShipMaterials:
    """Materials shared by all the player ships of a scene.

    Attribute names are the property names the ship builders read.
    """

    def __init__(
        self,
        hull: Any,
        hullMid: Any,
        hullDark: Any,
        accent: Any,
        canopy: Any,
        trim: Any,
        nozzle: Any,
        reactorCore: Any,
        reactorExhaust: Any,
        reactorFlame: Any,
        reactorPlasma: Any,
        edgeGlow: Any = None,
        intakeBlack: Any = None,
        glass: Any = None,
    ) -> None:
        self.hull = hull
        # Two darker shades of the hull's metal (D-327).
        self.hullMid = hullMid
        self.hullDark = hullDark
        self.accent = accent
        self.canopy = canopy
        # Darker metal for panel lines, frames, intakes and barrels.
        self.trim = trim
        self.nozzle = nozzle
        self.reactorCore = reactorCore
        self.reactorExhaust = reactorExhaust
        self.reactorFlame = reactorFlame
        self.reactorPlasma = reactorPlasma
        # The glowing edges of the wings, the canards and the canopy (D-335).
        self.edgeGlow = edgeGlow
        # The matte black inside the intakes (D-347).
        self.intakeBlack = intakeBlack
        # The canopy's tinted, see-through glass (D-354).
        self.glass = glass


def _rgb_color(rgb: Any) -> Any:
    """Return `new Color3(...rgb)`."""
    return color3(rgb[0], rgb[1], rgb[2])


def _metal(name: str, look: Any, scene: Scene) -> Any:
    """Return a physically based metal with the look's albedo, metallic and roughness.

    Its colour takes the brighter hull light (GFX-ART-08).
    """
    mat = new_pbr_material(name, scene)
    mat.albedoColor = _rgb_color(look.albedo)
    mat.metallic = look.metallic
    mat.roughness = look.roughness
    mat.directIntensity = READABILITY.hullLight.direct
    mat.environmentIntensity = READABILITY.hullLight.environment
    return mat


def _light(name: str, emissive: Any, scene: Scene) -> Any:
    """Return an unlit, self-lit material of the given emissive colour."""
    mat = new_standard_material(name, scene)
    mat.emissiveColor = _rgb_color(emissive)
    mat.diffuseColor = color3_black()
    mat.specularColor = color3_black()
    mat.disableLighting = True
    return mat


def _glow(name: str, look: Any, scene: Scene) -> Any:
    """Return a light with its alpha, drawn from both sides."""
    mat = _light(name, look.emissive, scene)
    mat.alpha = look.alpha
    mat.backFaceCulling = False
    return mat


def _create_ship_materials(scene: Scene) -> ShipMaterials:
    """All the ship materials of `scene`, made from `SHIP_LOOK`."""
    canopy = _metal("ship-canopy", SHIP_LOOK.canopy, scene)
    canopy.emissiveColor = _rgb_color(SHIP_LOOK.canopy.emissive)
    reactor_core = _light("ship-reactor-core", SHIP_LOOK.reactorCore.emissive, scene)
    reactor_core.backFaceCulling = False
    edge_glow = _light("ship-edge-glow", SHIP_LOOK.edgeGlow.emissive, scene)
    edge_glow.backFaceCulling = False
    glass = _metal("ship-glass", SHIP_LOOK.glass, scene)
    glass.alpha = SHIP_LOOK.glass.alpha
    return ShipMaterials(
        _metal("ship-hull", SHIP_LOOK.hull, scene),
        _metal("ship-hull-mid", SHIP_LOOK.hullMid, scene),
        _metal("ship-hull-dark", SHIP_LOOK.hullDark, scene),
        _metal("ship-accent", SHIP_LOOK.accent, scene),
        canopy,
        _metal("ship-trim", SHIP_LOOK.trim, scene),
        _metal("ship-nozzle", SHIP_LOOK.nozzle, scene),
        reactor_core,
        _glow("ship-reactor-exhaust", SHIP_LOOK.reactorExhaust, scene),
        _glow("ship-reactor-flame", SHIP_LOOK.reactorFlame, scene),
        _glow("ship-reactor-plasma", SHIP_LOOK.reactorPlasma, scene),
        edge_glow,
        _metal("ship-intake-black", SHIP_LOOK.intakeBlack, scene),
        glass,
    )


def _cached_materials(scene: Scene) -> ShipMaterials | None:
    """`SHIP_MATERIALS_CACHE.get(scene) || null`: the scene's materials, once made."""
    __pragma__("js", "{}", "return SHIP_MATERIALS_CACHE.get(scene) || null;")
    return None


def get_ship_materials(scene: Scene) -> ShipMaterials:
    """Return the scene's ship materials, creating them on first use."""
    found = _cached_materials(scene)
    if found:
        return found
    created = _create_ship_materials(scene)
    __pragma__("js", "{}", "SHIP_MATERIALS_CACHE.set(scene, created);")
    return created
