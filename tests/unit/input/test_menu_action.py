"""Unit tests of `src/input/menu_action.py`."""

from input.menu_action import (
    DIRECTIONS,
    MENU_ACTIONS,
    MenuSelect,
    MenuSet,
    is_menu_action,
    is_menu_direction,
)


def test_p01_r12_every_direction_is_a_menu_action() -> None:
    assert set(DIRECTIONS) <= set(MENU_ACTIONS)
    assert [is_menu_direction(d) for d in DIRECTIONS] == [True] * 4


def test_p01_r12_non_directions_are_not_moves() -> None:
    for action in ["confirm", "back", "cancel", "pause", "resume"]:
        assert not is_menu_direction(action)


def test_p01_r12_is_menu_action_accepts_only_known_strings() -> None:
    assert is_menu_action("confirm")
    assert not is_menu_action("jump")
    assert not is_menu_action(3)
    assert not is_menu_action(None)


def test_p12_r04_menu_set_keeps_slider_index_and_value() -> None:
    command = MenuSet(2, 0.5)
    assert command.set == 2
    assert command.value == 0.5


def test_p01_r12_menu_select_keeps_entry_index() -> None:
    assert MenuSelect(4).select == 4
