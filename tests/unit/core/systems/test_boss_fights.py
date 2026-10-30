"""Tests of the boss fights of a level (P07-R03, R06), `core/systems/boss_fights.py`."""

import subprocess
import sys
from pathlib import Path

import pytest
import transcrypt

from core.scenery.scroll_track import ScrollTrack
from core.systems.boss_fights import (
    SLACK,
    BossBar,
    BossFightHooks,
    BossFightRules,
    BossFights,
    LevelBoss,
    validate_level_bosses,
)


class _Part:
    def __init__(self, max_health: float) -> None:
        self.max_health = max_health


class _Boss:
    """A boss as the fights see it: its speed on the ground, its health and whether it is gone."""

    def __init__(self, parts: list[float], ground_speed: float = 0.5, core: float = 10) -> None:
        self.name = "Hulk"
        self.ground_speed = ground_speed
        self.parts = [_Part(p) for p in parts]
        self.core = core
        self.remaining_health = core + sum(parts)
        self.full_health = core + sum(parts)
        self.gone = False


class _Kind:
    def __init__(self, id: str, boss: _Boss) -> None:
        self.id = id
        self.name = id
        self.boss = boss
        self.areas: list[object] = []

    def spawn(self, area: object) -> _Boss:
        self.areas.append(area)
        return self.boss


def _seek(track: ScrollTrack, progress: float) -> None:
    """Puts the level at `progress` world units (`ScrollTrack.seek` takes seconds)."""
    track.seek(progress / track.speed)


def _fights(
    bosses: list[LevelBoss],
    boss: _Boss | None = None,
    rules: BossFightRules | None = None,
) -> tuple[BossFights, ScrollTrack, _Kind, list[_Boss]]:
    fight_boss = boss if boss is not None else _Boss([10])
    kind = _Kind("hulk", fight_boss)
    added: list[_Boss] = []
    hooks = BossFightHooks(lambda: "AREA", added.append)  # type: ignore[arg-type]
    rules = rules if rules is not None else BossFightRules(0, 2)
    track = ScrollTrack(10, 1000)
    fights = BossFights(bosses, [kind], rules, hooks)  # type: ignore[list-item]
    return fights, track, kind, added


def test_p07_r06_a_boss_kind_must_be_one_of_the_kinds_of_the_game() -> None:
    with pytest.raises(ValueError, match='Unknown boss kind "ghost"'):
        validate_level_bosses([LevelBoss("ghost", "mini", 10)], ["hulk"])


def test_p07_r06_a_boss_must_come_at_a_non_negative_distance() -> None:
    with pytest.raises(ValueError, match="bad distance"):
        validate_level_bosses([LevelBoss("hulk", "mini", -1)], ["hulk"])
    validate_level_bosses([LevelBoss("hulk", "mini", 0)], ["hulk"])


def test_p07_r06_creating_the_fights_validates_the_bosses() -> None:
    with pytest.raises(ValueError):
        _fights([LevelBoss("ghost", "final", 10)])


def test_p07_r06_a_boss_comes_in_once_the_level_gets_to_it() -> None:
    fights, track, kind, added = _fights([LevelBoss("hulk", "final", 50)])
    _seek(track, 40)
    fights.step(0.1, track)
    assert fights.active is False
    assert added == []
    _seek(track, 50)
    fights.step(0.1, track)
    assert fights.active is True
    assert added == [kind.boss]
    assert kind.areas == ["AREA"]
    assert fights.boss is kind.boss
    assert fights.rank == "final"
    assert fights.passed == 1


def test_p07_r06_a_boss_starts_within_the_slack_of_its_distance() -> None:
    fights, track, _, _ = _fights([LevelBoss("hulk", "mini", 50)])
    _seek(track, 50 - SLACK / 2)
    fights.step(0.1, track)
    assert fights.active is True


def test_p07_r03_the_track_is_held_and_the_ground_slows_to_the_boss_speed() -> None:
    boss = _Boss([10], ground_speed=0.25)
    fights, track, _, _ = _fights(
        [LevelBoss("hulk", "mini", 0)], boss=boss, rules=BossFightRules(2, 1)
    )
    fights.step(0.1, track)
    assert track.held is True
    assert track.speed_factor == 1
    track.step(2)
    assert track.speed_factor == pytest.approx(0.25)


def test_p07_r03_with_no_ease_time_the_ground_changes_speed_at_once() -> None:
    boss = _Boss([10], ground_speed=0.25)
    fights, track, _, _ = _fights([LevelBoss("hulk", "mini", 0)], boss=boss)
    fights.step(0.1, track)
    assert track.speed_factor == 0.25


def test_p07_r06_no_other_boss_comes_in_while_one_is_fought() -> None:
    boss = _Boss([10])
    fights, track, kind, added = _fights(
        [LevelBoss("hulk", "mini", 10), LevelBoss("hulk", "final", 20)], boss=boss
    )
    _seek(track, 30)
    fights.step(0.5, track)
    assert added == [boss]
    fights.step(0.5, track)
    assert added == [boss]
    assert fights.passed == 1


def test_p07_r06_the_next_boss_comes_once_the_fight_is_over() -> None:
    first = _Boss([10])
    second = _Boss([10])
    fights, track, kind, added = _fights(
        [LevelBoss("hulk", "mini", 10), LevelBoss("hulk", "final", 20)], boss=first
    )
    _seek(track, 30)
    fights.step(0.5, track)
    first.gone = True
    fights.step(0.5, track)
    assert fights.active is False
    kind.boss = second
    fights.step(0.5, track)
    assert added == [first, second]
    assert fights.passed == 2


def test_p07_r06_a_boss_defeated_is_recorded_and_the_ground_goes_back() -> None:
    boss = _Boss([10], ground_speed=0.25)
    fights, track, _, _ = _fights(
        [LevelBoss("hulk", "final", 0)], boss=boss, rules=BossFightRules(0, 1)
    )
    fights.step(0.1, track)
    assert fights.final_defeated is False
    boss.gone = True
    fights.step(0.1, track)
    assert fights.active is False
    assert fights.just_defeated is not None
    assert fights.just_defeated.rank == "final"
    assert fights.defeated == [fights.just_defeated]
    assert fights.final_defeated is True
    assert track.held is False
    assert track.speed_factor == 1
    fights.step(0.1, track)
    assert fights.just_defeated is None


def test_p07_r06_the_level_knows_whether_it_has_a_final_boss() -> None:
    fights, _, _, _ = _fights([LevelBoss("hulk", "mini", 5)])
    assert fights.has_final is False
    assert fights.bosses[0].rank == "mini"
    fights, _, _, _ = _fights([LevelBoss("hulk", "mini", 5), LevelBoss("hulk", "final", 9)])
    assert fights.has_final is True


def test_p07_r06_bosses_come_in_by_distance_whatever_the_order_given() -> None:
    fights, _, _, _ = _fights([LevelBoss("hulk", "final", 9), LevelBoss("hulk", "mini", 5)])
    assert [b.rank for b in fights.bosses] == ["mini", "final"]


def test_p07_r02_the_health_bar_fills_as_the_boss_arrives() -> None:
    boss = _Boss([10, 10], core=10)
    fights, track, _, _ = _fights([LevelBoss("hulk", "mini", 0)], boss=boss)
    assert fights.bar is None
    fights.step(0.1, track)
    fights.step(1.0, track)
    bar = fights.bar
    assert isinstance(bar, BossBar)
    assert bar.name == "Hulk"
    assert bar.rank == "mini"
    assert bar.health == 30
    assert bar.full_health == 30
    # Halfway through its 2 seconds of filling up.
    assert bar.share == pytest.approx(0.5)
    fights.step(5.0, track)
    assert fights.bar.share == pytest.approx(1.0)


def test_p07_r02_the_health_bar_notches_mark_the_end_of_each_part() -> None:
    boss = _Boss([10, 5], core=5)
    fights, track, _, _ = _fights([LevelBoss("hulk", "mini", 0)], boss=boss)
    fights.step(0.1, track)
    assert fights.bar.notches == pytest.approx([10 / 20, 15 / 20])


def test_p07_r06_skipping_drops_the_fight_and_restores_the_ground() -> None:
    boss = _Boss([10], ground_speed=0.25)
    fights, track, _, _ = _fights(
        [LevelBoss("hulk", "mini", 10), LevelBoss("hulk", "final", 50)],
        boss=boss,
        rules=BossFightRules(0, 1),
    )
    _seek(track, 10)
    fights.step(0.1, track)
    assert fights.active is True
    fights.skip_to(track)
    assert fights.active is False
    assert track.held is False
    assert track.speed_factor == 1
    assert fights.boss is None
    assert fights.rank is None
    # The level is at the mini boss's distance, so that boss is the next one: it comes again.
    assert fights.passed == 0
    fights.step(0.1, track)
    assert fights.rank == "mini"


def test_p06_r09_skipping_to_a_distance_makes_the_next_boss_the_first_one_after_it() -> None:
    fights, track, _, _ = _fights([LevelBoss("hulk", "mini", 10), LevelBoss("hulk", "final", 50)])
    _seek(track, 20)
    fights.skip_to(track)
    assert fights.passed == 1
    _seek(track, 60)
    fights.step(0.1, track)
    assert fights.rank == "final"


def test_p06_r09_skipping_past_every_boss_leaves_none_to_come() -> None:
    fights, track, _, added = _fights([LevelBoss("hulk", "mini", 10)])
    _seek(track, 100)
    fights.skip_to(track)
    assert fights.passed == 1
    fights.step(0.1, track)
    assert added == []


def test_p06_r09_skipping_with_a_count_passes_that_many_bosses() -> None:
    fights, track, _, _ = _fights([LevelBoss("hulk", "mini", 10), LevelBoss("hulk", "final", 50)])
    _seek(track, 0)
    fights.skip_to(track, passed=1)
    assert fights.passed == 1
    _seek(track, 60)
    fights.step(0.1, track)
    assert fights.rank == "final"


def test_boss_modules_import_in_a_clean_interpreter() -> None:
    """The boss modules import each other only for annotations: a clean interpreter can import
    the systems that use them first."""
    repo = Path(__file__).resolve().parents[4]
    stubs = Path(next(iter(transcrypt.__path__))).resolve() / "modules"
    code = (
        f"import sys; sys.path.insert(0, {str(repo / 'src')!r}); "
        f"sys.path.append({str(stubs)!r}); import core.systems.boss_fights"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
