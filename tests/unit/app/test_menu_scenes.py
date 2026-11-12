# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/menu_scenes.py`: the menu scene's loading steps and its drawing.

Babylon's scenes and the showcase environment are fakes here.
"""

from types import SimpleNamespace
from typing import Any

import pytest

from app import menu_scenes
from app.menu_scenes import MenuScenes, prepare_menu_scenes, render_menu_scenes
from config.menu import MENU_CONFIG


class FakeScene:
    """A Babylon scene: what is drawn, and the promise `whenReadyAsync` gives."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.renders = 0
        self.metadata: Any = None
        self.ready = "ready:" + label
        self.activeCamera = SimpleNamespace(viewport=None)

    def render(self) -> None:
        self.renders += 1

    def whenReadyAsync(self) -> str:
        return self.ready


class FakeGlow:
    def __init__(self) -> None:
        self.excluded: list[str] = []

    def addExcludedMesh(self, mesh: str) -> None:
        self.excluded.append(mesh)


class Babylon:
    """What `menu_scenes` calls instead of Babylon: the scenes made and the environments applied."""

    def __init__(self) -> None:
        self.scenes: list[FakeScene] = []
        self.environments: list[tuple[FakeScene, Any]] = []
        self.glows: list[FakeGlow] = []

    def new_scene(self, engine: str) -> FakeScene:
        assert engine == "engine"
        scene = FakeScene("scene" + str(len(self.scenes)))
        self.scenes.append(scene)
        return scene

    def apply_showcase_environment(self, scene: FakeScene, options: Any) -> FakeGlow:
        self.environments.append((scene, options))
        glow = FakeGlow()
        self.glows.append(glow)
        return glow


def _js_set(target: Any, key: str, value: Any) -> None:
    if isinstance(target, dict):
        target[key] = value
    else:
        setattr(target, key, value)


@pytest.fixture
def babylon(monkeypatch: pytest.MonkeyPatch) -> Babylon:
    fake = Babylon()
    monkeypatch.setattr(menu_scenes, "new_scene", fake.new_scene)
    monkeypatch.setattr(menu_scenes, "apply_showcase_environment", fake.apply_showcase_environment)
    monkeypatch.setattr(menu_scenes, "js_object", dict)
    monkeypatch.setattr(menu_scenes, "js_set", _js_set)
    monkeypatch.setattr(menu_scenes, "new_viewport", lambda *box: box)
    return fake


def make_game(viewport: tuple[float, float, float, float] | None = None) -> SimpleNamespace:
    backdrop = SimpleNamespace(glowExcludedMeshes=["sky", "sun"])

    def menu_backdrop(scene: FakeScene) -> Any:
        backdrop.scene = scene
        return backdrop

    return SimpleNamespace(
        id="strato",
        playfield=SimpleNamespace(viewport=viewport),
        view=SimpleNamespace(menu_backdrop=menu_backdrop),
    )


def run_tasks(tasks: list[Any]) -> list[Any]:
    return [task() for task in tasks]


def test_ui_load_03_the_menu_scene_is_built_in_loading_steps(babylon: Babylon) -> None:
    """Also UI-TITLE-09 (the game's backdrop behind the menus)."""
    game = make_game()
    load = prepare_menu_scenes("engine", game, True)
    assert len(load.tasks) == 2
    waits = run_tasks(load.tasks)
    (backdrop_scene,) = babylon.scenes
    # The wait is the scene's own readiness promise.
    assert waits[1] == backdrop_scene.ready
    scenes = load.result()
    assert isinstance(scenes, MenuScenes)
    assert scenes.backdrop_scene is backdrop_scene
    assert scenes.backdrop.scene is backdrop_scene
    assert backdrop_scene.metadata == {"gameId": "strato"}


def test_ui_load_03_with_the_environment_the_backdrop_is_lit_and_glows(
    babylon: Babylon,
) -> None:
    run_tasks(prepare_menu_scenes("engine", make_game(), True).tasks)
    (backdrop_scene,) = babylon.scenes
    assert [scene for scene, _ in babylon.environments] == [backdrop_scene]
    options = babylon.environments[0][1]
    environment = MENU_CONFIG.environment
    assert options.cube_size == environment.cube_size
    assert options.intensity == environment.intensity
    assert options.stops == environment.stops
    assert options.glow is MENU_CONFIG.glow
    # The backdrop's own meshes stay out of its glow.
    assert babylon.glows[0].excluded == ["sky", "sun"]


def test_ui_load_03_without_the_environment_nothing_is_lit(babylon: Babylon) -> None:
    run_tasks(prepare_menu_scenes("engine", make_game(), False).tasks)
    assert babylon.environments == []
    assert [scene.renders for scene in babylon.scenes] == [0]


def test_ui_look_02_the_menu_scene_draws_in_the_playfield_window(babylon: Babylon) -> None:
    """D-319: the menus have the game's aspect ratio, their 3D drawn where a level is."""
    run_tasks(prepare_menu_scenes("engine", make_game(viewport=(0.25, 0, 0.5, 1)), False).tasks)
    assert [scene.activeCamera.viewport for scene in babylon.scenes] == [(0.25, 0, 0.5, 1)]


def test_ui_look_02_without_a_playfield_window_the_menus_take_the_screen(babylon: Babylon) -> None:
    run_tasks(prepare_menu_scenes("engine", make_game(), False).tasks)
    assert [scene.activeCamera.viewport for scene in babylon.scenes] == [None]


def test_ui_load_03_the_scene_is_not_there_before_its_steps_ran(babylon: Babylon) -> None:
    load = prepare_menu_scenes("engine", make_game(), True)
    # Waiting on a scene not built yet does nothing.
    assert load.tasks[1]() is None
    with pytest.raises(ValueError, match="not loaded yet"):
        load.result()
    assert babylon.scenes == []


@pytest.mark.parametrize(("screen", "drawn"), [("loading", 0), ("title", 1), ("level-select", 1)])
def test_ui_title_09_the_backdrop_is_drawn_behind_the_menus(screen: str, drawn: int) -> None:
    """Nothing on the loading screen."""
    backdrop_scene = FakeScene("backdrop")
    render_menu_scenes(MenuScenes(backdrop_scene, None), screen)
    assert backdrop_scene.renders == drawn
