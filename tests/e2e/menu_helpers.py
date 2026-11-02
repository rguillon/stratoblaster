# Copyright (c) 2026 Renaud Guillon
"""Helpers of the e2e tests.

Read the game through `window.__GAME_TEST__` (`src/debug/test_api.py`) and step it (ENG-52). e2e
builds have no render loop: the game only moves when a test steps it, so no test waits on game time
(ENG-58). `getState()` returns plain objects with camelCase keys, read here as dicts.
"""

# Real time, for the timeouts only: the game's own time is stepped (ENG-52).
import time
from collections.abc import Callable
from typing import Any

from playwright.sync_api import Locator, Page, expect

# Loading the menus (and a level's scenery) is real work, not game time: under software WebGL on CI
# it can take a while. In ms, as Playwright counts.
LOAD_TIMEOUT = 60_000

# Frames stepped between two checks of `step_until`.
POLL_FRAMES = 10

# Fails when the test API is missing (a production build, or the page not started yet).
_API = "const api = window.__GAME_TEST__; if (!api) throw new Error('__GAME_TEST__ is missing');"


def game_state(page: Page) -> dict[str, Any]:
    """Return what `__GAME_TEST__.getState()` returns."""
    state: dict[str, Any] = page.evaluate(f"() => {{ {_API} return api.getState(); }}")
    return state


def game(page: Page) -> dict[str, Any] | None:
    """Return the level being played, or None."""
    level_state: dict[str, Any] | None = game_state(page)["game"]
    return level_state


def boss(page: Page) -> dict[str, Any] | None:
    """Return the boss being fought, or None."""
    level_state = game(page)
    return level_state["boss"] if level_state else None


def boss_name(page: Page) -> str | None:
    fought = boss(page)
    return fought["name"] if fought else None


def boss_stage(page: Page) -> int:
    fought = boss(page)
    return fought["stage"] if fought else -1


def step(page: Page, frames: int = 1, render: bool = True) -> None:
    """Run the app by `frames` frames of 1/60 s, then render once (unless `render` is False)."""
    page.evaluate(f"([n, r]) => {{ {_API} api.step(n, r); }}", [frames, render])


def advance(page: Page, seconds: float) -> None:
    """Run the app by `seconds` of game time (whole frames), then render once."""
    page.evaluate(f"(s) => {{ {_API} api.advance(s); }}", seconds)


def poll[T](
    read: Callable[[], T],
    check: Callable[[T], bool],
    timeout: float = LOAD_TIMEOUT,
    message: str = "",
) -> T:
    """Read `read()` until `check` accepts it (the value is returned).

    Fails after `timeout` ms of real time.
    """
    deadline = time.monotonic() + timeout / 1000
    while True:
        value = read()
        if check(value):
            return value
        if time.monotonic() > deadline:
            msg = f"{message or 'poll'}: timed out, last value {value!r}"
            raise AssertionError(msg)
        time.sleep(0.02)


def step_until[T](
    page: Page,
    read: Callable[[], T],
    check: Callable[[T], bool],
    frames: int = POLL_FRAMES,
    timeout: float = LOAD_TIMEOUT,
) -> T:
    """Step the app `frames` frames at a time until `check(read())` holds; return the value read.

    .

        The frames are not drawn while it waits (only the game's state is read), the frame it stops
        at is (DEV-API-11). Fails after `timeout` ms of real time.
    """
    deadline = time.monotonic() + timeout / 1000
    while True:
        step(page, frames, render=False)
        value = read()
        if check(value):
            step(page, 0)
            return value
        if time.monotonic() > deadline:
            msg = f"step_until: timed out, last value {value!r}"
            raise AssertionError(msg)


def matches(actual: Any, expected: Any) -> bool:
    """Return whether `actual` has every key of `expected` with the same value.

    Nested dicts too, like Playwright's `toMatchObject`.
    """
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and matches(actual[key], value) for key, value in expected.items()
        )
    return bool(actual == expected)


def wait_idle(page: Page) -> None:
    """Step the app until no screen transition runs (input is ignored during one, UI-FLOW-08).

    Then renders the frame it stopped at.
    """
    page.evaluate(
        f"""() => {{
            {_API}
            // At least one frame, so input sent before is read. A fade lasts 15 frames; the result
            // overlay ignores input for a second (UI-OVER-04).
            api.step(1, false);
            for (let i = 0; i < 600 && api.getState().transitioning; i++) api.step(1, false);
            api.step(0);
        }}"""
    )


def open_game(page: Page) -> None:
    """Open the game and wait for the title screen, faded in."""
    page.goto("./")
    page.wait_for_function(
        "() => window.__GAME_TEST__?.getState().screen === 'title'", timeout=LOAD_TIMEOUT
    )
    wait_idle(page)


def open_debug(page: Page, query: str) -> None:
    """Open the game with debug options (DEV-OPT-01) and wait for their level to be playing."""
    page.goto(f"./{query}")
    page.wait_for_function(
        "() => window.__GAME_TEST__?.getState().screen === 'game'", timeout=LOAD_TIMEOUT
    )
    wait_for_load(page)
    step(page)


def send_action(page: Page, action: str) -> None:
    """Send a menu action through the test API, once the screen accepts input."""
    page.evaluate(
        f"""(a) => {{
            {_API}
            // Through any transition first, without drawing: the next check renders.
            for (let i = 0; i < 600 && api.getState().transitioning; i++) api.step(1, false);
            api.sendAction(a);
        }}""",
        action,
    )


def expect_state(page: Page, expected: dict[str, Any]) -> None:
    """Step the app a frame at a time, without rendering, until the state matches `expected`.

    `expected` is the screen, selection...; then it steps until the app takes input again.
    """

    def read() -> dict[str, Any]:
        state: dict[str, Any] = page.evaluate(
            f"() => {{ {_API} api.step(1, false); return api.getState(); }}"
        )
        return state

    poll(read, lambda state: matches(state, expected), message=f"expect_state {expected}")
    wait_idle(page)


def leave_level(page: Page) -> None:
    """Leaves the level being played through the pause menu (UI-PAUSE-10): pause, Main menu, Yes.

    .

        The title screen shows.
    """
    send_action(page, "pause")
    expect_state(page, {"screen": "pause", "paused": True})
    for action in ["down", "down", "confirm", "right", "confirm"]:
        send_action(page, action)
    expect_state(page, {"screen": "title", "paused": False})


def wait_for_load(page: Page) -> None:
    """Step through the loading of the level chosen.

    If one is loading (DEV-API-11; PERF-09: a level loads in steps, one per frame, behind its
    loading screen; its ground comes from a worker, so the page must get its messages between two
    checks). The loading frames are not drawn: under software WebGL a drawn frame of a level costs
    some 200 ms, and no test looks at them. The frame the loading stopped at is drawn once.
    """
    script = f"""() => {{
        {_API}
        const still = () => {{
            const state = api.getState();
            return state.screen === 'game' && state.game === null && state.levelResult === null;
        }};
        for (let i = 0; i < 5 && still(); i++) api.step(1, false);
        return still();
    }}"""
    deadline = time.monotonic() + LOAD_TIMEOUT / 1000
    loading = page.evaluate(script)
    if not loading:
        return
    while loading and time.monotonic() < deadline:
        page.wait_for_timeout(20)
        loading = page.evaluate(script)
    step(page, 0)


def level(page: Page) -> dict[str, Any]:
    """Return the level being played, once loaded; fails the test when there is none."""
    wait_for_load(page)
    level_state = game(page)
    if level_state is None:
        msg = "No level is being played"
        raise AssertionError(msg)
    return level_state


def wait_for_level_time(page: Page, seconds: float) -> None:
    """Run the level being played on to `seconds` of level time."""
    now: float = level(page)["time"]
    if now <= seconds:
        advance(page, seconds - now + 0.05)
    assert level(page)["time"] > seconds


def wait_out_transformation(page: Page) -> None:
    """Step on while the boss is transforming (it can then be neither hit nor broken by K)."""
    step_until(
        page, lambda: (level(page)["boss"] or {}).get("state"), lambda s: s != "transforming"
    )


def destroy_boss(page: Page, name: str) -> None:
    """Destroy the parts left then the core of the boss `name` with K (DEV-OPT-09), one at a time.

    The stage goes up with each, read from the boss's state (DEV-API-04). It waits out its
    transformations (they reveal more parts), and steps on to the "Level complete" overlay.
    """
    step_until(page, lambda: boss_name(page), lambda n: n == name)

    def progress() -> Any:
        fought = level(page)["boss"]
        return None if not fought else (fought["stage"], fought["form"], fought["state"])

    while (now := progress()) is not None and now[2] != "dying":
        wait_out_transformation(page)
        before = progress()
        page.keyboard.press("KeyK")
        step_until(page, progress, lambda v, b=before: v != b, frames=1)
    # The ship flies on a while, then off the top (reviewer, 2026-10-28): up to ~15 s of play.
    step_until(
        page, lambda: game_state(page)["levelResult"] is not None, lambda done: done, frames=120
    )
    step(page)
    expect(page.locator(".level-complete")).to_be_visible()


def overlap(a: Locator, b: Locator) -> bool:
    """Whether two elements' boxes overlap."""
    x, y = a.bounding_box(), b.bounding_box()
    if not x or not y:
        return False
    return (
        x["x"] < y["x"] + y["width"]
        and y["x"] < x["x"] + x["width"]
        and x["y"] < y["y"] + y["height"]
        and y["y"] < x["y"] + x["height"]
    )


def box_of(locator: Locator) -> dict[str, float]:
    """Return the box of an element shown on screen."""
    box = locator.bounding_box()
    if not box:
        msg = "not shown"
        raise AssertionError(msg)
    return dict(box)


def set_hidden(page: Page, hidden: bool) -> None:
    """Fakes the page going hidden or visible again (tab switched, window minimised)."""
    page.evaluate(
        """(h) => {
            Object.defineProperty(document, 'visibilityState', {
                configurable: true,
                get: () => (h ? 'hidden' : 'visible'),
            });
            document.dispatchEvent(new Event('visibilitychange'));
        }""",
        hidden,
    )


def add_cookie(page: Page, base_url: str, name: str, value: str) -> None:
    """Store the cookie `name` for the game's origin, before the page is opened."""
    page.context.add_cookies([{"name": name, "value": value, "url": base_url}])
