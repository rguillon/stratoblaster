"""Unit tests of `src/app/game_play_state.py`."""
# (the snapshots of the test API, P12-R12).

from types import SimpleNamespace

from app.game_play_state import game_play_sky, level_state


def run(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "track": SimpleNamespace(time=12.5, duration=90.0, speed_factor=1.5),
        "enemies": SimpleNamespace(
            enemies=[1, 2, 3],
            kills=4,
            spawned=7,
            shots=SimpleNamespace(count=5, bullets=[]),
        ),
        "waves": SimpleNamespace(triggered=2),
        "ship": SimpleNamespace(x=10.0, y=20.0),
        "shots": SimpleNamespace(firing=True, active_count=3, level=2),
        "bonuses": SimpleNamespace(bonuses=[SimpleNamespace(kind="shield")], dropped=2),
        "score": 1500,
        "bombs": SimpleNamespace(count=1),
        "hull": SimpleNamespace(health=6.0, lives=2, invincible=0.5),
        "fights": SimpleNamespace(boss=None, rank=None, defeated=["mini-1"]),
        "result": SimpleNamespace(level_id="1-2"),
        "phase": "playing",
        "checkpoint": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_p12_r12_the_level_snapshot_names_the_level_and_its_phase() -> None:
    state = level_state(run(), 2.0, 10.0)
    assert state["levelId"] == "1-2"
    assert state["phase"] == "playing"
    assert state["time"] == 12.5
    assert state["duration"] == 90.0
    assert state["timeScale"] == 2.0


def test_p12_r12_the_snapshot_counts_the_enemies_shots_and_bonuses() -> None:
    state = level_state(run(), 1.0, 10.0)
    assert state["enemies"] == 3
    assert state["destroyed"] == 4
    assert state["spawned"] == 7
    assert state["enemyShots"] == 5
    assert state["bonuses"] == 1
    assert state["bonusKinds"] == ["shield"]
    assert state["bonusesDropped"] == 2
    assert state["wavesTriggered"] == 2


def test_p12_r12_the_snapshot_gives_the_ship_the_weapons_and_the_score() -> None:
    state = level_state(run(), 1.0, 10.0)
    assert state["player"] == {"x": 10.0, "y": 20.0}
    assert state["firing"] is True
    assert state["shots"] == 3
    assert state["weaponLevel"] == 2
    assert state["score"] == 1500
    assert state["bombs"] == 1
    assert state["health"] == 6.0
    assert state["lives"] == 2
    assert state["invincible"] == 0.5
    assert state["bossesDefeated"] == 1
    assert state["groundSpeed"] == 1.5
    assert state["checkpoint"] is False


def test_p12_r12_a_level_without_a_hull_or_bonuses_reads_as_none_of_them() -> None:
    state = level_state(run(hull=None, bonuses=None, bombs=None), 1.0, 10.0)
    assert state["health"] == 10.0
    assert state["lives"] == 0
    assert state["invincible"] == 0
    assert state["bonuses"] == 0
    assert state["bonusKinds"] == []
    assert state["bombs"] == 0


def test_p07_r02_the_snapshot_describes_the_boss_being_fought() -> None:
    boss = SimpleNamespace(
        name="Warden",
        state="fighting",
        stage=2,
        parts=[SimpleNamespace(destroyed=True), SimpleNamespace(destroyed=False)],
        remaining_health=40.0,
        full_health=100.0,
    )
    state = level_state(run(fights=SimpleNamespace(boss=boss, rank="mini", defeated=[])), 1.0, 1)
    assert state["boss"] == {
        "name": "Warden",
        "rank": "mini",
        "state": "fighting",
        "stage": 2,
        "partsLeft": 1,
        "parts": 2,
        "health": 40.0,
        "fullHealth": 100.0,
    }


def test_p10_r05_the_sky_snapshot_keeps_the_weather_and_the_look() -> None:
    sky = game_play_sky(
        "rain", "snow", 300, 0.5, 1.0, 0.2, 0.3, 0.4, 0.9, 800.0, False, 0.0, 2, "laser"
    )
    assert sky["weather"] == "rain"
    assert sky["secondWeather"] == "snow"
    assert sky["weatherParticles"] == 300
    assert sky["fogEnd"] == 800.0
    assert sky["plumes"] == 2
    assert sky["shotStyle"] == "laser"
    assert sky["lava"] is False
