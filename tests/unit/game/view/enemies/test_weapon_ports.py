# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/weapon_ports.py`: the missile ports and the laser lenses."""

from typing import Any

from helpers.view_probes import drawn


def _box(builder: Any) -> tuple[list[float], list[float]]:
    pos = builder.geometry.positions
    return (
        [min(pos[i::3]) for i in range(3)],
        [max(pos[i::3]) for i in range(3)],
    )


def test_wpn_07_a_missile_muzzle_draws_a_hexagonal_port_standing_up_from_its_point() -> None:
    got = drawn(lambda p: p.muzzle([10, 5, 20], "missile"))
    low, high = _box(got["parts"].hull)
    # Six facets on a barrel standing on the point, its hole at the top.
    assert low[1] >= 5
    assert high[1] > 5 + 2
    assert len(got["parts"].charge.geometry.positions) > 0
    assert got["muzzles"] == [[[10, 5, 20], "missile"]]


def test_wpn_07_a_forward_port_ends_at_its_point() -> None:
    got = drawn(lambda p: p.muzzle([0, 3, 20], "missile", "forward"))
    low, high = _box(got["parts"].hull)
    assert high[2] > 20
    assert low[2] < 20 - 2


def test_wpn_06_a_laser_muzzle_draws_a_lens_at_the_end_of_a_barrel() -> None:
    got = drawn(lambda p: p.muzzle([0, 3, 20], "laser"))
    assert len(got["parts"].hull.geometry.positions) > 0
    low, high = _box(got["parts"].charge)
    assert high[2] > 20
    assert low[2] < 20


def test_a_gun_muzzle_draws_nothing_of_its_own() -> None:
    got = drawn(lambda p: p.muzzle([0, 3, 20]))
    assert len(got["parts"].hull.geometry.positions) == 0
