# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/dev_model_scene.py`: the enemies and bosses viewers' scene.

The level's camera and light without its ground (DEV-MENU-13, DEV-MENU-14, DEV-MENU-08). The Babylon
helpers, the camera, the lights and the environment are fakes; the playfield framing is real.
"""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeVector, patch_babylon

from app import dev_model_scene
from app.dev_model_scene import DevModelScene, DevModelStage, build_model_scene
from app.level_scene import LevelSceneOptions
from render.scenery.playfield_framing import frame_playfield

SCREEN = SimpleNamespace(width=480, height=720)
CAMERA_LOOK = SimpleNamespace(tiltDeg=20.0, fovDeg=40.0, flightAltitude=100.0)
STAGE_CONFIG = SimpleNamespace(near_clip=50, far_clip=5000)


class FakeCamera:
    def __init__(self, scene: Any, half_fov: float, clips: tuple[float, float]) -> None:
        self.scene = scene
        self.half_fov = half_fov
        self.clips = clips
        self.position = FakeVector()
        self.targets: list[FakeVector] = []

    def setTarget(self, target: FakeVector) -> None:
        self.targets.append(target)


class FakeTrack:
    """An atmosphere track: the look and scroll speed it was made of, and where it was read."""

    def __init__(self, look: Any, scroll_speed: float) -> None:
        self.look = look
        self.scroll_speed = scroll_speed
        self.read_at: list[float] = []

    def at(self, distance: float) -> str:
        self.read_at.append(distance)
        return "atmosphere-at-" + str(distance)


class FakeGlow:
    def __init__(self) -> None:
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


class Recorder:
    """What the scene asks of the render layer, recorded."""

    def __init__(self) -> None:
        self.tracks: list[FakeTrack] = []
        self.lit: list[tuple[Any, Any]] = []
        self.environments: list[tuple[Any, Any]] = []
        self.glows: list[FakeGlow] = []
        self.layers: list[tuple[Any, Any]] = []

    def atmosphere_track(self, look: Any, scroll_speed: float) -> FakeTrack:
        track = FakeTrack(look, scroll_speed)
        self.tracks.append(track)
        return track

    def light_scenery(self, scene: Any, atmosphere: Any) -> str:
        self.lit.append((scene, atmosphere))
        return "lights"

    def apply_showcase_environment(self, scene: Any, options: Any) -> FakeGlow:
        self.environments.append((scene, options))
        glow = FakeGlow()
        self.glows.append(glow)
        return glow

    def playfield_layer(self, scene: Any, options: Any) -> SimpleNamespace:
        self.layers.append((scene, options))
        return SimpleNamespace(root=SimpleNamespace(position=None))


@pytest.fixture
def render(monkeypatch: pytest.MonkeyPatch) -> Recorder:
    patch_babylon(monkeypatch, dev_model_scene)
    fake = Recorder()
    monkeypatch.setattr(dev_model_scene, "new_scene", lambda engine: SimpleNamespace(engine=engine))
    monkeypatch.setattr(dev_model_scene, "stage_camera", FakeCamera)
    monkeypatch.setattr(dev_model_scene, "atmosphere_track", fake.atmosphere_track)
    monkeypatch.setattr(dev_model_scene, "light_scenery", fake.light_scenery)
    monkeypatch.setattr(
        dev_model_scene, "apply_showcase_environment", fake.apply_showcase_environment
    )
    monkeypatch.setattr(dev_model_scene, "playfield_layer", fake.playfield_layer)
    return fake


def make_look() -> SimpleNamespace:
    return SimpleNamespace(
        sky=SimpleNamespace(environmentIntensity=0.8, stops=["noon"]),
        glow=SimpleNamespace(intensity=0.6, blurKernelSize=16),
    )


def make_game(look: Any) -> SimpleNamespace:
    scenery = SimpleNamespace(camera=CAMERA_LOOK, looks={"1-1": look})
    return SimpleNamespace(screen=SCREEN, view=SimpleNamespace(scenery=scenery))


LEVEL = SimpleNamespace(id="1-1", scroll_speed=30)


def make_options(environment: bool) -> LevelSceneOptions:
    return LevelSceneOptions(LEVEL, environment, "glow", 64, STAGE_CONFIG, None, None)


def test_dev_menu_08_the_stage_has_the_level_s_camera_and_its_light_at_the_start(
    render: Recorder,
) -> None:
    look = make_look()
    scene = SimpleNamespace()
    stage = DevModelStage(scene, make_game(look), LEVEL, look, STAGE_CONFIG)
    framing = frame_playfield(SCREEN, CAMERA_LOOK)
    assert stage.framing.height == pytest.approx(framing.height)
    assert stage.camera.scene is scene
    assert stage.camera.half_fov == pytest.approx(framing.half_fov)
    assert stage.camera.clips == (50, 5000)
    (track,) = render.tracks
    assert (track.look, track.scroll_speed, track.read_at) == (look, 30, [0])
    assert render.lit == [(scene, "atmosphere-at-0")]
    assert stage.lights == "lights"


def test_dev_menu_08_the_camera_follows_the_level_as_in_game(render: Recorder) -> None:
    del render
    look = make_look()
    stage = DevModelStage(SimpleNamespace(), make_game(look), LEVEL, look, STAGE_CONFIG)
    framing = frame_playfield(SCREEN, CAMERA_LOOK)
    stage.update(400, 0.02)
    position = stage.camera.position
    assert position.x == 0
    assert position.y == pytest.approx(100 + framing.height)
    assert position.z == pytest.approx(400 + framing.back)
    (target,) = stage.camera.targets
    assert target.x == 0
    assert target.y == pytest.approx(position.y + framing.direction[0])
    assert target.z == pytest.approx(position.z + framing.direction[1])


def test_dev_menu_08_a_playfield_point_is_on_the_flight_plane_centred_across(
    render: Recorder,
) -> None:
    del render
    look = make_look()
    stage = DevModelStage(SimpleNamespace(), make_game(look), LEVEL, look, STAGE_CONFIG)
    point = stage.playfield_point(40, 10, 400)
    assert (point.x, point.y, point.z) == (40 - 240, 100, 410)


def test_dev_menu_13_with_the_environment_the_sky_lights_the_models_without_ground_glow(
    render: Recorder,
) -> None:
    """Also DEV-MENU-14 (the bosses viewer shares the scene)."""
    look = make_look()
    options = make_options(True)
    built = build_model_scene("engine", make_game(look), LEVEL, options)
    assert isinstance(built, DevModelScene)
    assert built.scene.engine == "engine"
    ((lit, environment),) = render.environments
    assert lit is built.scene
    assert environment.cube_size == 64
    assert (environment.intensity, environment.stops) == (0.8, ["noon"])
    assert environment.glow.blur_kernel_size == 16  # D-250: as the look gives it
    # There is no ground: its glow layer goes.
    assert render.glows[0].disposed is True
    assert render.layers == [(built.scene, options)]


def test_dev_menu_13_the_scene_moves_its_camera_and_playfield_along_the_level(
    render: Recorder,
) -> None:
    built = build_model_scene("engine", make_game(make_look()), LEVEL, make_options(False))
    assert render.environments == []
    built.update(250, 0.02)
    assert built.stage.camera.position.z == pytest.approx(250 + built.stage.framing.back)
    position = built.playfield.root.position
    assert (position.x, position.y, position.z) == (-240, 100, 250)
