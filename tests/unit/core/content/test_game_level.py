"""A level the player can fly (`core.content.game_level`, P06)."""

from core.content.game_level import GameLevel, find_game_level


def test_a_game_level_keeps_its_parts_and_defaults_to_no_bosses() -> None:
    scenery, waves, difficulty = object(), object(), object()
    level = GameLevel("1-1", scenery, waves, difficulty)  # type: ignore[arg-type]
    assert level.id == "1-1"
    assert level.scenery is scenery
    assert level.waves is waves
    assert level.difficulty is difficulty
    assert level.bosses is None
    assert level.runout is None


def test_p06_r03_a_game_level_keeps_its_bosses_and_runout() -> None:
    bosses = [object()]
    level = GameLevel("1-2", object(), object(), object(), bosses, 4.0)  # type: ignore[arg-type]
    assert level.bosses is bosses
    assert level.runout == 4.0


def test_find_game_level_returns_the_level_with_the_id() -> None:
    first = GameLevel("1-1", object(), object(), object())  # type: ignore[arg-type]
    second = GameLevel("1-2", object(), object(), object())  # type: ignore[arg-type]
    assert find_game_level([first, second], "1-2") is second


def test_find_game_level_is_none_when_there_is_no_such_level() -> None:
    level = GameLevel("1-1", object(), object(), object())  # type: ignore[arg-type]
    assert find_game_level([level], "9-9") is None
    assert find_game_level([], "1-1") is None
