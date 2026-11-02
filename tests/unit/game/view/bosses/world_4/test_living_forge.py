# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/living_forge.py`: flesh shells."""

from helpers.view_probes import paths, recorder

from game.view.bosses.world_4 import living_forge as module


def test_a_flesh_shell_alternates_the_base_flesh_and_a_dark_seam_by_default() -> None:
    builder, log = recorder()
    module.flesh_shell(builder, [[0, 1], [1, 0]], [[0, 1, 0, 1], [5, 1, 0, 1]])
    assert paths(log) == ["loft"]
    (_section, _stations, color, place, options) = log[0][1]
    assert color == module.SKIN.base
    assert place is None
    assert options.paint(0, 1) == module.SKIN.dark
    assert options.paint(0, 0) is None
