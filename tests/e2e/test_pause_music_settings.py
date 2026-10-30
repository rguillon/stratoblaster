"""e2e: the pause menu, the settings and the audio (phase 12)."""

import re

import pytest
from e2e.menu_helpers import (
    add_cookie,
    advance,
    boss_name,
    boss_stage,
    box_of,
    expect_state,
    game,
    game_state,
    leave_level,
    open_debug,
    open_game,
    overlap,
    poll,
    send_action,
    set_hidden,
    step,
    step_until,
)
from playwright.sync_api import ConsoleMessage, Page, Request, expect

TOUCH_PHONE = {"has_touch": True, "viewport": {"width": 390, "height": 844}}
AUDIO_FILE = re.compile(r"\.(ogg|mp3|wav|m4a|aac|flac|opus)$", re.IGNORECASE)


def audio_state(page: Page) -> str:
    audio: str = game_state(page)["audio"]
    return audio


def play_first_level(page: Page) -> None:
    """Goes from the title to level 1-1 with the keyboard."""
    open_game(page)
    for screen in ["ship-select", "level-select", "game"]:
        page.keyboard.press("Enter")
        expect_state(page, {"screen": screen})


# -- P12: pause --------------------------------------------------------------------------------


@pytest.mark.parametrize(("width", "height"), [(390, 844), (800, 600)])
def test_p12_r01_the_pause_button_shows_is_at_least_44_px_and_covers_no_hud_part(
    page: Page, width: int, height: int
) -> None:
    page.set_viewport_size({"width": width, "height": height})
    open_debug(page, "?level=1-1&boss=final")
    step_until(page, lambda: boss_name(page), lambda n: n == "Storm Petrel")
    button = page.locator(".game-pause")
    expect(button).to_be_visible()
    expect(page.locator(".boss-bar")).to_be_visible()
    box = box_of(button)
    assert min(box["width"], box["height"]) >= 44
    assert box["y"] >= 0
    assert box["x"] + box["width"] <= width
    for other in [".hud-health", ".hud-weapon", ".hud-score", ".hud-progress", ".boss-bar"]:
        assert not overlap(button, page.locator(other)), other


def test_p12_r01_p12_r02_p_pauses_nothing_moves_resume_goes_on_from_the_same_point(
    page: Page,
) -> None:
    open_debug(page, "?level=1-2&t=20")
    advance(page, 1)
    page.keyboard.press("KeyP")
    expect_state(page, {"screen": "pause", "paused": True, "selectedId": "resume"})
    expect(page.locator(".pause-panel")).to_be_visible()
    expect(page.locator(".pause-entry")).to_have_text(["Resume", "Settings", "Main menu"])
    before = game(page) or {}
    advance(page, 10)
    after = game(page) or {}
    assert after["time"] == before["time"]
    assert after["player"] == before["player"]
    assert after["enemies"] == before["enemies"]
    send_action(page, "confirm")
    expect_state(page, {"screen": "game", "paused": False})
    expect(page.locator(".pause-panel")).to_have_count(0)
    advance(page, 0.5)
    assert (game(page) or {})["time"] > before["time"]


def test_p12_r02_back_resumes_no_and_back_on_the_question_go_back_to_the_paused_menu(
    page: Page,
) -> None:
    open_debug(page, "?level=1-1&t=10")
    send_action(page, "pause")
    expect_state(page, {"screen": "pause"})
    send_action(page, "back")
    expect_state(page, {"screen": "game", "paused": False})
    send_action(page, "pause")
    expect_state(page, {"screen": "pause"})
    for answer in ["confirm", "back"]:
        send_action(page, "down")
        send_action(page, "down")
        send_action(page, "confirm")
        expect_state(page, {"leaving": True, "choice": 0})
        expect(page.locator(".pause-question-text")).to_have_text("Leave the level?")
        send_action(page, answer)
        expect_state(page, {"screen": "pause", "paused": True, "leaving": False})
        send_action(page, "up")
        send_action(page, "up")
    assert game(page) is not None


def test_p12_r02_p11_r03_main_menu_then_yes_saves_a_score_above_the_saved_high_score(
    page: Page, base_url: str
) -> None:
    add_cookie(page, base_url, "stratoblaster_high_score", "1000")
    open_debug(page, "?level=1-1&boss=final")
    step_until(page, lambda: boss_name(page), lambda n: n == "Storm Petrel")
    # K destroys its four parts: 4 × 800 points.
    for stage in range(1, 5):
        page.keyboard.press("KeyK")
        step_until(page, lambda: boss_stage(page), lambda s, at=stage: s == at)
    score = (game(page) or {}).get("score", 0)
    assert score >= 3000
    leave_level(page)
    expect(page.locator(".title-high-score")).to_have_text(str(score))


def test_p12_r02_settings_from_the_pause_menu_then_back_keeps_the_level_paused(
    page: Page,
) -> None:
    open_debug(page, "?level=1-1&t=10")
    send_action(page, "pause")
    expect_state(page, {"screen": "pause"})
    time = (game(page) or {}).get("time")
    send_action(page, "down")
    send_action(page, "confirm")
    expect_state(page, {"screen": "settings", "paused": True})
    expect(page.locator(".settings-screen.over-level")).to_be_visible()
    advance(page, 2)
    send_action(page, "back")
    expect_state(page, {"screen": "pause", "paused": True})
    assert (game(page) or {}).get("time") == time


def test_p12_r03_p12_r11_a_hidden_page_pauses_the_level_and_suspends_the_audio(
    page: Page,
) -> None:
    play_first_level(page)
    poll(lambda: audio_state(page), lambda a: a == "running")
    set_hidden(page, True)
    expect_state(page, {"screen": "pause", "paused": True})
    poll(lambda: audio_state(page), lambda a: a == "suspended")
    set_hidden(page, False)
    poll(lambda: audio_state(page), lambda a: a == "running")
    step(page, 5)
    expect_state(page, {"screen": "pause", "paused": True})
    expect(page.locator(".pause-panel")).to_be_visible()
    # Hidden and shown again while paused: still paused.
    set_hidden(page, True)
    set_hidden(page, False)
    step(page, 5)
    assert game_state(page)["paused"] is True


# -- P12: settings -----------------------------------------------------------------------------


def test_p12_r04_from_the_title_music_shows_6_and_sound_effects_8_back_returns(
    page: Page,
) -> None:
    open_game(page)
    expect(page.locator(".title-settings")).to_have_text("Settings")
    page.keyboard.press("ArrowDown")
    expect_state(page, {"selectedId": "settings"})
    page.keyboard.press("Enter")
    expect_state(page, {"screen": "settings", "volumes": {"music": 6, "sfx": 8}})
    expect(page.locator(".slider-value")).to_have_text(["6", "8"])
    page.keyboard.press("Escape")
    expect_state(page, {"screen": "title", "selectedId": "settings"})


def test_p12_r04_music_set_to_3_is_kept_after_a_reload(page: Page) -> None:
    open_game(page)
    send_action(page, "down")
    send_action(page, "confirm")
    expect_state(page, {"screen": "settings"})
    for _ in range(3):
        send_action(page, "left")
    expect_state(page, {"volumes": {"music": 3, "sfx": 8}})
    send_action(page, "down")
    send_action(page, "left")
    expect_state(page, {"volumes": {"music": 3, "sfx": 7}})
    page.reload()
    open_game(page)
    assert game_state(page)["volumes"] == {"music": 3, "sfx": 7}


@pytest.mark.parametrize("value", ["banana", "42"])
def test_p12_r04_a_bad_volume_cookie_reads_as_the_default(
    page: Page, base_url: str, value: str
) -> None:
    add_cookie(page, base_url, "stratoblaster_music_volume", value)
    add_cookie(page, base_url, "stratoblaster_sfx_volume", value)
    open_game(page)
    assert game_state(page)["volumes"] == {"music": 6, "sfx": 8}


@pytest.mark.browser_context_args(**TOUCH_PHONE)
def test_p12_r04_taps_set_the_sliders_every_target_is_at_least_44_px(page: Page) -> None:
    open_game(page)
    page.locator(".title-settings").tap()
    page.locator(".title-settings").tap()
    expect_state(page, {"screen": "settings"})
    bars = page.locator(".slider-bar")
    for target in [bars.nth(0), bars.nth(1), page.locator(".menu-back")]:
        assert box_of(target)["height"] >= 44
    box = box_of(bars.nth(1))
    # The left edge of the bar: 0, silent.
    page.touchscreen.tap(box["x"] + 1, box["y"] + box["height"] / 2)
    expect_state(page, {"volumes": {"music": 6, "sfx": 0}, "selectedId": "sfx"})
    page.touchscreen.tap(box["x"] + box["width"] - 1, box["y"] + box["height"] / 2)
    expect_state(page, {"volumes": {"music": 6, "sfx": 10}})
    page.locator(".menu-back").tap()
    expect_state(page, {"screen": "title"})


# -- P12: audio --------------------------------------------------------------------------------


def test_p12_r05_no_audio_before_the_first_input_and_no_autoplay_warning(
    page: Page, base_url: str
) -> None:
    warnings: list[str] = []
    media: list[str] = []

    def on_console(message: ConsoleMessage) -> None:
        if message.type == "warning":
            warnings.append(message.text)

    def on_request(request: Request) -> None:
        if request.resource_type == "media" or AUDIO_FILE.search(request.url):
            media.append(request.url)

    page.on("console", on_console)
    page.on("request", on_request)
    open_game(page)
    assert game_state(page)["audio"] == "none"
    assert game_state(page)["music"] == "menu"
    page.keyboard.press("ArrowDown")
    step(page)
    poll(lambda: audio_state(page), lambda a: a == "running")
    assert [w for w in warnings if "audio" in w.lower()] == []
    assert media == [], f"audio files fetched from {base_url}"


def test_p12_r08_p12_r12_the_menu_theme_plays_in_the_menus_the_level_track_in_the_level(
    page: Page,
) -> None:
    open_game(page)
    assert game_state(page)["music"] == "menu"
    send_action(page, "confirm")
    expect_state(page, {"screen": "ship-select", "music": "menu"})
    open_debug(page, "?level=2-3")
    step(page, 2)
    assert game_state(page)["music"] == "level-2-3"


def test_p12_r08_p12_r12_the_boss_track_plays_in_its_fight(page: Page) -> None:
    open_debug(page, "?level=2-3&boss=mini")
    step_until(page, lambda: game_state(page)["music"], lambda m: m == "boss-2")


def test_p12_r09_p12_r12_a_gun_shot_and_a_menu_move_are_among_the_last_sounds(
    page: Page,
) -> None:
    open_debug(page, "?level=1-1&t=5")
    page.keyboard.down("Space")
    step_until(page, lambda: "gun-shot" in game_state(page)["sounds"], lambda heard: heard)
    page.keyboard.up("Space")
    send_action(page, "pause")
    expect_state(page, {"screen": "pause"})
    assert game_state(page)["sounds"][-1] == "pause"
    send_action(page, "down")
    step(page)
    assert game_state(page)["sounds"][-1] == "menu-move"
