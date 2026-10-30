"""The screens of the menu flow (`core.menu.menu_screen`, P01-R01)."""

import pytest

from core.menu.menu_screen import MENU_TRANSITIONS, can_transition


@pytest.mark.parametrize(
    ("source", "target"),
    [
        ("loading", "title"),
        ("title", "ship-select"),
        ("title", "settings"),
        ("ship-select", "level-select"),
        ("ship-select", "title"),
        ("level-select", "game"),
        ("level-select", "ship-select"),
        ("game", "pause"),
        ("game", "level-select"),  # A completed level returns to the level select (P06-R03).
        ("pause", "game"),
        ("pause", "settings"),
        ("pause", "title"),
        ("settings", "title"),
        ("settings", "pause"),
    ],
)
def test_p01_r01_the_flow_allows_its_transitions(source: str, target: str) -> None:
    assert can_transition(source, target)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("source", "target"),
    [
        ("loading", "game"),
        ("title", "game"),  # The flow goes through ship and level select first.
        ("game", "title"),  # The level is left through the pause menu.
        ("settings", "game"),
        ("title", "title"),
    ],
)
def test_p01_r01_the_flow_refuses_other_transitions(source: str, target: str) -> None:
    assert not can_transition(source, target)  # type: ignore[arg-type]


def test_every_screen_has_its_transitions_listed() -> None:
    assert set(MENU_TRANSITIONS) == {
        "loading",
        "title",
        "ship-select",
        "level-select",
        "game",
        "pause",
        "settings",
    }


def test_an_unknown_screen_raises() -> None:
    with pytest.raises(KeyError):
        can_transition("nowhere", "title")  # type: ignore[arg-type]
