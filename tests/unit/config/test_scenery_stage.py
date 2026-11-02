# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/config/scenery_stage.py`."""

import math

from fixtures.sample_game import PLAYFIELD_CAMERA, SAMPLE_GAME

from config.scenery_stage import SCENERY_STAGE_CONFIG
from render.scenery.playfield_framing import frame_playfield


def test_gfx_terrain_14_the_terrain_is_built_in_chunks_of_cells() -> None:
    """Also GFX-CAM-05: the ground is generated past the view by a margin."""
    stage = SCENERY_STAGE_CONFIG
    assert stage.chunk_length > stage.cell > 0
    assert stage.margin > 0


def test_gfx_sky_12_the_clouds_stay_above_the_ground_and_the_far_clip_beyond_the_sun() -> None:
    """Also GFX-CAM-06: the far clip."""
    stage = SCENERY_STAGE_CONFIG
    assert stage.cloud_clearance > 0
    assert stage.far_clip > stage.sun_distance


def test_gfx_prop_05_props_show_from_a_reach_band_in_steps() -> None:
    stage = SCENERY_STAGE_CONFIG
    low, high = stage.prop_reach
    assert 0 < low < high
    assert stage.prop_step > 0


def test_d216_the_near_clip_stays_well_before_the_flight_plane() -> None:
    """GFX-CAM-06."""
    framing = frame_playfield(SAMPLE_GAME.screen, PLAYFIELD_CAMERA)
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
    """GFX-PROP-14."""
    stage = SCENERY_STAGE_CONFIG
    # A chunk comes in `margin` past the ground in view: out of sight, so its trees can grow a row
    # per frame unseen.
    assert 0 < stage.tree_reach < stage.margin
    # The trees in sight are always drawn.
    assert stage.tree_reach <= min(stage.prop_reach)


def test_gfx_cam_06_the_stage_reach_and_clearance_are_ordered() -> None:
    """Also GFX-PROP-05 (the props' reach) and GFX-TERRAIN-14 (chunks of cells)."""
    stage = SCENERY_STAGE_CONFIG
    assert stage.prop_reach[0] < stage.prop_reach[1]
    assert stage.far_clip > stage.sun_distance
    assert stage.chunk_length > stage.cell > 0
