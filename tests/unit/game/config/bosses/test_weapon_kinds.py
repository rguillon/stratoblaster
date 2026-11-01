"""The kinds of hidden weapon (D-229; docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-
shape-shifts-design.md, Part A): their muzzles, volleys and launches."""

import pytest

from game.config.bosses.hidden_weapons import hidden_weapon, with_weapons
from game.config.bosses.weapon_kinds import (
    KINDS,
    WEAPON_SHAPE,
    weapon_guns,
    weapon_launches,
    weapon_volleys,
)
from game.config.record import record

NEW = ["cannon", "mortar", "battery", "sweeper", "hangar"]


def test_the_five_new_kinds_join_the_four_and_the_beam() -> None:
    assert KINDS[:5] == ["gatling", "lance", "rack", "orb", "beam"]
    assert all(kind in KINDS for kind in NEW)


def test_an_unknown_kind_is_refused() -> None:
    with pytest.raises(ValueError, match="Unknown hidden weapon kind"):
        weapon_guns("trebuchet", [0, 0], 10, None)
    with pytest.raises(ValueError, match="Unknown hidden weapon kind"):
        weapon_volleys("trebuchet", "x", "red", 1)


def test_the_cannon_has_one_heavy_barrel_on_a_turret_ahead_of_its_centre() -> None:
    guns = weapon_guns("cannon", [20, 10], 10, 4)
    assert guns.turret == [20, 10]
    assert len(guns.gun) == 1
    muzzle = guns.gun[0]
    assert muzzle[0] == 20
    # Down the screen, past its turret, over its pod.
    assert muzzle[1] < 10 - 10 * WEAPON_SHAPE.cannonTurret
    assert muzzle[2] > 4


def test_the_cannon_fires_spreads_of_three_large_shells_at_the_player() -> None:
    [shot] = weapon_volleys("cannon", "cannon-left", "red", 1.5)
    assert shot.shape.kind == "aimed"
    assert shot.shape.count == 3
    assert shot.shape.bullet.radius > 4
    assert shot["from"] == "cannon-left" and shot.first == 1.5


def test_the_mortar_lobs_flak_from_its_tube_mouth() -> None:
    guns = weapon_guns("mortar", [0, 0], 10, 5)
    [mouth] = guns.gun
    assert mouth[1] < 0 and mouth[2] > 5
    assert guns.turret is None
    [shot] = weapon_volleys("mortar", "mortar", "orange", 1)
    assert shot.shape.kind == "aimed"
    assert shot.shape.bullet.burst.count == 8


def test_the_battery_has_five_barrels_in_a_row_and_fires_fans_straight_down() -> None:
    guns = weapon_guns("battery", [10, 0], 10, 5)
    xs = [m[0] for m in guns.gun]
    assert len(xs) == 5
    assert xs == sorted(xs)
    assert xs[2] == pytest.approx(10)
    assert xs[4] - xs[0] == pytest.approx(4 * 10 * WEAPON_SHAPE.barrelGap)
    assert all(m[1] == guns.gun[0][1] < 0 for m in guns.gun)
    [shot] = weapon_volleys("battery", "battery", "green", 1)
    assert shot.shape.kind == "fan"
    assert shot.shape.headingDeg == 0
    assert shot.shape.count == 7


def test_the_sweeper_fires_a_sweeping_laser_from_its_turret() -> None:
    guns = weapon_guns("sweeper", [0, 30], 10, 5)
    assert guns.turret == [0, 30]
    assert guns.turretLaser is True
    assert guns.laser[0][1] == pytest.approx(30 - 10 * WEAPON_SHAPE.prongLength)
    [shot] = weapon_volleys("sweeper", "sweeper", "blue", 2)
    assert shot.shape.kind == "laser"
    assert shot.shape.laser.sweeps is True


def test_a_hangar_fires_nothing_but_launches_gnats() -> None:
    assert weapon_volleys("hangar", "hangar", "red", 1) == []
    assert weapon_launches("gatling", "gatling", 1) == []
    [launch] = weapon_launches("hangar", "bay", 3)
    assert launch["from"] == "bay"
    assert launch["kind"] == "gnats"
    assert launch["count"] == 2 and launch["first"] == 3


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
