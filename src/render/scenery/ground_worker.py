"""Generates levels' grounds and scenery textures off the main thread (P13-R03), ported from
`render/scenery/ground-worker.ts`. The module is the worker's script: importing it installs the
message handler on the worker's global scope.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from host.worker_data import to_plain  # noqa: E402
from render.scenery.level_ground import generate_in_two  # noqa: E402
from render.scenery.procedural_textures import texture_pixels  # noqa: E402


def _install_handler(handler: Any) -> None:
    """`self.onmessage = handler` on the worker's global scope (called with the message event)."""
    __pragma__("js", "{}", "self.onmessage = function (event) { handler(event); };")


def _post_ground(job_id: int, ground: Any) -> None:
    """`self.postMessage({ id, ground })`."""
    __pragma__("js", "{}", "self.postMessage({id: job_id, ground: ground});")


def _post_runout(job_id: int, runout: Any) -> None:
    """`self.postMessage({ id, runout })`."""
    __pragma__("js", "{}", "self.postMessage({id: job_id, runout: runout});")


def _post_pixels(job_id: int, pixels: Any) -> None:
    """`self.postMessage({ id, pixels }, [pixels.buffer])`: the pixels are moved, not copied."""
    __pragma__("js", "{}", "self.postMessage({id: job_id, pixels: pixels}, [pixels.buffer]);")


def _post_chunks(job_id: int, reply: Any) -> None:
    """`self.postMessage({ id, chunks, done })`: the chunks placed for a ground job."""
    __pragma__(
        "js",
        "{}",
        "self.postMessage({id: job_id, chunks: reply.chunks, done: reply.done});",
    )


def _no_chunks() -> Any:
    """Nothing placed: for a job the worker no longer keeps (the main thread places its own)."""
    __pragma__("js", "{}", "return {chunks: [], done: false};")
    return None


def _later(task: Any) -> None:
    """`setTimeout(task, 0)`."""
    __pragma__("js", "{}", "setTimeout(task, 0);")


# The grounds made in this worker, by job id (the last few: their chunks are asked for as the
# level scrolls).
_KEPT_JOBS = 4
_jobs: list[Any] = []


def _keep_job(job_id: int, made: Any) -> None:
    _jobs.append([job_id, made])
    if len(_jobs) > _KEPT_JOBS:
        _jobs.pop(0)


def _job_of(job_id: int) -> Any:
    for entry in _jobs:
        if entry[0] == job_id:
            return entry[1]
    return None


def _on_message(event: Any) -> None:
    data = event.data
    if data.kind == "chunks":
        # The worker places the chunks the level asks for, in order (P04-R04).
        made = _job_of(data.id)
        if made is None:
            _post_chunks(data.id, _no_chunks())
            return
        _post_chunks(data.id, to_plain(made.chunks(data.through)))
        return
    if data.kind == "ground":
        made = generate_in_two(data.level, data.seed)
        _keep_job(data.id, made)
        _post_ground(data.id, to_plain(made.ground))

        # Reviewer, 2026-10-28: the runout after the jobs already waiting (the level's textures),
        # as the level can start without it.
        def send_runout() -> None:
            _post_runout(data.id, to_plain(made.runout()))

        _later(send_runout)
        return
    pixels = texture_pixels(data.job)
    _post_pixels(data.id, pixels)


_install_handler(_on_message)
