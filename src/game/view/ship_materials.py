"""Materials shared by all the player ships of a scene"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.readability import READABILITY
from game.config.ship_look import SHIP_LOOK
from render.babylon import color3, color3_black, new_pbr_material, new_standard_material

__pragma__("skip")
from typing import Any  # noqa: E402

Scene = Any


__pragma__("noskip")

# The scene's materials, by scene.
__pragma__("js", "{}", "const SHIP_MATERIALS_CACHE = new WeakMap();")


class ShipMaterials:
    """Materials shared by all the player ships of a scene. Attribute names are the property names
    the ship builders read."""

    def __init__(  # noqa: PLR0913, PLR0917 (one argument per material, positional)
        self,
        hull: Any,
        accent: Any,
        canopy: Any,
        trim: Any,
        navLight: Any,  # noqa: N803
        nozzle: Any,
        reactorCore: Any,  # noqa: N803
        reactorExhaust: Any,  # noqa: N803
        reactorFlame: Any,  # noqa: N803
        reactorPlasma: Any,  # noqa: N803
    ) -> None:
        self.hull = hull
        self.accent = accent
        self.canopy = canopy
        # Darker metal for panel lines, frames, intakes and barrels.
        self.trim = trim
        # Small blue lights (wing tips, tails, cannon muzzles).
        self.navLight = navLight
        self.nozzle = nozzle
        self.reactorCore = reactorCore
        self.reactorExhaust = reactorExhaust
        self.reactorFlame = reactorFlame
        self.reactorPlasma = reactorPlasma


def _rgb_color(rgb: Any) -> Any:
    """`new Color3(...rgb)`."""
    return color3(rgb[0], rgb[1], rgb[2])


def _metal(name: str, look: Any, scene: Scene) -> Any:
    """A physically based metal with the look's albedo, metallic and roughness."""
    mat = new_pbr_material(name, scene)
    mat.albedoColor = _rgb_color(look.albedo)
    mat.metallic = look.metallic
    mat.roughness = look.roughness
    mat.directIntensity = READABILITY.hullLight.direct
    mat.environmentIntensity = READABILITY.hullLight.environment
    return mat


def _light(name: str, emissive: Any, scene: Scene) -> Any:
    """An unlit, self-lit material of the given emissive colour."""
    mat = new_standard_material(name, scene)
    mat.emissiveColor = _rgb_color(emissive)
    mat.diffuseColor = color3_black()
    mat.specularColor = color3_black()
    mat.disableLighting = True
    return mat


def _glow(name: str, look: Any, scene: Scene) -> Any:
    """A light with its alpha, drawn from both sides."""
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
    return ShipMaterials(
        _metal("ship-hull", SHIP_LOOK.hull, scene),
        _metal("ship-accent", SHIP_LOOK.accent, scene),
        canopy,
        _metal("ship-trim", SHIP_LOOK.trim, scene),
        _light("ship-nav-light", SHIP_LOOK.navLight.emissive, scene),
        _metal("ship-nozzle", SHIP_LOOK.nozzle, scene),
        reactor_core,
        _glow("ship-reactor-exhaust", SHIP_LOOK.reactorExhaust, scene),
        _glow("ship-reactor-flame", SHIP_LOOK.reactorFlame, scene),
        _glow("ship-reactor-plasma", SHIP_LOOK.reactorPlasma, scene),
    )


def get_ship_materials(scene: Scene) -> ShipMaterials:
    """Returns the scene's ship materials, creating them on first use."""
    found: Any = None
    __pragma__("js", "{}", "found = SHIP_MATERIALS_CACHE.get(scene);")
    if found:
        cached: ShipMaterials = found
        return cached
    created = _create_ship_materials(scene)
    __pragma__("js", "{}", "SHIP_MATERIALS_CACHE.set(scene, created);")
    return created
