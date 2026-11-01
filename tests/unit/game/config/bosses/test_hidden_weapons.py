"""Unit tests of `src/game/config/bosses/hidden_weapons.py`: armour regions (D-224) and the hidden
weapons joined to a boss design (D-221, D-229)."""

import pytest

from game.config.bosses.hidden_weapons import (
    armour_region,
    hidden_weapon,
    region_blasts,
    with_weapons,
)
from game.config.record import record


def test_a_region_is_mirrored_across_the_centre_line_unless_asked_not_to() -> None:
    region = armour_region("wings", 1, [[10, 0], [30, 0], [30, 20]], "wing")
    assert region.outlines[1] == [[-30, 20], [-30, 0], [-10, 0]]
    assert region.heights == [-1000, 1000]
    single = armour_region("back", 2, [[-5, 0], [5, 0], [0, 9]], "shell", [0, 4], False)
    assert len(single.outlines) == 1 and single.heights == [0, 4]
    with pytest.raises(ValueError, match="Unknown armour frame"):
        armour_region("x", 1, [[0, 0], [1, 0], [0, 1]], "lattice")


def test_a_region_bursts_in_blasts_spread_over_its_outlines() -> None:
    region = armour_region("wings", 1, [[10, 0], [30, 0], [30, 20], [10, 20]], "wing")
    blasts = region_blasts(region, 5)
    assert 2 <= len(blasts) <= 5
    # One on each side of the centre line.
    assert any(b[0] > 0 for b in blasts) and any(b[0] < 0 for b in blasts)
    assert blasts[0][:2] == [20, 10]
    assert blasts[0][2] >= 8
    assert all(b[2] > 0 for b in blasts)


def test_a_hangar_s_launches_join_the_boss_s_own() -> None:
    design = record(
        {
            "stats": {"parts": [{"id": "gun", "x": 0, "y": 0, "radius": 5, "health": 100}]},
            "guns": {},
            "stages": [[]],
            "launches": [{"from": "gun", "kind": "hornets", "count": 1, "every": 5}],
        }
    )
    bay = hidden_weapon("bay", "hangar", [0, 10], 10, 100, 1, "red", 3)
    result = with_weapons(design, [bay], [])
    assert [launch["from"] for launch in result.launches] == ["gun", "bay"]
    assert result.guns["bay"] == {}
