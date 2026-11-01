"""Unit tests of `src/game/sim/elite_kinds.py`."""

from helpers.enemy_steps import area

from game.sim.elite_kinds import ELITE_KINDS


def test_enm_01_the_five_elite_kinds_are_listed_in_the_spec_order() -> None:
    """The elite tier (ENM-01): ENM-HYDRA-13, ENM-ORBITER-14, ENM-SCISSOR-16, ENM-JUGGERNAUT-16,
    ENM-HIVE-14."""
    assert [kind.id for kind in ELITE_KINDS] == [
        "hydra",
        "orbiter",
        "scissor",
        "juggernaut",
        "hive",
    ]


def test_enm_07_an_elite_spawns_one_enemy_group_per_call() -> None:
    """Also ENM-HIVE-08: a Hive comes in alone."""
    hive = next(k for k in ELITE_KINDS if k.id == "hive")
    assert len(hive.spawn(area())) == 1
