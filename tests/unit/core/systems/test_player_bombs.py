"""Tests of the player's bombs (GD-32, P11-R05), `core/systems/player_bombs.py`."""

from core.systems.player_bombs import ActiveBomb, BombRules, PlayerBombs


def _rules(max_bombs: float | None = 5) -> BombRules:
    return BombRules(start=3, damage=50, seconds=2, max_bombs=max_bombs)


def test_gd32_a_new_run_starts_with_the_rule_bombs() -> None:
    bombs = PlayerBombs(_rules())
    assert bombs.count == 3
    assert bombs.active is None
    assert bombs.fired == 0


def test_gd32_bombs_kept_from_the_level_before_override_the_start() -> None:
    assert PlayerBombs(_rules(), count=1).count == 1


def test_p11_r05_a_press_sets_one_bomb_off_and_uses_one_up() -> None:
    bombs = PlayerBombs(_rules())
    assert bombs.fire(10, 20) is True
    assert bombs.count == 2
    assert bombs.fired == 1
    active = bombs.active
    assert isinstance(active, ActiveBomb)
    assert (active.x, active.y, active.age, active.seconds) == (10, 20, 0, 2)


def test_p11_r05_no_bomb_goes_off_while_one_is_active() -> None:
    bombs = PlayerBombs(_rules())
    bombs.fire(0, 0)
    assert bombs.fire(0, 0) is False
    assert bombs.count == 2


def test_p11_r05_no_bomb_goes_off_with_none_left() -> None:
    bombs = PlayerBombs(_rules(), count=0)
    assert bombs.fire(0, 0) is False
    assert bombs.fired == 0


def test_p11_r05_a_bomb_goes_off_for_its_seconds_then_another_can_fire() -> None:
    bombs = PlayerBombs(_rules())
    bombs.fire(0, 0)
    bombs.step(1)
    assert bombs.active is not None
    assert bombs.active.age == 1
    bombs.step(1)
    assert bombs.active is None
    assert bombs.fire(0, 0) is True


def test_p11_r05_stepping_with_no_bomb_does_nothing() -> None:
    bombs = PlayerBombs(_rules())
    bombs.step(5)
    assert bombs.active is None


def test_p11_r07_a_bomb_bonus_adds_one_up_to_the_most() -> None:
    bombs = PlayerBombs(_rules(max_bombs=4))
    assert bombs.add() is True
    assert bombs.count == 4
    assert bombs.add() is False
    assert bombs.count == 4


def test_p11_r07_a_bomb_bonus_has_no_limit_without_a_most() -> None:
    bombs = PlayerBombs(_rules(max_bombs=None))
    for _ in range(10):
        assert bombs.add() is True
    assert bombs.count == 13


def test_p11_r05_a_lost_life_tops_the_bombs_back_up_to_the_start() -> None:
    bombs = PlayerBombs(_rules(), count=0)
    bombs.refill()
    assert bombs.count == 3


def test_p11_r05_a_lost_life_keeps_more_bombs_than_the_start() -> None:
    bombs = PlayerBombs(_rules(), count=5)
    bombs.refill()
    assert bombs.count == 5
