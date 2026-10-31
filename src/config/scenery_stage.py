"""Tunables of the generated ground under the playfield camera (P04): the game"""


class SceneryStageConfig:
    """The generated ground and sky around the camera, in the order of `SCENERY_STAGE_CONFIG`."""

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
        near_clip: float,
    ) -> None:
        # Terrain chunk length along Z, and the grid cell of the terrain mesh.
        self.chunk_length = chunk_length
        self.cell = cell
        # Extra ground generated around what the camera sees.
        self.margin = margin
        # Cloud layers stay at least this high above the highest ground.
        self.cloud_clearance = cloud_clearance
        self.sun_distance = sun_distance
        self.far_clip = far_clip
        # D-216: the camera's near clipping plane. Nothing it draws comes nearer than the flight
        # plane, about 570 away at the top of the screen; a near plane at 1 left the depth buffer
        # about 0.08 per step at the ground, about 1,000 away, and the props' flat parts (plots,
        # lots, decks, 0.2 over the ground) fought with it and blinked.
        self.near_clip = near_clip
        # Review: props are drawn only near the ground in view. The tallest stand about 60 high,
        # and the camera looks down at about 35 degrees at the top edge: they show from about 90
        # past it.
        self.prop_reach = prop_reach
        self.prop_step = prop_step


SCENERY_STAGE_CONFIG = SceneryStageConfig(320, 8, 80, 15, 2500, 4000, (40, 120), 40, 200)
