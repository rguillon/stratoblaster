# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/menu_flow.py`."""
# (specs/ui/screen-flow.md and the screens around it).

import pytest

from app.menu_flow import MenuFlow
from app.menu_state import MenuFlowOptions
from app.settings_menu import Volumes
from core.content.level_catalog import LevelCatalog, LevelEntry
from core.systems.level_run_types import LevelCheckpoint, LevelResult
from core.systems.run_arsenal import WeaponLevels
from input.menu_action import MenuSelect, MenuSet

SHIP = "alpha"


def catalog(second_unlocked: bool = False) -> LevelCatalog:
    return LevelCatalog(
        2,
        [
            LevelEntry("1-1", "1-1", 1, 1, unlocked=True),
            LevelEntry("1-2", "1-2", 1, 2, second_unlocked),
            LevelEntry("1-3", "1-3", 1, 3, unlocked=False),
        ],
    )


def make_flow(
    *,
    second_unlocked: bool = False,
    volumes: Volumes | None = None,
    result_delay: float | None = None,
) -> MenuFlow:
    return MenuFlow(
        MenuFlowOptions(
            SHIP,
            catalog(second_unlocked),
            0.25,
            result_delay,
            volumes,
            10,
        )
    )


def settle(flow: MenuFlow) -> None:
    """Lets the screen transition end, so commands are heard again."""
    flow.update(1.0)


def at_title() -> MenuFlow:
    flow = make_flow()
    flow.finish_loading()
    settle(flow)
    return flow


def at_game(**options: object) -> MenuFlow:
    flow = make_flow(**options)  # type: ignore[arg-type]
    flow.finish_loading()
    settle(flow)
    assert flow.dispatch("confirm") == "screen"  # title -> level select
    settle(flow)
    assert flow.dispatch("confirm") == "screen"  # level 1-1 -> game
    settle(flow)
    return flow


def result(outcome: str = "complete", checkpoint: LevelCheckpoint | None = None) -> LevelResult:
    return LevelResult("1-1", 10, 10, outcome, 1234.0, new_high_score=False, checkpoint=checkpoint)


def checkpoint() -> LevelCheckpoint:
    return LevelCheckpoint(0.5, 1, WeaponLevels("guns", {"guns": 2.0}), 900.0)


def test_ui_flow_01_the_flow_starts_on_the_loading_screen_and_ignores_input_there() -> None:
    """Also UI-LOAD-04 (the title follows the loading by itself)."""
    flow = make_flow()
    assert flow.state.screen == "loading"
    assert flow.dispatch("down") == "none"
    flow.finish_loading()
    assert flow.state.screen == "title"


def test_ui_flow_08_input_is_ignored_during_a_screen_transition() -> None:
    flow = make_flow()
    flow.finish_loading()
    assert flow.state.transitioning is True
    assert flow.dispatch("down") == "none"
    settle(flow)
    assert flow.state.transitioning is False
    assert flow.dispatch("down") == "moved"


def test_ui_title_06_the_title_entries_move_with_up_and_down_and_confirm_goes_on() -> None:
    flow = at_title()
    assert flow.state.selected_id == "start"
    assert flow.dispatch("down") == "moved"
    assert flow.state.selected_id == "settings"
    assert flow.dispatch("down") == "none"
    assert flow.dispatch("up") == "moved"
    assert flow.dispatch("confirm") == "screen"
    assert flow.state.screen == "level-select"


def test_ui_set_01_settings_from_the_title_and_back_returns_to_the_title() -> None:
    """Also UI-TITLE-06 and UI-FLOW-05."""
    flow = at_title()
    flow.dispatch(MenuSelect(1))
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    assert flow.state.screen == "settings"
    assert flow.paused is False
    assert flow.dispatch("back") == "screen"
    settle(flow)
    assert flow.state.screen == "title"


def test_ui_input_09_selecting_an_entry_directly_and_bad_indexes() -> None:
    flow = at_title()
    assert flow.dispatch(MenuSelect(1)) == "moved"
    assert flow.dispatch(MenuSelect(1)) == "none"
    assert flow.dispatch(MenuSelect(5)) == "none"
    assert flow.dispatch(MenuSelect(-1)) == "none"


def test_ui_flow_02_start_goes_to_the_level_select_with_the_game_s_one_ship() -> None:
    flow = at_title()
    assert flow.state.ship_id == SHIP
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    assert flow.state.screen == "level-select"
    assert flow.state.ship_id == SHIP


def test_ui_flow_05_back_walks_the_menus_in_reverse() -> None:
    flow = at_title()
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.screen == "level-select"
    assert flow.dispatch("back") == "screen"
    settle(flow)
    assert flow.state.screen == "title"
    assert flow.dispatch("back") == "none"


def test_ui_level_04_a_locked_level_gives_the_locked_feedback_and_stays() -> None:
    flow = at_title()
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selection == 0
    assert flow.dispatch("down") == "moved"
    assert flow.state.selection == 2
    assert flow.dispatch("confirm") == "locked"
    assert flow.state.screen == "level-select"


def test_ui_level_06_the_level_select_starts_on_the_first_unlocked_level() -> None:
    flow = make_flow(second_unlocked=False)
    flow.finish_loading()
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selection == 0
    assert flow.state.selected_id == "1-1"


def test_ui_level_08_a_level_starts_with_a_new_attempt_and_pauses_in_game() -> None:
    flow = at_game()
    assert flow.state.screen == "game"
    assert flow.state.chosen_level_id == "1-1"
    assert flow.state.attempt == 1
    assert flow.paused is False


def test_ui_pause_01_escape_pauses_a_level_and_back_does_nothing_in_it() -> None:
    """Also UI-PAUSE-05 and UI-FLOW-06."""
    flow = at_game()
    assert flow.dispatch("back") == "none"
    assert flow.dispatch("resume") == "none"
    assert flow.dispatch("cancel") == "paused"
    settle(flow)
    assert flow.state.screen == "pause"
    assert flow.paused is True


def test_ui_pause_08_the_pause_menu_resume_entry_goes_back_to_the_same_attempt() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    assert flow.dispatch("confirm") == "resumed"
    settle(flow)
    assert flow.state.screen == "game"
    assert flow.state.attempt == 1


def test_ui_pause_08_start_or_back_on_the_pause_menu_resumes_the_level() -> None:
    """Also UI-INPUT-02."""
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    assert flow.dispatch("back") == "resumed"
    settle(flow)
    assert flow.state.screen == "game"
    flow.dispatch("pause")
    settle(flow)
    assert flow.dispatch("pause") == "resumed"


def test_ui_pause_07_the_pause_menu_moves_between_its_entries() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    assert flow.state.selected_id == "resume"
    assert flow.dispatch("down") == "moved"
    assert flow.state.selected_id == "settings"
    assert flow.dispatch("up") == "moved"
    assert flow.dispatch("left") == "none"


def test_ui_pause_09_settings_opened_from_the_pause_menu_keep_the_level_paused() -> None:
    """Also UI-SET-07."""
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    flow.dispatch("down")
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    assert flow.state.screen == "settings"
    assert flow.paused is True
    assert flow.dispatch("back") == "screen"
    settle(flow)
    assert flow.state.screen == "pause"


def test_ui_pause_10_leaving_the_level_asks_first_and_yes_goes_to_the_title() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    flow.dispatch("down")
    flow.dispatch("down")
    assert flow.dispatch("confirm") == "screen"
    assert flow.state.leaving is True
    assert flow.state.choice == 0
    assert flow.dispatch("right") == "moved"
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    assert flow.state.screen == "title"
    assert flow.paused is False


def test_ui_pause_10_answering_no_closes_the_question_and_back_closes_it_too() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    flow.dispatch("down")
    flow.dispatch("down")
    flow.dispatch("confirm")
    assert flow.dispatch("confirm") == "screen"
    assert flow.state.leaving is False
    flow.dispatch("down")
    flow.dispatch("down")
    flow.dispatch("confirm")
    assert flow.dispatch("back") == "screen"
    assert flow.state.leaving is False


def test_ui_pause_10_the_question_takes_a_direct_pick_of_no_or_yes() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    flow.dispatch("down")
    flow.dispatch("down")
    flow.dispatch("confirm")
    assert flow.dispatch(MenuSelect(1)) == "moved"
    assert flow.state.choice == 1
    assert flow.dispatch(MenuSelect(4)) == "none"


def test_ui_pause_07_the_pause_menu_ignores_a_direct_pick_out_of_range() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    assert flow.dispatch(MenuSelect(7)) == "none"
    assert flow.dispatch(MenuSelect(2)) == "moved"


def test_ui_over_03_a_completed_level_shows_its_result_and_confirm_goes_to_the_next() -> None:
    """Also UI-OVER-01 and UI-LEVEL-07."""
    flow = at_game(second_unlocked=True)
    flow.complete_level(result())
    settle(flow)
    assert flow.state.level_result is not None
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    assert flow.state.screen == "level-select"
    assert flow.state.selection == 1


def test_ui_level_07_no_next_level_when_the_next_one_is_locked() -> None:
    flow = at_game()
    flow.complete_level(result())
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selection == 0


def test_ui_flow_07_a_lost_level_goes_back_to_the_same_level() -> None:
    """Also UI-LEVEL-07 and UI-OVER-05."""
    flow = at_game(second_unlocked=True)
    flow.complete_level(result(outcome="over"))
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selection == 0


def test_ui_pause_06_pausing_and_commands_are_ignored_on_the_result_panel() -> None:
    """Also UI-OVER-04."""
    flow = at_game()
    flow.complete_level(result())
    settle(flow)
    assert flow.pause() is False
    assert flow.dispatch("pause") == "none"
    assert flow.dispatch("back") == "none"
    assert flow.dispatch("down") == "none"


def test_ui_over_01_a_result_is_ignored_on_other_screens() -> None:
    flow = at_title()
    flow.complete_level(result())
    settle(flow)
    assert flow.state.level_result is None


def test_ui_over_06_a_game_over_with_a_checkpoint_offers_two_choices() -> None:
    flow = at_game()
    flow.complete_level(result(outcome="over", checkpoint=checkpoint()))
    settle(flow)
    assert flow.state.choice == 0
    assert flow.dispatch("right") == "moved"
    assert flow.state.choice == 1
    assert flow.dispatch("left") == "moved"
    assert flow.dispatch("left") == "none"
    assert flow.dispatch(MenuSelect(1)) == "moved"
    assert flow.dispatch(MenuSelect(2)) == "none"


def test_ui_over_07_continue_starts_the_level_again_from_its_checkpoint() -> None:
    """Also GAME-LIFE-11 and UI-FLOW-07."""
    flow = at_game()
    flow.complete_level(result(outcome="over", checkpoint=checkpoint()))
    settle(flow)
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    state = flow.state
    assert state.screen == "game"
    assert state.level_result is None
    assert state.attempt == 2
    assert state.resume is not None
    assert state.resume.bosses_passed == 1


def test_ui_over_07_level_select_from_the_game_over_panel_leaves_the_level() -> None:
    flow = at_game()
    flow.complete_level(result(outcome="over", checkpoint=checkpoint()))
    settle(flow)
    flow.dispatch("right")
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    assert flow.state.screen == "level-select"


def test_dev_opt_01_a_directly_started_level_skips_the_menus() -> None:
    flow = make_flow(second_unlocked=True)
    assert flow.play_direct("1-2") is True
    state = flow.state
    assert state.screen == "game"
    assert state.ship_id == SHIP
    assert state.chosen_level_id == "1-2"
    assert state.transitioning is False


@pytest.mark.parametrize(
    ("level", "unlocked"),
    [
        ("nope", True),
        ("1-3", True),
        ("1-2", False),
    ],
)
def test_dev_opt_01_a_direct_start_is_refused_for_unknown_or_locked_levels(
    level: str, unlocked: bool
) -> None:
    flow = make_flow(second_unlocked=unlocked)
    assert flow.play_direct(level) is False
    assert flow.state.screen == "loading"


def test_ui_set_03_a_slider_command_changes_the_volume_and_redraws() -> None:
    flow = make_flow(volumes=Volumes(4, 6))
    flow.finish_loading()
    settle(flow)
    flow.dispatch("down")
    flow.dispatch("confirm")
    settle(flow)
    before = flow.revision
    assert flow.dispatch(MenuSet(0, 7)) == "adjusted"
    assert flow.state.volumes.music == 7
    assert flow.state.volumes.sfx == 6
    assert flow.revision > before


def test_ui_set_05_the_default_volumes_are_used_when_none_are_given() -> None:
    flow = make_flow()
    assert (flow.state.volumes.music, flow.state.volumes.sfx) == (10, 10)


def test_ui_flow_04_a_revision_goes_up_on_every_change() -> None:
    flow = make_flow()
    start = flow.revision
    flow.finish_loading()
    assert flow.revision > start
    settle(flow)
    before = flow.revision
    flow.dispatch("down")
    assert flow.revision > before


def test_ui_flow_04_a_menu_needs_a_ship_and_at_least_one_level() -> None:
    with pytest.raises(ValueError, match="needs a ship"):
        MenuFlow(MenuFlowOptions("", catalog(), 0.25, None, None, None))
    with pytest.raises(ValueError, match="at least one level"):
        MenuFlow(MenuFlowOptions(SHIP, LevelCatalog(1, []), 0.25, None, None, None))


def test_ui_flow_01_the_selected_id_of_each_screen() -> None:
    flow = make_flow()
    assert flow.state.selected_id is None
    flow.finish_loading()
    settle(flow)
    assert flow.state.selected_id == "start"
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selected_id == "1-1"


def test_ui_over_04_a_result_delay_replaces_the_transition_time() -> None:
    flow = make_flow(result_delay=2.0)
    flow.finish_loading()
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    flow.complete_level(result())
    assert flow.state.transitioning is True
    flow.update(1.0)
    assert flow.state.transitioning is True
    flow.update(1.5)
    assert flow.state.transitioning is False


# D-199: the dev menu and its viewers (`?dev`).

DEV_COUNTS = [3, 4, 2, 5, 6, 3, 2]


def dev_flow() -> MenuFlow:
    flow = MenuFlow(MenuFlowOptions(SHIP, catalog(), 0.25, None, None, 10, list(DEV_COUNTS)))
    flow.finish_loading()
    settle(flow)
    return flow


def at_dev_menu() -> MenuFlow:
    flow = dev_flow()
    flow.dispatch("down")
    flow.dispatch("down")
    flow.dispatch("confirm")
    settle(flow)
    return flow


def fullscreen_flow(dev: bool = False) -> MenuFlow:
    counts = list(DEV_COUNTS) if dev else None
    flow = MenuFlow(MenuFlowOptions(SHIP, catalog(), 0.25, None, None, 10, counts, None, True))
    flow.finish_loading()
    settle(flow)
    return flow


def test_ui_title_11_the_full_screen_entry_follows_settings_and_toggles_without_leaving() -> None:
    flow = fullscreen_flow()
    flow.dispatch("down")
    flow.dispatch("down")
    assert flow.state.selected_id == "fullscreen"
    assert flow.dispatch("down") == "none"
    assert flow.dispatch("confirm") == "fullscreen"
    assert flow.state.screen == "title"
    assert flow.state.selected_id == "fullscreen"


def test_ui_title_11_the_full_screen_entry_comes_before_dev() -> None:
    flow = fullscreen_flow(dev=True)
    for _ in range(3):
        flow.dispatch("down")
    assert flow.state.selected_id == "dev"
    flow.dispatch("up")
    assert flow.state.selected_id == "fullscreen"


def test_d199_without_dev_counts_the_title_has_no_dev_entry() -> None:
    """DEV-MENU-01."""
    flow = at_title()
    flow.dispatch("down")
    flow.dispatch("down")
    assert flow.state.selected_id == "settings"


def test_d199_the_dev_entry_comes_after_settings_and_opens_the_dev_menu() -> None:
    """DEV-MENU-01, DEV-MENU-03."""
    flow = dev_flow()
    flow.dispatch("down")
    flow.dispatch("down")
    assert flow.state.selected_id == "dev"
    assert flow.dispatch("confirm") == "screen"
    assert flow.state.screen == "dev"
    assert flow.state.selected_id == "ships"
    assert flow.state.dev_viewer is None


def test_d199_a_dev_menu_entry_opens_its_viewer_on_its_first_item() -> None:
    """DEV-MENU-03."""
    flow = at_dev_menu()
    flow.dispatch("down")
    assert flow.state.selected_id == "enemies"
    flow.dispatch("confirm")
    state = flow.state
    assert (state.screen, state.dev_viewer, state.selection) == ("dev-viewer", "enemies", 0)
    # The model viewers open in close-up.
    assert state.dev_close_up is True


def test_d199_the_arrows_move_through_the_items_round_the_list() -> None:
    """DEV-MENU-06."""
    flow = at_dev_menu()
    flow.dispatch("confirm")
    settle(flow)
    assert flow.dispatch("left") == "moved"
    assert flow.state.selection == DEV_COUNTS[0] - 1
    flow.dispatch("down")
    assert flow.state.selection == 0
    flow.dispatch("right")
    flow.dispatch("up")
    flow.dispatch("right")
    assert flow.state.selection == 1


def test_d199_confirm_flips_the_viewer_toggle() -> None:
    flow = at_dev_menu()
    flow.dispatch("confirm")
    settle(flow)
    assert flow.dispatch("confirm") == "adjusted"
    assert flow.state.dev_close_up is False
    flow.dispatch("confirm")
    assert flow.state.dev_close_up is True


def test_d199_the_levels_viewer_starts_stopped() -> None:
    """DEV-MENU-06, DEV-MENU-18."""
    flow = at_dev_menu()
    for _ in range(4):
        flow.dispatch("down")
    flow.dispatch("confirm")
    assert flow.state.dev_viewer == "levels"
    assert flow.state.dev_close_up is False


def test_d199_back_goes_to_the_dev_menu_then_to_the_title_on_its_dev_entry() -> None:
    flow = at_dev_menu()
    flow.dispatch("down")
    flow.dispatch("confirm")
    settle(flow)
    flow.dispatch("right")
    assert flow.dispatch("cancel") == "screen"
    assert flow.state.screen == "dev"
    assert flow.state.selected_id == "enemies"
    settle(flow)
    assert flow.dispatch("back") == "screen"
    assert flow.state.screen == "title"
    assert flow.state.selected_id == "dev"


def test_d199_a_viewer_keeps_its_item_when_opened_again() -> None:
    flow = at_dev_menu()
    flow.dispatch("confirm")
    settle(flow)
    flow.dispatch("right")
    flow.dispatch("back")
    settle(flow)
    flow.dispatch("confirm")
    assert flow.state.selection == 1


def test_d199_other_actions_do_nothing_in_a_viewer() -> None:
    flow = at_dev_menu()
    flow.dispatch("confirm")
    settle(flow)
    assert flow.dispatch("pause") == "none"
    assert flow.state.selection == 0


def test_d204_a_tap_on_a_viewer_button_shows_its_item() -> None:
    """DEV-MENU-07."""
    flow = at_dev_menu()
    flow.dispatch("confirm")
    settle(flow)
    assert flow.dispatch(MenuSelect(2)) == "moved"
    assert flow.state.selection == 2
    assert flow.dispatch(MenuSelect(2)) == "none"
    assert flow.dispatch(MenuSelect(DEV_COUNTS[0])) == "none"
    assert flow.dispatch(MenuSelect(-1)) == "none"
    assert flow.state.selection == 2


def test_d199_a_viewer_of_one_item_does_not_move() -> None:
    flow = MenuFlow(MenuFlowOptions(SHIP, catalog(), 0.25, None, None, 10, [1]))
    flow.finish_loading()
    settle(flow)
    flow.dispatch("down")
    flow.dispatch("down")
    flow.dispatch("confirm")
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.dispatch("right") == "none"
    # The other viewers have no count: nothing to move through either.
    flow.dispatch("back")
    settle(flow)
    flow.dispatch("down")
    flow.dispatch("confirm")
    settle(flow)
    assert flow.dispatch("right") == "none"


def test_d202_up_and_down_jump_between_the_groups_of_a_grouped_viewer() -> None:
    groups = [["a", "a", "b"], [], [], [], []]
    options = MenuFlowOptions(SHIP, catalog(), 0.25, None, None, 10, [3, 1, 1, 1, 1], groups)
    flow = MenuFlow(options)
    flow.finish_loading()
    settle(flow)
    flow.dispatch("down")
    flow.dispatch("down")
    flow.dispatch("confirm")
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    flow.dispatch("right")
    assert flow.state.selection == 1
    flow.dispatch("down")
    assert flow.state.selection == 2
    flow.dispatch("down")
    assert flow.state.selection == 0
    flow.dispatch("up")
    assert flow.state.selection == 2
    flow.dispatch("right")
    assert flow.state.selection == 0


def at_settings() -> MenuFlow:
    """Return the flow on the settings screen, opened from the title."""
    flow = at_title()
    flow.dispatch(MenuSelect(1))
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.screen == "settings"
    return flow


def test_ui_flow_03_a_screen_change_the_flow_does_not_allow_changes_nothing() -> None:
    flow = at_title()
    revision = flow.revision
    assert flow.go_to("game") is False
    assert flow.state.screen == "title"
    assert flow.revision == revision


def test_ui_set_03_up_and_down_pick_a_slider_and_left_and_right_change_it() -> None:
    """At 10, Right leaves it at 10 and changes nothing."""
    flow = at_settings()
    assert flow.state.selected_id == "music"
    assert flow.dispatch("left") == "adjusted"
    assert flow.state.volumes.music == 9
    assert flow.dispatch("right") == "adjusted"
    revision = flow.revision
    assert flow.dispatch("right") == "none"
    assert flow.state.volumes.music == 10
    assert flow.revision == revision
    assert flow.dispatch("down") == "moved"
    assert flow.state.selected_id == "sfx"
    assert flow.dispatch("down") == "none"


def test_ui_set_03_tapping_a_slider_selects_it() -> None:
    flow = at_settings()
    flow.dispatch("down")
    assert flow.dispatch(MenuSelect(0)) == "moved"
    assert flow.state.selected_id == "music"
    assert flow.dispatch(MenuSelect(0)) == "none"


def test_ui_set_01_confirm_on_the_settings_screen_does_nothing() -> None:
    flow = at_settings()
    revision = flow.revision
    assert flow.dispatch("confirm") == "none"
    assert flow.state.screen == "settings"
    assert flow.revision == revision


def at_sounds_viewer() -> MenuFlow:
    flow = at_dev_menu()
    for _ in range(5):
        flow.dispatch("down")
    assert flow.state.selected_id == "sounds"
    flow.dispatch("confirm")
    settle(flow)
    return flow


def test_dev_menu_19_on_an_audio_viewer_the_item_picked_plays_with_no_menu_sound() -> None:
    """The feedback is `played` for a move, a tap and Confirm (which flips the toggle)."""
    flow = at_sounds_viewer()
    assert flow.state.dev_viewer == "sounds"
    assert flow.dispatch("right") == "played"
    assert flow.state.selection == 1
    assert flow.dispatch(MenuSelect(2)) == "played"
    assert flow.dispatch(MenuSelect(2)) == "none"
    toggle = flow.state.dev_close_up
    assert flow.dispatch("confirm") == "played"
    assert flow.state.dev_close_up is not toggle
    assert flow.dispatch("back") == "screen"
    assert flow.state.screen == "dev"


def test_dev_menu_20_the_music_viewer_is_the_last_entry_and_up_down_jump_its_groups() -> None:
    groups = [["", "", ""], [], [], [], [], ["", "", ""], ["Menu", "Levels"]]
    flow = MenuFlow(
        MenuFlowOptions(SHIP, catalog(), 0.25, None, None, 10, list(DEV_COUNTS), groups)
    )
    flow.finish_loading()
    settle(flow)
    flow.dispatch("down")
    flow.dispatch("down")
    flow.dispatch("confirm")
    settle(flow)
    for _ in range(len(DEV_COUNTS) - 1):
        flow.dispatch("down")
    assert flow.state.selected_id == "music"
    flow.dispatch("confirm")
    settle(flow)
    assert flow.dispatch("down") == "played"
    assert flow.state.selection == 1


def at_enemies_viewer() -> MenuFlow:
    flow = at_dev_menu()
    flow.dispatch("down")
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.dev_viewer == "enemies"
    return flow


def test_dev_menu_21_a_tap_on_a_view_button_picks_the_view_of_the_enemies_viewer() -> None:
    flow = at_enemies_viewer()
    assert flow.state.dev_mode == 0
    assert flow.dispatch(MenuSelect(-2)) == "adjusted"
    assert flow.state.dev_mode == 1
    assert flow.dispatch(MenuSelect(-3)) == "adjusted"
    assert flow.state.dev_mode == 2
    # The same view again, or one that does not exist: nothing.
    assert flow.dispatch(MenuSelect(-3)) == "none"
    assert flow.dispatch(MenuSelect(-4)) == "none"
    assert flow.state.dev_mode == 2
    # The view is the viewer's own, kept when it is left and opened again.
    flow.dispatch("back")
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.dev_mode == 2


def test_dev_menu_21_the_ships_viewer_has_no_views() -> None:
    flow = at_dev_menu()
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.dev_viewer == "ships"
    assert flow.dispatch(MenuSelect(-2)) == "none"
    assert flow.state.dev_mode == 0
