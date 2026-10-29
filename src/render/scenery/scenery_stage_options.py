"""Options of a `SceneryStage` (P04, P08-R12), ported from
`render/scenery/scenery-stage-options.ts`."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from core.content.game_definition import LogicalScreen  # noqa: E402
from core.scenery.scenery_level import SceneryLevel  # noqa: E402
from render.scenery.atmosphere_of import AtmosphereOptions  # noqa: E402
from render.scenery.scenery_kit import SceneryKitFactory  # noqa: E402
from render.scenery.scenery_look import (  # noqa: E402
    PlayfieldCameraLook,
    SceneryLook,
)

__pragma__("noskip")


class SceneryStageConfig:
    """Engine settings of a `SceneryStage`: `chunk_length` (terrain chunk length along Z) and
    `cell` (grid cell size); `margin` (extra ground generated around what the camera sees);
    `cloud_clearance` (smallest gap between the highest ground and a cloud layer); `sun_distance`
    (how far behind the scene the sun is placed, for its shadows); `far_clip` (far clipping
    distance of the camera); `prop_reach` (how far before and past the ground in view props are
    drawn, as [near, far]); `prop_step` (how much the drawn range is widened, so it is uploaded
    again only now and then)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        chunk_length: float,
        cell: float,
        margin: float,
        cloud_clearance: float,
        sun_distance: float,
        far_clip: float,
        prop_reach: tuple[float, float],
        prop_step: float,
    ) -> None:
        self.chunk_length = chunk_length
        self.cell = cell
        self.margin = margin
        self.cloud_clearance = cloud_clearance
        self.sun_distance = sun_distance
        self.far_clip = far_clip
        self.prop_reach = prop_reach
        self.prop_step = prop_step


class SceneryStageOptions:
    """What a `SceneryStage` is built from: the `screen`, the `camera` look, the `level`, its
    `look`, the `prop_models` (by kind), the scenery `kit` factory, the stage `config` and the
    debug `atmosphere` choices (P08-R12, optional)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        screen: LogicalScreen,
        camera: PlayfieldCameraLook,
        level: SceneryLevel,
        look: SceneryLook,
        prop_models: Any,
        kit: SceneryKitFactory,
        config: SceneryStageConfig,
        atmosphere: AtmosphereOptions | None = None,
    ) -> None:
        self.screen = screen
        self.camera = camera
        self.level = level
        self.look = look
        self.prop_models = prop_models
        self.kit = kit
        self.config = config
        self.atmosphere = atmosphere
