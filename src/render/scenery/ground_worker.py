"""Generates levels' grounds and scenery textures off the main thread (P13-R03), ported from
`render/scenery/ground-worker.ts`. The module is the worker's script: importing it installs the
message handler on the worker's global scope.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

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


def _later(task: Any) -> None:
    """`setTimeout(task, 0)`."""
    __pragma__("js", "{}", "setTimeout(task, 0);")


def _on_message(event: Any) -> None:
    data = event.data
    if data.kind == "ground":
        made = generate_in_two(data.level, data.seed)
        _post_ground(data.id, made.ground)

        # Reviewer, 2026-10-28: the runout after the jobs already waiting (the level's textures),
        # as the level can start without it.
        def send_runout() -> None:
            _post_runout(data.id, made.runout())

        _later(send_runout)
        return
    pixels = texture_pixels(data.job)
    _post_pixels(data.id, pixels)


_install_handler(_on_message)
