# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/boss_reveal.py`.

Hidden weapon parts unfold as a boss transforms (BOSS-43; docs/superpowers/specs/2026-10-31-boss-
armour-shedding-design.md).
"""

import math
from types import SimpleNamespace

import pytest

from game.config.boss_look import BOSS_LOOK
from game.config.record import record
from game.view.bosses import boss_reveal
from game.view.bosses.boss_reveal import (
    HIDDEN,
    REVEALING,
    SHOWN,
    RevealView,
    Slide,
    back_out,
    build_reveal,
    ease,
    hinge_pose,
    reveal_phase,
    share,
    slide_offset,
    weapon_hinge,
)

LOOK = BOSS_LOOK.reveal


def test_a_part_is_hidden_until_its_transformation_then_coming_out_then_shown() -> None:
    assert reveal_phase(None, 0, 0) == SHOWN
    assert reveal_phase(1, 0, 0) == HIDDEN
    assert reveal_phase(2, 0, 1) == HIDDEN
    assert reveal_phase(1, 0, 1) == REVEALING
    assert reveal_phase(1, 1, 0) == SHOWN
    assert reveal_phase(1, 1, 2) == SHOWN


def test_ease_goes_smoothly_from_0_to_1() -> None:
    assert (ease(-1), ease(0), ease(0.5), ease(1), ease(2)) == (0, 0, 0.5, 1, 1)


def test_back_out_overshoots_then_settles_on_1() -> None:
    assert back_out(0, 1.7) == pytest.approx(0)
    assert back_out(1, 1.7) == pytest.approx(1)
    assert max(back_out(k / 100, 1.7) for k in range(101)) > 1.05


def test_share_is_how_far_through_a_span() -> None:
    assert (share(0.1, [0.2, 0.6]), share(0.4, [0.2, 0.6]), share(0.9, [0.2, 0.6])) == (
        0,
        pytest.approx(0.5),
        1,
    )


def test_a_hinged_part_starts_folded_and_sunk_and_ends_at_rest() -> None:
    base = [1.0, 2.0, 3.0]
    hinge = [-20.0, 0.0, 10.0]
    start = hinge_pose(base, hinge, 2.4, 6, 0)
    assert start.yaw == pytest.approx(2.4)
    assert start.position[1] == pytest.approx(2 - 6)
    end = hinge_pose(base, hinge, 2.4, 6, 1)
    assert end.yaw == 0
    assert end.position == pytest.approx(base)


def test_the_hinge_stays_put_as_the_part_swings() -> None:
    base = [0.0, 0.0, 0.0]
    hinge = [-20.0, 0.0, 10.0]
    for t in [0, 0.3, 0.7]:
        pose = hinge_pose(base, hinge, 2.4, 0, t)
        c = math.cos(pose.yaw)
        s = math.sin(pose.yaw)
        # The hinge point of the turned, moved root lands back on itself.
        x = hinge[0] * c + hinge[2] * s + pose.position[0]
        z = -hinge[0] * s + hinge[2] * c + pose.position[2]
        assert [x, z] == pytest.approx([hinge[0], hinge[2]])


def test_a_barrel_slides_out_from_back_along_its_axis_and_overshoots() -> None:
    assert slide_offset([0, 0, 1], 10, 0) == pytest.approx([0, 0, -10])
    assert slide_offset([0, 0, 1], 10, 1) == pytest.approx([0, 0, 0])
    assert max(slide_offset([0, 0, 1], 10, k / 50)[2] for k in range(51)) > 0


def test_a_weapon_hinges_on_its_mount_or_its_inner_side() -> None:
    # Model +X is the screen's left: a weapon there hinges towards the centre line.
    hinge, fold = weapon_hinge([30, 0, -5], 10, None)
    assert hinge == [21, 0, -5]
    assert fold > 0
    hinge, fold = weapon_hinge([-30, 0, -5], 10, None)
    assert hinge == [-21, 0, -5]
    assert fold < 0
    hinge, fold = weapon_hinge([0, 0, 20], 10, None)
    assert hinge == [0, 0, 11]
    # A mount: offset in px (X right, Y up), its own fold.
    hinge, fold = weapon_hinge([30, 0, -5], 10, [4, 2, 1.0])
    assert hinge == [26, 0, -7]
    assert fold == 1.0


def _node() -> SimpleNamespace:
    def setter(target: SimpleNamespace) -> object:
        def set_(x: float, y: float, z: float) -> None:
            target.x, target.y, target.z = x, y, z

        return set_

    position = SimpleNamespace(x=0.0, y=0.0, z=0.0)
    position.set = setter(position)
    scaling = SimpleNamespace(x=1.0, y=1.0, z=1.0)
    scaling.set = setter(scaling)
    return SimpleNamespace(position=position, scaling=scaling, rotation=SimpleNamespace(y=0.0))


@pytest.fixture
def enabled(monkeypatch: pytest.MonkeyPatch) -> dict[int, bool]:
    seen: dict[int, bool] = {}
    monkeypatch.setattr(boss_reveal, "set_enabled", lambda node, on: seen.__setitem__(id(node), on))
    return seen


def _view(root: SimpleNamespace, barrel: SimpleNamespace) -> RevealView:
    slide = Slide(barrel, [0, 0, 0], [0, 0, 1], 10)
    return RevealView(1, root, [0, 0, 0], [[21, 0, -5], 2.4], 8, [slide])


def test_a_hidden_part_is_not_shown(enabled: dict[int, bool]) -> None:
    root, barrel = _node(), _node()
    assert _view(root, barrel).show(0, 0, 0) == HIDDEN
    assert enabled[id(root)] is False


def test_it_stays_folded_away_until_the_armour_has_burst(enabled: dict[int, bool]) -> None:
    root, barrel = _node(), _node()
    view = _view(root, barrel)
    assert view.show(0, 1, LOOK.swing[0] / 2) == REVEALING
    assert enabled[id(root)] is False
    view.show(0, 1, (LOOK.swing[0] + LOOK.swing[1]) / 2)
    assert enabled[id(root)] is True
    assert 0 < root.rotation.y < 2.4
    assert root.position.y < 0
    # Its barrel is still in.
    assert barrel.position.z == pytest.approx(-10)


@pytest.mark.usefixtures("enabled")
def test_it_ends_unfolded_with_its_barrel_out_and_never_scales() -> None:
    root, barrel = _node(), _node()
    view = _view(root, barrel)
    for k in range(21):
        view.show(0, 1, k / 20)
        assert (root.scaling.x, barrel.scaling.x) == (1, 1)
    assert root.rotation.y == 0
    assert [root.position.x, root.position.y, root.position.z] == pytest.approx([0, 0, 0])
    assert barrel.position.z == pytest.approx(0)
    assert view.show(1, 0, 0) == SHOWN
    assert barrel.position.z == pytest.approx(0)


def test_build_reveal_reads_the_weapon_mount() -> None:
    root = _node()
    root.position.set(1, 2, 3)
    spec = SimpleNamespace(id="gun", x=-30, y=5, radius=10, reveal=2)
    design = SimpleNamespace(weapons=record({"gun": {"kind": "lance", "mount": [4, 2, 1.0]}}))
    view = build_reveal(design, spec, root, [])
    assert view.reveal == 2
    assert view.base == [1, 2, 3]
    assert view.hinge == [[26, 0, -7], 1.0]
    assert view.sink == pytest.approx(10 * LOOK.sink)
    plain = build_reveal(SimpleNamespace(weapons=None), spec, root, [])
    assert plain.hinge[1] > 0


def test_d228_a_weapon_on_a_rig_rises_into_place_with_no_swing() -> None:
    root = _node()
    spec = SimpleNamespace(id="tail", x=0, y=30, radius=6, reveal=1)
    design = SimpleNamespace(weapons=record({"tail": {"kind": "beam", "rig": True}}))
    view = build_reveal(design, spec, root, [])
    assert view.hinge == [[0, 0, -30], 0]
    assert view.sink == pytest.approx(3)
