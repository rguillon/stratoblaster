"""Unit tests of `src/app/menu_state.py`."""
# (the menu flow's data).

from app.menu_state import MenuFlowOptions, MenuState
from app.settings_menu import Volumes
from core.content.level_catalog import LevelCatalog


def test_p01_r01_a_menu_state_keeps_the_fields_it_was_built_with() -> None:
    state = MenuState(
        "level-select",
        2,
        "1-3",
        "beta",
        "alpha",
        "1-2",
        True,
        None,
        1,
        4,
        None,
        False,
        False,
        Volumes(5, 6),
    )
    assert (state.screen, state.selection, state.selected_id) == ("level-select", 2, "1-3")
    assert state.highlighted_ship_id == "beta"
    assert state.chosen_ship_id == "alpha"
    assert state.transitioning is True
    assert state.attempt == 4
    assert state.volumes.sfx == 6


def test_p01_r01_the_flow_options_keep_their_data() -> None:
    levels = LevelCatalog(1, [])
    options = MenuFlowOptions(["alpha"], levels, None, 0.25, None, None, 10)
    assert options.ship_ids == ["alpha"]
    assert options.levels is levels
    assert options.transition_seconds == 0.25
    assert options.volume_steps == 10
