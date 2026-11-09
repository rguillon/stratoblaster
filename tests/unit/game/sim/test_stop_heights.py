# Copyright (c) 2026 Renaud Guillon
"""D-313: the enemies that stop on the playfield spread down it, not along its top."""

import pytest
from helpers.enemy_steps import area

from game.sim.enemy_kinds import ENEMY_KINDS

# The kinds that stop to attack (or before their dive), and their stop height's attribute.
HOLDERS = ["harrier", "sweeper", "prism", "lancer", "spinner", "hydra", "scissor", "juggernaut"]


def _stops(kind_id: str, count: int = 200) -> list[float]:
    kind = next(k for k in ENEMY_KINDS if k.id == kind_id)
    # Each holder has a `stop_y`.
    return [
        enemy.stop_y / 600  # type: ignore[attr-defined]
        for seed in range(count)
        for enemy in kind.spawn(area(width=400, height=600, seed=seed))
    ]


@pytest.mark.parametrize("kind_id", HOLDERS)
def test_d_313_a_holder_stops_at_heights_spread_down_to_the_middle(kind_id: str) -> None:
    heights = _stops(kind_id)
    # Not all in the top quarter: many come down to the middle of the playfield or below it.
    assert min(heights) < 0.6, kind_id
    assert sum(h < 0.75 for h in heights) > len(heights) / 3, kind_id
    # And never down onto the player at the bottom.
    assert min(heights) >= 0.4, kind_id
    assert max(heights) - min(heights) > 0.25, kind_id
