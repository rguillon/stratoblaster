# Copyright (c) 2026 Renaud Guillon
"""Options of a `SceneryStage` (phase 4)."""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from core.content.game_definition import LogicalScreen
from core.scenery.scenery_level import SceneryLevel
from render.scenery.atmosphere_of import AtmosphereOptions
from render.scenery.scenery_kit import SceneryKitFactory
from render.scenery.scenery_look import (
    PlayfieldCameraLook,
    SceneryLook,
)

# __pragma__ ("noskip")


class SceneryStageConfig:
    """Engine settings of a `SceneryStage`.

    `chunk_length` (terrain chunk length along Z) and `cell` (grid cell size); `margin` (extra
    ground generated around what the camera sees); `cloud_clearance` (smallest gap between the
    highest ground and a cloud layer); `sun_distance` (how far behind the scene the sun is placed,
    for its shadows); `far_clip` (far clipping distance of the camera); `prop_reach` (how far before
    and past the ground in view props are drawn, as [near, far]); `prop_step` (how much the drawn
    range is widened, so it is uploaded again only now and then); `near_clip` (D-216: the camera's
    near clipping distance); `tree_reach` (D-212: how far before and past the ground in view a tree
    can be seen).
    """

    def __init__(
        self,
        chunk_length: float,
        cell: float,
        margin: float,
        cloud_clearance: float,
        sun_distance: float,
        far_clip: float,
        prop_reach: tuple[float, float],
        prop_step: float,
        near_clip: float,
        tree_reach: float,
    ) -> None:
        self.chunk_length = chunk_length
        self.cell = cell
        self.margin = margin
        self.cloud_clearance = cloud_clearance
        self.sun_distance = sun_distance
        self.far_clip = far_clip
        self.prop_reach = prop_reach
        self.prop_step = prop_step
        self.near_clip = near_clip
        self.tree_reach = tree_reach


class SceneryStageOptions:
    """What a `SceneryStage` is built from.

    The `screen` (the playfield window, D-252), the `camera` look, the `level`, its `look`, the
    `prop_models` (by kind), the scenery `kit` factory, the stage `config`, the debug
    `atmosphere` choices (DEV-OPT-04, DEV-OPT-05, optional) and the `viewport` of the canvas the
    camera draws into (x, y, width, height as shares of it; the whole canvas when None).
    """

    def __init__(
        self,
        screen: LogicalScreen,
        camera: PlayfieldCameraLook,
        level: SceneryLevel,
        look: SceneryLook,
        prop_models: Any,
        kit: SceneryKitFactory,
        config: SceneryStageConfig,
        atmosphere: AtmosphereOptions | None = None,
        viewport: tuple[float, float, float, float] | None = None,
    ) -> None:
        self.screen = screen
        self.camera = camera
        self.level = level
        self.look = look
        self.prop_models = prop_models
        self.kit = kit
        self.config = config
        self.atmosphere = atmosphere
        self.viewport = viewport
