"""The real scenery kit (P04, P08, P09, P10): generated terrain textures blended in the terrain
shader, a sea with drifting generated waves that reflect the sky and the sun (or lava), generated
cloud layers, and the sun's shadows (PCF, ENG-103). Needs a WebGL engine. Ported from
`render/scenery/scenery-kit.visual.ts`.
"""

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    babylon_class,
    babylon_constant,
    color3,
    is_instance_of,
    new_pbr_material,
    new_raw_texture,
    new_shadow_generator,
    new_standard_material,
    vector3,
)
from render.scenery.aurora_material_visual import create_aurora_material
from render.scenery.cloud_material_visual import create_cloud_material
from render.scenery.lava_material_visual import LavaFrame, create_lava_material
from render.scenery.plume_material_visual import create_plume_material
from render.scenery.procedural_textures import (
    NOISE_FREQUENCY,
    build_ground_texture,
    build_noise_texture,
    build_water_normal_map,
)
from render.scenery.rain_rings_material_visual import create_rain_rings_material
from render.scenery.scenery_kit import (
    FogState,
    create_prop_materials,
    create_road_material,
    set_ground_lights,
)
from render.scenery.terrain_blend_plugin_visual import (
    TerrainBlendState,
    TerrainTextures,
    new_terrain_blend_plugin,
)
from render.scenery.weather_material_visual import create_weather_material

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

ANISOTROPY = 8


def _raw_texture(scene: Any, pixels: Any, size: int) -> Any:
    """A tiling RGBA texture of `pixels`, trilinear and anisotropic."""
    sampling = babylon_class("Texture").TRILINEAR_SAMPLINGMODE
    texture = new_raw_texture(
        pixels,
        size,
        size,
        babylon_constant("TEXTUREFORMAT_RGBA"),
        scene,
        True,
        False,
        sampling,
    )
    texture.wrapU = babylon_class("Texture").WRAP_ADDRESSMODE
    texture.wrapV = babylon_class("Texture").WRAP_ADDRESSMODE
    texture.anisotropicFilteringLevel = ANISOTROPY
    return texture


def _terrain_material(scene: Any, look: Any, state: TerrainBlendState, seed: int) -> Any:
    t = look.terrain

    def ground(layer: Any, n: int) -> Any:
        return _raw_texture(
            scene, build_ground_texture(t.textureSize, layer, seed + n), t.textureSize
        )

    material = new_standard_material("terrain", scene)
    material.diffuseColor = color3(1, 1, 1)
    material.specularColor = color3(t.specular, t.specular, t.specular)
    textures = TerrainTextures(
        ground(t.low, 1),
        ground(t.ground, 2),
        ground(t.steep, 3),
        ground(t.high, 4),
        ground(t.lush, 8),
        ground(t.paved, 9),
        ground(t.sand, 10),
        _raw_texture(
            scene,
            build_noise_texture(t.textureSize, NOISE_FREQUENCY, seed + 5),
            t.textureSize,
        ),
    )
    new_terrain_blend_plugin(material, t, textures, state)
    return material


def _sea_material(scene: Any, look: Any, size: Any, seed: int) -> Any:
    sea = look.sea
    material = new_pbr_material("sea", scene)
    material.albedoColor = color3(sea.color[0], sea.color[1], sea.color[2])
    material.metallic = 0
    material.roughness = sea.roughness
    material.alpha = sea.alpha
    material.transparencyMode = babylon_class("PBRMaterial").PBRMATERIAL_ALPHABLEND
    material.directIntensity = sea.sunGlint
    normal_map = sea.normalMap
    normals = _raw_texture(
        scene,
        build_water_normal_map(normal_map.size, normal_map, seed + 6),
        normal_map.size,
    )
    normals.uScale = size.width / sea.tileSize
    normals.vScale = size.length_ / sea.tileSize
    material.bumpTexture = normals
    return material


def _liquid_of(scene: Any, context: Any) -> tuple[TerrainBlendState, Any]:
    """The terrain's live state and, for a lava level (P10-R05), the lava's material."""
    look = context.look
    lava = look.sea.lava
    state = TerrainBlendState(context.sea_level, True, 0, lava if lava else None, None)
    return state, (create_lava_material(scene, lava, look.sea.drift) if lava else None)


class VisualSceneryKit:
    """The real scenery kit (`create_scenery_kit`): terrain, sea, props, roads, the cloud,
    weather, rings, aurora and plume materials, and the sun's shadows."""

    def __init__(self, scene: Any, context: Any) -> None:
        look = context.look
        sun = context.sun
        seed = context.seed
        state, lava = _liquid_of(scene, context)
        self._scene = scene
        self._look = look
        self._state = state
        self._lava = lava
        self._sea = lava.material if lava else _sea_material(scene, look, context.sea_size, seed)
        self._cloud_texture = _raw_texture(
            scene,
            build_noise_texture(look.terrain.textureSize, NOISE_FREQUENCY / 2, seed + 7),
            look.terrain.textureSize,
        )
        shadows = new_shadow_generator(look.sun.shadow.map_size, sun)
        shadows.usePercentageCloserFiltering = True
        shadows.filteringQuality = babylon_class("ShadowGenerator").QUALITY_MEDIUM
        shadows.bias = look.sun.shadow.bias
        shadows.normalBias = look.sun.shadow.normalBias
        shadows.setDarkness(look.sun.shadow.darkness)
        # A fixed shadow frustum: re-fitting it to the scene every frame made the shadows shimmer
        # (the stage moves the sun by whole texels, phase 4 review).
        sun.autoUpdateExtends = False
        sun.shadowFrustumSize = look.sun.shadow.frustum
        self._shadows = shadows
        self._camera = vector3(0, 0, 0)
        self.props = create_prop_materials(scene, look)
        self.terrain = _terrain_material(scene, look, state, seed)
        self.sea = self._sea
        self.roads = create_road_material(scene)
        self.weather = create_weather_material
        self.rings = create_rain_rings_material
        self.plume = create_plume_material

    def cloud(self, look: Any) -> Any:
        return create_cloud_material(self._scene, look, self._cloud_texture, lambda: self._camera)

    def aurora(self) -> Any:
        return create_aurora_material(self._scene)

    def add_shadow_caster(self, mesh: Any) -> None:
        self._shadows.addShadowCaster(mesh, False)

    def update(self, frame: Any) -> None:
        self._camera = frame.camera_position
        self._state.time = frame.time
        # P08-R04: softer shadows under a heavy cover, ground lights by the time of day.
        self._shadows.setDarkness(frame.atmosphere.sun.shadow_darkness)
        set_ground_lights(self.props, frame.atmosphere.ground_lights)
        self._state.sea_enabled = frame.sea_enabled
        if frame.ground:
            self._state.ground = frame.ground
        atmosphere = frame.atmosphere
        if self._lava:
            fog = FogState(atmosphere.sky.haze, atmosphere.fog.start, atmosphere.fog.end)
            self._lava.set(LavaFrame(frame.time, fog))
        bump = self._sea.bumpTexture if is_instance_of(self._sea, "PBRMaterial") else None
        if is_instance_of(bump, "Texture"):
            assert bump is not None
            bump.uOffset = (frame.time * self._look.sea.drift[0]) / self._look.sea.tileSize
            bump.vOffset = (frame.time * self._look.sea.drift[1]) / self._look.sea.tileSize


def create_scenery_kit(scene: Any, context: Any) -> VisualSceneryKit:
    """The real scenery kit (the `SceneryKitFactory` that needs WebGL)."""
    return VisualSceneryKit(scene, context)
