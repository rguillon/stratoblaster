# Copyright (c) 2026 Renaud Guillon
"""Generates levels' grounds and scenery textures in workers (PERF-14).

So a level can be prepared while the player is still choosing it, without freezing the menus.

Unless stopped, every ground the game asks for is generated there (`generate_grounds_with`). The
grounds, their chunks and street surfaces go to the ground worker; the scenery textures, which
need nothing of the ground, to texture workers of their own where the machine has the cores, so
they are made at the same time as the ground and its roads (D-414).
"""

from org.transcrypt.stubs.browser import __pragma__

from host.worker_data import to_plain
from render.scenery.level_ground import GroundReplies, generate_grounds_with
from render.scenery.procedural_textures import TextureJob, has_texture, keep_texture

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Any

# __pragma__ ("noskip")


def _new_map() -> Any:
    """Return an empty JavaScript `Map`."""
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


def _chunks_message(job_id: int, through: float) -> Any:
    """`{ kind: 'chunks', id, through }`: asks for the chunks of a ground up to a Z."""
    __pragma__("js", "{}", "return {kind: 'chunks', id: job_id, through: through};")
    return None


def _roads_message(ground_id: int, spans: Any, look: Any, grid: bool) -> Any:
    """`{ kind: 'roads', ground, spans, look, grid, id }`: asks for the street surfaces of chunks.

    It is for a ground (`spans`: `[index, z_min, z_max]` each), with its road look.
    """
    __pragma__(
        "js",
        "{}",
        "return {kind: 'roads', ground: ground_id, spans: spans, look: look, grid: grid};",
    )
    return None


def _worker_available() -> bool:
    """`typeof Worker !== 'undefined'`."""
    __pragma__("js", "{}", "return typeof Worker !== 'undefined';")
    return False


def _cores() -> int:
    """`navigator.hardwareConcurrency`: the machine's logical processors (2 when unknown)."""
    __pragma__("js", "{}", "return (self.navigator && navigator.hardwareConcurrency) || 2;")
    return 2


def texture_worker_count(cores: int) -> int:
    """How many texture workers to start besides the ground worker (D-414).

    One per core left over by the main thread and the ground worker, at most two (a level has ten
    or so textures, the longest a third of the work): at least one, so the textures never queue
    behind a ground.
    """
    return max(1, min(2, cores - 2))


def _new_game_worker() -> Any:
    """Return the game's ground worker (`ground_worker.js`, next to this module).

    It is named only here, by a relative URL (ENG-82, ENG-123).
    """
    __pragma__(
        "js",
        "{}",
        "return new Worker(new URL('./ground_worker.js', import.meta.url), {type: 'module'});",
    )
    return None


class _Waiting:
    """The jobs posted to a worker waiting for their reply: the handlers by job id."""

    def __init__(self, port: Any) -> None:
        self.port = port
        self.handlers: Any = _new_map()

    def on_message(self, event: Any) -> None:
        data = event.data
        done = True
        if _map_has(self.handlers, data.id):
            done = _map_get(self.handlers, data.id)(data)
        if done:
            _map_delete(self.handlers, data.id)

    def fail(self) -> None:
        """Hand every job waiting its failure (`None`)."""
        for done in _map_values(self.handlers):
            done(None)
        _map_clear(self.handlers)


class BackgroundLoader:
    """Generates levels' grounds and scenery textures in a worker (PERF-14).

    `port` is the ground worker's side it talks to, a `Worker` or a fake: `postMessage(message)`,
    `onmessage`, `onerror` and `terminate()` (optional); `texture_ports`, the texture workers', the
    same (none: the textures go to the ground worker too, D-414). What it posts is copied to plain
    data first (ENG-164).
    """

    def __init__(self, port: Any, texture_ports: list[Any] | None = None) -> None:
        self.port = port
        # The number of the next job (unique across the workers).
        self._next = 0
        self._waiting = _Waiting(port)
        # Textures asked for and not back yet, by key.
        self._textures: Any = _new_map()
        port.onmessage = self._waiting.on_message
        # A broken worker: every job waiting fails (the ground is then generated on the main
        # thread).
        port.onerror = self._on_error
        self._texture_workers: list[_Waiting] = []
        for texture_port in texture_ports or []:
            self._texture_workers.append(self._texture_worker(texture_port))
        # The texture worker the next texture goes to.
        self._turn = 0
        generate_grounds_with(self._ground_generator)

    def _on_error(self, _event: Any) -> None:
        self._waiting.fail()

    def _texture_worker(self, port: Any) -> _Waiting:
        """Listen to texture worker `port`; a broken one fails its jobs and gets no more."""
        waiting = _Waiting(port)
        port.onmessage = waiting.on_message

        def on_error(_event: Any) -> None:
            waiting.fail()
            self._texture_workers = [w for w in self._texture_workers if w is not waiting]

        port.onerror = on_error
        return waiting

    def _ground_generator(self, level: Any, seed: int, replies: GroundReplies) -> None:
        # Whether the ground, then the runout and the chunks (asked for later) came back.
        state = [False, False, False]
        job = [0]

        def ask(through: float) -> None:
            self.port.postMessage(_chunks_message(job[0], through))

        def ask_roads(spans: Any, look: Any, grid: bool, done: Callable[[Any], None]) -> None:
            def on_reply(reply: Any) -> bool:
                done(reply)
                return True

            self._post(_roads_message(job[0], spans, to_plain(look), grid), on_reply)

        def on_reply(reply: Any) -> bool:
            if not state[0]:
                state[0] = True
                if reply and reply.ground:
                    replies.ground(reply.ground, ask, ask_roads)
                    return False
                replies.ground(None, ask, ask_roads)
                return True
            if reply is None:
                return True
            if reply.runout:
                state[1] = True
                replies.runout(reply.runout)
            if reply.chunks:
                replies.chunks(reply.chunks)
                state[2] = reply.done
            return state[1] and state[2]

        job[0] = self._post_ground(level, seed, on_reply)

    def prefetch_textures(self, jobs: Sequence[TextureJob]) -> None:
        """Generate the textures of `jobs` not kept yet, keeping them when they come back."""
        for job in jobs:
            key = _json_of(job)
            if has_texture(job) or _map_has(self._textures, key):
                continue
            _map_set(self._textures, key, True)
            self._post_texture(job, key)

    def _texture_reply(self, job: TextureJob, key: str) -> Callable[[Any], bool]:
        """Return the handler of a texture job's reply.

        It is a function of its own, not made in a loop.
        """

        def on_reply(reply: Any) -> bool:
            _map_delete(self._textures, key)
            if reply and reply.pixels:
                keep_texture(job, reply.pixels)
            return True

        return on_reply

    def _post_texture(self, job: TextureJob, key: str) -> None:
        """Post the texture job to the texture workers in turn, or to the ground worker."""
        message = _texture_message(0, to_plain(job))
        waiting = self._waiting
        count = len(self._texture_workers)
        if count > 0:
            waiting = self._texture_workers[self._turn % count]
            self._turn += 1
        self._post_to(waiting, message, self._texture_reply(job, key))

    def _post_ground(self, level: Any, seed: int, done: Callable[[Any], bool]) -> int:
        return self._post(_ground_message(0, to_plain(level), seed), done)

    def stop(self) -> None:
        """Stop generating in the background: the grounds are made on the main thread again."""
        generate_grounds_with(None)
        ports = [self.port]
        ports.extend([waiting.port for waiting in self._texture_workers])
        for port in ports:
            if hasattr(port, "terminate"):
                port.terminate()

    def _post(self, message: Any, done: Callable[[Any], bool]) -> int:
        return self._post_to(self._waiting, message, done)

    def _post_to(self, waiting: _Waiting, message: Any, done: Callable[[Any], bool]) -> int:
        job_id = self._next
        self._next += 1
        message.id = job_id
        _map_set(waiting.handlers, job_id, done)
        waiting.port.postMessage(message)
        return job_id


def start_background_loader() -> BackgroundLoader | None:
    """Return a loader on the game's workers, if the browser has workers (none in unit tests).

    The ground worker, and `texture_worker_count` texture workers (the same script, D-414).
    """
    if not _worker_available():
        return None
    textures = [_new_game_worker() for _ in range(texture_worker_count(_cores()))]
    return BackgroundLoader(_new_game_worker(), textures)
