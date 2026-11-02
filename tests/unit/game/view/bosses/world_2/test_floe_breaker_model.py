# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/floe_breaker_model.py`: its harpoon turrets."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import drawn_at, muzzle_kinds, turret_point
from helpers.view_probes import probe_builder

from game.config.record import record
from game.view.bosses.mini_boss_shapes import turret
from game.view.bosses.world_2 import floe_breaker_model as module


def test_sign_of_is_minus_one_zero_or_one() -> None:
    assert [module.sign_of(-2), module.sign_of(0), module.sign_of(7)] == [-1.0, 0.0, 1.0]


def _turret_reading_fields(specs: list[Any]) -> Any:
    """`turret`, its spec read as a record.

    `harpoon_turret` hands it a dict literal, which the browser reads as an object (`spec.radius`)
    but CPython does not: the spec is made a record, as Transcrypt's dict literal is.
    """

    def draw(parts: Any, at: Any, spec: Any) -> None:
        specs.append(record(spec))
        turret(parts, at, specs[-1])

    return draw


@pytest.mark.parametrize(("piece", "hatch"), [("harpoon-left", -1), ("harpoon-right", 1)])
def test_mb_floe_breaker_03_a_harpoon_turret_has_one_long_barrel_and_its_hatch_outboard(
    monkeypatch: Any, piece: str, hatch: int
) -> None:
    specs: list[Any] = []
    monkeypatch.setattr(module, "turret", _turret_reading_fields(specs))
    capture = probe_builder(monkeypatch, module.build_floe_breaker)
    harpoon = drawn_at(capture.drawing["turrets"][piece], turret_point(capture.design, piece))
    assert muzzle_kinds(harpoon) == ["gun"]
    spec = specs[0]
    assert (spec.barrels, spec.length, spec.hatch) == (1, 10, hatch)
    assert spec.neon == module.CYAN
