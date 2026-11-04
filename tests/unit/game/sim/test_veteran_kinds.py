# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/veteran_kinds.py`."""

import itertools

from helpers.enemy_steps import area

from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.veteran_kinds import VETERAN_KINDS


def test_enm_01_the_veteran_era_kinds_are_the_wasp_mortar_and_phantom() -> None:
    """Their tiers (ENM-01): the Wasp in tier 2, the Phantom and the Mortar in tier 3.

    ENM-WASP-12, ENM-MORTAR-11, ENM-PHANTOM-14.
    """
    assert [kind.id for kind in VETERAN_KINDS] == ["wasp", "mortar", "phantom"]


def test_enm_wasp_07_a_wasp_group_is_the_configured_number_of_wasps_side_by_side() -> None:
    wasp = VETERAN_KINDS[0]
    group = wasp.spawn(area(width=400))
    assert len(group) == VETERAN_CONFIG.wasp.groupSize
    xs = [w.x for w in group]
    assert xs == sorted(xs)
    spacing = VETERAN_CONFIG.wasp.groupSpacing
    for a, b in itertools.pairwise(xs):
        assert abs((b - a) - spacing) < 1e-9


def test_enm_mortar_07_a_mortar_comes_in_as_a_single_enemy() -> None:
    mortar = next(k for k in VETERAN_KINDS if k.id == "mortar")
    assert len(mortar.spawn(area())) == 1
