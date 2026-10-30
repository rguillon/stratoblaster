"""Tests of the bonuses (phase 6 review, GD-31, P11-R07), `core/systems/bonus_world.py`."""

import pytest

from core.math.rng import create_rng
from core.systems.bonus_world import (
    BonusChance,
    BonusRules,
    BonusWorld,
    LifeAndBomb,
    drop_chance,
)


class _Source:
    """A destroyed thing that may drop a bonus (DropSource)."""

    def __init__(
        self,
        x: float = 50,
        y: float = 50,
        max_health: float = 10,
        drop: float | None = None,
    ) -> None:
        self.id = 0
        self.x = x
        self.y = y
        self.radius = 3
        self.health = 0
        self.max_health = max_health
        self.drop_chance = drop
        self.points = None


class _Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def _rules(
    per_health: float = 0.1,
    lo: float = 0.0,
    hi: float = 1.0,
    special: LifeAndBomb | None = None,
    overflow: LifeAndBomb | None = None,
) -> BonusRules:
    return BonusRules(
        BonusChance(per_health, lo, hi),
        fall_speed=10,
        pickup_radius=5,
        special=special,
        overflow_points=overflow,
    )


def _always(value: float) -> object:
    return lambda: value


def test_gd31_a_target_with_its_own_chance_uses_it() -> None:
    assert drop_chance(_rules(), _Source(drop=0.7)) == 0.7


def test_gd31_the_chance_grows_with_health_within_its_limits() -> None:
    rules = _rules(per_health=0.1, lo=0.2, hi=0.6)
    assert drop_chance(rules, _Source(max_health=1)) == pytest.approx(0.2)
    assert drop_chance(rules, _Source(max_health=4)) == pytest.approx(0.4)
    assert drop_chance(rules, _Source(max_health=100)) == pytest.approx(0.6)


def test_gd31_a_destroyed_enemy_drops_a_weapon_bonus_when_the_draw_succeeds() -> None:
    world = BonusWorld(_rules(), create_rng(1), (0, 100), 10)
    world.drop([_Source(drop=1.0)])
    assert [b.kind for b in world.bonuses] == ["weapon"]
    assert world.dropped == 1


def test_gd31_no_bonus_drops_when_the_draw_fails() -> None:
    world = BonusWorld(_rules(), _always(0.99), (0, 100), 10)  # type: ignore[arg-type]
    world.drop([_Source(drop=0.5)])
    assert world.bonuses == []
    assert world.dropped == 0


def test_p11_r07_a_special_enemy_may_drop_a_life_before_a_bomb_or_weapon() -> None:
    odds = LifeAndBomb(0.5, 0.5)
    world = BonusWorld(
        _rules(special=odds),
        _always(0.0),
        (0, 100),
        10,  # type: ignore[arg-type]
        _always(0.0),
    )  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: True)
    assert [b.kind for b in world.bonuses] == ["life"]


def test_p11_r07_a_special_enemy_drops_a_bomb_when_the_life_draw_fails() -> None:
    odds = LifeAndBomb(0.1, 0.5)
    world = BonusWorld(
        _rules(special=odds),
        _always(0.0),
        (0, 100),
        10,  # type: ignore[arg-type]
        _always(0.3),
    )  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: True)
    assert [b.kind for b in world.bonuses] == ["bomb"]


def test_p11_r07_the_weapon_draw_always_happens_even_when_a_special_bonus_is_dropped() -> None:
    calls: list[float] = []

    def weapon_draw() -> float:
        calls.append(0)
        return 0.0

    odds = LifeAndBomb(1.0, 1.0)
    world = BonusWorld(_rules(special=odds), weapon_draw, (0, 100), 10, _always(0.0))  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: True)
    assert calls == [0]
    assert [b.kind for b in world.bonuses] == ["life"]


def test_p11_r07_an_ordinary_enemy_never_drops_a_special_bonus() -> None:
    odds = LifeAndBomb(1.0, 1.0)
    # The weapon draw (0.99) succeeds against a 100% chance; the special draws are never made.
    world = BonusWorld(
        _rules(special=odds),
        _always(0.99),
        (0, 100),
        10,  # type: ignore[arg-type]
        _always(0.0),
    )  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: False)
    assert [b.kind for b in world.bonuses] == ["weapon"]


def test_p11_r07_a_special_draw_on_a_rules_without_special_odds_is_skipped() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10, _always(0.0))  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: True)
    assert [b.kind for b in world.bonuses] == ["weapon"]


def test_gd31_the_special_draw_defaults_to_the_weapon_draw() -> None:
    world = BonusWorld(_rules(), create_rng(3), (0, 100), 10)
    assert world._special_random is world._random


def test_gd31_a_bonus_falls_and_is_removed_below_the_playfield() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10)  # type: ignore[arg-type]
    world.place("weapon", _Point(50, 0))
    world.step(1)
    assert world.bonuses[0].y == -10
    assert world.bonuses[0].age == 1
    world.step(1)
    assert world.bonuses == []


def test_gd31_a_bonus_is_kept_within_the_ships_reach_when_it_drops() -> None:
    world = BonusWorld(_rules(), _always(0.0), (20, 80), 10)  # type: ignore[arg-type]
    world.place("life", _Point(5, 30))
    world.place("bomb", _Point(99, 30))
    assert [b.x for b in world.bonuses] == [20, 80]
    assert [b.kind for b in world.bonuses] == ["life", "bomb"]
    assert [b.id for b in world.bonuses] == [1, 2]


def test_gd31_the_ship_picks_up_the_bonuses_it_touches() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10)  # type: ignore[arg-type]
    world.place("weapon", _Point(50, 50))
    world.place("life", _Point(90, 50))
    world.step(0.1, _Point(52, 50))
    assert [b.kind for b in world.picked] == ["weapon"]
    assert [b.kind for b in world.bonuses] == ["life"]
    assert world.collected == 1
    world.step(0.1)
    assert world.picked == []
    assert world.collected == 1


def test_gd31_without_a_ship_nothing_is_picked_up() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10)  # type: ignore[arg-type]
    world.place("weapon", _Point(50, 50))
    world.step(0.0, None)
    assert world.picked == []
    assert len(world.bonuses) == 1


def test_gd31_clearing_the_world_removes_the_bonuses_and_pickups() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10)  # type: ignore[arg-type]
    world.place("weapon", _Point(50, 50))
    world.step(0, _Point(50, 50))
    world.clear()
    assert world.bonuses == []
    assert world.picked == []
