# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/harbour_kraken_cargo.py`: the container bay."""

from typing import Any

from helpers.view_probes import drawn

from game.view.bosses.world_2 import harbour_kraken_cargo as module


def _paints(monkeypatch: Any) -> list[Any]:
    """Draw the container bay; return the paint of each container (egg) it lays."""
    paints: list[Any] = []
    monkeypatch.setattr(module, "_container", lambda _p, _at, paint: paints.append(paint))
    drawn(lambda p: module.container_bay(p, [0.0, 0.0, 10.0]))
    return paints


def test_fb_harbour_kraken_03_the_bay_stacks_its_containers_in_turning_paints(
    monkeypatch: Any,
) -> None:
    paints = _paints(monkeypatch)
    assert len(paints) == sum(stack[2] for stack in module.STACKS)
    assert paints[:2] == [module.PAINT[0], module.PAINT[1]]


def test_fb_harbour_kraken_03_a_container_with_no_paint_is_plain_hull_metal(
    monkeypatch: Any,
) -> None:
    # A paint the look lacks reads as undefined in the browser (None here).
    monkeypatch.setattr(module, "PAINT", [None])
    assert set(map(tuple, _paints(monkeypatch))) == {tuple(module.H.base)}
