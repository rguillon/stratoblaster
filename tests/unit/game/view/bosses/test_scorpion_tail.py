# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/scorpion_tail.py`.

The Scorpion's tail, arched over its back at rest, unfolding straight out behind it as it turns
round (MB-SCORPION-04, MB-SCORPION-11, D-228).
"""

import itertools
import math
from types import SimpleNamespace

import pytest
from helpers.bosses_top_fakes import FakeNode, patch_models
from helpers.islands import loose_triangles

from game.config.boss_look import BOSS_LOOK
from game.view.bosses import scorpion_tail
from game.view.bosses.scorpion_look import YELLOW
from game.view.bosses.scorpion_tail import (
    STRETCH,
    TAIL,
    build_tail_rig,
    segment_count,
    tail_pose,
    tail_triangles,
    unfolding,
)


def tail_tip(unfold: float) -> list[float]:
    """Where the tail of `tail_pose(unfold)` ends, `(z, y)`: the far end of its last segment."""
    z, y, angle, stretch = tail_pose(unfold)[-1]
    a, b = TAIL[-2], TAIL[-1]
    length = math.hypot(b[0] - a[0], b[1] - a[1]) * stretch
    return [z + math.cos(angle) * length, y + math.sin(angle) * length]


def test_at_rest_the_tail_follows_its_arched_spine() -> None:
    pose = tail_pose(0)
    assert len(pose) == segment_count() == len(TAIL) - 1
    for i, seg in enumerate(pose):
        assert seg[:2] == pytest.approx(TAIL[i])
        assert seg[3] == 1
    assert tail_tip(0) == pytest.approx(TAIL[-1])


def test_unfolded_it_runs_straight_out_behind_a_little_longer() -> None:
    pose = tail_pose(1)
    assert all(seg[2] == pytest.approx(math.pi) for seg in pose)
    assert all(seg[1] == pytest.approx(TAIL[0][1]) for seg in pose)
    assert all(seg[3] == pytest.approx(STRETCH) for seg in pose)
    tip = tail_tip(1)
    length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in itertools.pairwise(TAIL))
    assert tip == pytest.approx([TAIL[0][0] - length * STRETCH, TAIL[0][1]])


def test_halfway_it_swings_back_over_the_top() -> None:
    tip = tail_tip(0.5)
    assert tip[1] > TAIL[0][1]
    assert TAIL[-1][0] > tip[0] > tail_tip(1)[0]


def test_the_tail_holds_together_arched_and_unfolded() -> None:
    for unfold in [0, 0.5, 1]:
        assert not any(loose_triangles(tail_triangles(unfold), BOSS_LOOK.armour.hold))


def test_it_unfolds_from_the_armour_burst_to_the_weapons_swinging_up() -> None:
    look = BOSS_LOOK.reveal

    def boss(form: int, into: int, t: float) -> SimpleNamespace:
        return SimpleNamespace(form=form, transforming_into=into, transform=t)

    assert unfolding(None) == 0
    assert unfolding(boss(0, 0, 0)) == 0
    assert unfolding(boss(0, 1, look.burst)) == 0
    assert unfolding(boss(0, 1, look.swing[1])) == 1
    assert 0 < unfolding(boss(0, 1, (look.burst + look.swing[1]) / 2)) < 1
    assert unfolding(boss(1, 0, 0)) == 1


def test_d228_the_tail_rig_is_a_model_a_segment_each_on_its_node_under_the_boss(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    builder = patch_models(monkeypatch, scorpion_tail)
    root = FakeNode("scorpion", "scene")
    rig = build_tail_rig(root, YELLOW, None)
    assert len(rig.nodes) == len(rig.models) == segment_count()
    for i in range(segment_count()):
        assert rig.nodes[i].name == "scorpion-tail-" + str(i)
        assert rig.nodes[i].parent is root
        assert rig.models[i].root.parent is rig.nodes[i]
        assert builder.faces("scorpion-tail-" + str(i), "flesh") > 0


def test_mb_scorpion_11_the_rig_poses_its_segments_as_the_tail_unfolds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_models(monkeypatch, scorpion_tail)
    rig = build_tail_rig(FakeNode("scorpion", "scene"), YELLOW, None)
    rig.show(None, {"charge": 0}, 0.1)
    rest = tail_pose(0)
    for i, node in enumerate(rig.nodes):
        assert node.position.xyz() == pytest.approx([0, rest[i][1], rest[i][0]])
        assert node.rotation.x == pytest.approx(-rest[i][2])
        assert node.scaling.xyz() == pytest.approx([1, 1, 1])
    turned = SimpleNamespace(form=1, transforming_into=0, transform=0)
    rig.show(turned, {"charge": 0}, 0.1)
    out = tail_pose(1)
    for i, node in enumerate(rig.nodes):
        assert node.position.xyz() == pytest.approx([0, out[i][1], out[i][0]])
        assert node.scaling.z == pytest.approx(STRETCH)
    assert all(len(m.synced) == 2 for m in rig.models)
