# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/weapon_ports.py`: the missile ports and the laser lenses."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, drawn, probe_builder

from core.entities.barrel import Barrel
from game.config.enemy_look import ENEMY_LOOK
from game.config.weapons import WEAPONS
from game.view.enemies.enemy_mesh import rocket_sunk
from game.view.enemies.enemy_models import ENEMY_MODELS
from game.view.enemies.weapon_ports import HEX_INNER, port_bore, port_radius, rocket_radius


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
    assert high[2] == pytest.approx(20)
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


@pytest.mark.parametrize("missile", [4, 5, 8])
def test_wpn_07_the_bore_is_wider_than_the_rocket_and_the_tube_than_the_bore(
    missile: float,
) -> None:
    drawn_radius = ENEMY_LOOK.missile.radius * missile / ENEMY_LOOK.missile.baseRadius
    assert rocket_radius(missile) == pytest.approx(drawn_radius)
    # The hexagon's inner radius clears the round rocket.
    assert port_bore(missile) * HEX_INNER > rocket_radius(missile)
    assert port_radius(missile) > port_bore(missile)


def test_wpn_07_the_port_is_hollow_and_its_rocket_is_a_piece_of_its_own() -> None:
    got = drawn(lambda p: p.muzzle([0, 3, 20], "missile", "up", 5, 1))
    # Nothing of the port's hull covers its mouth: no face at the top inside the bore.
    hull = got["parts"].hull.geometry.positions
    top = max(hull[1::3])
    inside = [
        (hull[i], hull[i + 2])
        for i in range(0, len(hull), 3)
        if hull[i + 1] == pytest.approx(top)
        and (hull[i] ** 2 + (hull[i + 2] - 20) ** 2) ** 0.5 < port_bore(5) * HEX_INNER - 1e-6
    ]
    assert inside == []
    rockets = [s for s in got["slides"] if s.kind == "rocket"]
    assert len(rockets) == 1
    assert rockets[0].index == 1
    # A port pointing up sinks its rocket down.
    assert rockets[0].down == -1


class _Launching:
    def __init__(self, fired_at: float | None, age: float) -> None:
        self.launchers = [Barrel([0, 0, 0])]
        self.launchers[0].fired_at = fired_at
        self.age = age


def test_wpn_07_the_rocket_is_gone_after_a_launch_then_rises_back_as_it_reloads() -> None:
    reload = WEAPONS.missileReloadSeconds
    assert rocket_sunk(_Launching(None, 3), 0) == 0
    assert rocket_sunk(_Launching(2, 2), 0) == 1
    assert rocket_sunk(_Launching(2, 2 + reload * WEAPONS.missileReloadShow * 0.9), 0) == 1
    halfway = rocket_sunk(_Launching(2, 2 + reload * 0.7), 0)
    assert 0 < halfway < 1
    assert rocket_sunk(_Launching(2, 2 + reload), 0) == 0
    # An enemy that reports no launcher (a boss's piece) is always loaded.
    assert rocket_sunk(object(), 0) == 0


def test_wpn_07_a_port_lit_on_its_sides_has_no_glowing_rim_at_its_mouth() -> None:
    lit = drawn(lambda p: p.muzzle([0, 3, 20], "missile", "up", 5, 0))
    plain = drawn(lambda p: p.muzzle([0, 3, 20], "missile", "up", 5, 0, False))
    assert len(lit["parts"].charge.geometry.positions) > 0
    assert len(plain["parts"].charge.geometry.positions) == 0
    # Not even the edge trim: it is drawn on the bare metal, which is not trimmed.
    assert len(plain["parts"].hull.geometry.positions) == 0
    assert len(plain["parts"].bare.geometry.positions) > 0


def _triangles(builder: Any) -> list[list[list[float]]]:
    pos = builder.geometry.positions
    idx = builder.geometry.indices
    return [
        [[pos[idx[t + k] * 3 + c] for c in range(3)] for k in range(3)]
        for t in range(0, len(idx), 3)
    ]


def _crosses_axis(tri: list[list[float]], x: float, y: float) -> tuple[bool, float]:
    """Whether a triangle crosses the line along Z through (x, y), and the Z where it does."""
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = tri
    det = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(det) < 1e-9:
        return False, 0.0
    u = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / det
    v = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / det
    w = 1 - u - v
    inside = min(u, v, w) >= -1e-9
    return inside, u * az + v * bz + w * cz


@pytest.mark.parametrize("model", ["rocketeer", "harrier", "mortar"])
def test_wpn_07_nothing_closes_a_launcher_s_well(model: str) -> None:
    """The bore is open from the mouth down to its floor: the rocket is seen in it and leaving."""
    body = drawings_of(probe_builder(pytest.MonkeyPatch(), ENEMY_MODELS[model]))["body"]
    parts = body["parts"]
    ports = [at for at, kind in body["muzzles"] if kind == "missile"]
    assert ports
    for at in ports:
        for builder in (parts.hull, parts.bare, parts.flesh):
            for tri in _triangles(builder):
                crosses, z = _crosses_axis(tri, at[0], at[1])
                # Nothing across the bore from the floor of the shallowest well up to the mouth.
                assert not (crosses and at[2] - 2 < z < at[2] + 0.01), (model, at, z)
