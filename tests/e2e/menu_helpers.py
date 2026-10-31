"""Helpers of the e2e tests: read the game through `window.__GAME_TEST__` (`src/debug/test_api.py`)
and step it (ENG-52).

e2e builds have no render loop: the game only moves when a test steps it, so no test waits on game
time. `getState()` returns plain objects with camelCase keys, read here as dicts.
"""

# Real time, for the timeouts only: the game's own time is stepped (ENG-52).
import time  # noqa: TID251
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
    """What `__GAME_TEST__.getState()` returns."""
    state: dict[str, Any] = page.evaluate(f"() => {{ {_API} return api.getState(); }}")
    return state


def game(page: Page) -> dict[str, Any] | None:
    """The level being played, or None."""
    level_state: dict[str, Any] | None = game_state(page)["game"]
    return level_state


def boss(page: Page) -> dict[str, Any] | None:
    """The boss being fought, or None."""
    level_state = game(page)
    return level_state["boss"] if level_state else None


def boss_name(page: Page) -> str | None:
    fought = boss(page)
    return fought["name"] if fought else None


def boss_stage(page: Page) -> int:
    fought = boss(page)
    return fought["stage"] if fought else -1


def step(page: Page, frames: int = 1, render: bool = True) -> None:
    """Runs the app by `frames` frames of 1/60 s, then renders once (unless `render` is False)."""
    page.evaluate(f"([n, r]) => {{ {_API} api.step(n, r); }}", [frames, render])


def advance(page: Page, seconds: float) -> None:
    """Runs the app by `seconds` of game time (whole frames), then renders once."""
    page.evaluate(f"(s) => {{ {_API} api.advance(s); }}", seconds)


def poll[T](
    read: Callable[[], T],
    check: Callable[[T], bool],
    timeout: float = LOAD_TIMEOUT,
    message: str = "",
) -> T:
    """Reads `read()` until `check` accepts it (the value is returned); fails after `timeout` ms of
    real time."""
    deadline = time.monotonic() + timeout / 1000
    while True:
        value = read()
        if check(value):
            return value
        if time.monotonic() > deadline:
            raise AssertionError(f"{message or 'poll'}: timed out, last value {value!r}")
        time.sleep(0.02)


def step_until[T](
    page: Page,
    read: Callable[[], T],
    check: Callable[[T], bool],
    frames: int = POLL_FRAMES,
    timeout: float = LOAD_TIMEOUT,
) -> T:
    """Steps the app `frames` frames at a time until `check(read())` holds; returns the value read.
    The frames are not drawn while it waits (only the game's state is read), the frame it stops
    at is. Fails after `timeout` ms of real time."""
    deadline = time.monotonic() + timeout / 1000
    while True:
        step(page, frames, False)
        value = read()
        if check(value):
            step(page, 0)
            return value
        if time.monotonic() > deadline:
            raise AssertionError(f"step_until: timed out, last value {value!r}")


def matches(actual: Any, expected: Any) -> bool:
    """Whether `actual` has every key of `expected` with the same value (nested dicts too), like
    Playwright's `toMatchObject`."""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and matches(actual[key], value) for key, value in expected.items()
        )
    return bool(actual == expected)


def wait_idle(page: Page) -> None:
    """Steps the app until no screen transition runs (input is ignored during one, P01-R15), then
    renders the frame it stopped at."""
    page.evaluate(
        f"""() => {{
            {_API}
            // At least one frame, so input sent before is read. A fade lasts 15 frames; the result
            // overlay ignores input for a second (P06-R03).
            api.step(1, false);
            for (let i = 0; i < 600 && api.getState().transitioning; i++) api.step(1, false);
            api.step(0);
        }}"""
    )


def open_game(page: Page) -> None:
    """Opens the game and waits for the title screen, faded in."""
    page.goto("./")
    page.wait_for_function(
        "() => window.__GAME_TEST__?.getState().screen === 'title'", timeout=LOAD_TIMEOUT
    )
    wait_idle(page)


def open_debug(page: Page, query: str) -> None:
    """Opens the game with debug options (P06-R09) and waits for their level to be playing."""
    page.goto(f"./{query}")
    page.wait_for_function(
        "() => window.__GAME_TEST__?.getState().screen === 'game'", timeout=LOAD_TIMEOUT
    )
    wait_for_load(page)
    step(page)


def send_action(page: Page, action: str) -> None:
    """Sends a menu action through the test API, once the screen accepts input."""
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
    """Steps the app a frame at a time, without rendering, until the state matches `expected`
    (screen, selection...), then until it takes input again."""

    def read() -> dict[str, Any]:
        state: dict[str, Any] = page.evaluate(
            f"() => {{ {_API} api.step(1, false); return api.getState(); }}"
        )
        return state

    poll(read, lambda state: matches(state, expected), message=f"expect_state {expected}")
    wait_idle(page)


def leave_level(page: Page) -> None:
    """Leaves the level being played through the pause menu (P12-R02): pause, Main menu, Yes. The
    title screen shows."""
    send_action(page, "pause")
    expect_state(page, {"screen": "pause", "paused": True})
    for action in ["down", "down", "confirm", "right", "confirm"]:
        send_action(page, action)
    expect_state(page, {"screen": "title", "paused": False})


def wait_for_load(page: Page) -> None:
    """Steps through the loading of the level chosen, if one is loading (P13-R03: a level loads in
    steps, one per frame, behind its loading screen; its ground comes from a worker, so the page
    must get its messages between two checks). The loading frames are not drawn: under software
    WebGL a drawn frame of a level costs some 200 ms, and no test looks at them. The frame the
    loading stopped at is drawn once."""
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
    """The level being played, once loaded; fails the test when there is none."""
    wait_for_load(page)
    level_state = game(page)
    if level_state is None:
        raise AssertionError("No level is being played")
    return level_state


def wait_for_level_time(page: Page, seconds: float) -> None:
    """Runs the level being played on to `seconds` of level time."""
    now: float = level(page)["time"]
    if now <= seconds:
        advance(page, seconds - now + 0.05)
    assert level(page)["time"] > seconds


def destroy_boss(page: Page, name: str) -> None:
    """Destroys the parts left then the core of the boss `name` with K (P07-R09), one at a time
    (the stage goes up), and steps on to the "Level complete" overlay."""
    step_until(page, lambda: boss_name(page), lambda n: n == name)
    fought = level(page)["boss"] or {}
    parts: int = fought.get("parts", 0)
    done: int = fought.get("stage", 0)
    for stage in range(done + 1, parts + 1):
        page.keyboard.press("KeyK")
        step_until(page, lambda: boss_stage(page), lambda s, at=stage: s == at)
    page.keyboard.press("KeyK")
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
    """The box of an element shown on screen."""
    box = locator.bounding_box()
    if not box:
        raise AssertionError("not shown")
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
    """Stores the cookie `name` for the game's origin, before the page is opened."""
    page.context.add_cookies([{"name": name, "value": value, "url": base_url}])
