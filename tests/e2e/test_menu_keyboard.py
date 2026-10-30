"""e2e: the menus with the keyboard only (P01-R09, P12-R01, P12-R02)."""

from e2e.menu_helpers import expect_state, game_state, open_game, step
from playwright.sync_api import Page


def press_position(page: Page, code: str, key: str) -> None:
    """Dispatches a key press as a layout would: `code` is the position, `key` the label."""
    page.evaluate(
        """([c, k]) => {
            window.dispatchEvent(new KeyboardEvent('keydown', { code: c, key: k }));
            window.dispatchEvent(new KeyboardEvent('keyup', { code: c, key: k }));
        }""",
        [code, key],
    )


def test_p01_r09_the_whole_flow_with_arrows_enter_space_and_esc(page: Page) -> None:
    open_game(page)
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "ship-select", "selectedId": "balanced"})
    page.keyboard.press("ArrowRight")
    expect_state(page, {"selectedId": "heavy"})
    page.keyboard.press("Space")
    expect_state(page, {"screen": "level-select", "selectedId": "1-1", "chosenShipId": "heavy"})
    page.keyboard.press("Escape")
    expect_state(page, {"screen": "ship-select", "selectedId": "heavy"})
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "level-select"})
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "game", "chosenShipId": "heavy", "chosenLevelId": "1-1"})
    # P12-R01: Backspace no longer leaves the level; Esc pauses and resumes, P too.
    page.keyboard.press("Backspace")
    step(page, 3)
    assert game_state(page)["screen"] == "game"
    page.keyboard.press("Escape")
    expect_state(page, {"screen": "pause", "paused": True, "selectedId": "resume"})
    page.keyboard.press("Escape")
    expect_state(page, {"screen": "game", "paused": False})
    page.keyboard.press("KeyP")
    expect_state(page, {"screen": "pause", "paused": True})
    # P12-R02: Main menu asks first; Yes leaves to the title.
    page.keyboard.press("ArrowDown")
    page.keyboard.press("ArrowDown")
    expect_state(page, {"selectedId": "main-menu"})
    page.keyboard.press("Enter")
    expect_state(page, {"leaving": True, "choice": 0})
    page.keyboard.press("ArrowRight")
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "title"})


def test_p01_r09_on_azerty_z_q_s_d_the_wasd_positions_move_the_selection(page: Page) -> None:
    open_game(page)
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "ship-select"})
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "level-select", "selectedId": "1-1"})
    press_position(page, "KeyD", "d")
    expect_state(page, {"selectedId": "1-2"})
    press_position(page, "KeyS", "s")
    expect_state(page, {"selectedId": "2-2"})
    press_position(page, "KeyA", "q")
    expect_state(page, {"selectedId": "2-1"})
    press_position(page, "KeyW", "z")
    expect_state(page, {"selectedId": "1-1"})
    # The keys labelled W and A on AZERTY are elsewhere: they do nothing.
    press_position(page, "KeyZ", "w")
    press_position(page, "KeyQ", "a")
    step(page, 3)
    assert game_state(page)["selectedId"] == "1-1"


def test_p01_r09_holding_right_moves_once_then_repeats_after_the_repeat_delay(page: Page) -> None:
    open_game(page)
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "ship-select"})
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "level-select", "selectedId": "1-1"})
    # Exact timings are unit-tested (keyboard menu input).
    page.keyboard.down("ArrowRight")
    step(page)
    assert game_state(page)["selection"] == 1
    # Held for a second of game time, it repeats.
    step(page, 60)
    assert game_state(page)["selection"] >= 3
    page.keyboard.up("ArrowRight")
