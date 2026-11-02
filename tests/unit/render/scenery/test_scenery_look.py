# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/scenery_look.py`: the records of the lava and the clouds."""

from helpers.render_looks import make_look

from render.scenery.scenery_look import CloudLayerLook, LavaEdge, LavaLook, SeaLook, SeaNormalMap

CRUST = (0.1, 0.05, 0.0)
PLATE = (0.3, 0.1, 0.05)
GLOW = (1.0, 0.4, 0.0)
HOT = (1.0, 0.9, 0.6)


def _lava() -> LavaLook:
    edge = LavaEdge(GLOW, 0.8, 2.5)
    return LavaLook(CRUST, PLATE, GLOW, HOT, 12, 0.15, 0.25, 1.8, edge)


def test_a_lava_edge_keeps_its_glow_colour_width_and_cracks() -> None:
    edge = LavaEdge(GLOW, 0.8, 2.5)
    assert edge.color == GLOW
    assert edge.width == 0.8
    assert edge.cracks == 2.5


def test_gfx_terrain_16_a_lava_look_keeps_its_fields_in_the_order_given() -> None:
    lava = _lava()
    assert (lava.crust, lava.plate, lava.glow, lava.hot) == (CRUST, PLATE, GLOW, HOT)
    assert (lava.cell, lava.crack, lava.churn, lava.intensity) == (12, 0.15, 0.25, 1.8)
    assert lava.edge.cracks == 2.5


def test_gfx_terrain_16_a_sea_with_lava_is_lava_and_a_plain_sea_is_water() -> None:
    lava = _lava()
    sea = SeaLook((0.2, 0.1, 0.0), 1, 0.4, 0.5, SeaNormalMap(64, 4, 2, 0.3), 16, (0, 0), lava)
    assert sea.lava is lava
    assert make_look().sea.lava is None


def test_gfx_sky_11_a_cloud_layer_look_keeps_its_fields_in_the_order_given() -> None:
    cloud = CloudLayerLook(140, 0.6, 0.8, 512, (3, -1), 0.4, (1, 1, 1), (0.6, 0.6, 0.7))
    assert (cloud.altitude, cloud.coverage, cloud.opacity) == (140, 0.6, 0.8)
    assert (cloud.tileSize, cloud.drift, cloud.softness) == (512, (3, -1), 0.4)
    assert (cloud.color, cloud.shade) == ((1, 1, 1), (0.6, 0.6, 0.7))
