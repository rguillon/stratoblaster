# Copyright (c) 2026 Renaud Guillon
"""e2e: the dev menu's sounds and music viewers (specs/dev/dev-menu.md DEV-MENU-19, DEV-MENU-20).

With `?dev`, the title screen's Dev entry opens the dev menu; its Sounds and Music entries open a
grid of buttons, one per sound or track, and the one picked plays (read through the test API's
audio state, DEV-API-02).
"""

from e2e.menu_helpers import (
    LOAD_TIMEOUT,
    advance,
    box_of,
    expect_state,
    game_state,
    poll,
    send_action,
    wait_idle,
)
from playwright.sync_api import Page, expect


def open_dev_menu(page: Page) -> None:
    """Open the game with `?dev` and go to the dev menu with the keyboard (DEV-MENU-01)."""
    page.goto("./?dev")
    page.wait_for_function(
        "() => window.__GAME_TEST__?.getState().screen === 'title'", timeout=LOAD_TIMEOUT
    )
    wait_idle(page)
    # Dev is the last entry: after Settings, and after Full screen where the browser allows it
    # (UI-TITLE-11).
    for _ in range(3):
        page.keyboard.press("ArrowDown")
    expect_state(page, {"screen": "title", "selectedId": "dev"})
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "dev", "selectedId": "ships"})


def test_dev_menu_19_the_sounds_viewer_has_a_button_per_sound_and_plays_the_one_picked(
    page: Page,
) -> None:
    open_dev_menu(page)
    for _ in range(5):
        send_action(page, "down")
    expect_state(page, {"screen": "dev", "selectedId": "sounds"})
    send_action(page, "confirm")
    expect_state(page, {"screen": "dev-viewer", "selection": 0})
    poll(lambda: game_state(page)["audio"], lambda a: a == "running")
    buttons = page.locator(".dev-audio-screen .dev-menu-item")
    expect(buttons.first).to_have_text("fire:bullet")
    assert buttons.count() > 20
    # The arrows pick and play; the button's sound is heard, with no menu sound over it.
    page.keyboard.press("ArrowRight")
    expect_state(page, {"screen": "dev-viewer", "selection": 1})
    assert game_state(page)["sounds"][-1] == "missile-launch"
    expect(page.locator(".dev-audio-screen .dev-status")).to_have_text("Playing: missile-launch")
    # A tap on a button plays its sound.
    buttons.nth(0).click()
    expect_state(page, {"screen": "dev-viewer", "selection": 0})
    assert game_state(page)["sounds"][-1] == "gun-shot"
    # Enter plays the sound again.
    page.keyboard.press("Enter")
    wait_idle(page)
    assert game_state(page)["sounds"][-2:] == ["gun-shot", "gun-shot"]
    # The menu music goes on under the sounds.
    assert game_state(page)["music"] == "menu"
    # A button held repeats its sound until it is let go.
    box = box_of(buttons.nth(2))
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    expect_state(page, {"screen": "dev-viewer", "selection": 2})
    heard = game_state(page)["sounds"]
    assert heard[-1] == "laser-start"
    advance(page, 1.0)
    repeats = game_state(page)["sounds"].count("laser-start") - heard.count("laser-start")
    assert repeats >= 2
    page.mouse.up()
    before = game_state(page)["sounds"].count("laser-start")
    advance(page, 1.0)
    assert game_state(page)["sounds"].count("laser-start") == before
    page.keyboard.press("Escape")
    expect_state(page, {"screen": "dev", "selectedId": "sounds"})


def test_dev_menu_20_the_music_viewer_lists_each_track_once_and_plays_the_one_picked(
    page: Page,
) -> None:
    open_dev_menu(page)
    for _ in range(6):
        send_action(page, "down")
    expect_state(page, {"screen": "dev", "selectedId": "music"})
    send_action(page, "confirm")
    expect_state(page, {"screen": "dev-viewer", "selection": 0})
    poll(lambda: game_state(page)["audio"], lambda a: a == "running")
    buttons = page.locator(".dev-audio-screen .dev-menu-item")
    labels = buttons.all_text_contents()
    assert labels[:2] == ["menu", "level-1-1"]
    assert labels.count("boss-1") == 1
    assert "jingle-complete" in labels
    groups = page.locator(".dev-audio-screen .dev-menu-group").all_text_contents()
    assert [g.split(" (")[0] for g in groups] == ["Menu", "Levels", "Bosses", "Jingles"]
    # The next track replaces the music; a jingle plays over it.
    page.keyboard.press("ArrowRight")
    expect_state(page, {"screen": "dev-viewer", "selection": 1})
    assert game_state(page)["music"] == "level-1-1"
    buttons.nth(labels.index("jingle-complete")).click()
    wait_idle(page)
    assert game_state(page)["music"] == "level-1-1"
    expect(page.locator(".dev-audio-screen .dev-status")).to_contain_text("Playing: level-1-1")
    # Back on the dev menu, the menu theme returns.
    page.keyboard.press("Escape")
    expect_state(page, {"screen": "dev", "selectedId": "music"})
    assert game_state(page)["music"] == "menu"
