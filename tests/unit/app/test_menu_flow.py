"""Unit tests of `src/app/menu_flow.py`."""
# (P01-R01 and the screens around it).

import pytest

from app.menu_flow import MenuFlow
from app.menu_state import MenuFlowOptions
from app.settings_menu import Volumes
from core.content.level_catalog import LevelCatalog, LevelEntry
from core.systems.level_run_types import LevelCheckpoint, LevelResult
from core.systems.run_arsenal import WeaponLevels
from input.menu_action import MenuSelect, MenuSet

SHIPS = ["alpha", "beta", "gamma"]


def catalog(second_unlocked: bool = False) -> LevelCatalog:
    return LevelCatalog(
        2,
        [
            LevelEntry("1-1", "1-1", 1, 1, True),
            LevelEntry("1-2", "1-2", 1, 2, second_unlocked),
            LevelEntry("1-3", "1-3", 1, 3, False),
        ],
    )


def make_flow(
    *,
    second_unlocked: bool = False,
    initial_ship: str | None = None,
    volumes: Volumes | None = None,
    result_delay: float | None = None,
) -> MenuFlow:
    return MenuFlow(
        MenuFlowOptions(
            list(SHIPS),
            catalog(second_unlocked),
            initial_ship,
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
    assert flow.dispatch("confirm") == "screen"  # title -> ship select
    settle(flow)
    assert flow.dispatch("confirm") == "screen"  # ship -> level select
    settle(flow)
    assert flow.dispatch("confirm") == "screen"  # level 1-1 -> game
    settle(flow)
    return flow


def result(outcome: str = "complete", checkpoint: LevelCheckpoint | None = None) -> LevelResult:
    return LevelResult("1-1", 10, 10, outcome, 1234.0, False, checkpoint)


def checkpoint() -> LevelCheckpoint:
    return LevelCheckpoint(0.5, 1, WeaponLevels("guns", {"guns": 2.0}), 900.0)


def test_p01_r01_the_flow_starts_on_the_loading_screen_and_ignores_input_there() -> None:
    flow = make_flow()
    assert flow.state.screen == "loading"
    assert flow.dispatch("down") == "none"
    flow.finish_loading()
    assert flow.state.screen == "title"


def test_p01_r15_input_is_ignored_during_a_screen_transition() -> None:
    flow = make_flow()
    flow.finish_loading()
    assert flow.state.transitioning is True
    assert flow.dispatch("down") == "none"
    settle(flow)
    assert flow.state.transitioning is False
    assert flow.dispatch("down") == "moved"


def test_p01_r04_the_title_entries_move_with_up_and_down_and_confirm_goes_on() -> None:
    flow = at_title()
    assert flow.state.selected_id == "start"
    assert flow.dispatch("down") == "moved"
    assert flow.state.selected_id == "settings"
    assert flow.dispatch("down") == "none"
    assert flow.dispatch("up") == "moved"
    assert flow.dispatch("confirm") == "screen"
    assert flow.state.screen == "ship-select"


def test_p12_r04_settings_from_the_title_and_back_returns_to_the_title() -> None:
    flow = at_title()
    flow.dispatch(MenuSelect(1))
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    assert flow.state.screen == "settings"
    assert flow.paused is False
    assert flow.dispatch("back") == "screen"
    settle(flow)
    assert flow.state.screen == "title"


def test_p01_r11_selecting_an_entry_directly_and_bad_indexes() -> None:
    flow = at_title()
    assert flow.dispatch(MenuSelect(1)) == "moved"
    assert flow.dispatch(MenuSelect(1)) == "none"
    assert flow.dispatch(MenuSelect(5)) == "none"
    assert flow.dispatch(MenuSelect(-1)) == "none"


def test_p01_r06_the_ship_select_wraps_around_and_confirm_chooses_the_ship() -> None:
    flow = at_title()
    flow.dispatch("confirm")
    settle(flow)
    assert flow.dispatch("left") == "moved"
    assert flow.state.highlighted_ship_id == "gamma"
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.chosen_ship_id == "gamma"
    assert flow.state.screen == "level-select"


def test_p01_r14_the_highlighted_ship_starts_as_the_saved_one() -> None:
    flow = make_flow(initial_ship="beta")
    flow.finish_loading()
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.highlighted_ship_id == "beta"


def test_p01_r14_an_unknown_saved_ship_falls_back_to_the_first() -> None:
    flow = make_flow(initial_ship="nope")
    flow.finish_loading()
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.highlighted_ship_id == "alpha"


def test_p01_r01_back_walks_the_menus_in_reverse() -> None:
    flow = at_title()
    flow.dispatch("confirm")
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.screen == "level-select"
    assert flow.dispatch("back") == "screen"
    settle(flow)
    assert flow.state.screen == "ship-select"
    assert flow.dispatch("back") == "screen"
    settle(flow)
    assert flow.state.screen == "title"
    assert flow.dispatch("back") == "none"


def test_p01_r07_a_locked_level_gives_the_locked_feedback_and_stays() -> None:
    flow = at_title()
    flow.dispatch("confirm")
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selection == 0
    assert flow.dispatch("down") == "moved"
    assert flow.state.selection == 2
    assert flow.dispatch("confirm") == "locked"
    assert flow.state.screen == "level-select"


def test_p01_r07_the_level_select_starts_on_the_first_unlocked_level() -> None:
    flow = make_flow(second_unlocked=False)
    flow.finish_loading()
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selection == 0
    assert flow.state.selected_id == "1-1"


def test_p06_r02_a_level_starts_with_a_new_attempt_and_pauses_in_game() -> None:
    flow = at_game()
    assert flow.state.screen == "game"
    assert flow.state.chosen_level_id == "1-1"
    assert flow.state.attempt == 1
    assert flow.paused is False


def test_p12_r01_escape_pauses_a_level_and_back_does_nothing_in_it() -> None:
    flow = at_game()
    assert flow.dispatch("back") == "none"
    assert flow.dispatch("resume") == "none"
    assert flow.dispatch("cancel") == "paused"
    settle(flow)
    assert flow.state.screen == "pause"
    assert flow.paused is True


def test_p12_r02_the_pause_menu_resume_entry_goes_back_to_the_same_attempt() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    assert flow.dispatch("confirm") == "resumed"
    settle(flow)
    assert flow.state.screen == "game"
    assert flow.state.attempt == 1


def test_p12_r01_start_or_back_on_the_pause_menu_resumes_the_level() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    assert flow.dispatch("back") == "resumed"
    settle(flow)
    assert flow.state.screen == "game"
    flow.dispatch("pause")
    settle(flow)
    assert flow.dispatch("pause") == "resumed"


def test_p12_r02_the_pause_menu_moves_between_its_entries() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    assert flow.state.selected_id == "resume"
    assert flow.dispatch("down") == "moved"
    assert flow.state.selected_id == "settings"
    assert flow.dispatch("up") == "moved"
    assert flow.dispatch("left") == "none"


def test_p12_r04_settings_opened_from_the_pause_menu_keep_the_level_paused() -> None:
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


def test_p12_r02_leaving_the_level_asks_first_and_yes_goes_to_the_title() -> None:
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


def test_p12_r02_answering_no_closes_the_question_and_back_closes_it_too() -> None:
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


def test_p12_r02_the_question_takes_a_direct_pick_of_no_or_yes() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    flow.dispatch("down")
    flow.dispatch("down")
    flow.dispatch("confirm")
    assert flow.dispatch(MenuSelect(1)) == "moved"
    assert flow.state.choice == 1
    assert flow.dispatch(MenuSelect(4)) == "none"


def test_p12_r02_the_pause_menu_ignores_a_direct_pick_out_of_range() -> None:
    flow = at_game()
    flow.dispatch("pause")
    settle(flow)
    assert flow.dispatch(MenuSelect(7)) == "none"
    assert flow.dispatch(MenuSelect(2)) == "moved"


def test_p06_r03_a_completed_level_shows_its_result_and_confirm_goes_to_the_next() -> None:
    flow = at_game(second_unlocked=True)
    flow.complete_level(result())
    settle(flow)
    assert flow.state.level_result is not None
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    assert flow.state.screen == "level-select"
    assert flow.state.selection == 1


def test_p06_r03_no_next_level_when_the_next_one_is_locked() -> None:
    flow = at_game()
    flow.complete_level(result())
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selection == 0


def test_p06_r03_a_lost_level_goes_back_to_the_same_level() -> None:
    flow = at_game(second_unlocked=True)
    flow.complete_level(result(outcome="over"))
    settle(flow)
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selection == 0


def test_p06_r03_pausing_and_commands_are_ignored_on_the_result_panel() -> None:
    flow = at_game()
    flow.complete_level(result())
    settle(flow)
    assert flow.pause() is False
    assert flow.dispatch("pause") == "none"
    assert flow.dispatch("back") == "none"
    assert flow.dispatch("down") == "none"


def test_p11_r03_a_result_is_ignored_on_other_screens() -> None:
    flow = at_title()
    flow.complete_level(result())
    settle(flow)
    assert flow.state.level_result is None


def test_p07_r08_a_game_over_with_a_checkpoint_offers_two_choices() -> None:
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


def test_p07_r08_continue_starts_the_level_again_from_its_checkpoint() -> None:
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


def test_p07_r08_level_select_from_the_game_over_panel_leaves_the_level() -> None:
    flow = at_game()
    flow.complete_level(result(outcome="over", checkpoint=checkpoint()))
    settle(flow)
    flow.dispatch("right")
    assert flow.dispatch("confirm") == "screen"
    settle(flow)
    assert flow.state.screen == "level-select"


def test_p01_r11_a_directly_started_level_skips_the_menus() -> None:
    flow = make_flow(second_unlocked=True)
    assert flow.play_direct("beta", "1-2") is True
    state = flow.state
    assert state.screen == "game"
    assert state.chosen_ship_id == "beta"
    assert state.chosen_level_id == "1-2"
    assert state.transitioning is False


@pytest.mark.parametrize(
    ("ship", "level", "unlocked"),
    [
        ("nope", "1-1", True),
        ("alpha", "nope", True),
        ("alpha", "1-3", True),
        ("alpha", "1-2", False),
    ],
)
def test_p06_r09_a_direct_start_is_refused_for_unknown_or_locked_choices(
    ship: str, level: str, unlocked: bool
) -> None:
    flow = make_flow(second_unlocked=unlocked)
    assert flow.play_direct(ship, level) is False
    assert flow.state.screen == "loading"


def test_p12_r04_a_slider_command_changes_the_volume_and_redraws() -> None:
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


def test_p12_r04_the_default_volumes_are_used_when_none_are_given() -> None:
    flow = make_flow()
    assert (flow.state.volumes.music, flow.state.volumes.sfx) == (10, 10)


def test_p01_r01_a_revision_goes_up_on_every_change() -> None:
    flow = make_flow()
    start = flow.revision
    flow.finish_loading()
    assert flow.revision > start
    settle(flow)
    before = flow.revision
    flow.dispatch("down")
    assert flow.revision > before


def test_p01_r01_a_menu_needs_at_least_one_ship_and_one_level() -> None:
    with pytest.raises(ValueError):
        MenuFlow(MenuFlowOptions([], catalog(), None, 0.25, None, None, None))
    with pytest.raises(ValueError):
        MenuFlow(MenuFlowOptions(list(SHIPS), LevelCatalog(1, []), None, 0.25, None, None, None))


def test_p01_r01_the_selected_id_of_each_screen() -> None:
    flow = make_flow()
    assert flow.state.selected_id is None
    flow.finish_loading()
    settle(flow)
    assert flow.state.selected_id == "start"
    flow.dispatch("confirm")
    settle(flow)
    assert flow.state.selected_id == "alpha"


def test_p13_r02_a_result_delay_replaces_the_transition_time() -> None:
    flow = make_flow(result_delay=2.0)
    flow.finish_loading()
    settle(flow)
    flow.dispatch("confirm")
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

DEV_COUNTS = [3, 4, 2, 5, 6]


def dev_flow() -> MenuFlow:
    flow = MenuFlow(
        MenuFlowOptions(list(SHIPS), catalog(), None, 0.25, None, None, 10, list(DEV_COUNTS))
    )
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


def test_d199_without_dev_counts_the_title_has_no_dev_entry() -> None:
    flow = at_title()
    flow.dispatch("down")
    flow.dispatch("down")
    assert flow.state.selected_id == "settings"


def test_d199_the_dev_entry_comes_after_settings_and_opens_the_dev_menu() -> None:
    flow = dev_flow()
    flow.dispatch("down")
    flow.dispatch("down")
    assert flow.state.selected_id == "dev"
    assert flow.dispatch("confirm") == "screen"
    assert flow.state.screen == "dev"
    assert flow.state.selected_id == "ships"
    assert flow.state.dev_viewer is None


def test_d199_a_dev_menu_entry_opens_its_viewer_on_its_first_item() -> None:
    flow = at_dev_menu()
    flow.dispatch("down")
    assert flow.state.selected_id == "enemies"
    flow.dispatch("confirm")
    state = flow.state
    assert (state.screen, state.dev_viewer, state.selection) == ("dev-viewer", "enemies", 0)
    # The model viewers open in close-up.
    assert state.dev_close_up is True


def test_d199_the_arrows_move_through_the_items_round_the_list() -> None:
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
    flow = MenuFlow(MenuFlowOptions(list(SHIPS), catalog(), None, 0.25, None, None, 10, [1]))
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
    options = MenuFlowOptions(
        list(SHIPS), catalog(), None, 0.25, None, None, 10, [3, 1, 1, 1, 1], groups
    )
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
