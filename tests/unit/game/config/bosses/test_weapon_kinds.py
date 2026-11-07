# Copyright (c) 2026 Renaud Guillon
"""The kinds of hidden weapon: their muzzles, volleys and launches.

Specs: BOSS-40, D-229, docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-shape-shifts-
design.md, Part A.
"""

import pytest

from game.config.bosses.boss_guns import mount_muzzles
from game.config.bosses.weapon_kinds import (
    BEAM,
    KINDS,
    ORB_BARRELS,
    WEAPON_FIRE,
    WEAPON_SHAPE,
    weapon_launches,
    weapon_mounts,
    weapon_volleys,
)

NEW = ["cannon", "mortar", "battery", "sweeper", "hangar"]


def test_the_five_new_kinds_join_the_four_and_the_beam() -> None:
    assert KINDS[:5] == ["gatling", "lance", "rack", "orb", "beam"]
    assert all(kind in KINDS for kind in NEW)


def test_an_unknown_kind_is_refused() -> None:
    with pytest.raises(ValueError, match="Unknown hidden weapon kind"):
        weapon_mounts("trebuchet", "x", [0, 0], 10, None)
    with pytest.raises(ValueError, match="Unknown hidden weapon kind"):
        weapon_volleys("trebuchet", "x", "red", 1)


@pytest.mark.parametrize("kind", [kind for kind in KINDS if kind != "hangar"])
def test_boss_58_every_kind_but_the_hangar_has_one_mount_named_as_its_part(kind: str) -> None:
    [mount] = weapon_mounts(kind, "weapon", [20, 10], 10, 4)
    assert mount.id == mount.piece == "weapon"
    assert mount.at == [20, 10]
    assert mount.height == 4


def test_boss_58_a_pod_standing_on_a_surface_carries_its_mount_on_its_top() -> None:
    [mount] = weapon_mounts("gatling", "g", [0, 0], 10, [3, 7])
    assert mount.height == 7
    [low] = weapon_mounts("gatling", "g", [0, 0], 10, None)
    assert low.height == 10 * WEAPON_SHAPE.height


def test_the_gatling_has_three_barrels_side_by_side_on_a_turret() -> None:
    [mount] = weapon_mounts("gatling", "gatling", [0, 0], 10, 4)
    assert (mount.kind, mount.layout, mount.barrels, mount.turret) == ("gun", "fan", 3, True)


def test_the_cannon_has_three_heavy_barrels_on_a_turret_down_the_screen() -> None:
    [mount] = weapon_mounts("cannon", "cannon", [20, 10], 10, 4)
    assert mount.kind == "gun"
    assert mount.turret is True
    assert mount.barrels == WEAPON_FIRE.cannon.count
    muzzles = mount_muzzles(mount)
    # Down the screen, past its turret, over its pod.
    assert all(m[1] < 10 - 10 * WEAPON_SHAPE.cannonTurret for m in muzzles)
    assert all(m[2] > 4 for m in muzzles)
    assert sum(m[0] for m in muzzles) / len(muzzles) == pytest.approx(20)


def test_the_cannon_fires_spreads_of_three_large_shells_at_the_player() -> None:
    [shot] = weapon_volleys("cannon", "cannon-left", "red", 1.5)
    assert shot.shape.kind == "aimed"
    assert shot.shape.count == 3
    assert shot.shape.bullet.radius > 4
    assert shot["from"] == "cannon-left"
    assert shot.first == 1.5


def test_the_mortar_lobs_flak_from_its_one_wide_barrel() -> None:
    [mount] = weapon_mounts("mortar", "mortar", [0, 0], 10, 5)
    assert mount.barrels == 1
    [mouth] = mount_muzzles(mount)
    assert mouth[1] < 0
    assert mouth[2] > 5
    [shot] = weapon_volleys("mortar", "mortar", "orange", 1)
    assert shot.shape.kind == "aimed"
    assert shot.shape.bullet.burst.count == 8


def test_the_battery_has_five_barrels_in_a_row_and_fires_fans_straight_down() -> None:
    [mount] = weapon_mounts("battery", "battery", [10, 0], 10, 5)
    muzzles = mount_muzzles(mount)
    xs = [m[0] for m in muzzles]
    assert len(xs) == WEAPON_SHAPE.barrels == 5
    assert xs == sorted(xs)
    assert xs[2] == pytest.approx(10)
    assert all(m[1] == pytest.approx(muzzles[0][1]) for m in muzzles)
    assert muzzles[0][1] < 0
    [shot] = weapon_volleys("battery", "battery", "green", 1)
    assert shot.shape.kind == "fan"
    assert shot.shape.headingDeg == 0
    assert shot.shape.count == 7


def test_the_sweeper_fires_a_sweeping_laser_from_its_turret() -> None:
    [mount] = weapon_mounts("sweeper", "sweeper", [0, 30], 10, 5)
    assert mount.kind == "laser"
    assert mount.turret is True
    [lens] = mount_muzzles(mount)
    assert lens[1] < 30 - 10 * WEAPON_SHAPE.prongLength
    [shot] = weapon_volleys("sweeper", "sweeper", "blue", 2)
    assert shot.shape.kind == "laser"
    assert shot.shape.laser.sweeps is True


def test_the_lance_is_a_fixed_laser_pointing_down_the_screen() -> None:
    [mount] = weapon_mounts("lance", "lance", [0, 0], 10, 5)
    assert (mount.kind, mount.turret, mount.restDeg) == ("laser", False, 0)
    [lens] = mount_muzzles(mount)
    assert lens[1] < -10 * WEAPON_SHAPE.lance


def test_the_beam_points_out_behind_the_boss() -> None:
    [mount] = weapon_mounts("beam", "beam", [0, 0], 10, 5)
    assert (mount.kind, mount.restDeg) == ("laser", 180)
    [lens] = mount_muzzles(mount)
    assert lens[1] > 0


def test_the_rack_is_a_block_of_four_missile_ports() -> None:
    [mount] = weapon_mounts("rack", "rack", [0, 0], 10, 5)
    assert (mount.kind, mount.barrels) == ("missile", 4)
    assert len(mount_muzzles(mount)) == 4


def test_the_orb_is_a_rotor_with_a_barrel_per_bullet_of_its_rings() -> None:
    [mount] = weapon_mounts("orb", "orb", [0, 0], 10, 5)
    assert (mount.kind, mount.layout, mount.barrels) == ("gun", "ring", ORB_BARRELS)
    [shot] = weapon_volleys("orb", "orb", "green", 1)
    assert shot.shape.kind == "ring"
    assert shot.shape.count == ORB_BARRELS


def test_a_hangar_fires_nothing_but_launches_hornets() -> None:
    assert weapon_mounts("hangar", "hangar", [0, 0], 10, 5) == []
    assert weapon_volleys("hangar", "hangar", "red", 1) == []
    assert weapon_launches("gatling", "gatling", 1) == []
    [launch] = weapon_launches("hangar", "bay", 3)
    assert launch["from"] == "bay"
    assert launch["kind"] == "hornets"
    assert launch["count"] == 2
    assert launch["first"] == 3


def test_the_beam_fires_its_wide_laser_every_few_seconds() -> None:
    """D-229: the beam's giant laser, BEAM wide, for BEAM.firing seconds."""
    [shot] = weapon_volleys("beam", "beam-left", "red", 4)
    assert shot["from"] == "beam-left"
    assert shot.shape.kind == "laser"
    assert shot.shape.laser.width == BEAM.width
    assert shot.shape.laser.firingSeconds == BEAM.firing
    assert shot.every == BEAM.every
    assert shot.first == 4
