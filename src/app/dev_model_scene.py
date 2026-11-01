"""The scene of the enemies and bosses viewers (D-199): no level's ground (no terrain, roads, props,
sea nor clouds, and no wait for the ground worker), only the level's light and sky reflections, the
game's playfield camera and the playfield layer the models are drawn on. The models are lit and
framed as in the level, over a plain dark backdrop.
"""

from org.transcrypt.stubs.browser import __pragma__

from app.level_scene import LevelSceneOptions, ground_glow_look, playfield_layer, scenery_look
from render.babylon import new_scene, vector3
from render.environment.showcase_environment_visual import (
    ShowcaseEnvironmentOptions,
    apply_showcase_environment,
)
from render.scenery.atmosphere_of import atmosphere_track
from render.scenery.playfield_framing import frame_playfield
from render.scenery.scenery_lighting import light_scenery
from render.scenery.stage_parts import stage_camera

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class DevModelStage:
    """The playfield camera of a level, without its ground: `camera`, `framing`, `update` and
    `playfield_point` as a `SceneryStage`'s."""

    def __init__(self, scene: Any, game: Any, level: Any, look: Any, config: Any) -> None:
        self.scene = scene
        self._screen = game.screen
        self._camera_look = game.view.scenery.camera
        self.framing = frame_playfield(self._screen, self._camera_look)
        self.camera = stage_camera(
            scene, self.framing.half_fov, (config.near_clip, config.far_clip)
        )
        self.lights = light_scenery(scene, atmosphere_track(look, level.scroll_speed).at(0))

    def playfield_point(self, x: float, y: float, distance: float) -> Any:
        """World position of a playfield point (logical pixels, origin at its bottom left)."""
        return vector3(x - self._screen.width / 2, self._camera_look.flightAltitude, distance + y)

    def update(self, distance: float, _dt: float) -> None:
        """Puts the camera where the level's is at `distance` along it."""
        camera = self.camera.position
        camera.set(
            0,
            self._camera_look.flightAltitude + self.framing.height,
            distance + self.framing.back,
        )
        dy = self.framing.direction[0]
        dz = self.framing.direction[1]
        self.camera.setTarget(vector3(0, camera.y + dy, camera.z + dz))


class DevModelScene:
    """What the viewer draws the models in: `scene`, `stage` (a `DevModelStage`) and `playfield`
    (the playfield layer, as a `LevelScene`'s); `update` moves them along the level."""

    def __init__(self, scene: Any, stage: DevModelStage, playfield: Any) -> None:
        self.scene = scene
        self.stage = stage
        self.playfield = playfield

    def update(self, distance: float, dt: float) -> None:
        self.stage.update(distance, dt)
        self.playfield.root.position = self.stage.playfield_point(0, 0, distance)


def build_model_scene(engine: Any, game: Any, level: Any, options: LevelSceneOptions) -> Any:
    """The models' scene for `level` (its light and sky), built at once: see the module doc."""
    look = scenery_look(game, level)
    scene = new_scene(engine)
    if options.environment:
        glow = apply_showcase_environment(
            scene,
            ShowcaseEnvironmentOptions(
                options.environment_cube_size,
                look.sky.environmentIntensity,
                look.sky.stops,
                ground_glow_look(look.glow),
            ),
        )
        # The ground's glow layer: there is no ground, the playfield has its own.
        glow.dispose()
    stage = DevModelStage(scene, game, level, look, options.stage)
    return DevModelScene(scene, stage, playfield_layer(scene, options))
