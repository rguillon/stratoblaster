# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/refinery_titan_parts.py`: the rotary turret."""

import pytest
from helpers.view_probes import drawn

from game.view.bosses.refinery_titan_parts import (
    BARREL_LENGTH,
    BARRELS,
    TITAN_DECK,
    TURRET_HOUSING,
    draw_rotary,
)


def test_fb_refinery_titan_03_a_rotary_turret_has_three_barrels_with_lit_muzzles() -> None:
    at = [10, 0, 20]
    turret = drawn(lambda p: draw_rotary(p, at))
    parts = turret["parts"]
    assert len(parts.hull.geometry.positions) > 0
    assert len(parts.charge.geometry.positions) > 0
    assert len(parts.neon.geometry.positions) > 0
    # One muzzle a barrel, at its tip, past the housing's front along the turret's axis.
    axis = at[1] + TITAN_DECK["sponson"] + 9
    front = at[2] + TURRET_HOUSING[2][0]
    tips = [[at[0] + b[0], axis + b[1], front + BARREL_LENGTH + 1.6] for b in BARRELS]
    assert len(turret["muzzles"]) == len(tips)
    for muzzle, tip in zip(turret["muzzles"], tips, strict=True):
        assert muzzle[0] == pytest.approx(tip)
    assert [m[1] for m in turret["muzzles"]] == ["gun", "gun", "gun"]
