# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/boss_damage.py`."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from game.config.boss_look import BOSS_LOOK
from game.view.bosses import boss_damage
from game.view.bosses.boss_damage import Smoke, build_smoke


class _Puff:
    """A puff: a position, a scaling and a visibility, set by the smoke each step."""

    def __init__(self) -> None:
        self.position = MagicMock()
        self.scaling = MagicMock()
        self.visibility = 1.0


def test_boss_17_a_puff_rises_and_drifts_back_as_it_fades_and_grows() -> None:
    puffs = [_Puff()]
    smoke = Smoke(node=None, puffs=puffs, radius=3.0)
    smoke.step(0.0)
    # At age 0 the puff is at the base of the smoke, small and opaque.
    puffs[0].position.set.assert_called_with(0, 3.0, -0.0)
    puffs[0].scaling.setAll.assert_called_with(0.6)
    assert puffs[0].visibility == pytest.approx(1)


def test_boss_17_the_puffs_are_spread_evenly_through_the_cycle() -> None:
    look = BOSS_LOOK.smoke
    puffs = [_Puff(), _Puff()]
    smoke = Smoke(node=None, puffs=puffs, radius=0.0)
    smoke.step(0.0)
    # Two puffs: the second one starts half way through the cycle.
    assert puffs[0].visibility == pytest.approx(1)
    assert puffs[1].position.set.call_args.args[1] == pytest.approx(look.rise * 0.5)


def test_boss_17_smoke_restarts_its_cycle_when_a_puff_is_spent() -> None:
    look = BOSS_LOOK.smoke
    puffs = [_Puff()]
    smoke = Smoke(node=None, puffs=puffs, radius=0.0)
    smoke.step(look.seconds)
    # Back at the base after one full cycle.
    assert puffs[0].position.set.call_args.args[1] == pytest.approx(0, abs=1e-9)


def test_boss_17_a_puff_is_at_full_height_and_faded_just_before_it_restarts() -> None:
    look = BOSS_LOOK.smoke
    puffs = [_Puff()]
    smoke = Smoke(node=None, puffs=puffs, radius=0.0)
    smoke.step(look.seconds * 0.999)
    assert puffs[0].visibility == pytest.approx(0, abs=0.01)
    assert puffs[0].position.set.call_args.args[1] == pytest.approx(look.rise, rel=0.01)


def test_boss_17_build_smoke_puts_its_puffs_on_a_node_under_the_parent(monkeypatch: Any) -> None:
    look = BOSS_LOOK.smoke
    node = MagicMock(name="smoke-node")
    monkeypatch.setattr(boss_damage, "new_transform_node", lambda _label, _scene: node)
    meshes: list[MagicMock] = []

    def mesh_of(name: Any, _geo: Any, _material: Any, _scene: Any) -> Any:
        mesh = MagicMock(name=name)
        meshes.append(mesh)
        return mesh

    monkeypatch.setattr(boss_damage, "mesh_of", mesh_of)
    monkeypatch.setattr(boss_damage, "effect_materials", lambda _scene: {"smoke": "mat"})
    parent = object()
    smoke = build_smoke("boss", 4.0, scene=object(), parent=parent)
    assert smoke.node is node
    assert node.parent is parent
    assert len(meshes) == look.puffs
    assert all(m.parent is node for m in meshes)
