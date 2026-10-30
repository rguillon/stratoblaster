"""Unit tests of `src/game/sim/elite_kinds.py`."""

from helpers.enemy_steps import area

from game.sim.elite_kinds import ELITE_KINDS


def test_p05_r19_the_five_elite_kinds_are_listed_in_the_spec_order() -> None:
    assert [kind.id for kind in ELITE_KINDS] == [
        "hydra",
        "orbiter",
        "scissor",
        "juggernaut",
        "hive",
    ]


def test_p05_r19_an_elite_spawns_one_enemy_group_per_call() -> None:
    hive = next(k for k in ELITE_KINDS if k.id == "hive")
    assert len(hive.spawn(area())) == 1
