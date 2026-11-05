# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/elite_scissor_model.py`."""

import math
from typing import Any

import pytest
from helpers.view_probes import drawings_of, jointed_design_ids, probe_builder

from game.view.bosses.boss_limbs import boss_point
from game.view.enemies import elite_scissor_model as module
from game.view.enemies.weapon_ports import LENS_RADIUS


def _box(builder: Any) -> tuple[list[float], list[float]]:
    pos = builder.geometry.positions
    return [min(pos[i::3]) for i in range(3)], [max(pos[i::3]) for i in range(3)]


def test_enm_scissor_05_scissor_draws_its_two_arms_on_their_shoulders(monkeypatch: Any) -> None:
    capture = probe_builder(monkeypatch, module.build_scissor)
    design_ids, drawn_ids = jointed_design_ids(capture)
    assert capture.name == "scissor"
    assert sorted(design_ids) == sorted(drawn_ids) == ["arm-left", "arm-right"]
    drawn = drawings_of(capture)
    assert {"limbs.shoulder-left", "limbs.shoulder-right"} <= set(drawn)
    for spec in module.CFG.arms:
        muzzles = drawn["parts." + spec.id]["muzzles"]
        tip = boss_point(spec.muzzle[0], spec.muzzle[1], spec.muzzle[2])
        # One laser emitter, marked at the arm's tip.
        assert muzzles == [[tip, "laser"]]


@pytest.mark.parametrize("index", [0, 1])
def test_enm_scissor_06_each_arm_s_emitter_points_along_its_arm(
    monkeypatch: Any, index: int
) -> None:
    """The lens and coils (the charge lights) lie on the arm's line, past its tip."""
    capture = probe_builder(monkeypatch, module.build_scissor)
    spec = module.CFG.arms[index]
    arm = drawings_of(capture)["parts." + spec.id]["parts"]
    tip = boss_point(spec.muzzle[0], spec.muzzle[1], spec.muzzle[2])
    pos = arm.charge.geometry.positions
    assert len(pos) > 0
    # Every charge vertex is off the arm's axis by no more than its coils' radius.
    ux, uz = math.sin(spec.aim), math.cos(spec.aim)
    for i in range(0, len(pos), 3):
        dx, dz = pos[i] - tip[0], pos[i + 2] - tip[2]
        assert abs(dx * uz - dz * ux) <= LENS_RADIUS * 1.2 + 1e-6
    # The lens reaches past the tip along the arm.
    reach = max((pos[i] - tip[0]) * ux + (pos[i + 2] - tip[2]) * uz for i in range(0, len(pos), 3))
    assert reach > 0
    # Its barrel is metal, behind the tip (no white cone any more).
    assert len(arm.hull.geometry.positions) > 0


def test_enm_scissor_04_scissor_body_has_two_reactors_in_sacs_at_its_tail(
    monkeypatch: Any,
) -> None:
    capture = probe_builder(monkeypatch, module.build_scissor)
    body = drawings_of(capture)["body"]
    reactors = body["reactors"]
    assert sorted(r.at for r in reactors) == [[-3, 0.3, -31], [3, 0.3, -31]]
    # Each sits in a flesh sac, at the body's tail.
    low, _high = _box(body["parts"].flesh)
    assert low[2] <= -31
    # The body marks no muzzle: the lasers are on the arms.
    assert body["muzzles"] == []
