# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/jointed_model.py`."""

from types import SimpleNamespace
from typing import Any

import pytest

from game.view.enemies import jointed_model as jm
from game.view.enemies.jointed_model import Frame, joint_frames, sub


class _Node:
    """A transform node stand-in: a parent, a position and a rotation."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.parent = None
        self.at = None
        self.rotation = SimpleNamespace(y=0.0)
        self.position = SimpleNamespace(set=self._set)

    def _set(self, x: float, y: float, z: float) -> None:
        self.at = [x, y, z]


class _Root(_Node):
    def getScene(self) -> str:
        return "scene"


def _spec(parent: Any, x: Any, y: Any) -> Any:
    return {"parent": parent, "x": x, "y": y}


@pytest.fixture(autouse=True)
def nodes(monkeypatch: Any) -> None:
    monkeypatch.setattr(jm, "new_transform_node", lambda label, _scene: _Node(label))


def test_sub_is_component_wise_difference() -> None:
    assert sub([3, 2, 1], [1, 1, 1]) == [2, 1, 0]


def test_enm_27_a_joint_hangs_on_its_parent_at_the_offset_of_its_pivots(monkeypatch: Any) -> None:
    monkeypatch.setattr(jm, "field", lambda obj, key, default: obj.get(key, default))
    root = _Root("root")
    design = {"joints": {"hip": _spec(None, 0, 0), "knee": _spec("hip", 0, -3)}}
    frames = joint_frames("enemy", design, root)
    hip, knee = frames["hip"], frames["knee"]
    assert hip.node.parent is root
    assert knee.node.parent is hip.node
    # The knee pivots 3 units down from the hip (the design's y is up, the model's z is back).
    assert knee.node.at == pytest.approx(sub(knee.origin, hip.origin))


def test_a_joint_with_no_parent_pivots_on_the_root(monkeypatch: Any) -> None:
    monkeypatch.setattr(jm, "field", lambda obj, key, default: obj.get(key, default))
    root = _Root("root")
    design = {"joints": {"shoulder": _spec(None, 2, 1)}}
    frames = joint_frames("enemy", design, root)
    assert frames["shoulder"].node.parent is root
    assert frames["shoulder"].origin == pytest.approx([-2, 0, -1])


def test_a_joint_on_a_missing_joint_is_an_error(monkeypatch: Any) -> None:
    monkeypatch.setattr(jm, "field", lambda obj, key, default: obj.get(key, default))
    root = _Root("root")
    design = {"joints": {"tail": _spec("ghost", 0, 0)}}
    with pytest.raises(Exception, match='has no joint "ghost"'):
        joint_frames("enemy", design, root)


def test_frame_keeps_its_node_and_pivot() -> None:
    frame = Frame("node", [1, 2, 3])
    assert frame.node == "node"
    assert frame.origin == [1, 2, 3]
