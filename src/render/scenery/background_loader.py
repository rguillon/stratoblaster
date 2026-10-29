"""Generates levels' grounds and scenery textures in a worker (P13-R03), ported from
`render/scenery/background-loader.ts`, so a level can be prepared while the player is still
choosing it, without freezing the menus. Unless stopped, every ground the game asks for is
generated there (`generate_grounds_with`).
"""

from org.transcrypt.stubs.browser import __pragma__

from host.worker_data import to_plain
from render.scenery.level_ground import GroundReplies, generate_grounds_with
from render.scenery.procedural_textures import TextureJob, has_texture, keep_texture

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Any  # noqa: E402

__pragma__("noskip")


class WorkerPort:
    """The worker's side the loader talks to (a `Worker`, or a fake in tests): `post_message(job)`,
    `onmessage`, `onerror` and `terminate()` (optional)."""


def _new_map() -> Any:
    """An empty JavaScript `Map`."""
    __pragma__("js", "{}", "return new Map();")
    return None


def _map_has(cache: Any, key: Any) -> bool:
    __pragma__("js", "{}", "return cache.has(key);")
    return False


def _map_get(cache: Any, key: Any) -> Any:
    __pragma__("js", "{}", "return cache.get(key);")
    return None


def _map_set(cache: Any, key: Any, value: Any) -> None:
    __pragma__("js", "{}", "cache.set(key, value);")


def _map_delete(cache: Any, key: Any) -> None:
    __pragma__("js", "{}", "cache.delete(key);")


def _map_values(cache: Any) -> list[Any]:
    """`Array.from(cache.values())`."""
    __pragma__("js", "{}", "return Array.from(cache.values());")
    return []


def _map_clear(cache: Any) -> None:
    __pragma__("js", "{}", "cache.clear();")


def _json_of(value: Any) -> str:
    """`JSON.stringify(value)`."""
    __pragma__("js", "{}", "return JSON.stringify(value);")
    return ""


def _ground_message(job_id: int, level: Any, seed: int) -> Any:
    """`{ kind: 'ground', level, seed, id }`: the message of a ground job."""
    __pragma__("js", "{}", "return {kind: 'ground', level: level, seed: seed, id: job_id};")
    return None


def _texture_message(job_id: int, job: Any) -> Any:
    """`{ kind: 'texture', job, id }`: the message of a texture job."""
    __pragma__("js", "{}", "return {kind: 'texture', job: job, id: job_id};")
    return None


def _worker_available() -> bool:
    """`typeof Worker !== 'undefined'`."""
    __pragma__("js", "{}", "return typeof Worker !== 'undefined';")
    return False


def _new_game_worker() -> Any:
    """The game's ground worker (`ground_worker.js`, next to this module)."""
    __pragma__(
        "js",
        "{}",
        "return new Worker(new URL('./ground_worker.js', import.meta.url), {type: 'module'});",
    )
    return None


class _Waiting:
    """A job waiting for its reply: the number of the next job, and the handlers by job id."""

    def __init__(self) -> None:
        self.next = 0
        self.handlers: Any = _new_map()


class BackgroundLoader:
    """Generates levels' grounds and scenery textures in a worker (P13-R03)."""

    def __init__(self, port: Any) -> None:
        self.port = port
        self._waiting = _Waiting()
        # Textures asked for and not back yet, by key.
        self._textures: Any = _new_map()
        port.onmessage = self._on_message
        # A broken worker: every job waiting fails (the ground is then generated on the main
        # thread).
        port.onerror = self._on_error
        generate_grounds_with(self._ground_generator)

    def _on_message(self, event: Any) -> None:
        data = event.data
        done = True
        if _map_has(self._waiting.handlers, data.id):
            done = _map_get(self._waiting.handlers, data.id)(data)
        if done:
            _map_delete(self._waiting.handlers, data.id)

    def _on_error(self, event: Any) -> None:
        for done in _map_values(self._waiting.handlers):
            done(None)
        _map_clear(self._waiting.handlers)

    def _ground_generator(self, level: Any, seed: int, replies: GroundReplies) -> None:
        state = [False]

        def on_reply(reply: Any) -> bool:
            if not state[0] and reply and reply.ground:
                state[0] = True
                replies.ground(reply.ground)
                return False
            if state[0]:
                replies.runout(reply.runout if reply else None)
            else:
                replies.ground(None)
            return True

        self._post_ground(level, seed, on_reply)

    def prefetch_textures(self, jobs: Sequence[TextureJob]) -> None:
        """Generates the textures of `jobs` not kept yet, keeping them when they come back."""
        for job in jobs:
            key = _json_of(job)
            if has_texture(job) or _map_has(self._textures, key):
                continue
            _map_set(self._textures, key, True)
            self._post_texture(job, key)

    def _texture_reply(self, job: TextureJob, key: str) -> Callable[[Any], bool]:
        """The handler of a texture job's reply (a function of its own, not made in a loop)."""

        def on_reply(reply: Any) -> bool:
            _map_delete(self._textures, key)
            if reply and reply.pixels:
                keep_texture(job, reply.pixels)
            return True

        return on_reply

    def _post_texture(self, job: TextureJob, key: str) -> None:
        self._post(_texture_message(0, to_plain(job)), self._texture_reply(job, key))

    def _post_ground(self, level: Any, seed: int, done: Callable[[Any], bool]) -> None:
        self._post(_ground_message(0, to_plain(level), seed), done)

    def stop(self) -> None:
        """Stops generating in the background: the grounds are generated on the main thread
        again."""
        generate_grounds_with(None)
        if hasattr(self.port, "terminate"):
            self.port.terminate()

    def _post(self, message: Any, done: Callable[[Any], bool]) -> None:
        job_id = self._waiting.next
        self._waiting.next += 1
        message.id = job_id
        _map_set(self._waiting.handlers, job_id, done)
        self.port.postMessage(message)


def start_background_loader() -> BackgroundLoader | None:
    """A loader on the game's worker, if the browser has workers (none in unit tests)."""
    if not _worker_available():
        return None
    return BackgroundLoader(_new_game_worker())
