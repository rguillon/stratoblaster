# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/jointed_model.py`."""

from types import SimpleNamespace
from typing import Any

import pytest

from core.entities.jointed_enemy import JointedEnemy
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


# --- The jointed model built from its design and drawing (ENM-27 to ENM-29). ---


class _Model:
    """What `build_enemy_model` gives: a root node and a sync recording its calls."""

    def __init__(self, name: str, draw: Any, breath: Any) -> None:
        self.name = name
        self.draw = draw
        self.breath = breath
        self.root = _Part(name)
        self.synced: list[Any] = []

    def sync(self, enemy: Any, dt: float) -> None:
        self.synced.append((enemy, dt))


class _Part(_Root):
    """A model root: a node that can be shown or hidden."""

    def __init__(self, label: str) -> None:
        super().__init__(label)
        self.enabled = True

    def setEnabled(self, on: bool) -> None:
        self.enabled = on


@pytest.fixture
def models(monkeypatch: Any) -> dict[str, _Model]:
    """Record the models built, by name, each a `_Model`; the breath is `"breath"`."""
    built: dict[str, _Model] = {}

    def build(name: str, _scene: Any, color: Any, draw: Any, breath: Any) -> _Model:
        assert color == [1, 1, 0]
        built[name] = _Model(name, draw, breath)
        return built[name]

    monkeypatch.setattr(jm, "build_enemy_model", build)
    monkeypatch.setattr(jm, "new_breath", lambda: "breath")
    return built


DESIGN = {
    "joints": {"hip": _spec(None, 4, 2)},
    "parts": [
        {"id": "claw", "joint": "hip"},
        {"id": "orb", "orbits": True},
        {"id": "plate"},
    ],
}


def _drawing(**extra: Any) -> dict[str, Any]:
    return {
        "body": "draw-body",
        "limbs": {"hip": "draw-leg", "tail": "draw-tail"},
        "parts": {"claw": "draw-claw", "orb": "draw-orb", "plate": "draw-plate"},
        **extra,
    }


def test_enm_44_the_hull_limbs_and_parts_breathe_as_one(models: dict[str, _Model]) -> None:
    jm.build_jointed_model("crab", "scene", [1, 1, 0], DESIGN, _drawing(ring="draw-ring"))
    assert set(models) == {
        "crab",
        "crab-ring",
        "crab-hip",
        "crab-tail",
        "crab-claw",
        "crab-orb",
        "crab-plate",
    }
    assert {model.breath for model in models.values()} == {"breath"}
    assert models["crab"].draw == "draw-body"
    assert models["crab-claw"].draw == "draw-claw"


def test_enm_27_limbs_and_parts_hang_on_their_joints_drawn_as_at_rest(
    models: dict[str, _Model],
) -> None:
    built = jm.build_jointed_model("crab", "scene", [1, 1, 0], DESIGN, _drawing())
    root = models["crab"].root
    assert built.root is root
    hip = models["crab-hip"].root.parent
    assert hip.label == "crab-hip-joint"
    assert hip.parent is root
    # A piece on a joint is drawn in model space: moved back from the joint's pivot.
    pivot = [-4, 0, -2]
    assert models["crab-hip"].root.at == [-p for p in pivot]
    assert models["crab-claw"].root.parent is hip
    assert models["crab-claw"].root.at == [-p for p in pivot]


def test_enm_27_a_limb_or_part_on_no_joint_of_the_design_hangs_on_the_root(
    models: dict[str, _Model],
) -> None:
    jm.build_jointed_model("crab", "scene", [1, 1, 0], DESIGN, _drawing())
    root = models["crab"].root
    assert models["crab-tail"].root.parent is root
    assert models["crab-tail"].root.at == [0, 0, 0]
    assert models["crab-plate"].root.parent is root


def test_enm_27_orbiting_parts_and_the_ring_turn_on_the_ring_node(
    models: dict[str, _Model],
) -> None:
    jm.build_jointed_model("crab", "scene", [1, 1, 0], DESIGN, _drawing(ring="draw-ring"))
    ring = models["crab-orb"].root.parent
    assert ring.label == "crab-ring"
    assert ring.parent is models["crab"].root
    assert models["crab-ring"].root.parent is ring


def test_enm_27_a_model_without_a_ring_drawing_has_no_ring_piece(
    models: dict[str, _Model],
) -> None:
    jm.build_jointed_model("crab", "scene", [1, 1, 0], {"parts": []}, {"body": "draw-body"})
    assert set(models) == {"crab"}


def test_a_part_the_drawing_does_not_draw_is_an_error(models: dict[str, _Model]) -> None:
    drawing = _drawing()
    drawing["parts"]["plate"] = None
    with pytest.raises(jm.JointedModelError, match='does not draw its part "plate"'):
        jm.build_jointed_model("crab", "scene", [1, 1, 0], DESIGN, drawing)
    assert models["crab-claw"].draw == "draw-claw"


class _Crab(JointedEnemy):
    """A jointed enemy with only what the model reads: its joints' angles, spin and parts."""

    def __init__(self, angles: dict[str, float], spin: float, destroyed: list[bool]) -> None:
        # The state the model reads, without the sim's set-up.
        self.joints = SimpleNamespace(angle=lambda joint_id: angles[joint_id])
        self.spin = spin
        self.parts = [SimpleNamespace(destroyed=d) for d in destroyed]


def test_enm_28_the_joints_and_ring_turn_as_the_enemy_s_do(models: dict[str, _Model]) -> None:
    built = jm.build_jointed_model("crab", "scene", [1, 1, 0], DESIGN, _drawing(ring="draw-ring"))
    crab = _Crab({"hip": 0.4}, 1.25, [False, False, False])
    built.sync(crab, 0.02)
    assert models["crab-hip"].root.parent.rotation.y == pytest.approx(0.4)
    assert models["crab-orb"].root.parent.rotation.y == pytest.approx(1.25)
    # The hull and every piece are kept in step.
    assert all(model.synced == [(crab, 0.02)] for model in models.values())


def test_enm_29_a_destroyed_part_disappears(models: dict[str, _Model]) -> None:
    built = jm.build_jointed_model("crab", "scene", [1, 1, 0], DESIGN, _drawing())
    # The plate has no part in the enemy (yet): it is shown.
    built.sync(_Crab({"hip": 0.0}, 0.0, [True, False]), 0.02)
    assert models["crab-claw"].root.enabled is False
    assert models["crab-orb"].root.enabled is True
    assert models["crab-plate"].root.enabled is True


def test_an_enemy_without_joints_only_steps_the_model(models: dict[str, _Model]) -> None:
    built = jm.build_jointed_model("crab", "scene", [1, 1, 0], DESIGN, _drawing())
    plain = SimpleNamespace(charge=0.0)
    built.sync(plain, 0.1)
    assert models["crab"].synced == [(plain, 0.1)]
    assert models["crab-hip"].root.parent.rotation.y == 0.0
    assert models["crab-claw"].root.enabled is True
