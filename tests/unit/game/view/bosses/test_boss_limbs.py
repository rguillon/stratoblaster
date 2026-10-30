"""Unit tests of `src/game/view/bosses/boss_limbs.py`."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.view.bosses import boss_limbs
from game.view.bosses.boss_limbs import (
    ORIGIN,
    BossLimbs,
    JointFrame,
    JointFrames,
    _index_of_part,
    boss_point,
    hang,
)


class Rec(dict):
    """A config record: a dict whose keys are also readable as attributes, as the game's are."""

    def __getattr__(self, key: str):
        try:
            return self[key]
        except KeyError as error:
            raise AttributeError(key) from error


class _Node:
    """A transform node stand-in: a parent and a position it is set to."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.parent = None
        self.rotation = SimpleNamespace(y=0.0)
        self.position = SimpleNamespace(set=self._set)
        self.at = None

    def _set(self, x: float, y: float, z: float) -> None:
        self.at = [x, y, z]


@pytest.fixture
def scene_nodes(monkeypatch):
    """Nodes made by `new_transform_node` are `_Node`s; visibility changes are recorded."""
    made: list[_Node] = []

    def new_node(label: str, _scene) -> _Node:
        node = _Node(label)
        made.append(node)
        return node

    monkeypatch.setattr(boss_limbs, "new_transform_node", new_node)
    enabled: list[tuple[_Node, bool]] = []
    monkeypatch.setattr(boss_limbs, "set_enabled", lambda node, on: enabled.append((node, on)))
    monkeypatch.setattr(boss_limbs, "_keys", lambda value: list(value.keys()))
    monkeypatch.setattr(boss_limbs, "_entries", lambda value: list(value.items()))
    return SimpleNamespace(made=made, enabled=enabled)


def _root() -> _Node:
    root = _Node("root")
    root.getScene = lambda: "scene"
    return root


def _design(joints: dict, parts: list | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        id="boss",
        stats=Rec(
            joints=Rec({k: Rec(v) if v is not None else None for k, v in joints.items()}),
            parts=parts or [],
        ),
    )


def test_boss_point_puts_the_nose_down_the_screen_with_x_mirrored():
    assert boss_point(3, 4) == [-3, 0, -4]
    assert boss_point(3, 4, height=2) == [-3, 2, -4]


def test_joint_frames_hang_each_joint_on_its_parent_at_its_pivot(scene_nodes):
    design = _design(
        {
            "neck": {"parent": None, "x": 2, "y": 3},
            "head": {"parent": "neck", "x": 4, "y": 3},
        }
    )
    frames = JointFrames(design, _root())
    neck = frames.frame("neck", None)
    head = frames.frame("head", None)
    assert neck.origin == pytest.approx([-2, 0, -3])
    # The head's node hangs on the neck's and sits 2 units across from it.
    assert head.node.parent is neck.node
    assert head.node.at == pytest.approx([-2, 0, 0])


def test_a_joint_on_no_joint_hangs_on_the_root(scene_nodes):
    root = _root()
    frames = JointFrames(_design({"hip": {"parent": None, "x": 0, "y": 0}}), root)
    assert frames.frame("hip", None).node.parent is root


def test_joint_with_a_missing_parent_is_an_error(scene_nodes):
    design = _design({"tail": {"parent": "ghost", "x": 0, "y": 0}, "ghost": None})
    with pytest.raises(ValueError, match='has no joint "ghost"'):
        JointFrames(design, _root())


def test_frame_of_no_joint_is_the_holder_at_the_origin(scene_nodes):
    frames = JointFrames(_design({}), _root())
    holder = _Node("holder")
    found = frames.frame(None, holder)
    assert found.node is holder
    assert found.origin == ORIGIN


def test_frame_of_an_unknown_joint_is_an_error(scene_nodes):
    frames = JointFrames(_design({}), _root())
    with pytest.raises(ValueError, match='No boss joint "arm"'):
        frames.frame("arm", _Node("holder"))


def test_show_turns_each_joint_as_the_boss_joints_are(scene_nodes):
    design = _design({"neck": Rec(parent=None, x=0, y=0)})
    frames = JointFrames(design, _root())
    boss = SimpleNamespace(joints=SimpleNamespace(angle=lambda joint_id: 0.75))
    frames.show(boss)
    assert frames.frame("neck", None).node.rotation.y == pytest.approx(0.75)


def test_show_without_a_boss_returns_the_joints_to_rest(scene_nodes):
    design = _design({"neck": Rec(parent=None, x=0, y=0)})
    frames = JointFrames(design, _root())
    frames.frame("neck", None).node.rotation.y = 2.0
    frames.show(None)
    assert frames.frame("neck", None).node.rotation.y == 0


def test_hang_puts_a_node_on_a_frame_at_its_model_point(scene_nodes):
    frame = JointFrame(_Node("joint"), [1, 1, 1])
    node = _Node("limb")
    hang(node, [4, 2, 1], frame)
    assert node.parent is frame.node
    assert node.at == pytest.approx([3, 1, 0])


def test_index_of_part_finds_the_part_by_id_or_is_minus_one():
    parts = [SimpleNamespace(id="a"), SimpleNamespace(id="b")]
    assert _index_of_part(parts, "b") == 1
    assert _index_of_part(parts, "z") == -1


def _limb_build(joint, draw):
    """A limb group: a model with a root and a sync, and a `show` that is recorded."""
    group = MagicMock()
    group.model.root = _Node("limb-" + joint)
    return group


def test_limbs_hang_on_their_joints_and_follow_their_parts(scene_nodes):
    design = _design(
        {"neck": Rec(parent=None, x=0, y=0)},
        parts=[SimpleNamespace(id="jaw")],
    )
    joints = JointFrames(design, _root())
    limbs = BossLimbs(
        design,
        {"neck": Rec(draw=None, part="jaw")},
        joints,
        _limb_build,
    )
    assert len(limbs._limbs) == 1
    group, part = limbs._limbs[0]
    assert part == 0
    assert group.model.root.parent is joints.frame("neck", None).node


def test_a_limb_for_an_unknown_part_is_an_error(scene_nodes):
    design = _design({"neck": Rec(parent=None, x=0, y=0)}, parts=[])
    joints = JointFrames(design, _root())
    with pytest.raises(ValueError, match="belongs to no part"):
        BossLimbs(design, {"neck": Rec(draw=None, part="ghost")}, joints, _limb_build)


def test_a_limb_of_a_destroyed_part_is_hidden_with_it(scene_nodes):
    design = _design(
        {"neck": Rec(parent=None, x=0, y=0)},
        parts=[SimpleNamespace(id="jaw")],
    )
    joints = JointFrames(design, _root())
    limbs = BossLimbs(design, {"neck": Rec(draw=None, part="jaw")}, joints, _limb_build)
    group, _part = limbs._limbs[0]
    group.show = MagicMock()
    destroyed = SimpleNamespace(destroyed=True, since_hit=0.0)
    boss = SimpleNamespace(
        joints=SimpleNamespace(angle=lambda joint_id: 0.0),
        parts=[destroyed],
        core=SimpleNamespace(since_hit=1.0),
    )
    limbs.show(boss, {}, 0.1)
    # The limb is hidden with its part, and it still shows its wound state.
    assert (group.model.root, False) in scene_nodes.enabled
    group.show.assert_called_once_with(0.0)


def test_a_limb_of_a_live_core_limb_flashes_with_the_core(scene_nodes):
    design = _design({"neck": Rec(parent=None, x=0, y=0)}, parts=[])
    joints = JointFrames(design, _root())
    limbs = BossLimbs(design, {"neck": Rec(draw=None)}, joints, _limb_build)
    group, part = limbs._limbs[0]
    assert part == -1
    group.show = MagicMock()
    boss = SimpleNamespace(
        joints=SimpleNamespace(angle=lambda joint_id: 0.0),
        parts=[],
        core=SimpleNamespace(since_hit=0.5),
    )
    limbs.show(boss, {}, 0.1)
    group.show.assert_called_once_with(0.5)
    assert (group.model.root, True) in scene_nodes.enabled


def test_a_limb_without_a_boss_is_synced_but_not_shown(scene_nodes):
    design = _design({"neck": Rec(parent=None, x=0, y=0)}, parts=[])
    joints = JointFrames(design, _root())
    limbs = BossLimbs(design, {"neck": Rec(draw=None)}, joints, _limb_build)
    group, _part = limbs._limbs[0]
    group.show = MagicMock()
    limbs.show(None, "lit", 0.1)
    group.model.sync.assert_called_once_with("lit", 0.1)
    group.show.assert_not_called()
