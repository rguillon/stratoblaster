"""Unit tests of `src/game/view/bosses/boss_reveal.py`: hidden weapon parts coming out as a boss
transforms."""

import math
from types import SimpleNamespace

import pytest

from game.config.boss_look import BOSS_LOOK
from game.view.bosses import boss_reveal
from game.view.bosses.boss_reveal import (
    HIDDEN,
    REVEALING,
    SHOWN,
    RevealView,
    ease,
    plate_pose,
    reveal_phase,
    rise_pose,
    unfold_pose,
)


def test_a_part_is_hidden_until_its_transformation_then_coming_out_then_shown() -> None:
    assert reveal_phase(None, 0, 0) == SHOWN
    assert reveal_phase(1, 0, 0) == HIDDEN
    assert reveal_phase(2, 0, 1) == HIDDEN
    assert reveal_phase(1, 0, 1) == REVEALING
    assert reveal_phase(1, 1, 0) == SHOWN
    assert reveal_phase(1, 1, 2) == SHOWN


def test_ease_goes_smoothly_from_0_to_1() -> None:
    assert (ease(-1), ease(0), ease(0.5), ease(1), ease(2)) == (0, 0, 0.5, 1, 1)


def test_an_unfolding_part_grows_from_its_spot_and_swings_out() -> None:
    base = [1.0, 2.0, 3.0]
    at = [-20.0, 4.0, 10.0]
    start = unfold_pose(base, at, 0)
    assert start.scale == 0
    # At scale 0 the whole part sits at its spot.
    assert start.position == pytest.approx([base[i] + at[i] for i in range(3)])
    assert abs(start.yaw) == pytest.approx(BOSS_LOOK.reveal.unfoldTurn)
    end = unfold_pose(base, at, 1)
    assert end.scale == 1
    assert end.yaw == 0
    assert end.position == pytest.approx(base)


def test_parts_either_side_swing_out_opposite_ways() -> None:
    assert unfold_pose([0, 0, 0], [5, 0, 0], 0).yaw == -unfold_pose([0, 0, 0], [-5, 0, 0], 0).yaw


def test_an_armoured_part_rises_from_under_the_hull() -> None:
    base = [0.0, 1.0, 0.0]
    assert rise_pose(base, 10, 0).position[1] == pytest.approx(1 - 10 * BOSS_LOOK.reveal.sink)
    assert rise_pose(base, 10, 1).position == base


def test_a_plate_is_thrown_out_from_the_centre_and_shrinks_away() -> None:
    at = [30.0, 0.0, -40.0]
    rest = plate_pose(at, 10, 0)
    assert rest.position == pytest.approx([0, 0, 0])
    assert rest.scale == 1
    half = plate_pose(at, 10, 0.5)
    out = half.position
    # Outward, along the plate's direction from the centre.
    assert out[0] * at[0] + out[2] * at[2] > 0
    assert out[0] / out[2] == pytest.approx(at[0] / at[2])
    assert out[1] > 0
    assert half.yaw > 0
    assert plate_pose(at, 10, 1).scale == 0


def _node() -> SimpleNamespace:
    return SimpleNamespace(
        position=SimpleNamespace(set=lambda *v: None, x=0, y=0, z=0),
        scaling=SimpleNamespace(set=lambda *v: None),
        rotation=SimpleNamespace(y=0),
        enabled=None,
    )


@pytest.fixture
def enabled(monkeypatch: pytest.MonkeyPatch) -> dict[int, bool]:
    seen: dict[int, bool] = {}
    monkeypatch.setattr(boss_reveal, "set_enabled", lambda node, on: seen.__setitem__(id(node), on))
    return seen


def test_a_hidden_part_is_not_shown_and_its_plate_is(enabled: dict[int, bool]) -> None:
    root, plate = _node(), _node()
    view = RevealView(1, "armour", root, [0, 0, 0], [5, 0, 5], 4, plate, [0, 0, 0])
    assert view.show(0, 0, 0) == HIDDEN
    assert enabled[id(root)] is False
    assert enabled[id(plate)] is True


def test_once_revealed_the_plate_is_gone(enabled: dict[int, bool]) -> None:
    root, plate = _node(), _node()
    view = RevealView(1, "armour", root, [0, 0, 0], [5, 0, 5], 4, plate, [0, 0, 0])
    assert view.show(0, 1, 0.5) == REVEALING
    assert enabled[id(plate)] is True
    assert view.show(1, 0, 0) == SHOWN
    assert enabled[id(plate)] is False


def test_an_unfolding_part_turns_as_it_comes_out(enabled: dict[int, bool]) -> None:
    root = _node()
    view = RevealView(1, "unfold", root, [0, 0, 0], [5, 0, 5], 4, None, [0, 0, 0])
    view.show(0, 1, 0.25)
    assert root.rotation.y != 0
    assert abs(root.rotation.y) < BOSS_LOOK.reveal.unfoldTurn
    assert math.isfinite(root.rotation.y)
