# Copyright (c) 2026 Renaud Guillon
"""A player outside the page: the AI player of `make serve-ai` (D-266, D-268), in e2e builds only.

With `?ai` in the URL, the e2e build runs in real time. After every 4th step of a level played (not
paused, not over), as the brain learned to decide, it asks the page's own server (`POST /ai`: the
level, the attempt, its time and duration, and the scene of `debug/play_scene.py`) and waits for
the answer: `[hold, tap]`, the keys to hold and the keys to tap once (`KeyboardEvent.code`s; a
bomb, a weapon switch: one press each decision), which go to the level's controls as the
keyboard's would and are read by the next step. The request is synchronous so that the game waits
for the brain however fast it draws: the brain sees the steps it learned on. Out of a level, or
when the server does not answer, every key it held is let go; the menus stay the human's.
"""

from org.transcrypt.stubs.browser import __pragma__

from debug.play_scene import play_scene
from render.babylon import js_object, js_set

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")

# Where the page's server answers; the steps of a level between two of its decisions (as it
# learned); how often it checks, out of a level, that it holds no key.
AI_PATH = "/ai"
STEPS_PER_DECISION = 4
RELEASE_SECONDS = 0.25
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
    """Asks the server for the keys to hold every 4 steps of a level, and holds them.

    `ask(path, body)` sends `body` and returns the answer (`[hold, tap]`, two lists of key codes),
    or None when there is none; it returns only once answered.
    """

    def __init__(self, app: Any, ask: Any) -> None:
        self._app = app
        self._ask = ask
        self._held: list[str] = []
        self._steps = 0

    def step(self) -> None:
        """After a step of a level: every 4th, ask for the keys of the next 4."""
        self._steps += 1
        if self._steps % STEPS_PER_DECISION != 0:
            return
        reading = remote_reading(self._app)
        answer = self._ask(AI_PATH, reading) if reading is not None else None
        if answer is None:
            self.hold([])
            return
        self.hold(answer[0])
        controls = self._app.controls
        for key in answer[1]:
            # A press and a release: one press, taken by the next step (GAME-CTRL-06).
            controls.key(key, True)
            controls.key(key, False)

    def tick(self) -> None:
        """Let every key go out of a level (in the menus, paused, once it is over)."""
        if _played(self._app) is None:
            self.hold([])

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


def ask_json(path: str, body: Any) -> Any:
    """POST `body` as JSON and wait for the answer: its JSON, or None on any failure.

    A synchronous request: the page waits (a few milliseconds on the same machine).
    """
    __pragma__(
        "js",
        "{}",
        """
    try {
        var request = new XMLHttpRequest();
        request.open('POST', path, false);
        request.setRequestHeader('Content-Type', 'application/json');
        request.send(JSON.stringify(body));
        return request.status === 200 ? JSON.parse(request.responseText) : null;
    } catch (error) {
        return null;
    }
    """,
    )
    return None


def install_remote_player(app: Any, start_interval: Any, ask: Any) -> RemotePlayer:
    """Have the brain decide after each 4 steps of a level, and let go out of a level."""
    player = RemotePlayer(app, ask)
    # Lambdas: a bound method passed as a value loses `self` in JavaScript.
    app.watch_steps(lambda _run: player.step())
    start_interval(lambda: player.tick(), RELEASE_SECONDS)
    return player
