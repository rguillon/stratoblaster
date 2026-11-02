# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/level_scene.py`: a level's scene, its glows and its playfield layer.

The Babylon helpers are the `render_fakes` ones; the scenery stage, the glow layers, the outline
layer and the environment are recording fakes.
"""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, FakeVector, patch_babylon

from app import level_scene
from app.level_scene import (
    GROUND_GLOW_SAMPLES,
    LevelScene,
    LevelSceneOptions,
    build_level_scene,
    compile_shaders,
    ground_glow_look,
    playfield_layer,
    scenery_look,
    sky_state,
)
from render import node_adopter
from render.scenery.cloud_layers import ABOVE_CLOUDS_GROUP, BELOW_CLOUDS_GROUP


class FakeGlowLayer:
    """A glow layer: the meshes it draws, and those drawn with their own material."""

    def __init__(self, args: tuple[Any, ...] = ()) -> None:
        self.args = args
        self.included: list[Any] = []
        self.own_material: list[Any] = []
        self.intensity = 0.0
        self.renderingGroupId = 0

    def addIncludedOnlyMesh(self, mesh: Any) -> None:
        self.included.append(mesh)

    def referenceMeshToUseItsOwnMaterial(self, mesh: Any) -> None:
        self.own_material.append(mesh)


class FakeOutlineLayer:
    def __init__(self, look: Any) -> None:
        self.look = look
        self.added: list[Any] = []

    def add(self, mesh: Any) -> bool:
        self.added.append(mesh)
        return True


class FakeStage:
    """The scenery stage: what the ground's glow reads, and where the playfield is."""

    def __init__(self, scene: Any, options: Any) -> None:
        self.scene = scene
        self.options = options
        self.glowing_meshes = ["street-light"]
        self.glow_occluders = ["building"]
        self.window_meshes = ["windows"]
        self.lava: Any = "lava"
        self.terrain_watchers: list[Any] = []
        self.updates: list[tuple[float, float]] = []
        self.atmosphere = SimpleNamespace(
            sky=SimpleNamespace(stops=["dawn"], environment_intensity=0.7)
        )

    def watch_terrain(self, on_chunk: Any) -> None:
        self.terrain_watchers.append(on_chunk)

    def update(self, distance: float, dt: float) -> None:
        self.updates.append((distance, dt))

    def playfield_point(self, x: float, y: float, distance: float) -> FakeVector:
        return FakeVector(x, y, distance)


class Recorder:
    """What `level_scene` calls in the render layer, recorded."""

    def __init__(self) -> None:
        self.glow_layers: list[FakeGlowLayer] = []
        self.outlines: list[FakeOutlineLayer] = []
        self.environments: list[tuple[Any, Any]] = []
        self.environment_glows: list[FakeGlowLayer] = []
        self.sky_updates: list[tuple[Any, ...]] = []
        self.compiled_outlines: list[Any] = []
        self.stages: list[FakeStage] = []
        self.lava = True

    def new_glow_layer(self, *args: Any) -> FakeGlowLayer:
        layer = FakeGlowLayer(args)
        self.glow_layers.append(layer)
        return layer

    def outline_layer(self, look: Any) -> FakeOutlineLayer:
        layer = FakeOutlineLayer(look)
        self.outlines.append(layer)
        return layer

    def apply_showcase_environment(self, scene: Any, options: Any) -> FakeGlowLayer:
        self.environments.append((scene, options))
        glow = FakeGlowLayer()
        self.environment_glows.append(glow)
        return glow

    def update_sky_environment(self, *args: Any) -> None:
        self.sky_updates.append(args)

    def scenery_stage(self, scene: Any, options: Any) -> FakeStage:
        stage = FakeStage(scene, options)
        if not self.lava:
            stage.lava = None
        self.stages.append(stage)
        return stage


@pytest.fixture
def render(monkeypatch: pytest.MonkeyPatch) -> Recorder:
    patch_babylon(monkeypatch, level_scene)
    patch_babylon(monkeypatch, node_adopter)
    fake = Recorder()
    monkeypatch.setattr(level_scene, "new_scene", lambda _engine: FakeScene())
    monkeypatch.setattr(level_scene, "new_glow_layer", fake.new_glow_layer)
    monkeypatch.setattr(level_scene, "OutlineLayer", fake.outline_layer)
    monkeypatch.setattr(level_scene, "apply_showcase_environment", fake.apply_showcase_environment)
    monkeypatch.setattr(level_scene, "update_sky_environment", fake.update_sky_environment)
    monkeypatch.setattr(level_scene, "compile_outlines", fake.compiled_outlines.append)
    monkeypatch.setattr(level_scene, "SceneryStage", fake.scenery_stage)
    return fake


class FakeScenery:
    """`game.view.scenery`: read by attribute, and by key for its prop models (ENG-156)."""

    def __init__(self, looks: dict[str, Any]) -> None:
        self.looks = looks
        self.camera = "camera-look"
        self._fields = {"propModels": "prop-models"}

    def __getitem__(self, key: str) -> Any:
        return self._fields[key]


def make_look() -> SimpleNamespace:
    return SimpleNamespace(
        sky=SimpleNamespace(environmentIntensity=0.8, stops=["noon"]),
        glow=SimpleNamespace(intensity=0.6, blurKernelSize=16),
    )


def make_level() -> SimpleNamespace:
    return SimpleNamespace(
        id="1-1",
        scroll_speed=20,
        sections=[SimpleNamespace(seconds=10), SimpleNamespace(seconds=5)],
    )


def make_game(look: Any) -> SimpleNamespace:
    return SimpleNamespace(
        screen="screen", view=SimpleNamespace(scenery=FakeScenery({"1-1": look}))
    )


def make_options(environment: bool, outline: Any = None) -> LevelSceneOptions:
    playfield_glow = SimpleNamespace(blurKernelSize=32, intensity=0.9)
    return LevelSceneOptions(
        make_level(), environment, playfield_glow, 64, "stage-config", "atmosphere", outline
    )


def test_perf_20_the_shaders_of_meshes_with_a_material_and_their_rims_are_compiled(
    render: Recorder,
) -> None:
    material = SimpleNamespace(compiled=[])
    material.forceCompilation = material.compiled.append
    drawn = SimpleNamespace(material=material, subMeshes=["sub"])
    bare = SimpleNamespace(material=None, subMeshes=["sub"])
    empty = SimpleNamespace(material=material, subMeshes=[])
    meshes = [drawn, bare, empty]
    compile_shaders(meshes)
    assert material.compiled == [drawn]
    assert render.compiled_outlines == [meshes]


def test_dev_menu_08_the_look_of_a_level_is_found_or_is_an_error() -> None:
    look = make_look()
    game = make_game(look)
    assert scenery_look(game, SimpleNamespace(id="1-1")) is look
    with pytest.raises(ValueError, match='No look for scenery level "9-9"'):
        scenery_look(game, SimpleNamespace(id="9-9"))


def test_gfx_terrain_15_the_ground_glow_is_full_resolution_antialiased_and_as_wide() -> None:
    glow = ground_glow_look(SimpleNamespace(intensity=0.6, blurKernelSize=16))
    assert glow.intensity == 0.6
    # Twice Babylon's default resolution: twice the blur, as wide on screen.
    assert glow.blur_kernel_size == 32
    assert glow.ratio == 1
    assert glow.samples == GROUND_GLOW_SAMPLES


def _sky_view(look: Any, lava: Any, weather: Any, second: Any) -> SimpleNamespace:
    atmosphere = SimpleNamespace(
        weather=weather,
        second_weather=second,
        lightning=0.3,
        aurora=0.2,
        ground_lights=0.4,
        sun=SimpleNamespace(intensity=1.5),
        fog=SimpleNamespace(end=900),
    )
    stage = SimpleNamespace(
        atmosphere=atmosphere,
        weather_particles=120,
        rain_rings=0.5,
        lightning_flash=0.1,
        lava=lava,
        plumes=3,
        field=SimpleNamespace(height=lambda x, z: 4.0 if (x, z) == (0, 50) else math.nan),
    )
    return SimpleNamespace(stage=stage, look=look)


def test_dev_api_05_the_sky_state_tells_the_weathers_light_fog_and_liquid() -> None:
    view = _sky_view(
        SimpleNamespace(shotStyle="ice"),
        "lava-mesh",
        SimpleNamespace(kind="rain", strength=0.5),
        SimpleNamespace(kind="snow", strength=0),
    )
    sky = sky_state(view, SimpleNamespace(level=10.0), 50)
    assert sky == {
        "weather": "rain",
        # A weather of no strength is no weather.
        "secondWeather": "none",
        "weatherParticles": 120,
        "rainRings": 0.5,
        "lightning": 0.3,
        "flash": 0.1,
        "aurora": 0.2,
        "groundLights": 0.4,
        "sunIntensity": 1.5,
        "fogEnd": 900,
        "lava": True,
        # The liquid's level over the ground under the middle of the playfield.
        "liquidDepth": 6.0,
        "plumes": 3,
        "shotStyle": "ice",
    }


def test_dev_api_05_without_weather_sea_or_shot_style_the_defaults_are_told() -> None:
    """Also GFX-READ-11 (the default shot style)."""
    view = _sky_view(SimpleNamespace(shotStyle=None), None, None, None)
    sky = sky_state(view, None, 50)
    assert (sky["weather"], sky["secondWeather"]) == ("none", "none")
    assert sky["lava"] is False
    assert sky["liquidDepth"] == 0
    assert sky["shotStyle"] == "default"


def _adopt(adopter: Any, scene: FakeScene, make: Any) -> list[FakeNode]:
    made: list[FakeNode] = []

    def create() -> None:
        made.extend(make(scene))

    adopter.run(create)
    return made


def _playfield_meshes(scene: FakeScene) -> list[FakeNode]:
    neon = scene.add_node("neon", is_mesh=True)
    shot = scene.add_node("shot", is_mesh=True)
    shot.material = SimpleNamespace(alphaMode="ALPHA_ADD")
    smoke = scene.add_node("smoke", is_mesh=True)
    smoke.hasVertexAlpha = True
    # An instance is in the scene's meshes but is no `Mesh`.
    instance = FakeNode("instance", scene.next_id())
    scene.meshes.append(instance)
    return [neon, shot, smoke, instance]


def test_gfx_art_02_only_the_ships_neon_glows_on_the_playfield_above_the_clouds(
    render: Recorder,
) -> None:
    """Also GFX-CAM-07 (above the clouds) and phase 14 (every mesh may ask for its rim)."""
    scene = FakeScene()
    adopter = playfield_layer(scene, make_options(True, "outline-look"))
    assert adopter.root.name == "playfield"
    assert adopter.root.rotation.x == pytest.approx(math.pi / 2)
    assert adopter.rendering_group_id == ABOVE_CLOUDS_GROUP
    (glow,) = render.glow_layers
    assert glow.args == ("playfield-glow", scene, 32, None, None)
    assert (glow.intensity, glow.renderingGroupId) == (0.9, ABOVE_CLOUDS_GROUP)
    neon, shot, smoke, instance = _adopt(adopter, scene, _playfield_meshes)
    assert glow.included == [neon]
    (outline,) = render.outlines
    assert outline.look == "outline-look"
    assert outline.added == [neon, shot, smoke, instance]
    assert neon.parent is adopter.root


def test_gfx_art_02_without_the_environment_or_rims_nothing_glows_nor_is_rimmed(
    render: Recorder,
) -> None:
    scene = FakeScene()
    adopter = playfield_layer(scene, make_options(False))
    (neon, *_) = _adopt(adopter, scene, _playfield_meshes)
    assert render.glow_layers == []
    assert render.outlines == []
    assert neon.parent is adopter.root


def test_dev_menu_08_a_plain_level_scene_has_its_stage_track_and_playfield(
    render: Recorder,
) -> None:
    look = make_look()
    game = make_game(look)
    options = make_options(False)
    scene = build_level_scene("engine", game, options)
    assert isinstance(scene, LevelScene)
    assert render.environments == []
    (stage,) = render.stages
    assert scene.stage is stage
    assert stage.scene is scene.scene
    stage_options = stage.options
    assert stage_options.screen == "screen"
    assert stage_options.camera == "camera-look"
    assert stage_options.level is options.level
    assert stage_options.look is look
    assert stage_options.prop_models == "prop-models"
    assert stage_options.kit is level_scene.create_plain_scenery_kit
    assert stage_options.config == "stage-config"
    assert stage_options.atmosphere == "atmosphere"
    assert scene.look is look
    # 15 s of scrolling at 20 units a second.
    assert (scene.track.speed, scene.track.length_) == (20, 300)
    assert scene.playfield.root.name == "playfield"


@pytest.mark.parametrize("lava", [True, False])
def test_gfx_terrain_15_with_the_environment_the_ground_glows_without_glowing_through(
    render: Recorder, lava: bool
) -> None:
    """Also GFX-BLDG-15 (only lit windows) and GFX-TERRAIN-18 (the lava, with its own material)."""
    render.lava = lava
    scene = build_level_scene("engine", make_game(make_look()), make_options(True))
    ((lit, environment),) = render.environments
    assert lit is scene.scene
    assert environment.cube_size == 64
    assert (environment.intensity, environment.stops) == (0.8, ["noon"])
    assert environment.glow.blur_kernel_size == 32
    (stage,) = render.stages
    assert stage.options.kit is level_scene.create_scenery_kit
    (glow,) = render.environment_glows
    assert glow.renderingGroupId == BELOW_CLOUDS_GROUP
    # Each terrain chunk is added as it is built, drawn black there.
    (terrain_watcher,) = stage.terrain_watchers
    terrain_watcher("chunk")
    lava_mesh = ["lava"] if lava else []
    assert glow.included == ["street-light", "building", *lava_mesh, "chunk"]
    assert glow.own_material == ["windows", *lava_mesh]


@pytest.mark.parametrize(("environment", "sky_updates"), [(True, 1), (False, 0)])
def test_gfx_sky_05_a_level_scene_follows_the_level_and_its_sky(
    render: Recorder, environment: bool, sky_updates: int
) -> None:
    """Also GFX-SKY-10 (the sky lighting is its gradient's reflections, with the environment)."""
    scene = build_level_scene("engine", make_game(make_look()), make_options(environment))
    scene.update(120, 0.02)
    (stage,) = render.stages
    assert stage.updates == [(120, 0.02)]
    position = scene.playfield.root.position
    assert (position.x, position.y, position.z) == (0, 0, 120)
    assert render.sky_updates == [(scene.scene, 64, ["dawn"], 0.7)] * sky_updates
