# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/jaguar_parts.py`: its claw guns and tail cannon."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import (
    design_muzzles,
    drawn_at,
    muzzle_kinds,
    turret_drawings,
)
from helpers.view_probes import probe_builder

from game.view.bosses.world_3 import jaguar_parts as module
from game.view.bosses.world_3.jaguar_model import build_jaguar


@pytest.mark.parametrize("piece", ["claw-left", "claw-right"])
def test_mb_jaguar_04_a_claw_gun_has_twin_barrels_at_the_design_muzzles(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_jaguar)
    claw = turret_drawings(capture)[piece]
    assert muzzle_kinds(claw) == ["gun", "gun"]
    assert [at for at, _kind in claw["muzzles"]] == [
        pytest.approx(at) for at in design_muzzles(capture.design, piece, "gun")
    ]


def test_mb_jaguar_04_the_tail_cannon_fires_its_laser_from_the_design_muzzle(
    monkeypatch: Any,
) -> None:
    capture = probe_builder(monkeypatch, build_jaguar)
    cannon = turret_drawings(capture)["tail-cannon"]
    assert muzzle_kinds(cannon) == ["laser"]
    assert cannon["muzzles"][0][0] == pytest.approx(
        design_muzzles(capture.design, "tail-cannon", "laser")[0]
    )


def test_mb_jaguar_04_without_a_tail_muzzle_the_laser_leaves_from_the_pivot(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "JAGUAR_TAIL", [])
    cannon = drawn_at(module.tail_turret, [0.0, 0.0, -40.0])
    assert cannon["muzzles"] == [[[0.0, 0.0, -40.0], "laser"]]


def test_mb_jaguar_04_a_claw_mount_on_the_centre_line_is_drawn_as_a_left_one(
    monkeypatch: Any,
) -> None:
    rosettes: list[Any] = []
    monkeypatch.setattr(module, "rosette", lambda _hull, at, _r, _y: rosettes.append(at))
    for x in [0.0, 10.0]:
        drawn_at(module.claw_mount, [x, 0.0, 20.0])
    # The spot sits 4 out from the mount's centre, on the +X side for both.
    assert rosettes == [[4.0, 6.0], [14.0, 6.0]]
