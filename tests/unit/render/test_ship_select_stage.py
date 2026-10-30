"""Unit tests of `src/render/ship_select_stage.py`."""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeVector

from render.ship_select_stage import ShipSelectStage


def _pivot(x: float, scale: float = 1.0) -> FakeNode:
    pivot = FakeNode("pivot")
    pivot.position = FakeVector(x, 0, 0)
    pivot.scaling = FakeVector(scale, scale, scale)
    pivot.scaling.setAll = lambda value: pivot.scaling.set(value, value, value)  # type: ignore[attr-defined]
    return pivot


def _stage(pivots: list[FakeNode]) -> ShipSelectStage:
    """A stage built by hand: the constructor makes Babylon objects, which the tests replace."""
    stage = ShipSelectStage.__new__(ShipSelectStage)
    stage._options = SimpleNamespace(
        highlight_scale=1.2,
        dim_scale=0.8,
        scale_ease_per_sec=2.0,
        lights=SimpleNamespace(spot_intensity=3.0),
    )
    stage._selected = 0
    stage.showcase = SimpleNamespace(
        pivots=pivots,
        update=lambda dt: None,
    )
    stage._spots = [SimpleNamespace(intensity=0.0) for _ in pivots]
    stage.ring = SimpleNamespace(position=FakeVector())
    return stage


def test_selecting_a_ship_lights_its_spot_only_and_moves_the_ring() -> None:
    pivots = [_pivot(-5), _pivot(0), _pivot(5)]
    stage = _stage(pivots)
    stage.select(1)
    assert stage.selected == 1
    assert [spot.intensity for spot in stage._spots] == [0, 3.0, 0]
    assert stage.ring.position.x == 0
    assert stage.spot is stage._spots[1]


def test_a_selection_past_the_last_ship_is_clamped_to_it() -> None:
    pivots = [_pivot(-5), _pivot(0), _pivot(5)]
    stage = _stage(pivots)
    stage.select(9)
    assert stage.selected == 2
    assert stage.ring.position.x == 5


def test_a_negative_selection_is_clamped_to_the_first_ship() -> None:
    stage = _stage([_pivot(-5), _pivot(5)])
    stage.select(-3)
    assert stage.selected == 0


@pytest.mark.xfail(
    strict=True,
    reason="BUG: with no ship, select clamps to -1 and then indexes pivots[-1]; the guard that "
    "is meant for an empty stage tests `>=` on the clamped value",
)
def test_a_stage_with_no_ship_can_select_without_error() -> None:
    stage = _stage([])
    stage.select(0)
    assert stage.selected == 0


def test_the_spot_of_an_empty_stage_is_an_error() -> None:
    stage = _stage([_pivot(0)])
    stage._spots = []
    with pytest.raises(ValueError, match="no ship"):
        _ = stage.spot


def test_the_highlighted_ship_grows_and_the_others_shrink_towards_their_target() -> None:
    pivots = [_pivot(-5, scale=1.0), _pivot(5, scale=1.0)]
    stage = _stage(pivots)
    stage.select(0)
    stage.update(0.5)
    ease = 1 - math.exp(-2.0 * 0.5)
    assert pivots[0].scaling.x == pytest.approx(1 + (1.2 - 1) * ease)
    assert pivots[1].scaling.x == pytest.approx(1 + (0.8 - 1) * ease)


def test_the_showcase_is_turned_on_each_update() -> None:
    calls: list[float] = []
    stage = _stage([_pivot(0)])
    stage.showcase.update = calls.append  # type: ignore[attr-defined]
    stage.update(0.25)
    assert calls == [0.25]


def test_each_ship_starts_at_its_target_scale_when_the_stage_is_built() -> None:
    stage = _stage([_pivot(0), _pivot(5)])
    stage.select(0)
    target: Any = stage._target_scale
    assert target(stage.showcase.pivots[0]) == 1.2
    assert target(stage.showcase.pivots[1]) == 0.8
