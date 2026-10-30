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
