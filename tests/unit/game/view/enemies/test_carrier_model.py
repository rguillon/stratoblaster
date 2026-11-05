# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/carrier_model.py`."""

from typing import Any

from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import carrier_model as module


def test_enm_carrier_04_carrier_is_built_as_the_carrier_kind_in_its_neon(monkeypatch: Any) -> None:
    capture = probe_builder(monkeypatch, module.build_carrier)
    assert capture.name == "carrier"
    assert capture.neon == ENEMY_LOOK.neon.carrier


def test_enm_carrier_01_carrier_draws_its_body_on_real_builders(monkeypatch: Any) -> None:
    capture = probe_builder(monkeypatch, module.build_carrier)
    assert len(drawings_of(capture)["body"]["parts"].hull.geometry.positions) > 0


def test_enm_carrier_02_the_sponson_is_cut_into_the_pieces_between_its_bays() -> None:
    pieces = module.sponson_pieces([10, -10])
    assert len(pieces) == 3
    zs = [sorted(z for _x, z in piece) for piece in pieces]
    # In order along Z, each one stopping a bay's half width short of the bays around it.
    assert zs[0][-1] == -10 - module.BAY_HALF
    assert (zs[1][0], zs[1][-1]) == (-10 + module.BAY_HALF, 10 - module.BAY_HALF)
    assert zs[2][0] == 10 + module.BAY_HALF


def test_enm_carrier_02_no_piece_is_left_between_bays_closer_than_a_bay() -> None:
    # The bays overlap: nothing of the sponson is left between them, only before and after.
    pieces = module.sponson_pieces([-2, 2])
    assert len(pieces) == 2
    assert max(z for _x, z in pieces[0]) == -2 - module.BAY_HALF
    assert min(z for _x, z in pieces[1]) == 2 + module.BAY_HALF
