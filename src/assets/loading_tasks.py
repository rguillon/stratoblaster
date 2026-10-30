"""Loading tasks (ENG-108), ported from `assets/loading-tasks.ts`."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Awaitable, Callable, Sequence  # noqa: E402

# One step of the loading screen: building a scene, compiling shaders, fetching a file...
# A step may be synchronous (returns None) or return an awaitable.
LoadingTask = Callable[[], Awaitable[None] | None]
__pragma__("noskip")


async def run_loading_tasks(
    tasks: Sequence[LoadingTask],
    on_progress: Callable[[float], None],
    yield_to_browser: Callable[[], Awaitable[None]],
) -> None:
    """Runs `tasks` in order and reports real progress (ENG-108): 0 before the first task, then
    `done / total` after each one. `yield_to_browser` runs before each task so the progress bar
    can be painted between steps.

    A synchronous step is not awaited (a TypeScript `await` on it adds one microtask tick; nothing
    else in the sequence changes).
    """
    on_progress(0)
    for i in range(len(tasks)):
        await yield_to_browser()
        pending = tasks[i]()
        if pending is not None:
            await pending
        on_progress((i + 1) / len(tasks))
    if len(tasks) == 0:
        on_progress(1)
