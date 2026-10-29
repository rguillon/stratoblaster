"""The scene of a level under the playfield camera, ported from `app/level-scene.ts` (P04,
P05-R11, P06-R02): its generated ground, and a playfield layer above it where ships, enemies and
shots are drawn.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from app.game_play_state import game_play_sky
from core.scenery.scenery_level import level_length
from core.scenery.scroll_track import ScrollTrack
from render.babylon import (
    babylon_constant,
    is_instance_of,
    new_glow_layer,
    new_scene,
    new_transform_node,
)
from render.environment.showcase_environment_visual import (
    ShowcaseEnvironmentOptions,
    ShowcaseGlow,
    apply_showcase_environment,
    update_sky_environment,
)
from render.node_adopter import NodeAdopter
from render.outline import OutlineLayer
from render.scenery.cloud_layers import ABOVE_CLOUDS_GROUP, BELOW_CLOUDS_GROUP
from render.scenery.scenery_kit import create_plain_scenery_kit
from render.scenery.scenery_kit_visual import create_scenery_kit
from render.scenery.scenery_stage import SceneryStage
from render.scenery.scenery_stage_options import SceneryStageOptions

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Babylon's default resolution of a glow image, as a share of the screen's.
DEFAULT_GLOW_RATIO = 0.5

# Samples per pixel of the ground's glow image (antialiased: thin lights do not flicker).
GROUND_GLOW_SAMPLES = 4


class LevelSceneOptions:
    """What `build_level_scene` shows and how: `level` (the scenery), `environment` (generated
    textures, sky lighting, shadows and glow; needs a real WebGL engine), `glow` (of the
    playfield's self-lit parts), `environment_cube_size`, `stage` (its config), `atmosphere`
    (debug choices on the level's look, P08-R12, or None) and `outline` (rims, P14-R03, or None).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        level: Any,
        environment: bool,
        glow: Any,
        environment_cube_size: int,
        stage: Any,
        atmosphere: Any,
        outline: Any,
    ) -> None:
        self.level = level
        self.environment = environment
        self.glow = glow
        self.environment_cube_size = environment_cube_size
        self.stage = stage
        self.atmosphere = atmosphere
        self.outline = outline


def compile_shaders(meshes: Any) -> None:
    """Compiles the shaders of `meshes` (in parallel where WebGL can, P13-R04)."""
    for mesh in meshes:
        material = mesh.material
        if material is not None and len(mesh.subMeshes) > 0:
            material.forceCompilation(mesh)


def scenery_look(game: Any, level: Any) -> Any:
    """The look of `level`, or a descriptive error."""
    look = game.view.scenery.looks.get(level.id)
    if look is None:
        raise ValueError('No look for scenery level "' + level.id + '"')
    return look


def _playfield_glow(scene: Any, look: Any) -> Any:
    """A glow layer for the playfield's self-lit parts (enemy neon, shots), above the clouds."""
    glow = new_glow_layer("playfield-glow", scene, look.blurKernelSize, None, None)
    glow.intensity = look.intensity
    glow.renderingGroupId = ABOVE_CLOUDS_GROUP
    return glow


def ground_glow_look(glow: Any) -> Any:
    """The ground's glow drawn at full resolution and antialiased (reviewer, 2026-10-28: small
    lights blinked as the ground scrolled), its blur as wide on screen as before.
    """
    ratio = 1
    return ShowcaseGlow(
        glow.intensity,
        (glow.blurKernelSize * ratio) / DEFAULT_GLOW_RATIO,
        ratio,
        GROUND_GLOW_SAMPLES,
    )


def _glow_lava(glow: Any, stage: Any) -> None:
    """Phase 10 (P10-R05): the lava blooms in the ground's glow layer with its own material, the
    terrain drawn there too, black, so hills hide the lava under them.
    """
    lava = stage.lava
    if lava is None:
        return
    glow.addIncludedOnlyMesh(lava)
    glow.referenceMeshToUseItsOwnMaterial(lava)


def _glow_ground(glow: Any, stage: Any) -> None:
    """The ground's glow (reviewer, 2026-10-28): the lights, and the props, cars and terrain, drawn
    black there, so a light behind a building or a hill does not glow through it.
    """
    # Lists are concatenated by extend: `+` on two lists is a string concatenation in JavaScript.
    for mesh in stage.glowing_meshes:
        glow.addIncludedOnlyMesh(mesh)
    for mesh in stage.glow_occluders:
        glow.addIncludedOnlyMesh(mesh)

    def add_terrain(mesh: Any) -> None:
        glow.addIncludedOnlyMesh(mesh)

    stage.watch_terrain(add_terrain)
    _glow_lava(glow, stage)


def sky_state(view: Any, sea: Any, middle: float) -> Any:
    """How the level looks where the view is, for the test API (P08 ... P10): its weathers,
    lightning, aurora, light and fog, and (phase 10) whether its liquid (`sea`) is lava, how deep
    it is under the playfield at `middle` (<= 0: ground), the plumes drawn and the shot style.
    """
    stage = view.stage
    look = view.look
    atmosphere = stage.atmosphere

    def kind(weather: Any) -> str:
        return weather.kind if weather is not None and weather.strength > 0 else "none"

    liquid_depth = 0
    if sea is not None:
        liquid_depth = sea.level - stage.field.height(0, middle)
    shot_style = look.shotStyle if look.shotStyle is not None else "default"
    return game_play_sky(
        kind(atmosphere.weather),
        kind(atmosphere.second_weather),
        stage.weather_particles,
        stage.rain_rings,
        atmosphere.lightning,
        stage.lightning_flash,
        atmosphere.aurora,
        atmosphere.ground_lights,
        atmosphere.sun.intensity,
        atmosphere.fog.end,
        stage.lava is not None,
        liquid_depth,
        stage.plumes,
        shot_style,
    )


def _follow_sky(stage: Any, cube_size: int) -> None:
    """The sky lighting of `stage`'s scene, as its look is now (P08-R04)."""
    sky = stage.atmosphere.sky
    update_sky_environment(stage.scene, cube_size, sky.stops, sky.environment_intensity)


def _playfield_layer(scene: Any, options: LevelSceneOptions) -> NodeAdopter:
    """The playfield layer of a level: what is created through it is drawn above the clouds, with
    the playfield's glow and (phase 14) the rims meshes ask for.
    """
    glow = _playfield_glow(scene, options.glow) if options.environment else None
    outline = OutlineLayer(options.outline) if options.outline is not None else None
    root = new_transform_node("playfield", scene)
    # The playfield's XY plane onto the flight plane: Y along the level (+Z), -Z up (+Y).
    root.rotation.x = math.pi / 2

    def on_mesh(mesh: Any) -> None:
        # Shots are additive and bright enough already: only the ships' neon lights glow. Nor do
        # soft, see-through particles (vertex alpha: the blasts' fire and smoke), which the glow
        # layer would draw white, without their tints.
        material = mesh.material
        additive = material is not None and material.alphaMode == babylon_constant("ALPHA_ADD")
        if (
            glow is not None
            and is_instance_of(mesh, "Mesh")
            and not additive
            and not mesh.hasVertexAlpha
        ):
            glow.addIncludedOnlyMesh(mesh)
        if outline is not None:
            outline.add(mesh)

    return NodeAdopter(scene, root, ABOVE_CLOUDS_GROUP, on_mesh)


class LevelScene:
    """A level's scenery under the playfield camera, with a layer for everything on the playfield.

    `playfield` is the playfield plane: X right, Y up the screen, -Z towards the camera, one unit
    per logical pixel, origin at its bottom left (the space of `ShotFrame`). Code run through it
    draws there, above the clouds.
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        scene: Any,
        look: Any,
        stage: SceneryStage,
        track: ScrollTrack,
        playfield: NodeAdopter,
        environment: bool,
        cube_size: int,
    ) -> None:
        self.scene = scene
        # The level's look (phase 10: its shot style, P10-R07).
        self.look = look
        self.stage = stage
        self.track = track
        self.playfield = playfield
        self._environment = environment
        self._cube_size = cube_size

    def update(self, distance: float, dt: float) -> None:
        """Moves the scenery and the playfield to `distance` along the level."""
        self.stage.update(distance, dt)
        if self._environment:
            _follow_sky(self.stage, self._cube_size)
        self.playfield.root.position = self.stage.playfield_point(0, 0, distance)


def build_level_scene(engine: Any, game: Any, options: LevelSceneOptions) -> LevelScene:
    """Builds the scene of a level (P04, P05-R11, P06-R02): its generated ground under the tilted
    playfield camera, and the playfield layer above it where ships, enemies and shots are drawn.
    """
    level = options.level
    look = scenery_look(game, level)
    scene = new_scene(engine)
    ground_glow = None
    if options.environment:
        ground_glow = apply_showcase_environment(
            scene,
            ShowcaseEnvironmentOptions(
                options.environment_cube_size,
                look.sky.environmentIntensity,
                look.sky.stops,
                ground_glow_look(look.glow),
            ),
        )
    # The kit factory is one of two (with and without the environment): typed as Any.
    kit: Any = create_scenery_kit if options.environment else create_plain_scenery_kit
    stage_options = SceneryStageOptions(
        game.screen,
        game.view.scenery.camera,
        level,
        look,
        game.view.scenery.prop_models,
        kit,
        options.stage,
        options.atmosphere,
    )
    stage = SceneryStage(scene, stage_options)
    if ground_glow is not None:
        _glow_ground(ground_glow, stage)
        ground_glow.renderingGroupId = BELOW_CLOUDS_GROUP
    playfield = _playfield_layer(scene, options)
    return LevelScene(
        scene,
        look,
        stage,
        ScrollTrack(level.scrollSpeed, level_length(level)),
        playfield,
        options.environment,
        options.environment_cube_size,
    )
