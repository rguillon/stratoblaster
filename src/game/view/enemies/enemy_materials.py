"""The materials of the enemy models (P05, P14-R02, P16-R01)"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Any  # noqa: E402

type Rgb = list[float]
__pragma__("noskip")

from core.math.color import fold_into_family  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.config.readability import READABILITY  # noqa: E402
from render.babylon import (  # noqa: E402
    apply_vertex_data,
    block_material_marks,
    color3,
    color3_black,
    compute_normals,
    new_mesh,
    new_pbr_material,
    new_standard_material,
    vertex_data_of,
)


def enemy_color(color: Rgb) -> Sequence[float]:
    """`color` moved into the enemies' colour family (P14-R02)."""
    return fold_into_family(color, READABILITY.families.enemy)


def _with_colors(geo: Any, colors: list[float]) -> Any:
    """`{ ...geo, colors }`: a copy of a coloured geometry with other colours."""
    __pragma__("js", "{}", "return Object.assign({}, geo, {colors: colors});")
    return None


def in_enemy_family(geo: Any) -> Any:
    """`geo` with its vertex colours moved into the enemies' colour family (P14-R02)."""
    colors = list(geo.colors)
    i = 0
    while i + 3 < len(colors):
        rgb = enemy_color([colors[i] or 0, colors[i + 1] or 0, colors[i + 2] or 0])
        colors[i] = rgb[0]
        colors[i + 1] = rgb[1]
        colors[i + 2] = rgb[2]
        i += 4
    return _with_colors(geo, colors)


class EnemyMaterials:
    """The materials of the enemies of one scene: hull (dark metal), flesh (dark, waxy), neon."""

    def __init__(self, hull: Any, flesh: Any, neon: Any) -> None:
        # Dark metal, tinted by the vertex colours.
        self.hull = hull
        # Dark, waxy flesh (P16-R01), tinted by the vertex colours.
        self.flesh = flesh
        # Unlit neon, coloured by the vertex colours.
        self.neon = neon


class FlameMaterials:
    """The materials of a reactor's flame: exhaust, flame and plasma."""

    def __init__(self, exhaust: Any, flame: Any, plasma: Any) -> None:
        self.exhaust = exhaust
        self.flame = flame
        self.plasma = plasma


# Per-scene caches: pairs of [scene, value], matched by identity.
_ENEMY_CACHE = []  # type: list[list[Any]]
_TINTED_CACHE = []  # type: list[list[Any]]
_FLAME_CACHE = []  # type: list[list[Any]]


def _cached(cache: list[list[Any]], scene: Any) -> list[Any] | None:
    for pair in cache:
        if pair[0] is scene:
            return pair
    return None


def unlit(name: str, scene: Any) -> Any:
    """An unlit material: white emissive, black diffuse and specular."""
    was = block_material_marks(scene, True)
    mat = new_standard_material(name, scene)
    mat.emissiveColor = color3(1, 1, 1)
    mat.diffuseColor = color3_black()
    mat.specularColor = color3_black()
    mat.disableLighting = True
    block_material_marks(scene, was)
    return mat


def enemy_materials(scene: Any) -> EnemyMaterials:
    """The scene's enemy materials, created on first use."""
    pair = _cached(_ENEMY_CACHE, scene)
    if pair is None:
        mats = EnemyMaterials(
            metal("enemy-hull", color3(1, 1, 1), scene),
            flesh_of("enemy-flesh", color3(1, 1, 1), scene),
            unlit("enemy-neon", scene),
        )
        _ENEMY_CACHE.append([scene, mats])
        return mats
    cached: EnemyMaterials = pair[1]
    return cached


def metal(name: str, albedo: Any, scene: Any) -> Any:
    """Dark metal lit by the hull settings of the enemy look."""
    was = block_material_marks(scene, True)
    hull = new_pbr_material(name, scene)
    hull.albedoColor = albedo
    hull.metallic = ENEMY_LOOK.hull.metallic
    hull.roughness = ENEMY_LOOK.hull.roughness
    hull.directIntensity = READABILITY.hullLight.direct
    hull.environmentIntensity = READABILITY.hullLight.environment
    block_material_marks(scene, was)
    return hull


def flesh_of(name: str, albedo: Any, scene: Any) -> Any:
    """A waxy, barely metallic flesh (P16-R01), lit as the hulls are."""
    was = block_material_marks(scene, True)
    mat = metal(name, albedo, scene)
    mat.metallic = ENEMY_LOOK.flesh.metallic
    mat.roughness = ENEMY_LOOK.flesh.roughness
    block_material_marks(scene, was)
    return mat


# The materials that show an enemy's body, flashed white when a boss part is hit.
BODY_MATERIALS = ["enemy-hull", "enemy-flesh"]


def tinted_hull(scene: Any, neon: Sequence[float], flesh: bool = False) -> Any:
    """The dark metal of an enemy whose neon is `neon` (phase 5 review: enemies easier to see on
    the ground): tinted towards its neon colour, and faintly lit by it."""
    look = ENEMY_LOOK.hull
    pair = _cached(_TINTED_CACHE, scene)
    if pair is None:
        pair = [scene, {}]
        _TINTED_CACHE.append(pair)
    by_color = pair[1]
    key = ("flesh" if flesh else "hull") + ":" + ",".join([str(c) for c in neon])
    mat = by_color.get(key)
    if mat is None:
        tint = ENEMY_LOOK.flesh.tint if flesh else look.tint
        rgb = [1 + (c - 1) * tint for c in neon]
        albedo = color3(rgb[0], rgb[1], rgb[2])
        mat = (
            flesh_of("enemy-flesh", albedo, scene) if flesh else metal("enemy-hull", albedo, scene)
        )
        mat.emissiveColor = color3(neon[0], neon[1], neon[2]).scale(look.selfLight)
        by_color[key] = mat
    return mat


def rim_of(neon: Sequence[float]) -> Rgb:
    """The rim colour of an enemy whose neon is `neon` (P14-R04)."""
    outline = READABILITY.enemyOutline
    whiten = outline.whiten
    strength = outline.strength

    def lift(c: float) -> float:
        value: float = (c + (1 - c) * whiten) * strength
        return value

    return [lift(neon[0]), lift(neon[1]), lift(neon[2])]


def mesh_of(name: str, geo: Any, material: Any, scene: Any) -> Any:
    """A flat-shaded, vertex-coloured mesh."""
    mesh = new_mesh(name, scene)
    normals = compute_normals(geo.positions, geo.indices)
    data = vertex_data_of(geo.positions, geo.indices, normals, geo.colors)
    apply_vertex_data(data, mesh)
    mesh.material = material
    mesh.isPickable = False
    return mesh


def glowing(name: str, color: Sequence[float], alpha: float, scene: Any) -> Any:
    """An unlit, see-through material of `color` at `alpha`, drawn both sides."""
    was = block_material_marks(scene, True)
    mat = unlit(name, scene)
    mat.emissiveColor = color3(color[0], color[1], color[2])
    mat.alpha = alpha
    mat.backFaceCulling = False
    block_material_marks(scene, was)
    return mat


def flame_materials(scene: Any, color: Sequence[float]) -> Any:
    """Flame materials in `color`, shared by the scene's reactors of that colour."""
    look = ENEMY_LOOK.reactor
    pair = _cached(_FLAME_CACHE, scene)
    if pair is None:
        pair = [scene, {}]
        _FLAME_CACHE.append(pair)
    by_color = pair[1]
    key = ",".join([str(c) for c in color])
    mats = by_color.get(key)
    if mats is None:
        hot = [c + (1 - c) * look.whiten for c in color]
        mats = FlameMaterials(
            glowing("enemy-exhaust-" + key, color, look.exhaustAlpha, scene),
            glowing("enemy-flame-" + key, hot, look.flameAlpha, scene),
            glowing("enemy-plasma-" + key, color, look.plasmaAlpha, scene),
        )
        by_color[key] = mats
    return mats
