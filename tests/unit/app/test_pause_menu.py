"""Unit tests of `src/app/pause_menu.py`."""
# (P12-R02).

from app.pause_menu import PAUSE_ENTRIES, PauseMenu


def test_p12_r02_the_pause_menu_lists_resume_settings_and_main_menu() -> None:
    assert PAUSE_ENTRIES == ["resume", "settings", "main-menu"]


def test_p12_r02_the_menu_opens_on_resume_without_the_question() -> None:
    menu = PauseMenu()
    menu.open()
    assert menu.selection == 0
    assert menu.selected_id == "resume"
    assert menu.leaving is False
    assert menu.choice == 0


def test_p12_r02_up_and_down_move_between_the_entries_and_stop_at_the_ends() -> None:
    menu = PauseMenu()
    assert menu.move("up") == "none"
    assert menu.move("down") == "moved"
    assert menu.selected_id == "settings"
    assert menu.move("down") == "moved"
    assert menu.selected_id == "main-menu"
    assert menu.move("down") == "none"
    assert menu.move("left") == "none"


def test_p12_r02_a_direct_pick_selects_an_entry_and_refuses_a_bad_index() -> None:
    menu = PauseMenu()
    assert menu.select(2) == "moved"
    assert menu.select(2) == "none"
    assert menu.select(3) == "none"
    assert menu.select(-1) == "none"
    assert menu.select(0.5) == "none"


def test_p12_r02_confirm_on_resume_or_settings_leaves_the_menu() -> None:
    menu = PauseMenu()
    assert menu.confirm() == "resume"
    menu.select(1)
    assert menu.confirm() == "settings"


def test_p12_r02_main_menu_asks_leave_the_level_with_no_selected_first() -> None:
    menu = PauseMenu()
    menu.select(2)
    assert menu.confirm() == "ask"
    assert menu.leaving is True
    assert menu.choice == 0


def test_p12_r02_yes_on_the_question_leaves_the_level() -> None:
    menu = PauseMenu()
    menu.select(2)
    menu.confirm()
    assert menu.move("right") == "moved"
    assert menu.move("right") == "none"
    assert menu.confirm() == "leave"


def test_p12_r02_no_on_the_question_closes_it() -> None:
    menu = PauseMenu()
    menu.select(2)
    menu.confirm()
    assert menu.confirm() == "ask"
    assert menu.leaving is False


def test_p12_r02_back_closes_the_question_or_resumes_the_level() -> None:
    menu = PauseMenu()
    assert menu.back() == "resume"
    menu.select(2)
    menu.confirm()
    assert menu.back() == "ask"
    assert menu.leaving is False


def test_p12_r02_the_question_moves_with_left_and_up_towards_no() -> None:
    menu = PauseMenu()
    menu.select(2)
    menu.confirm()
    menu.move("down")
    assert menu.choice == 1
    menu.move("up")
    assert menu.choice == 0
    assert menu.move("up") == "none"
    assert menu.move("left") == "none"


def test_p12_r02_on_the_question_a_direct_pick_only_takes_no_or_yes() -> None:
    menu = PauseMenu()
    menu.select(2)
    menu.confirm()
    assert menu.select(1) == "moved"
    assert menu.select(1) == "none"
    assert menu.select(2) == "none"
    assert menu.select(0) == "moved"


def test_p12_r02_opening_the_menu_again_resets_the_question_and_selection() -> None:
    menu = PauseMenu()
    menu.select(2)
    menu.confirm()
    menu.open()
    assert menu.leaving is False
    assert menu.selection == 0
    assert menu.choice == 0


def test_p12_r02_a_selection_past_the_entries_reads_as_resume() -> None:
    menu = PauseMenu()
    menu._selection = 9  # noqa: SLF001 (the guard of an out-of-range selection)
    assert menu.selected_id == "resume"
