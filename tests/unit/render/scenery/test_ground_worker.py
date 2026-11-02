# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/ground_worker.py`: the worker's message handler (PERF-14).

The worker's `postMessage` calls are recorded, the ground generation is a fake that names what it
is asked for, and `to_plain` (ENG-164) wraps what it copies so a test can tell it was copied.
"""

from types import SimpleNamespace
from typing import Any

import pytest

from render.scenery import ground_worker
from render.scenery.ground_worker import install_message_handler


def _never(*_args: Any) -> None:
    """Fail: the placeholders must not call their callback (the browser calls it later)."""
    raise AssertionError


# The JavaScript-only helpers as the module defines them, taken before the fixture replaces them.
JS_HELPERS: list[tuple[Any, tuple[Any, ...]]] = [
    (ground_worker._install_handler, (_never,)),
    (ground_worker._post_ground, (0, "ground")),
    (ground_worker._post_runout, (0, "runout")),
    (ground_worker._post_pixels, (0, [0, 0, 0, 255])),
    (ground_worker._post_chunks, (0, SimpleNamespace(chunks=[], done=True))),
    (ground_worker._post_roads, (0, [], [1, 2])),
    (ground_worker._copy_pixels, ([1, 2],)),
    (ground_worker._no_chunks, ()),
    (ground_worker._later, (_never,)),
]
COPY_PIXELS = ground_worker._copy_pixels


class Made:
    """A ground made by `generate_in_two`: each call names what it was asked for."""

    def __init__(self, level: Any, seed: int) -> None:
        self.ground = ("ground", level, seed)
        self.atlas: Any = None

    def runout(self) -> Any:
        return ("runout", self.ground)

    def chunks(self, through: float) -> Any:
        return ("chunks", through)

    def roads(self, spans: Any, look: Any, grid: bool) -> Any:
        return SimpleNamespace(chunks=("roads", spans, look, grid), atlas=self.atlas)


class Worker:
    """What the handler did: the messages posted, the tasks put off, the grounds made."""

    def __init__(self) -> None:
        self.posted: list[tuple[Any, ...]] = []
        self.later: list[Any] = []
        self.made: list[Made] = []

    def send(self, kind: str, **fields: Any) -> None:
        ground_worker._on_message(SimpleNamespace(data=SimpleNamespace(kind=kind, **fields)))

    def generate(self, level: Any, seed: int) -> Made:
        made = Made(level, seed)
        self.made.append(made)
        return made


def _recorder(worker: Worker, kind: str) -> Any:
    return lambda *args: worker.posted.append((kind, *args))


@pytest.fixture
def worker(monkeypatch: pytest.MonkeyPatch) -> Worker:
    recorded = Worker()
    monkeypatch.setattr(ground_worker, "_jobs", [])
    for kind in ("ground", "runout", "pixels", "chunks", "roads"):
        monkeypatch.setattr(ground_worker, "_post_" + kind, _recorder(recorded, kind))
    monkeypatch.setattr(ground_worker, "to_plain", lambda value: {"plain": value})
    monkeypatch.setattr(
        ground_worker, "_copy_pixels", lambda pixels: None if pixels is None else ["copy", pixels]
    )
    monkeypatch.setattr(ground_worker, "_no_chunks", lambda: "no chunks")
    monkeypatch.setattr(ground_worker, "_later", recorded.later.append)
    monkeypatch.setattr(ground_worker, "generate_in_two", recorded.generate)
    monkeypatch.setattr(ground_worker, "texture_pixels", lambda job: ("pixels of", job))
    return recorded


@pytest.mark.parametrize(("helper", "args"), JS_HELPERS)
def test_the_javascript_helpers_do_nothing_under_cpython(
    helper: Any, args: tuple[Any, ...]
) -> None:
    """The worker's `self`, `postMessage`, `setTimeout` and array helpers are `__pragma__("js")`.

    CPython runs only the placeholder after them: None, and no callback called.
    """
    assert helper(*args) is None


def test_the_pixels_of_no_atlas_copy_to_none() -> None:
    assert COPY_PIXELS(None) is None


def test_perf_14_the_handler_is_installed_on_the_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    installed: list[Any] = []
    monkeypatch.setattr(ground_worker, "_install_handler", installed.append)
    install_message_handler()
    assert installed == [ground_worker._on_message]


def test_perf_15_eng_164_a_ground_is_posted_at_once_and_its_runout_later(worker: Worker) -> None:
    worker.send("ground", id=3, level="level", seed=7)
    assert worker.posted == [("ground", 3, {"plain": ("ground", "level", 7)})]
    # The runout waits for the jobs already queued (the level's textures).
    [send_runout] = worker.later
    send_runout()
    assert worker.posted[-1] == ("runout", 3, {"plain": ("runout", ("ground", "level", 7))})


def test_perf_16_eng_164_the_chunks_of_a_kept_ground_are_placed_and_posted(worker: Worker) -> None:
    worker.send("ground", id=3, level="level", seed=7)
    worker.send("chunks", id=3, through=2400.0)
    assert worker.posted[-1] == ("chunks", 3, {"plain": ("chunks", 2400.0)})


def test_perf_16_the_chunks_of_a_ground_not_kept_are_none(worker: Worker) -> None:
    worker.send("chunks", id=5, through=2400.0)
    assert worker.posted == [("chunks", 5, "no chunks")]


def test_perf_16_only_the_last_grounds_made_are_kept(worker: Worker) -> None:
    for job_id in range(ground_worker._KEPT_JOBS + 1):
        worker.send("ground", id=job_id, level="level", seed=job_id)
    worker.send("chunks", id=0, through=100.0)
    worker.send("chunks", id=1, through=100.0)
    assert worker.posted[-2:] == [
        ("chunks", 0, "no chunks"),
        ("chunks", 1, {"plain": ("chunks", 100.0)}),
    ]


def test_eng_164_the_street_surfaces_of_a_kept_ground_are_posted_with_the_atlas_copied(
    worker: Worker,
) -> None:
    worker.send("ground", id=3, level="level", seed=7)
    worker.made[0].atlas = [9, 9, 9, 9]
    worker.send("roads", id=4, ground=3, spans=[[0, 0, 100]], look="look", grid=True)
    assert worker.posted[-1] == (
        "roads",
        4,
        {"plain": ("roads", [[0, 0, 100]], "look", True)},
        ["copy", [9, 9, 9, 9]],
    )


def test_an_unchanged_road_atlas_is_not_posted(worker: Worker) -> None:
    worker.send("ground", id=3, level="level", seed=7)
    worker.send("roads", id=4, ground=3, spans=[], look="look", grid=False)
    assert worker.posted[-1] == ("roads", 4, {"plain": ("roads", [], "look", False)}, None)


def test_the_street_surfaces_of_a_ground_not_kept_are_none(worker: Worker) -> None:
    worker.send("roads", id=4, ground=8, spans=[[0, 0, 100]], look="look", grid=True)
    assert worker.posted == [("roads", 4, [], None)]


def test_perf_14_any_other_job_is_a_texture_whose_pixels_are_posted(worker: Worker) -> None:
    worker.send("texture", id=2, job="noise job")
    assert worker.posted == [("pixels", 2, ("pixels of", "noise job"))]
    assert worker.made == []
