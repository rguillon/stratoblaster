"""Unit tests of `src/config/scenery_stage.py`."""

from config.scenery_stage import SCENERY_STAGE_CONFIG


def test_p04_the_terrain_is_built_in_chunks_of_cells() -> None:
    stage = SCENERY_STAGE_CONFIG
    assert stage.chunk_length > stage.cell > 0
    assert stage.margin > 0


def test_p04_the_clouds_stay_above_the_ground_and_the_far_clip_beyond_the_sun() -> None:
    stage = SCENERY_STAGE_CONFIG
    assert stage.cloud_clearance > 0
    assert stage.far_clip > stage.sun_distance


def test_p04_props_show_from_a_reach_band_in_steps() -> None:
    stage = SCENERY_STAGE_CONFIG
    low, high = stage.prop_reach
    assert 0 < low < high
    assert stage.prop_step > 0


def test_d216_the_near_clip_stays_well_before_the_flight_plane() -> None:
    import math  # noqa: PLC0415

    from core.content.game_definition import LogicalScreen  # noqa: PLC0415
    from game.config.game import GAME_CONFIG  # noqa: PLC0415
    from game.config.scenery_look import PLAYFIELD_CAMERA  # noqa: PLC0415
    from render.scenery.playfield_framing import frame_playfield  # noqa: PLC0415

    screen = LogicalScreen(GAME_CONFIG.screen.width, GAME_CONFIG.screen.height)
    framing = frame_playfield(screen, PLAYFIELD_CAMERA)
    # The nearest the camera sees the flight plane: along the top edge of its view.
    nearest = framing.height / math.cos(framing.tilt - framing.half_fov)
    stage = SCENERY_STAGE_CONFIG
    assert 1 < stage.near_clip < nearest / 2
    # Far enough out that the ground, past the flight plane, keeps its depth precision.
    assert stage.near_clip >= 100


def test_d212_every_terrain_vertex_is_at_a_multiple_of_the_cell() -> None:
    # The trees sample the ground on the multiples of the cell (`PropPlacer._trees`): the chunks
    # start on that grid too, so the trees stand on the mesh drawn.
    stage = SCENERY_STAGE_CONFIG
    assert stage.chunk_length % stage.cell == 0


def test_d212_a_chunk_comes_in_before_its_trees_can_be_seen() -> None:
    stage = SCENERY_STAGE_CONFIG
    # A chunk comes in `margin` past the ground in view: out of sight, so its trees can grow a row
    # per frame unseen.
    assert 0 < stage.tree_reach < stage.margin
    # The trees in sight are always drawn.
    assert stage.tree_reach <= min(stage.prop_reach)
