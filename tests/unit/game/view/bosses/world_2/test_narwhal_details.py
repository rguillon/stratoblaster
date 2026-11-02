# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/narwhal_details.py`: the hull's flanks."""

import pytest

from game.view.bosses.world_2 import narwhal_details as module


def test_the_hull_is_widest_amidships_and_narrows_at_its_stern_and_bow() -> None:
    assert module._flank(0) == 17.5
    assert module._flank(-50) == pytest.approx(11.0)
    assert module._flank(40) == pytest.approx(13.5)
