"""Unit tests of `src/game/sim/veteran_kinds.py`."""

from helpers.enemy_steps import area

from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.veteran_kinds import VETERAN_KINDS


def test_p05_r14_the_five_veteran_kinds_are_listed_in_the_spec_order() -> None:
    assert [kind.id for kind in VETERAN_KINDS] == [
        "wasp",
        "mortar",
        "mantis",
        "phantom",
        "minelayer",
    ]


def test_p05_r14_a_wasp_group_is_the_configured_number_of_wasps_side_by_side() -> None:
    wasp = VETERAN_KINDS[0]
    group = wasp.spawn(area(width=400))
    assert len(group) == VETERAN_CONFIG.wasp.groupSize
    xs = [w.x for w in group]
    assert xs == sorted(xs)
    spacing = VETERAN_CONFIG.wasp.groupSpacing
    for a, b in zip(xs, xs[1:], strict=False):
        assert abs((b - a) - spacing) < 1e-9


def test_p05_r14_a_mortar_comes_in_as_a_single_enemy() -> None:
    mortar = next(k for k in VETERAN_KINDS if k.id == "mortar")
    assert len(mortar.spawn(area())) == 1
