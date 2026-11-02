# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/hidden_weapons.py`.

Armour regions (D-224) and the hidden weapons joined to a boss design (D-221, D-229).
"""

import pytest

from game.config.bosses.hidden_weapons import (
    armour_region,
    hidden_weapon,
    region_blasts,
    with_weapons,
)
from game.config.record import record


def test_a_region_is_mirrored_across_the_centre_line_unless_asked_not_to() -> None:
    """BOSS-42: a region's outline is mirrored across the centre line unless asked not to."""
    region = armour_region("wings", 1, [[10, 0], [30, 0], [30, 20]], "wing")
    assert region.outlines[1] == [[-30, 20], [-30, 0], [-10, 0]]
    assert region.heights == [-1000, 1000]
    single = armour_region("back", 2, [[-5, 0], [5, 0], [0, 9]], "shell", [0, 4], mirror=False)
    assert len(single.outlines) == 1
    assert single.heights == [0, 4]
    with pytest.raises(ValueError, match="Unknown armour frame"):
        armour_region("x", 1, [[0, 0], [1, 0], [0, 1]], "lattice")


def test_a_region_bursts_in_blasts_spread_over_its_outlines() -> None:
    """BOSS-37: each shed region bursts in up to `boss_region_blasts` blasts."""
    region = armour_region("wings", 1, [[10, 0], [30, 0], [30, 20], [10, 20]], "wing")
    blasts = region_blasts(region, 5)
    assert 2 <= len(blasts) <= 5
    # One on each side of the centre line.
    assert any(b[0] > 0 for b in blasts)
    assert any(b[0] < 0 for b in blasts)
    assert blasts[0][:2] == [20, 10]
    assert blasts[0][2] >= 8
    assert all(b[2] > 0 for b in blasts)


def test_a_hangar_s_launches_join_the_boss_s_own() -> None:
    design = record({
        "stats": {"parts": [{"id": "gun", "x": 0, "y": 0, "radius": 5, "health": 100}]},
        "guns": {},
        "stages": [[]],
        "launches": [{"from": "gun", "kind": "hornets", "count": 1, "every": 5}],
    })
    bay = hidden_weapon("bay", "hangar", [0, 10], 10, 100, 1, "red", 3)
    result = with_weapons(design, [bay], [])
    assert [launch["from"] for launch in result.launches] == ["gun", "bay"]
    assert result.guns["bay"] == {}


def test_boss_38_a_hidden_weapon_keeps_the_hinge_it_is_given() -> None:
    """D-221: a weapon unfolds about its `mount`; left out, the view picks its inner side."""
    mounted = hidden_weapon("gun", "gatling", [10, 0], 8, 300, 1, "red", 2, mount=[-4, 2, 1.5])
    assert mounted.look.mount == [-4, 2, 1.5]
    assert mounted.part.reveal == 1
    plain = hidden_weapon("gun", "gatling", [10, 0], 8, 300, 1, "red", 2)
    assert "mount" not in plain.look


def test_boss_35_more_volleys_join_every_stage_with_the_weapons_own() -> None:
    design = record({
        "stats": {"parts": [{"id": "hull", "x": 0, "y": 0, "radius": 5, "health": 100}]},
        "guns": {},
        "stages": [[], [{"from": "core", "every": 3}]],
    })
    extra = {"from": "core", "every": 9}
    result = with_weapons(design, [], [], [extra])
    assert [len(stage) for stage in result.stages] == [1, 2]
    assert all(stage[-1]["every"] == 9 for stage in result.stages)
