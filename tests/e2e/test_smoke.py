"""e2e: the game page opens, loads, and the menus lead to a level and back (ENG-54, P01, P12)."""

import re
from pathlib import Path

import pytest
from e2e.menu_helpers import (
    LOAD_TIMEOUT,
    add_cookie,
    advance,
    expect_state,
    game,
    game_state,
    leave_level,
    open_game,
    poll,
    send_action,
    wait_for_load,
)
from playwright.sync_api import Page, Request, expect

BUILD_INFO = Path(__file__).resolve().parents[2] / "src" / "build_info.py"


def app_version() -> str:
    """The version `make build-info` wrote for the title screen (ENG-83)."""
    found = re.search(r'APP_VERSION = "([^"]*)"', BUILD_INFO.read_text())
    assert found, "src/build_info.py has no APP_VERSION"
    return found.group(1)


def test_eng_54_p12_r12_loading_title_ships_levels_game_pause_resume_back_to_title(
    page: Page,
) -> None:
    page.goto("./")
    expect(page).to_have_title("Stratoblaster")
    expect(page.locator("#game-canvas")).to_be_visible()
    expect(page.locator("#fatal")).to_be_hidden()
    expect(page.locator(".title-screen")).to_be_visible(timeout=LOAD_TIMEOUT)
    expect_state(page, {"screen": "title", "selectedId": "start"})
    send_action(page, "confirm")
    expect_state(page, {"screen": "ship-select", "selectedId": "balanced"})
    send_action(page, "confirm")
    expect_state(page, {"screen": "level-select", "selectedId": "1-1", "chosenShipId": "balanced"})
    send_action(page, "confirm")
    expect_state(page, {"screen": "game", "chosenLevelId": "1-1"})
    expect(page.locator(".game-level")).to_have_text("Level 1-1")
    # P13-R03: the level loads in steps (its ground from a worker) before it plays.
    wait_for_load(page)
    poll(lambda: (game(page) or {}).get("levelId"), lambda i: i == "1-1")
    advance(page, 1)
    # P12-R12: `pause` pauses the level; nothing moves until `resume`.
    send_action(page, "pause")
    expect_state(page, {"screen": "pause", "paused": True})
    paused = (game(page) or {}).get("time", -1)
    advance(page, 2)
    assert (game(page) or {}).get("time") == paused
    send_action(page, "resume")
    expect_state(page, {"screen": "game", "paused": False})
    advance(page, 1)
    assert (game(page) or {})["time"] > paused
    # P12-R03: a hidden page pauses the level by itself.
    page.evaluate(
        """() => {
            Object.defineProperty(document, 'visibilityState', {
                configurable: true, get: () => 'hidden',
            });
            document.dispatchEvent(new Event('visibilitychange'));
        }"""
    )
    expect_state(page, {"screen": "pause", "paused": True})
    send_action(page, "resume")
    expect_state(page, {"screen": "game", "paused": False})
    leave_level(page)
    assert game(page) is None


def test_p01_r02_a_progress_bar_goes_from_0_to_100_then_the_title_appears(page: Page) -> None:
    page.goto("./")
    expect(page.locator(".loading-bar")).to_be_visible()
    expect(page.locator(".title-screen")).to_be_visible(timeout=LOAD_TIMEOUT)
    progress = game_state(page)["loadingProgress"]
    assert progress[0] == 0
    assert progress[-1] == 1
    assert len(progress) > 2
    assert sorted(progress) == progress


def test_p01_r03_without_webgl2_a_friendly_message_replaces_the_menu(page: Page) -> None:
    page.add_init_script(
        """(() => {
            const proto = HTMLCanvasElement.prototype;
            const original = proto.getContext;
            proto.getContext = function (id, ...rest) {
                return id === 'webgl2' ? null : original.call(this, id, ...rest);
            };
        })();"""
    )
    page.goto("./")
    expect(page.locator("#fatal")).to_be_visible()
    expect(page.locator("#fatal")).to_contain_text("cannot run in this browser or on this device")
    expect(page.locator(".menu-screen")).to_have_count(0)


def test_p01_r04_the_title_shows_start_a_high_score_of_0_the_hint_and_the_version(
    page: Page,
) -> None:
    open_game(page)
    expect(page.locator(".title-name")).to_have_text("Stratoblaster")
    # The title logo fits the screen width (no clipped letters).
    sizes = page.locator(".title-name").evaluate(
        "(el) => ({ logo: el.scrollWidth, screen: el.parentElement?.clientWidth ?? 0 })"
    )
    assert sizes["logo"] <= sizes["screen"]
    expect(page.locator(".title-start.selected")).to_have_text("Start")
    expect(page.locator(".title-high-score")).to_have_text("0")
    expect(page.locator(".title-hint")).to_contain_text("Space / Enter")
    expect(page.locator(".version-number")).to_have_text(f"v{app_version()}")
    expect(page.locator(".version-commit")).to_have_text(re.compile(r"^([0-9a-f]{7,}|unknown)$"))


@pytest.mark.parametrize(("value", "shown"), [("12345", "12345"), ("not-a-score", "0")])
def test_p01_r04_a_high_score_cookie_shows_its_value_or_0(
    page: Page, base_url: str, value: str, shown: str
) -> None:
    add_cookie(page, base_url, "stratoblaster_high_score", value)
    open_game(page)
    expect(page.locator(".title-high-score")).to_have_text(shown)


def test_p01_r05_p01_r13_everything_comes_from_the_same_origin(page: Page, base_url: str) -> None:
    foreign: list[str] = []

    def on_request(request: Request) -> None:
        if not request.url.startswith(base_url):
            foreign.append(request.url)

    page.on("request", on_request)
    open_game(page)
    assert foreign == []
