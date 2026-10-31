"""D-227: every boss model is one object, at rest and after each of its transformations: no piece
of it hangs in the air (its parts and weapons, its frames, its rig, its stems and pylons, the
pieces its armour cut leaves)."""

from typing import Any

import pytest
from helpers.boss_wholeness import boss_states, loose_pieces

from game.sim.boss_kinds import BOSS_DESIGNS


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=[d.id for d in BOSS_DESIGNS])
def test_d227_the_boss_holds_together_in_every_state(design: Any) -> None:
    mp = pytest.MonkeyPatch()
    try:
        states = boss_states(design.id, design, mp)
    finally:
        mp.undo()
    for form, tris in enumerate(states):
        assert loose_pieces(tris, 0) == [], f"after transformation {form}"
