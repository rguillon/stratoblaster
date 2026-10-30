"""Tests of the weapons of a run (phase 6 review), `core/systems/run_arsenal.py`."""

from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.run_arsenal import RunArsenal, WeaponLevels
from core.systems.shot_world import ShotWorld, ShotWorldOptions


def _weapon(id: str, levels: int = 2) -> ProjectileWeaponDefinition:
    return ProjectileWeaponDefinition(
        id,
        id,
        "muzzle",
        5,
        10,
        0,
        100,
        0,
        0,
        1,
        1,
        0,
        [[ShotStream(0, 0)] for _ in range(levels)],
    )


A = _weapon("a")
B = _weapon("b")


def _arsenal(weapons: list[ProjectileWeaponDefinition], start_level: float = 1) -> RunArsenal:
    shots = ShotWorld(ShotWorldOptions(100, 100, 10), weapons[0] if weapons else A)
    shots.select(shots.weapon, start_level)
    return RunArsenal(shots, weapons, start_level)


def test_p06_r07_switching_moves_to_the_next_weapon_at_its_start_level() -> None:
    arsenal = _arsenal([A, B], start_level=2)
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is B
    assert arsenal._shots.level == 2


def test_p06_r07_switching_wraps_around_and_keeps_each_weapons_level() -> None:
    arsenal = _arsenal([A, B])
    arsenal.level_up(1)
    arsenal.switch_weapon()
    arsenal.level_up(1)
    assert arsenal._shots.level == 2
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is A
    assert arsenal._shots.level == 2
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is B
    assert arsenal._shots.level == 2


def test_p06_r07_a_single_weapon_switches_to_itself_with_its_level_kept() -> None:
    arsenal = _arsenal([A])
    arsenal.level_up(1)
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is A
    assert arsenal._shots.level == 2


def test_p06_r07_switching_with_no_weapons_list_keeps_the_weapon() -> None:
    arsenal = _arsenal([])
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is A


def test_p06_r07_a_weapon_not_in_the_list_switches_to_the_first_one() -> None:
    arsenal = _arsenal([B])
    arsenal._shots.select(A, 1)
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is B


def test_p06_r07_level_up_adds_levels_up_to_the_last_one() -> None:
    arsenal = _arsenal([A])
    arsenal.level_up(0)
    assert arsenal._shots.level == 1
    arsenal.level_up(-1)
    assert arsenal._shots.level == 1
    arsenal.level_up(5)
    assert arsenal._shots.level == 2


def test_p07_r08_a_snapshot_keeps_the_weapon_and_the_level_of_each_weapon_used() -> None:
    arsenal = _arsenal([A, B])
    arsenal.level_up(1)
    arsenal.switch_weapon()
    arsenal.level_up(1)
    arsenal.level_up(0)
    snap = arsenal.snapshot()
    assert snap.weapon == "b"
    assert snap.levels == {"a": 2, "b": 2}


def test_p07_r08_restore_brings_back_the_snapshot_weapons_and_levels() -> None:
    saved = WeaponLevels("b", {"a": 2, "b": 1})
    arsenal = _arsenal([A, B])
    arsenal.restore(saved)
    assert arsenal._shots.weapon is B
    assert arsenal._shots.level == 1
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is A
    assert arsenal._shots.level == 2


def test_p07_r08_restore_with_an_unknown_weapon_keeps_the_current_one() -> None:
    arsenal = _arsenal([A, B])
    arsenal.restore(WeaponLevels("zzz", {"a": 2}))
    assert arsenal._shots.weapon is A
    assert arsenal._shots.level == 2


def test_p07_r08_restore_without_a_saved_level_starts_the_weapon_at_its_start() -> None:
    arsenal = _arsenal([A, B], start_level=1)
    arsenal.restore(WeaponLevels("b", {}))
    assert arsenal._shots.weapon is B
    assert arsenal._shots.level == 1


def test_p07_r08_restoring_forgets_the_levels_held_before() -> None:
    arsenal = _arsenal([A, B])
    arsenal.level_up(1)
    arsenal.restore(WeaponLevels("a", {}))
    arsenal.switch_weapon()
    arsenal.switch_weapon()
    assert arsenal._shots.level == 1
