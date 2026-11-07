# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/tier3_prism_model.py`."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, drawn, probe_builder

from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_prism import PRISM_CONFIG
from game.view.enemies import tier3_prism_model as module
from game.view.enemies.enemy_mesh import UNSEEN_BELOW
from render.geometry.facing import seen_from_above

# About the triangles of one reactor's nozzle, core and flame (`ENEMY_LOOK.reactor`).
REACTOR_TRIANGLES = 40


def _body(monkeypatch: Any) -> Any:
    return drawings_of(probe_builder(monkeypatch, module.build_prism))["body"]


def _xyz(positions: list[float]) -> list[tuple[float, float, float]]:
    return [(positions[i], positions[i + 1], positions[i + 2]) for i in range(0, len(positions), 3)]


def _muzzle_points() -> list[list[float]]:
    """Return the emitters in model space, as the model places them (`[x, height, -y]`)."""
    return [[e[0], e[2], -e[1]] for e in PRISM_CONFIG.emitters]


def test_enm_prism_01_prism_is_built_as_the_prism_kind_in_its_neon(monkeypatch: Any) -> None:
    capture = probe_builder(monkeypatch, module.build_prism)
    assert capture.name == "prism"
    assert capture.neon == ENEMY_LOOK.neon.prism


def test_enm_prism_02_prism_has_a_crystal_hull_and_a_glowing_core_crystal(
    monkeypatch: Any,
) -> None:
    parts = _body(monkeypatch)["parts"]
    hull = _xyz(parts.hull.geometry.positions)
    # The crystal runs from its tail to its nose, and the wings spread wide either side of it.
    zs = [z for _x, _y, z in hull]
    assert max(zs) >= module.CRYSTAL[-1][0]
    assert min(x for x, _y, _z in hull) <= -module.WING[2][0]
    assert max(x for x, _y, _z in hull) >= module.WING[2][0]
    # The core crystal is lit as a vein, on the hull's back, on its centre line.
    vein = _xyz(parts.vein.geometry.positions)
    assert vein
    assert all(abs(x) <= max(q[0] for q in module.CORE) + 1e-6 for x, _y, _z in vein)
    assert min(y for _x, y, _z in vein) >= module.CRYSTAL[1][3]
    # The wings' edges are neon.
    assert len(parts.neon.geometry.positions) > 0


def test_enm_prism_04_prism_has_two_laser_lenses_at_its_config_emitters(
    monkeypatch: Any,
) -> None:
    body = _body(monkeypatch)
    muzzles = body["muzzles"]
    assert [kind for _at, kind in muzzles] == ["laser", "laser"]
    # The model's muzzles are the config's emitters: model Z is down the screen's Y.
    assert sorted(tuple(at) for at, _kind in muzzles) == sorted(
        tuple(at) for at in _muzzle_points()
    )
    # Their barrels' mouths and their lenses are charge lights, at the emitters.
    charge = _xyz(body["parts"].charge.geometry.positions)
    assert charge
    for at in _muzzle_points():
        near = [p for p in charge if abs(p[0] - at[0]) <= module.LASER[0] * 1.5]
        assert near
        # Round the barrel's last half unit, and the lens out past its mouth.
        assert min(z for _x, _y, z in near) <= at[2] - 0.5
        assert max(z for _x, _y, z in near) > at[2]


def test_enm_prism_01_an_engine_pod_with_a_reactor_behind_each_laser(monkeypatch: Any) -> None:
    body = _body(monkeypatch)
    reactors = body["reactors"]
    # One per laser, none at the tail.
    assert len(reactors) == 2
    for at in _muzzle_points():
        behind = [r for r in reactors if r.at[0] == at[0]]
        assert len(behind) == 1
        reactor = behind[0]
        assert reactor.at[1] == at[1]
        # Behind the barrel and its pod.
        assert reactor.at[2] < at[2] - module.LASER[1] - module.ENGINE_LENGTH + 1.2
        assert reactor.radius == module.LASER_REACTOR


def test_enm_prism_01_the_engine_pod_is_a_lathe_along_z_with_its_reactor_at_its_back() -> None:
    at = [10.0, 2.0, -30.0]
    pod = drawn(lambda p: module.engine_pod(p, at))
    assert len(pod["reactors"]) == 1
    assert pod["reactors"][0].at == [at[0], at[1], at[2] - 0.2]
    hull = _xyz(pod["parts"].hull.geometry.positions)
    zs = [z for _x, _y, z in hull]
    assert min(zs) == pytest.approx(at[2])
    assert max(zs) == pytest.approx(at[2] + module.ENGINE_LENGTH)
    # Its widest point and the fin on its back.
    widest = max(q[0] for q in module.ENGINE_POD)
    assert max(x for x, _y, _z in hull) == pytest.approx(at[0] + widest, abs=0.3)
    top = max(q[1] for q in module.ENGINE_FIN)
    assert max(y for _x, y, _z in hull) == pytest.approx(at[1] + top)
    assert len(pod["parts"].neon.geometry.positions) > 0


def test_enm_prism_03_prism_stays_within_the_tier_3_triangle_budget(monkeypatch: Any) -> None:
    """Counted on what the game draws: the faces pointing down are dropped when built."""
    body = _body(monkeypatch)
    parts = body["parts"]
    triangles = sum(
        len(seen_from_above(builder.geometry, UNSEEN_BELOW).indices) // 3
        for builder in [parts.hull, parts.flesh, parts.neon, parts.vein, parts.charge]
    )
    triangles += REACTOR_TRIANGLES * len(body["reactors"])
    assert triangles <= ENEMY_LOOK.budget.tier3
