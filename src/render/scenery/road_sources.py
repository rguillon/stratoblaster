"""Where the street surfaces of a level's terrain chunks come from (phase 15): the ground worker
(`WorkerRoadSource`, asynchronous: the chunks arrive as the worker makes them) or the main thread
(`LocalRoadSource`, at once). Both are asked with `request(spans, look, grid)`, where a span is
`[index, z_min, z_max]`, and given up with `take(index)`, which is None until the chunk is ready.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.scenery.road_chunks import TileRoadChunks

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Any  # noqa: E402

__pragma__("noskip")


# The chunks by index: plain JavaScript objects, read and written raw (a Transcrypt dict is not).


def _new_object() -> Any:
    __pragma__("js", "{}", "return {};")
    return None


def _has(cache: Any, key: Any) -> bool:
    __pragma__("js", "{}", "return Object.prototype.hasOwnProperty.call(cache, key);")
    return False


def _get(cache: Any, key: Any) -> Any:
    __pragma__("js", "{}", "return cache[key];")
    return None


def _set(cache: Any, key: Any, value: Any) -> None:
    __pragma__("js", "{}", "cache[key] = value;")


def _delete(cache: Any, key: Any) -> None:
    __pragma__("js", "{}", "delete cache[key];")


class LocalRoadSource:
    """The street surfaces made on the main thread, when asked (no worker)."""

    def __init__(self, roads: Any, tiles: Any, ground: Any) -> None:
        self._roads = roads
        self._tiles = tiles
        self._ground = ground
        self._chunks: TileRoadChunks | None = None
        self._look: Any = None
        self._ready: Any = _new_object()

    def request(self, spans: Sequence[Sequence[Any]], look: Any, grid: bool) -> None:
        if self._chunks is None or look is not self._look:
            self._chunks = TileRoadChunks(self._roads, self._tiles, look, self._ground)
            self._look = look
            self._ready = _new_object()
        for span in spans:
            index = span[0]
            if _has(self._ready, index):
                continue
            chunks = self._chunks
            chunk = chunks.chunk(index, span[1], span[2], grid)
            if chunks.atlas_changed():
                chunk.atlas = chunks.atlas_pixels()
            _set(self._ready, index, chunk)

    def ready(self, index: int) -> bool:
        """Whether chunk `index` is made (and not taken yet)."""
        return _has(self._ready, index)

    def take(self, index: int) -> Any:
        if not _has(self._ready, index):
            return None
        chunk = _get(self._ready, index)
        _delete(self._ready, index)
        return chunk


class WorkerRoadSource:
    """The street surfaces made by the ground worker: asked for once per chunk, kept until taken.
    `ask(spans, look, grid, done)` sends the request; `done(reply)` takes its reply, whose `chunks`
    are the chunks asked for and whose `atlas` (when it changed) is the atlas's pixels."""

    def __init__(self, ask: Callable[[list[Any], Any, bool, Callable[[Any], None]], None]) -> None:
        self._ask = ask
        self._asked: Any = _new_object()
        self._ready: Any = _new_object()

    def request(self, spans: Sequence[Sequence[Any]], look: Any, grid: bool) -> None:
        fresh: list[Any] = []
        for span in spans:
            index = span[0]
            if not _has(self._asked, index) and not _has(self._ready, index):
                _set(self._asked, index, True)
                fresh.append(span)
        if len(fresh) > 0:
            self._ask(fresh, look, grid, self._receive)

    def _receive(self, reply: Any) -> None:
        for i in range(len(reply.chunks)):
            chunk = reply.chunks[i]
            # The atlas comes once, with the first chunk: the chunks of a reply all see it.
            if i == 0:
                chunk.atlas = reply.atlas
            _set(self._ready, chunk.index, chunk)

    def ready(self, index: int) -> bool:
        """Whether chunk `index` is back from the worker (and not taken yet)."""
        return _has(self._ready, index)

    def take(self, index: int) -> Any:
        if not _has(self._ready, index):
            return None
        chunk = _get(self._ready, index)
        _delete(self._ready, index)
        _delete(self._asked, index)
        return chunk
