# Copyright (c) 2026 Renaud Guillon
"""A player outside the page: the AI player of `make serve-ai` (D-266), in e2e builds only.

With `?ai` in the URL, the e2e build runs in real time and, about 15 times a second while a level
is played (not paused, not over), posts what is on the playfield to the page's own server
(`POST /ai`: the level, the attempt, its time and duration, and the scene of
`debug/play_scene.py`). The server's brain answers with the keys to hold (`KeyboardEvent.code`s),
which go to the level's controls as the keyboard's would. Out of a level, or when the server does
not answer, every key it held is let go; the menus stay the human's.
"""

from org.transcrypt.stubs.browser import __pragma__

from debug.play_scene import play_scene
from render.babylon import js_object, js_set

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")

# Where the page's server answers, and how often it is asked (about every 4 frames, as the brain
# learned to decide).
AI_PATH = "/ai"
AI_SECONDS = 4 / 60
# The phases of a level the brain plays in (GAME-LEVEL-10).
PLAYED = ("playing", "clearing")


def _played(app: Any) -> Any:
    """Return the run of the level played (not paused, not over), or None."""
    play = app.game()
    if play is None or app.menu.flow.state.paused:
        return None
    run = play.run
    return run if run.phase in PLAYED else None


def remote_reading(app: Any) -> Any:
    """Return what the server is sent for the level played, or None when none is played."""
    run = _played(app)
    if run is None:
        return None
    track = run.track
    reading = js_object()
    js_set(reading, "level", run.result.level_id)
    js_set(reading, "attempt", app.menu.flow.state.attempt)
    js_set(reading, "time", track.time)
    js_set(reading, "duration", track.duration)
    js_set(reading, "scene", play_scene(run))
    return reading


class RemotePlayer:
    """Asks the server for the keys to hold, one question at a time, and holds them.

    `post(path, body, on_reply)` sends `body` and calls `on_reply` with the answer (a list of key
    codes), or with None when there is none.
    """

    def __init__(self, app: Any, post: Any) -> None:
        self._app = app
        self._post = post
        self._held: list[str] = []
        self._waiting = False

    def tick(self) -> None:
        """Ask for the keys to hold now, unless an answer is still awaited."""
        if self._waiting:
            return
        reading = remote_reading(self._app)
        if reading is None:
            self.hold([])
            return
        self._waiting = True
        # A lambda: a bound method passed as a value loses `self` in JavaScript.
        self._post(AI_PATH, reading, lambda keys: self._answer(keys))

    def _answer(self, keys: Any) -> None:
        self._waiting = False
        self.hold(keys if keys is not None and _played(self._app) is not None else [])

    def hold(self, keys: list[str]) -> None:
        """Hold `keys` down and let go of the others it held.

        Each key held is sent down again: a held key repeats its key-down, which is no new press,
        and the level's controls let every key go when the page loses the focus (GAME-CTRL-07).
        """
        controls = self._app.controls
        for key in self._held:
            if key not in keys:
                controls.key(key, False)
        for key in keys:
            controls.key(key, True)
        self._held = list(keys)


def post_json(path: str, body: Any, on_reply: Any) -> None:
    """`fetch` POST of `body` as JSON; `on_reply` gets the JSON answer, or None on any failure."""
    __pragma__(
        "js",
        "{}",
        """
    fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'},
                 body: JSON.stringify(body)})
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (keys) { on_reply(keys); }, function () { on_reply(null); });
    """,
    )


def install_remote_player(app: Any, start_interval: Any, post: Any) -> RemotePlayer:
    """Start asking the server for the keys every `AI_SECONDS` (`start_interval(tick, seconds)`)."""
    player = RemotePlayer(app, post)
    start_interval(lambda: player.tick(), AI_SECONDS)
    return player
