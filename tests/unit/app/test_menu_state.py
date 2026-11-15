# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/menu_state.py`."""
# (the menu flow's data).

from app.menu_state import MenuFlowOptions, MenuState
from app.settings_menu import Volumes
from core.content.level_catalog import LevelCatalog


def test_ui_flow_04_a_menu_state_keeps_the_fields_it_was_built_with() -> None:
    state = MenuState(
        "level-select",
        2,
        "1-3",
        "alpha",
        "1-2",
        transitioning=True,
        level_result=None,
        choice=1,
        attempt=4,
        resume=None,
        paused=False,
        leaving=False,
        volumes=Volumes(5, 6),
    )
    assert (state.screen, state.selection, state.selected_id) == ("level-select", 2, "1-3")
    assert state.ship_id == "alpha"
    assert state.transitioning is True
    assert state.attempt == 4
    assert state.volumes.sfx == 6


def test_ui_flow_04_the_flow_options_keep_their_data() -> None:
    levels = LevelCatalog(1, [])
    options = MenuFlowOptions("alpha", levels, 0.25, None, None, 10)
    assert options.ship_id == "alpha"
    assert options.levels is levels
    assert options.transition_seconds == 0.25
    assert options.volume_steps == 10
