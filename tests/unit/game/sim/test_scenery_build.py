# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/scenery_build.py`."""

import pytest

from core.scenery.scenery_level import SceneryLevel, level_length
from game.config.record import merge
from game.config.world_1.scenery_coast import LEVEL_1_1
from game.config.world_4.scenery import LEVEL_4_5
from game.sim.levels import GAME_LEVELS
from game.sim.scenery_build import scenery_level


def test_a_level_keeps_its_sections_in_the_order_of_the_config() -> None:
    level = scenery_level(LEVEL_1_1)
    assert isinstance(level, SceneryLevel)
    assert [s.name for s in level.sections] == [s["name"] for s in LEVEL_1_1.sections]


def test_the_level_length_is_its_sections_seconds_at_its_scroll_speed() -> None:
    """GAME-LEVEL-03, here for 1-1 (LVL-1-1-02)."""
    level = scenery_level(LEVEL_1_1)
    seconds = sum(s["seconds"] for s in LEVEL_1_1.sections)
    assert level_length(level) == pytest.approx(seconds * LEVEL_1_1.scrollSpeed)


def test_every_game_level_builds_a_scenery_with_a_positive_length() -> None:
    for game_level in GAME_LEVELS:
        assert level_length(game_level.scenery) > 0, game_level.id


def test_a_late_world_level_builds_its_scenery_too() -> None:
    level = scenery_level(LEVEL_4_5)
    assert len(level.sections) == len(LEVEL_4_5.sections)


PATH = {"x": 40, "amplitude": 30, "wavelength": 900}

DRIFT = {"x": 4, "z": 2, "period": 12}


def _with_extras() -> SceneryLevel:
    """1-1 with the optional sculpts and props no level of the game uses yet."""
    section = merge(
        LEVEL_1_1.sections[0],
        {
            "flatten": {
                "path": PATH,
                "halfWidth": 60,
                "edge": 20,
                "height": 12,
                "roughness": 0.5,
            },
            "lakes": {"spacing": 400, "chance": 0.3, "radius": [40, 90], "level": 2, "edge": 15},
            "crevasses": {
                "spacing": 300,
                "width": 8,
                "depth": 20,
                "angleDeg": 30,
                "warp": 0.2,
                "share": 0.4,
            },
            "scarps": {
                "height": 30,
                "wavelength": 400,
                "angleDeg": 150,
                "warp": 0.9,
                "face": 0.1,
                "lowest": 0.2,
            },
        },
    )
    floe = {"id": "floe", "weight": 1, "footprint": 6, "scale": [1, 2], "drift": DRIFT}
    props = merge(
        LEVEL_1_1.props,
        {
            "floating": {"cellSize": 80, "perCell": 2, "depth": 1.5, "kinds": [floe]},
            "lines": [
                {
                    "kind": "pylon",
                    "path": PATH,
                    "spacing": 120,
                    "footprint": 5,
                    "maxSlope": 0.4,
                    "drift": DRIFT,
                }
            ],
            "landmarks": [
                {"kind": "tower", "z": 500, "footprint": [10, 12]},
                {"kind": "buoy", "z": 900, "footprint": [3, 3], "path": PATH, "onWater": True},
            ],
        },
    )
    return scenery_level(merge(LEVEL_1_1, {"sections": [section], "props": props}))


def test_a_section_s_flattened_band_lakes_and_crevasses_are_built_from_the_config() -> None:
    """GFX-TERRAIN-03: the sculpt operations."""
    (section,) = _with_extras().sections
    flatten = section.flatten
    assert (flatten.path.x, flatten.path.amplitude, flatten.path.wavelength) == (40, 30, 900)
    assert (flatten.half_width, flatten.edge, flatten.height, flatten.roughness) == (
        60,
        20,
        12,
        0.5,
    )
    lakes = section.lakes
    assert (lakes.spacing, lakes.chance, lakes.radius, lakes.level, lakes.edge) == (
        400,
        0.3,
        [40, 90],
        2,
        15,
    )
    crevasses = section.crevasses
    assert (crevasses.angle_deg, crevasses.warp, crevasses.share) == (30, 0.2, 0.4)
    assert (crevasses.spacing, crevasses.width, crevasses.depth) == (300, 8, 20)
    scarps = section.scarps
    assert (scarps.height, scarps.wavelength, scarps.angle_deg) == (30, 400, 150)
    assert (scarps.warp, scarps.face, scarps.lowest) == (0.9, 0.1, 0.2)


def test_the_cliff_rules_are_built_from_the_config() -> None:
    """GFX-PROP-19."""
    cliffs = scenery_level(LEVEL_1_1).props.cliffs
    assert cliffs is not None
    assert cliffs.kinds == ["crag-block-a", "crag-block-b", "crag-block-c"]
    assert (cliffs.min_slope, cliffs.spacing, cliffs.embed) == (0.55, 7, 1.5)
    assert (cliffs.height, cliffs.depth) == ([5, 8], [6, 10])


def test_a_section_without_scarps_has_none() -> None:
    """GFX-TERRAIN-19: an omitted optional feature."""
    section = scenery_level(LEVEL_1_1).sections[0]
    assert section.scarps is None


def test_floating_props_lines_and_landmarks_are_built_from_the_config() -> None:
    props = _with_extras().props
    floating = props.floating
    assert (floating.cell_size, floating.per_cell, floating.depth) == (80, 2, 1.5)
    (floe,) = floating.kinds
    assert floe.id == "floe"
    assert (floe.drift.x, floe.drift.z, floe.drift.period) == (4, 2, 12)
    (line,) = props.lines
    assert (line.kind, line.spacing, line.footprint, line.max_slope) == ("pylon", 120, 5, 0.4)
    assert line.path.wavelength == 900
    assert line.sections is None
    assert line.over_water is None
    assert line.drift.period == 12
    tower, buoy = props.landmarks
    assert (tower.kind, tower.z, tower.footprint) == ("tower", 500, [10, 12])
    assert (tower.x, tower.path, tower.rotation, tower.scale, tower.on_water) == (
        None,
        None,
        None,
        None,
        None,
    )
    assert buoy.path.x == 40
    assert buoy.on_water is True
