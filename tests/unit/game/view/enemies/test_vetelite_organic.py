# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/vetelite_organic.py`: the membrane wings' sides."""

from typing import Any

import pytest
from helpers.view_probes import drawn

from game.config.record import record
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.vetelite_organic import membrane_pair, sided

WING = record({
    "root": [2.0, 1.0],
    "tips": [[9.0, 3.0], [8.0, -2.0]],
    "y": 0.5,
    "thickness": 0.3,
    "strut": 0.4,
})


@pytest.mark.parametrize("s", [1, -1])
def test_a_wing_is_mirrored_to_its_side_with_its_other_fields_kept(s: int) -> None:
    wing = sided(WING, s)
    assert wing["root"] == [s * 2.0, 1.0]
    assert wing["tips"] == [[s * 9.0, 3.0], [s * 8.0, -2.0]]
    assert (wing["y"], wing["thickness"], wing["strut"]) == (0.5, 0.3, 0.4)


def test_mirroring_a_wing_leaves_the_wing_it_copies_as_it_was() -> None:
    sided(WING, -1)
    assert WING["root"] == [2.0, 1.0]
    assert WING["tips"] == [[9.0, 3.0], [8.0, -2.0]]


def test_enm_42_a_membrane_pair_is_one_fluttering_wing_on_each_side() -> None:
    """Also ENM-WASP-05: a membrane skin on a bone strut, hinged at its root."""

    def draw(p: Any) -> None:
        membrane_pair(p, WING, 9)

    wings = drawn(draw)["wings"]
    assert [w.side for w in wings] == list(SIDES)
    assert [w.pivot for w in wings] == [[s * 2.0, 0.5, 1.0] for s in SIDES]
    assert all(w.span == 9 for w in wings)
    assert all(len(w.parts.flesh.geometry.positions) > 0 for w in wings)
