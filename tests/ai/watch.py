# Copyright (c) 2026 Renaud Guillon
"""`make serve-ai`: watch the brain play the real game, in your own browser.

A local server (no browser of its own: open its address in any browser) serves the e2e build of
the game (`dist-e2e/`) with `?ai` in its address: the game then runs in real time, and while a
level is played (not paused, not over) it posts what is on the playfield to `POST /ai` about 15
times a second (`src/debug/remote_player.py`, D-291). The brain answers here, in Python, with the
keys to hold: the arrows, Space (fire), R (a bomb), E (the next weapon). Choose a level in the
menus as usual (or give `--level`); the menus and the panels are yours. Ctrl-C stops it.

    uv run python -m ai.watch [--level 2-3] [--port 5174]
"""

import argparse
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import torch

from ai import REPO_ROOT
from ai.brain import BRAIN_FILE, Batch, Brain, load_brain
from ai.game_env import LEVEL_IDS, level_difficulty
from ai.observation import Scene, observe_scene

DIST = REPO_ROOT / "dist-e2e"
AI_PATH = "/ai"
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


class Player:
    """The brain at the controls of the page's level, one decision every 4 frames."""

    def __init__(self, brain: Brain, greedy: bool) -> None:
        self.brain = brain
        self.greedy = greedy
        self.memory = brain.initial_memory(1)
        self._playing: tuple[str, int] | None = None

    def keys(self, reading: dict[str, Any] | None) -> tuple[set[str], set[str]]:
        """Return the keys to hold and the keys to tap once, for what the page shows.

        None outside a level played. A bomb or a weapon switch is a tap (a press and a release
        before the next step): each decision that chooses one is one press, as when it learned
        (holding the key down would make only one press of many decisions).
        """
        if reading is None:
            self._playing = None
            return set(), set()
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
        taps: set[str] = set()
        if bomb == 1:
            taps.add(BOMB_KEY)
        if switch == 1:
            taps.add(SWITCH_KEY)
        return set(MOVE_KEYS[move]) | {FIRE_KEY}, taps


def page_query(level: str | None) -> str:
    """Return the query of the game's address: `ai` (D-291), and the level to start, if any."""
    query: dict[str, str] = {"ai": "1"}
    if level is not None:
        query["level"] = level
    return "?" + urlencode(query)


class _Handler(SimpleHTTPRequestHandler):
    """The game's files, `/` sent on to the game with `?ai`, and the brain's answers."""

    player: Player
    query: str
    lock: threading.Lock

    def log_message(self, *_args: Any) -> None:
        pass

    def do_GET(self) -> None:  # the name http.server calls
        if self.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/index.html" + self.query)
            self.end_headers()
            return
        super().do_GET()

    def do_POST(self) -> None:  # the name http.server calls
        if self.path != AI_PATH:
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        reading = json.loads(self.rfile.read(length) or b"null")
        with self.lock:  # one brain, one memory: one decision at a time
            hold, taps = self.player.keys(reading)
        keys = [sorted(hold), sorted(taps)]
        body = json.dumps(keys).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_server(player: Player, query: str, host: str, port: int) -> ThreadingHTTPServer:
    """Return the server of the game and of the brain's answers (not started)."""
    handler = type(
        "Handler", (_Handler,), {"player": player, "query": query, "lock": threading.Lock()}
    )
    return ThreadingHTTPServer((host, port), partial(handler, directory=str(DIST)))


def serve(brain_path: Path, level: str | None, host: str, port: int, greedy: bool) -> None:
    """Serve the game and let the brain play its levels, until Ctrl-C."""
    if not (DIST / "index.html").exists():
        msg = f"No e2e build in {DIST}: run `make serve-ai` (it builds it)."
        raise SystemExit(msg)
    if not brain_path.exists():
        msg = f"No brain in {brain_path}: run `make learn` first."
        raise SystemExit(msg)
    torch.set_num_threads(2)
    brain, stats = load_brain(brain_path)
    brain.eval()
    server = make_server(Player(brain, greedy), page_query(level), host, port)
    shown = "localhost" if host in ("127.0.0.1", "0.0.0.0") else host  # noqa: S104
    print(
        f"The brain of {brain_path} ({stats.updates} updates, {stats.hours:.1f} h of learning)"
        f" plays the levels you start at http://{shown}:{server.server_address[1]}/"
        " (Ctrl-C to stop).",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Serve the game for the brain to play it.")
    parser.add_argument("--level", choices=LEVEL_IDS, help="start this level (else: the menus)")
    parser.add_argument("--host", default="127.0.0.1", help="0.0.0.0: reachable from elsewhere")
    parser.add_argument("--port", type=int, default=5174)
    parser.add_argument(
        "--greedy",
        action="store_true",
        help="the likeliest move only (default: moves drawn as the brain learned to play)",
    )
    parser.add_argument("--brain", type=Path, default=BRAIN_FILE)
    args = parser.parse_args(argv)
    serve(args.brain, args.level, args.host, args.port, args.greedy)


if __name__ == "__main__":
    main()
