"""Unit tests of `src/assets/loading_tasks.py`."""

import asyncio
from collections.abc import Coroutine
from typing import Any

from assets.loading_tasks import run_loading_tasks


async def _no_yield() -> None:
    return None


def run(coroutine: Coroutine[Any, Any, None]) -> None:
    asyncio.run(coroutine)


def test_eng108_progress_starts_at_zero_then_reaches_one_step_by_step() -> None:
    progress: list[float] = []
    steps: list[str] = []

    def first() -> None:
        steps.append("first")

    def second() -> None:
        steps.append("second")

    run(run_loading_tasks([first, second], progress.append, _no_yield))
    assert steps == ["first", "second"]
    assert progress == [0, 0.5, 1]


def test_eng108_an_awaitable_step_is_awaited_before_its_progress_is_reported() -> None:
    order: list[str] = []

    async def slow() -> None:
        await asyncio.sleep(0)
        order.append("slow done")

    def record(value: float) -> None:
        order.append(f"progress {value}")

    run(run_loading_tasks([slow], record, _no_yield))
    assert order == ["progress 0", "slow done", "progress 1.0"]


def test_eng108_the_browser_gets_a_turn_before_every_step() -> None:
    turns: list[str] = []

    async def yield_to_browser() -> None:
        turns.append("yield")

    def task() -> None:
        turns.append("task")

    run(run_loading_tasks([task, task], lambda _p: None, yield_to_browser))
    assert turns == ["yield", "task", "yield", "task"]


def test_eng108_no_task_reports_done_at_once() -> None:
    progress: list[float] = []
    run(run_loading_tasks([], progress.append, _no_yield))
    assert progress == [0, 1]
