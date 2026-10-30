"""Unit tests of `src/audio/level_cues.py`."""

from types import SimpleNamespace
from typing import Any

from audio.level_cues import LevelCues


def make_run(**overrides: Any) -> SimpleNamespace:
    """A `LevelRun` stand-in with the fields the cues read, all quiet at the start."""
    run = SimpleNamespace(
        shots=SimpleNamespace(volleys=0, weapon=SimpleNamespace(id="blaster"), beam=[], level=1),
        ship=SimpleNamespace(x=100.0),
        enemies=SimpleNamespace(
            shots=SimpleNamespace(bullets=[], missiles=[], lasers=[]),
            broken_parts=[],
        ),
        impacts=[],
        blasts=[],
        hits=[],
        bonuses=SimpleNamespace(picked=[]),
        hull=SimpleNamespace(lives=3),
        bombs=SimpleNamespace(fired=0),
        fights=SimpleNamespace(defeated=[]),
    )
    for key, value in overrides.items():
        setattr(run, key, value)
    return run


def names(cues: list) -> list[str]:
    return [cue.cue for cue in cues]


def test_p12_r09_the_first_step_only_takes_the_starting_state() -> None:
    cues = LevelCues(40)
    run = make_run()
    run.shots.volleys = 1
    assert cues.observe(run) == []
    run.shots.volleys = 2
    assert names(cues.observe(run)) == ["fire:blaster"]


def test_p12_r09_a_volley_is_one_cue_at_the_ship() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.shots.volleys = 1
    found = cues.observe(run)
    assert names(found) == ["fire:blaster"]
    assert found[0].x == 100.0


def test_p12_r09_a_beam_sounds_when_it_starts_and_not_while_it_goes_on() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.shots.beam = [object()]
    assert names(cues.observe(run)) == ["beam-start:blaster"]
    assert cues.beam == "blaster"
    assert cues.observe(run) == []
    run.shots.beam = []
    cues.observe(run)
    assert cues.beam is None


def test_p12_r09_a_new_enemy_bullet_sounds_once() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    bullet = SimpleNamespace(alive=True, x=50.0)
    run.enemies.shots.bullets.append(bullet)
    assert names(cues.observe(run)) == ["enemy-bullet"]
    assert cues.observe(run) == []


def test_p12_r09_a_dead_bullet_is_not_tracked() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.enemies.shots.bullets.append(SimpleNamespace(alive=False, x=50.0))
    assert cues.observe(run) == []


def test_p12_r09_a_new_enemy_missile_sounds_by_its_id() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.enemies.shots.missiles.append(SimpleNamespace(alive=True, id=1, x=5.0))
    assert names(cues.observe(run)) == ["enemy-missile"]
    assert cues.observe(run) == []
    run.enemies.shots.missiles.append(SimpleNamespace(alive=True, id=2, x=5.0))
    assert names(cues.observe(run)) == ["enemy-missile"]


def test_p12_r09_a_laser_warns_then_fires_once_when_its_phase_changes() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    laser = SimpleNamespace(phase="warning", x=30.0)
    run.enemies.shots.lasers.append(laser)
    assert names(cues.observe(run)) == ["laser-warning"]
    laser.phase = "firing"
    assert names(cues.observe(run)) == ["laser-fire"]
    assert cues.observe(run) == []


def test_p12_r09_impacts_blasts_and_broken_parts_each_have_a_cue() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.impacts = [SimpleNamespace(blocked=False, x=1.0), SimpleNamespace(blocked=True, x=2.0)]
    run.blasts = [
        SimpleNamespace(kind="enemy", radius=50.0, x=3.0),
        SimpleNamespace(kind="enemy", radius=10.0, x=4.0),
    ]
    run.enemies.broken_parts = [SimpleNamespace(x=5.0)]
    found = names(cues.observe(run))
    assert "hit" in found
    assert "hit-blocked" in found
    assert "blast-large" in found
    assert "blast-small" in found
    assert "part-destroyed" in found


def test_p12_r09_one_cue_of_a_kind_per_step() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.impacts = [SimpleNamespace(blocked=False, x=1.0)] * 3
    assert names(cues.observe(run)).count("hit") == 1


def test_p12_r09_a_player_hit_or_a_lost_life_or_an_ignored_hit() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.hits = [
        SimpleNamespace(event="hit", x=1.0),
        SimpleNamespace(event="ignored", x=2.0),
    ]
    assert names(cues.observe(run)) == ["player-hit"]
    run.hits = [SimpleNamespace(event="dead", x=1.0)]
    assert names(cues.observe(run)) == ["life-lost"]


def test_p12_r09_picked_bonuses_sound_by_their_kind() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.bonuses = SimpleNamespace(picked=[SimpleNamespace(kind="shield", x=9.0)])
    assert names(cues.observe(run)) == ["bonus:shield"]


def test_p12_r09_no_bonus_system_means_nothing_picked() -> None:
    cues = LevelCues(40)
    run = make_run(bonuses=None)
    cues.observe(run)
    assert cues.observe(run) == []


def test_p12_r09_a_weapon_switch_is_reported_over_a_level_up() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.shots.weapon = SimpleNamespace(id="spread")
    run.shots.level = 2
    assert names(cues.observe(run)) == ["weapon-switch"]


def test_p12_r09_a_weapon_level_up_on_the_same_weapon() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.shots.level = 2
    assert names(cues.observe(run)) == ["weapon-up"]


def test_p12_r09_an_extra_life_a_bomb_and_a_boss_kill() -> None:
    cues = LevelCues(40)
    run = make_run()
    cues.observe(run)
    run.hull = SimpleNamespace(lives=4)
    run.bombs = SimpleNamespace(fired=1)
    run.fights = SimpleNamespace(defeated=["boss-1"])
    assert names(cues.observe(run)) == ["extra-life", "bomb", "boss-destroyed"]


def test_p12_r09_a_level_without_a_hull_or_bombs_counts_zero() -> None:
    cues = LevelCues(40)
    run = make_run(hull=None, bombs=None)
    cues.observe(run)
    assert cues.observe(run) == []
