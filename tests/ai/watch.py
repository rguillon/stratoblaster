# Copyright (c) 2026 Renaud Guillon
"""`make serve-ai`: watch the brain play the real game, in a browser window.

It serves the e2e build of the game (`dist-e2e/`, with its test API), opens it in a Chromium
window and runs the game at 60 frames a second (the e2e build only moves when stepped). Choose a
ship and a level in the menus as usual (or give `--level`): while a level is played, the brain
plays it. Every 4 frames (as it learned) it reads what is on the playfield
(`__GAME_TEST__.getScene()`), chooses a move in Python, and presses the game's keys: the arrows,
Space (held: fire), R (a bomb), E (the next weapon). The menus, the pause and the "Level complete"
or "Game over" panels are yours. Closing the window or Ctrl-C stops it.

    uv run python -m ai.watch [--level 2-3] [--ship heavy] [--speed 0.5]
"""

import argparse
import contextlib
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import torch
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

from ai import REPO_ROOT
from ai.brain import BRAIN_FILE, Batch, Brain, load_brain
from ai.game_env import LEVEL_IDS, SHIP_IDS, level_difficulty
from ai.observation import Scene, observe_scene

DIST = REPO_ROOT / "dist-e2e"
FRAMES_PER_DECISION = 4
FRAME_SECONDS = 1 / 60
# Seconds past a level's length the brain learned an episode may last (`EpisodeSetup`).
EXTRA_SECONDS = 240.0
# The keys of each move (`MOVES`: still, N, NE, E, SE, S, SW, W, NW).
MOVE_KEYS: tuple[frozenset[str], ...] = (
    frozenset(),
    frozenset({"ArrowUp"}),
    frozenset({"ArrowUp", "ArrowRight"}),
    frozenset({"ArrowRight"}),
    frozenset({"ArrowDown", "ArrowRight"}),
    frozenset({"ArrowDown"}),
    frozenset({"ArrowDown", "ArrowLeft"}),
    frozenset({"ArrowLeft"}),
    frozenset({"ArrowUp", "ArrowLeft"}),
)
FIRE_KEY = "Space"
BOMB_KEY = "KeyR"
SWITCH_KEY = "KeyE"
# What the page gives at each decision: the level played and its scene, or null in the menus,
# while it loads, while it is paused, and once it is over.
_READ = """() => {
    const api = window.__GAME_TEST__;
    const state = api.getState();
    const game = state.game;
    if (!game || state.paused || (game.phase !== 'playing' && game.phase !== 'clearing')) {
        return null;
    }
    return {level: game.levelId, attempt: state.attempt, time: game.time,
            duration: game.duration, scene: api.getScene()};
}"""


class Keys:
    """The game keys the brain holds down, pressed and let go through the page."""

    def __init__(self, page: Page) -> None:
        self._page = page
        self._down: set[str] = set()

    def hold(self, keys: set[str]) -> None:
        """Hold exactly `keys` down."""
        for key in sorted(self._down - keys):
            self._page.keyboard.up(key)
        for key in sorted(keys - self._down):
            self._page.keyboard.down(key)
        self._down = set(keys)

    def release(self) -> None:
        self.hold(set())


class Player:
    """The brain at the controls of the page's level, one decision every 4 frames."""

    def __init__(self, brain: Brain, greedy: bool) -> None:
        self.brain = brain
        self.greedy = greedy
        self.memory = brain.initial_memory(1)
        self._playing: tuple[str, int] | None = None

    def keys(self, reading: dict[str, Any] | None) -> set[str]:
        """Return the keys to hold for what the page shows: none outside a level played."""
        if reading is None:
            self._playing = None
            return set()
        attempt = (reading["level"], reading["attempt"])
        if attempt != self._playing:  # a new level, or the same one started again
            self._playing = attempt
            self.memory = self.brain.initial_memory(1)
        difficulty = level_difficulty(reading["level"])
        limit = reading["duration"] + EXTRA_SECONDS
        time_left = max(0.0, 1.0 - reading["time"] / limit)
        scene = Scene(reading["scene"], difficulty.bullet_speed, difficulty.fire_rate, time_left)
        with torch.no_grad():
            decision, self.memory = self.brain(Batch.of([observe_scene(scene)]), self.memory)
        move, bomb, switch = decision.sample(self.greedy)[0].tolist()
        keys = set(MOVE_KEYS[move]) | {FIRE_KEY}
        if bomb == 1:
            keys.add(BOMB_KEY)
        if switch == 1:
            keys.add(SWITCH_KEY)
        return keys


def _serve(directory: Path) -> ThreadingHTTPServer:
    """Serve `directory` on a free local port, in the background."""

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *_args: Any) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(directory)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def _url(port: int, level: str | None, ship: str | None) -> str:
    url = f"http://127.0.0.1:{port}/"
    if level is not None:
        url += f"?level={level}" + (f"&ship={ship}" if ship else "")
    return url


def watch(
    brain_path: Path,
    level: str | None,
    ship: str | None,
    speed: float,
    greedy: bool,
    headless: bool = False,
    draw_every: int = 1,
) -> None:
    """Open the game and let the brain play its levels until the window is closed."""
    if not (DIST / "index.html").exists():
        msg = f"No e2e build in {DIST}: run `make serve-ai` (it builds it)."
        raise SystemExit(msg)
    if not brain_path.exists():
        msg = f"No brain in {brain_path}: run `make learn` first."
        raise SystemExit(msg)
    torch.set_num_threads(2)
    brain, stats = load_brain(brain_path)
    brain.eval()
    player = Player(brain, greedy)
    server = _serve(DIST)
    url = _url(server.server_address[1], level, ship)
    print(
        f"The brain of {brain_path} ({stats.updates} updates, {stats.hours:.1f} h of learning)"
        f" plays the levels you start at {url}. Close the window or Ctrl-C to stop."
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=headless,
            args=["--autoplay-policy=no-user-gesture-required", "--window-size=1600,900"],
        )
        page = browser.new_page(no_viewport=True)
        page.goto(url)
        page.wait_for_function("() => window.__GAME_TEST__ !== undefined")
        keys = Keys(page)
        try:
            _run(page, player, keys, FRAME_SECONDS / speed, draw_every)
        except (PlaywrightError, KeyboardInterrupt):
            pass  # the window was closed, or Ctrl-C
        finally:
            server.shutdown()
            # After Ctrl-C the browser's driver (in the same process group) is gone already.
            with contextlib.suppress(Exception):
                browser.close()


def _run(page: Page, player: Player, keys: Keys, frame_seconds: float, draw_every: int) -> None:
    """Step the game in real time (or at the asked speed), the brain deciding every 4 frames.

    One frame in `draw_every` is drawn (a frame drawn by software WebGL takes some 200 ms).
    """
    next_frame = time.monotonic()
    frame = 0
    while not page.is_closed():
        if frame % FRAMES_PER_DECISION == 0:
            reading = page.evaluate(_READ)
            keys.hold(player.keys(reading))
            if reading is not None and frame % 600 == 0:
                _report(reading)
        draw = frame % draw_every == 0
        page.evaluate("draw => window.__GAME_TEST__.step(1, draw)", draw)
        frame += 1
        next_frame += frame_seconds
        wait = next_frame - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        else:
            next_frame = time.monotonic()  # slower than real time: go on from now


def _report(reading: dict[str, Any]) -> None:
    scene = reading["scene"]
    hull = scene["hull"]
    lives = f", {hull[2]:g} lives, health {hull[0]:.0f}" if hull is not None else ""
    progress, length = scene["track"]
    print(
        f"  {reading['level']} at {reading['time']:.0f} s: {progress / length:.0%} through"
        f"{lives}, {len(scene['targets'])} targets, {len(scene['bullets'])} bullets",
        flush=True,
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Watch the brain play the game in a browser.")
    parser.add_argument("--level", choices=LEVEL_IDS, help="start this level (else: the menus)")
    parser.add_argument("--ship", choices=SHIP_IDS, help="with this ship (with --level)")
    parser.add_argument("--speed", type=float, default=1.0, help="game speed (1: real time)")
    parser.add_argument("--sample", action="store_true", help="sample moves instead of the best")
    parser.add_argument("--brain", type=Path, default=BRAIN_FILE)
    parser.add_argument("--headless", action="store_true", help="no window (to check it runs)")
    parser.add_argument("--draw-every", type=int, default=1, help="draw one frame in N")
    args = parser.parse_args(argv)
    watch(
        args.brain,
        args.level,
        args.ship,
        args.speed,
        not args.sample,
        args.headless,
        max(1, args.draw_every),
    )


if __name__ == "__main__":
    main()
