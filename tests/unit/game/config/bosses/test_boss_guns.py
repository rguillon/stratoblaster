# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/boss_guns.py`: the bosses' gun mounts (BOSS-58)."""

import math

import pytest

from game.config.bosses.boss_guns import (
    GUN_SHAPE,
    MIN_GAP,
    MISSILE_BLOCK,
    axis_height,
    gun_mount,
    laser_mount,
    missile_mount,
    mount_muzzles,
    mount_order,
    port_spots,
)
from game.config.record import merge

DEG = math.pi / 180


def test_boss_58_a_gun_mount_s_defaults_a_turret_dome_and_trimmed_single_barrel() -> None:
    mount = gun_mount("gun", "arm", [3, -4], 5, {"size": 4, "barrels": 1, "bore": 1, "length": 8})
    assert (mount.id, mount.piece, mount.kind, mount.at, mount.height) == (
        "gun",
        "arm",
        "gun",
        [3, -4],
        5,
    )
    assert (mount.layout, mount.gap, mount.size, mount.restDeg) == ("fan", 0, 4, 0)
    assert (mount.turret, mount.trim, mount.style, mount.axis) == (True, True, "dome", 0.38)


def test_boss_58_a_row_of_barrels_is_spread_at_least_min_gap_bores_and_its_dome_covers_it() -> None:
    """A row has no edge trim on its barrels."""
    mount = gun_mount("row", "core", [0, 0], 5, {"size": 2, "barrels": 3, "bore": 1, "length": 8})
    assert mount.gap == MIN_GAP
    assert mount.size == pytest.approx(MIN_GAP + 1.6)
    assert mount.trim is False


def test_boss_58_a_gun_mount_keeps_the_options_it_is_given() -> None:
    options = {
        "size": 6,
        "barrels": 4,
        "bore": 1,
        "length": 5,
        "layout": "ring",
        "gap": 2,
        "restDeg": 45,
        "turret": False,
        "trim": True,
        "style": "mortar",
        "axis": 0.6,
    }
    mount = gun_mount("rotor", "core", [0, 0], 5, options)
    assert (mount.layout, mount.gap, mount.size, mount.restDeg) == ("ring", 2, 6, 45)
    assert (mount.turret, mount.trim, mount.style, mount.axis) == (False, True, "mortar", 0.6)


def test_boss_58_a_gun_mount_of_an_unknown_layout_is_refused() -> None:
    with pytest.raises(ValueError, match="Unknown gun layout"):
        gun_mount("g", "core", [0, 0], 5, {"size": 2, "barrels": 1, "bore": 1, "layout": "star"})


def test_boss_58_a_mount_of_an_unknown_kind_is_refused() -> None:
    mount = merge(missile_mount("m", "core", [0, 0], 5, 2), {"kind": "catapult"})
    with pytest.raises(ValueError, match='Unknown boss mount kind "catapult"'):
        mount_muzzles(mount)


def test_boss_58_a_rotor_s_barrels_point_all_round_its_hub_their_tips_along_them() -> None:
    mount = gun_mount(
        "rotor",
        "core",
        [10, 20],
        5,
        {"size": 5, "barrels": 4, "bore": 1, "length": 6, "layout": "ring"},
    )
    muzzles = mount_muzzles(mount)
    reach = 5 * GUN_SHAPE.hubRoot + 6
    assert [m[3] for m in muzzles] == [0, 90, 180, 270]
    for x, y, height, angle in muzzles:
        # From the hub out through the tip: the barrel's heading, its boss pointing down.
        assert math.hypot(x - 10, y - 20) == pytest.approx(reach)
        heading = math.atan2(x - 10, y - 20)
        off = math.remainder(heading - (math.pi + angle * DEG), 2 * math.pi)
        assert off == pytest.approx(0, abs=1e-9)
        assert height == pytest.approx(5 + 5 * GUN_SHAPE.axis)


def test_boss_58_a_row_s_barrels_point_its_way_side_by_side() -> None:
    mount = gun_mount("row", "core", [0, 0], 5, {"size": 4, "barrels": 2, "bore": 1, "length": 6})
    tips = mount_muzzles(mount)
    reach = 4 * GUN_SHAPE.root + 6
    flat = [v for t in tips for v in (t[0], t[1], t[3])]
    assert flat == pytest.approx([-MIN_GAP / 2, -reach, 0, MIN_GAP / 2, -reach, 0])


def test_wpn_06_a_laser_mount_has_one_lens_and_no_turret_by_default() -> None:
    mount = laser_mount("eye", "core", [0, -10], 3, {"size": 4, "bore": 2, "length": 7})
    assert (mount.kind, mount.barrels, mount.turret, mount.restDeg) == ("laser", 1, False, 0)
    # A laser mount has no axis of its own: its barrel lies at the gun's.
    assert axis_height(mount) == pytest.approx(3 + 4 * GUN_SHAPE.axis)
    turning = laser_mount(
        "eye", "core", [0, 0], 3, {"size": 4, "bore": 2, "length": 7, "turret": True, "restDeg": 20}
    )
    assert (turning.turret, turning.restDeg) == (True, 20)
    [lens] = mount_muzzles(turning)
    assert lens[3] == 20


def test_wpn_07_a_lone_silo_s_port_is_on_its_mount() -> None:
    mount = missile_mount("silo", "core", [5, 6], 2, 1)
    assert port_spots(mount) == [[5, 6]]
    assert mount_muzzles(mount) == [[5, 6, 2 + MISSILE_BLOCK.well]]


def test_wpn_07_a_block_s_ports_stand_in_two_columns_front_row_first() -> None:
    mount = missile_mount("rack", "core", [0, 0], 2, 3)
    pitch = MISSILE_BLOCK.pitch
    half = pitch / 2
    flat = [v for spot in port_spots(mount) for v in spot]
    assert flat == pytest.approx([-half, half, half, half, -half, -half])
    assert (mount.turret, mount.restDeg) == (False, 0)


def test_boss_58_barrels_and_ports_are_numbered_in_mount_order_each_kind_on_its_own() -> None:
    mounts = [
        gun_mount("a", "core", [0, 0], 1, {"size": 3, "barrels": 2, "bore": 1, "length": 4}),
        missile_mount("b", "core", [0, 0], 1, 4),
        laser_mount("c", "core", [0, 0], 1, {"size": 3, "bore": 1, "length": 4}),
        gun_mount("d", "core", [0, 0], 1, {"size": 3, "barrels": 1, "bore": 1, "length": 4}),
        missile_mount("e", "core", [0, 0], 1, 2),
    ]
    assert mount_order(mounts) == [0, 0, 0, 2, 4]
