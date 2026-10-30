"""The player ship viewer, ported from `app/start-ship-viewer.ts`: every player ship of the game,
side by side, rotating."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from config.ship_viewer import SHIP_VIEWER_CONFIG as CFG  # noqa: E402
from render.babylon import (  # noqa: E402
    camera_fov_mode_horizontal_fixed,
    color4,
    new_arc_rotate_camera,
    new_directional_light,
    new_hemispheric_light,
    new_scene,
    vector3,
    vector3_up,
    vector3_zero,
)
from render.environment.showcase_environment_visual import (  # noqa: E402
    ShowcaseEnvironmentOptions,
    ShowcaseGlow,
    apply_showcase_environment,
)
from render.mesh_stats import count_triangles  # noqa: E402
from render.model_showcase import ModelShowcase  # noqa: E402
from ui.caption_row import render_caption_row  # noqa: E402
from ui.ship_caption import ship_caption  # noqa: E402


class ShipCaptions:
    """Where to show each ship's name, stats and polygon count (`doc`, `parent`)."""

    def __init__(self, doc: Any, parent: Any) -> None:
        self.doc = doc
        self.parent = parent


class ShipViewerOptions:
    """Options of `start_ship_viewer`.

    `environment`: procedural image-based lighting and glow (needs a real WebGL engine). `captions`:
    None for no captions. `frame_seconds`: seconds elapsed since the previous frame, None for the
    engine's frame time."""

    def __init__(
        self, environment: bool, captions: ShipCaptions | None, frame_seconds: Any
    ) -> None:
        self.environment = environment
        self.captions = captions
        self.frame_seconds = frame_seconds


def frame_source(engine: Any) -> Any:
    """The engine's frame time, in seconds."""
    return lambda: engine.getDeltaTime() / 1000


def _ship_models(game: Any) -> list[Any]:
    models: list[Any] = []
    for ship in game.player_ships.ships:
        factory = game.view.player_ship_models.get(ship.id)
        if not factory:
            raise ValueError('No model for player ship "' + ship.id + '"')
        models.append(factory)
    return models


def _create_camera(scene: Any, row_width: float) -> Any:
    look = CFG.camera
    radius = ((row_width / 2) * look.framing_margin) / math.tan(look.horizontal_fov / 2)
    camera = new_arc_rotate_camera(
        "viewer-camera", look.alpha, look.beta, radius, vector3_zero(), scene
    )
    camera.fovMode = camera_fov_mode_horizontal_fixed()
    camera.fov = look.horizontal_fov
    camera.lowerRadiusLimit = radius * look.min_zoom_factor
    camera.upperRadiusLimit = radius * look.max_zoom_factor
    if scene.getEngine().getRenderingCanvas():
        camera.attachControl(True)
    return camera


def _add_lights(scene: Any) -> None:
    lights = CFG.lights
    ambient = new_hemispheric_light("viewer-ambient", vector3_up(), scene)
    ambient.intensity = lights.ambient_intensity
    key = new_directional_light(
        "viewer-key",
        vector3(lights.key_direction[0], lights.key_direction[1], lights.key_direction[2]),
        scene,
    )
    key.intensity = lights.key_intensity
    rim = new_directional_light(
        "viewer-rim",
        vector3(lights.rim_direction[0], lights.rim_direction[1], lights.rim_direction[2]),
        scene,
    )
    rim.intensity = lights.rim_intensity


class RunningShipViewer:
    """Handle on a running ship viewer: its `scene`, `camera` and `showcase`."""

    def __init__(self, engine: Any, scene: Any, camera: Any, showcase: Any, row: Any) -> None:
        self._engine = engine
        self.scene = scene
        self.camera = camera
        self.showcase = showcase
        self._row = row

    def dispose(self) -> None:
        self._engine.stopRenderLoop()
        if self._row:
            self._row.remove()
        self.scene.dispose()


def start_ship_viewer(engine: Any, game: Any, options: ShipViewerOptions) -> RunningShipViewer:
    """Starts the player ship viewer: every player ship of the game, side by side, rotating."""
    models = _ship_models(game)
    scene = new_scene(engine)
    clear = CFG.clear_color
    scene.clearColor = color4(clear[0], clear[1], clear[2], clear[3])
    showcase_options: Any = CFG
    showcase = ModelShowcase(scene, models, showcase_options)
    camera = _create_camera(scene, showcase.width)
    _add_lights(scene)
    if options.environment:
        env: Any = CFG.environment
        glow: Any = CFG.glow
        apply_showcase_environment(
            scene,
            ShowcaseEnvironmentOptions(
                env.cube_size,
                env.intensity,
                env.stops,
                ShowcaseGlow(glow.intensity, glow.blur_kernel_size),
            ),
        )

    captions = options.captions
    row = None
    if captions:
        entries: list[Any] = []
        for i, ship in enumerate(game.player_ships.ships):
            pivot = showcase.pivots[i] if i < len(showcase.pivots) else None
            polygons = count_triangles(pivot) if pivot else None
            entries.append(ship_caption(game.player_ships, ship.id, polygons))
        row = render_caption_row(
            captions.doc, captions.parent, entries, 100 / CFG.camera.framing_margin
        )

    frame_seconds = options.frame_seconds if options.frame_seconds else frame_source(engine)
    scene.onBeforeRenderObservable.add(lambda _info: showcase.update(frame_seconds()))

    def render_frame() -> None:
        scene.render()

    engine.runRenderLoop(render_frame)
    return RunningShipViewer(engine, scene, camera, showcase, row)
