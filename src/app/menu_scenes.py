"""The 3D scenes behind the menus, ported from `app/menu-scenes.ts`: the game's backdrop, and the
ship select stage over it.
"""

from org.transcrypt.stubs.browser import __pragma__

from config.menu import MENU_CONFIG
from render.babylon import js_object, js_set, new_scene
from render.environment.showcase_environment_visual import (
    ShowcaseEnvironmentOptions,
    apply_showcase_environment,
)
from render.ship_select_stage import ShipSelectStage

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class MenuScenes:
    """The 3D scenes behind the menus: the game's backdrop, and the ship select stage over it."""

    def __init__(self, backdrop_scene: Any, backdrop: Any, ship_scene: Any, stage: Any) -> None:
        self.backdrop_scene = backdrop_scene
        self.backdrop = backdrop
        self.ship_scene = ship_scene
        self.stage = stage


class MenuSceneLoad:
    """The loading tasks that build the menu scenes, and the function that returns them."""

    def __init__(self, tasks: list[Any], result: Any) -> None:
        self.tasks = tasks
        self.result = result


class _Built:
    """What the loading tasks have built so far (filled in step by step)."""

    def __init__(self) -> None:
        self.backdrop_scene: Any = None
        self.backdrop: Any = None
        self.ship_scene: Any = None
        self.stage: Any = None


def _ship_models(game: Any) -> list[Any]:
    models = game.view.player_ship_models
    factories: list[Any] = []
    for ship in game.player_ships.ships:
        factory = models.get(ship.id)
        if not factory:
            raise ValueError('No model for player ship "' + ship.id + '"')
        factories.append(factory)
    return factories


def _stage_options() -> Any:
    """The ship select stage's layout and look: the config's `ship_select` (see below)."""
    return MENU_CONFIG.ship_select


def _environment_options() -> Any:
    """The options of the showcase environment: the config's `environment` and `glow` (the TS
    spread `{...MENU_CONFIG.environment, glow}`); the config classes have the fields of the render
    option classes, which Python matches by structure.
    """
    environment: Any = MENU_CONFIG.environment
    glow: Any = MENU_CONFIG.glow
    return ShowcaseEnvironmentOptions(
        environment.cube_size, environment.intensity, environment.stops, glow
    )


def _build_backdrop(built: _Built, engine: Any, game: Any, environment: bool) -> None:
    built.backdrop_scene = new_scene(engine)
    metadata = js_object()
    js_set(metadata, "gameId", game.id)
    js_set(built.backdrop_scene, "metadata", metadata)
    built.backdrop = game.view.menu_backdrop(built.backdrop_scene)
    if not environment:
        return
    glow = apply_showcase_environment(built.backdrop_scene, _environment_options())
    for mesh in built.backdrop.glowExcludedMeshes:
        glow.addExcludedMesh(mesh)


def _build_ships(built: _Built, engine: Any, game: Any, environment: bool) -> None:
    built.ship_scene = new_scene(engine)
    # Drawn over the backdrop: keep its colours, clear only depth.
    js_set(built.ship_scene, "autoClear", False)
    built.stage = ShipSelectStage(built.ship_scene, _ship_models(game), _stage_options())
    if environment:
        apply_showcase_environment(built.ship_scene, _environment_options())


def _highlight_ships(built: _Built, environment: bool) -> None:
    # P13-R02: each ship drawn once highlighted, hidden by the loading screen, so the GPU driver
    # has every highlight state ready before the first press on the ship select screen.
    if not environment or built.ship_scene is None or built.stage is None:
        return
    count = len(built.stage.showcase.pivots)
    for step in range(count):
        built.stage.select(count - 1 - step)
        built.ship_scene.render()


def prepare_menu_scenes(engine: Any, game: Any, environment: bool) -> MenuSceneLoad:
    """Splits the creation of the menu scenes into loading steps (P01-R02): build the backdrop,
    build the ships, then compile each scene's shaders and draw each ship highlighted once.
    `result()` is available once every task has run. `environment` (image-based lighting, glow)
    needs a real WebGL engine.
    """
    built = _Built()

    def result() -> MenuScenes:
        if built.backdrop_scene is None or built.backdrop is None:
            raise ValueError("The menu scenes are not loaded yet")
        if built.ship_scene is None or built.stage is None:
            raise ValueError("The menu scenes are not loaded yet")
        return MenuScenes(built.backdrop_scene, built.backdrop, built.ship_scene, built.stage)

    tasks: list[Any] = [
        lambda: _build_backdrop(built, engine, game, environment),
        lambda: _build_ships(built, engine, game, environment),
        lambda: _wait_backdrop(built),
        lambda: _wait_ships(built),
        lambda: _highlight_ships(built, environment),
    ]
    return MenuSceneLoad(tasks, result)


def _wait_backdrop(built: _Built) -> Any:
    if built.backdrop_scene is not None:
        return built.backdrop_scene.whenReadyAsync()
    return None


def _wait_ships(built: _Built) -> Any:
    if built.ship_scene is not None:
        return built.ship_scene.whenReadyAsync()
    return None


def render_menu_scenes(scenes: MenuScenes, screen: str) -> None:
    """Renders the scenes of `screen`: the backdrop, plus the ships on the ship select screen."""
    if screen == "loading":
        return
    scenes.backdrop_scene.render()
    if screen == "ship-select":
        scenes.ship_scene.render()
