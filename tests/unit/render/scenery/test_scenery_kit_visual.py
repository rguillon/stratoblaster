# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/scenery_kit_visual.py`: the real scenery kit's wiring.

The Babylon objects are fakes that keep what is set on them; the generated textures are named by
what they were made from, and the other `*_visual` materials are recorders.
"""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeSettable, FakeVector, patch_babylon
from helpers.render_looks import make_look

from render.scenery import scenery_kit, scenery_kit_visual
from render.scenery.lava_material_visual import LavaFrame
from render.scenery.procedural_textures import NOISE_FREQUENCY
from render.scenery.scenery_kit import GroundTransform, SceneryKitContext, SceneryKitFrame, SeaSize
from render.scenery.scenery_kit_visual import ANISOTROPY, VisualSceneryKit, create_scenery_kit
from render.scenery.scenery_look import SeaLook, SeaNormalMap
from render.scenery.terrain_blend_plugin_visual import TerrainBlendState, TerrainTextures

SEED = 10
CLASSES = {
    "Texture": SimpleNamespace(TRILINEAR_SAMPLINGMODE="trilinear", WRAP_ADDRESSMODE="wrap"),
    "PBRMaterial": SimpleNamespace(PBRMATERIAL_ALPHABLEND="alpha blend"),
    "ShadowGenerator": SimpleNamespace(QUALITY_MEDIUM="medium"),
}


class FakeMaterial:
    """A `StandardMaterial`."""

    def __init__(self, name: str, scene: Any) -> None:
        self.name = name
        self.scene = scene


class FakePbr(FakeMaterial):
    """A `PBRMaterial`."""


class FakeTexture:
    """A `RawTexture`: what it was made from."""

    def __init__(self, *args: Any) -> None:
        self.args = args
        self.uOffset = 0.0
        self.vOffset = 0.0


class FakeShadows:
    """A `ShadowGenerator`: its map size, its light, its darkness and casters."""

    def __init__(self, size: int, light: Any) -> None:
        self.size = size
        self.light = light
        self.darkness: float | None = None
        self.casters: list[tuple[Any, bool]] = []

    def setDarkness(self, darkness: float) -> None:
        self.darkness = darkness

    def addShadowCaster(self, mesh: Any, children: bool) -> None:
        self.casters.append((mesh, children))


class FakeLava:
    """The lava's material: the frames it was set to."""

    def __init__(self, scene: Any, look: Any, drift: Any) -> None:
        self.args = (scene, look, drift)
        self.material = FakeMaterial("lava", scene)
        self.frames: list[LavaFrame] = []

    def set(self, frame: LavaFrame) -> None:
        self.frames.append(frame)


class Made:
    """What the kit asked of the modules it wires together."""

    def __init__(self) -> None:
        self.plugins: list[tuple[Any, ...]] = []
        self.ground_layers: list[tuple[Any, int]] = []
        self.windows: list[tuple[Any, ...]] = []
        self.clouds: list[tuple[Any, ...]] = []
        self.lavas: list[FakeLava] = []


def _is_instance_of(value: Any, name: str) -> bool:
    kinds = {"PBRMaterial": FakePbr, "StandardMaterial": FakeMaterial, "Texture": FakeTexture}
    return isinstance(value, kinds[name])


@pytest.fixture
def made(monkeypatch: pytest.MonkeyPatch) -> Made:
    recorded = Made()
    for module in (scenery_kit, scenery_kit_visual):
        patch_babylon(monkeypatch, module)
        monkeypatch.setattr(module, "new_standard_material", FakeMaterial)
        monkeypatch.setattr(module, "is_instance_of", _is_instance_of)
    module = scenery_kit_visual

    def ground_texture(size: int, layer: Any, seed: int) -> Any:
        recorded.ground_layers.append((layer, seed))
        return ("ground", size, seed)

    def new_lava(scene: Any, look: Any, drift: Any) -> FakeLava:
        lava = FakeLava(scene, look, drift)
        recorded.lavas.append(lava)
        return lava

    monkeypatch.setattr(module, "babylon_class", CLASSES.__getitem__)
    monkeypatch.setattr(module, "new_raw_texture", FakeTexture)
    monkeypatch.setattr(module, "new_pbr_material", FakePbr)
    monkeypatch.setattr(module, "new_shadow_generator", FakeShadows)
    monkeypatch.setattr(module, "build_ground_texture", ground_texture)
    monkeypatch.setattr(
        module,
        "build_noise_texture",
        lambda size, frequency, seed: ("noise", size, frequency, seed),
    )
    monkeypatch.setattr(
        module, "build_water_normal_map", lambda size, options, seed: ("water", size, options, seed)
    )
    monkeypatch.setattr(
        module, "new_terrain_blend_plugin", lambda *args: recorded.plugins.append(args)
    )
    monkeypatch.setattr(module, "create_lava_material", new_lava)
    monkeypatch.setattr(module, "add_window_material", lambda *args: recorded.windows.append(args))
    monkeypatch.setattr(
        module, "create_cloud_material", lambda *args: recorded.clouds.append(args) or "cloud"
    )
    monkeypatch.setattr(module, "create_aurora_material", lambda scene: ("aurora", scene))
    monkeypatch.setattr(module, "ImposterAtlas", lambda *args: ("atlas", *args))
    return recorded


def _lava_look() -> Any:
    lava = SimpleNamespace(glow=(1, 0.4, 0.1))
    sea = SeaLook((0.2, 0, 0), 0.6, 0.1, 0.5, SeaNormalMap(64, 4, 2, 0.3), 16, (0.5, -1), lava)
    return make_look(sea=sea)


def _kit(look: Any = None) -> VisualSceneryKit:
    sun = SimpleNamespace(autoUpdateExtends=True, shadowFrustumSize=0)
    context = SceneryKitContext(look or make_look(), sun, 2, SeaSize(64, 128), SEED)
    return create_scenery_kit("scene", context)


def _frame(time: float, ground: GroundTransform | None = None) -> SceneryKitFrame:
    atmosphere = SimpleNamespace(
        sun=SimpleNamespace(shadow_darkness=0.3),
        ground_lights=0.4,
        sky=SimpleNamespace(haze=(0.1, 0.2, 0.3)),
        fog=SimpleNamespace(start=50, end=500),
    )
    return SceneryKitFrame(time, FakeVector(1, 2, 3), False, atmosphere, ground)


def _values(color: Any) -> tuple[float, ...]:
    settable: FakeSettable = color
    return settable.values


@pytest.mark.usefixtures("made")
def test_the_generated_textures_tile_trilinear_and_anisotropic() -> None:
    kit = _kit()
    texture: FakeTexture = kit._cloud_texture
    size = make_look().terrain.textureSize
    pixels = ("noise", size, NOISE_FREQUENCY / 2, SEED + 7)
    assert texture.args == (
        pixels,
        size,
        size,
        "TEXTUREFORMAT_RGBA",
        "scene",
        True,
        False,
        "trilinear",
    )
    assert (texture.wrapU, texture.wrapV) == ("wrap", "wrap")
    assert texture.anisotropicFilteringLevel == ANISOTROPY


def test_the_terrain_blends_its_generated_layers(made: Made) -> None:
    look = make_look()
    kit = _kit(look)
    t = look.terrain
    layers = [t.low, t.ground, t.steep, t.high, t.lush, t.paved, t.sand]
    assert made.ground_layers == list(
        zip(layers, [SEED + n for n in (1, 2, 3, 4, 8, 9, 10)], strict=True)
    )
    [(material, terrain, textures, state)] = made.plugins
    assert material is kit.terrain
    assert material.name == "terrain"
    assert _values(material.diffuseColor) == (1, 1, 1)
    assert terrain is t
    assert isinstance(textures, TerrainTextures)
    assert textures.paved.args[0] == ("ground", t.textureSize, SEED + 9)
    assert textures.noise.args[0] == ("noise", t.textureSize, NOISE_FREQUENCY, SEED + 5)
    assert state is kit._state


@pytest.mark.usefixtures("made")
def test_gfx_terrain_12_the_terrain_is_as_matte_as_its_look() -> None:
    look = make_look()
    specular = look.terrain.specular
    assert _values(_kit(look).terrain.specularColor) == (specular, specular, specular)


def test_gfx_water_03_the_sea_reflects_through_drifting_generated_waves(made: Made) -> None:
    look = make_look()
    kit = _kit(look)
    sea = kit.sea
    assert isinstance(sea, FakePbr)
    assert sea.name == "sea"
    assert _values(sea.albedoColor) == look.sea.color
    assert (sea.metallic, sea.roughness, sea.alpha) == (0, look.sea.roughness, look.sea.alpha)
    assert sea.transparencyMode == "alpha blend"
    assert sea.directIntensity == look.sea.sunGlint
    bump = sea.bumpTexture
    assert bump.args[0] == ("water", 64, look.sea.normalMap, SEED + 6)
    assert (bump.uScale, bump.vScale) == (64 / look.sea.tileSize, 128 / look.sea.tileSize)
    state: TerrainBlendState = kit._state
    assert (state.sea_level, state.sea_enabled, state.time, state.lava) == (2, True, 0, None)
    assert made.lavas == []


def test_gfx_terrain_16_a_lava_level_has_a_lava_sea(made: Made) -> None:
    look = _lava_look()
    kit = _kit(look)
    [lava] = made.lavas
    assert lava.args == ("scene", look.sea.lava, look.sea.drift)
    assert kit.sea is lava.material
    assert kit._state.lava is look.sea.lava


@pytest.mark.usefixtures("made")
def test_eng_103_gfx_sky_02_the_sun_casts_soft_shadows_in_a_fixed_frustum() -> None:
    look = make_look()
    kit = _kit(look)
    shadows: FakeShadows = kit._shadows
    shadow = look.sun.shadow
    assert shadows.size == shadow.mapSize
    assert shadows.usePercentageCloserFiltering
    assert shadows.filteringQuality == "medium"
    assert (shadows.bias, shadows.normalBias) == (shadow.bias, shadow.normalBias)
    assert shadows.darkness == shadow.darkness
    assert shadows.light.autoUpdateExtends is False
    assert shadows.light.shadowFrustumSize == shadow.frustum
    kit.add_shadow_caster("mesh")
    assert shadows.casters == [("mesh", False)]


def test_the_props_get_their_windows_and_the_kit_its_factories(made: Made) -> None:
    look = make_look()
    kit = _kit(look)
    assert made.windows == [(kit.props, "scene", look)]
    assert kit.props.structure.name == "prop-structure"
    assert kit.roads.name == "roads"
    assert kit.weather is scenery_kit_visual.create_weather_material
    assert kit.rings is scenery_kit_visual.create_rain_rings_material
    assert kit.plume is scenery_kit_visual.create_plume_material


def test_a_cloud_layer_sees_the_camera_where_it_is_now(made: Made) -> None:
    kit = _kit()
    assert kit.cloud("cloud look") == "cloud"
    [(scene, look, texture, camera)] = made.clouds
    assert (scene, look, texture) == ("scene", "cloud look", kit._cloud_texture)
    frame = _frame(1)
    kit.update(frame)
    assert camera() is frame.camera_position


@pytest.mark.usefixtures("made")
def test_the_aurora_is_made_in_the_scene() -> None:
    assert _kit().aurora() == ("aurora", "scene")


@pytest.mark.usefixtures("made")
def test_d211_an_imposter_atlas_is_made_only_for_a_look() -> None:
    assert _kit().imposter_atlas(None, 3) is None
    # Toned as the props' structure: 1 when the world has no tone.
    assert _kit().imposter_atlas("look", 3) == ("atlas", "scene", "look", 3, 1)
    assert _kit(make_look(tone=0.7)).imposter_atlas("look", 2) == ("atlas", "scene", "look", 2, 0.7)


@pytest.mark.usefixtures("made")
def test_gfx_sky_06_gfx_sky_08_each_frame_sets_the_shadows_lights_and_terrain_state() -> None:
    kit = _kit()
    kit.update(_frame(2.5))
    assert kit._shadows.darkness == 0.3
    assert _values(kit.props.lights.emissiveColor) == (0.4, 0.4, 0.4)
    state: TerrainBlendState = kit._state
    assert (state.time, state.sea_enabled, state.ground) == (2.5, False, None)
    ground = GroundTransform(2, 40)
    kit.update(_frame(3, ground))
    assert state.ground is ground
    # A frame without a ground transform keeps the last one.
    kit.update(_frame(4))
    assert state.ground is ground


@pytest.mark.usefixtures("made")
def test_gfx_water_03_the_waves_drift_with_time() -> None:
    look = make_look()
    kit = _kit(look)
    kit.update(_frame(8))
    bump = kit.sea.bumpTexture
    drift = look.sea.drift
    assert bump.uOffset == pytest.approx(8 * drift[0] / look.sea.tileSize)
    assert bump.vOffset == pytest.approx(8 * drift[1] / look.sea.tileSize)


def test_gfx_terrain_16_the_lava_churns_in_the_fog_of_the_frame(made: Made) -> None:
    kit = _kit(_lava_look())
    kit.update(_frame(5))
    [lava] = made.lavas
    [frame] = lava.frames
    assert frame.time == 5
    assert (frame.fog.color, frame.fog.start, frame.fog.end) == ((0.1, 0.2, 0.3), 50, 500)
    # The lava's own material has no wave texture to drift.
    assert not hasattr(kit.sea, "bumpTexture")
