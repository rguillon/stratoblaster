"""Unit tests of `src/app/game_play_hud.py`."""
# (P07-R02, P11-R02, R06).

from types import SimpleNamespace

from helpers.dom import FakeDocument

from app.game_play_hud import (
    LevelOverlaysOptions,
    boss_bar_frame,
    create_hud,
    create_level_overlays,
    hud_frame,
)
from ui.game_hud import GameHud


def texts() -> SimpleNamespace:
    return SimpleNamespace(hudMiniBoss="MINI BOSS", hudBoss="BOSS")


def run(**overrides: object) -> SimpleNamespace:
    weapon = SimpleNamespace(name="Guns", levels=[1, 2, 3])
    values: dict[str, object] = {
        "fights": SimpleNamespace(bar=None),
        "shots": SimpleNamespace(weapon=weapon, level=2),
        "track": SimpleNamespace(progress=30.0, length_=120.0),
        "hull": SimpleNamespace(health=4.0, lives=2),
        "bombs": SimpleNamespace(count=3),
        "score": 500,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_p07_r02_no_boss_fought_means_no_boss_bar() -> None:
    assert boss_bar_frame(run(), texts()) is None


def test_p07_r02_the_boss_bar_names_the_boss_and_its_rank() -> None:
    bar = SimpleNamespace(name="Warden", rank="mini", share=0.5, notches=[0.25])
    frame = boss_bar_frame(run(fights=SimpleNamespace(bar=bar)), texts())
    assert frame is not None
    assert (frame.name, frame.rank, frame.share, frame.notches) == (
        "Warden",
        "MINI BOSS",
        0.5,
        [0.25],
    )
    bar.rank = "final"
    assert boss_bar_frame(run(fights=SimpleNamespace(bar=bar)), texts()).rank == "BOSS"


def test_p11_r02_the_hud_frame_shows_health_lives_weapon_and_progress() -> None:
    frame = hud_frame(run(), 10, texts())
    assert (frame.health, frame.max_health, frame.lives) == (4.0, 10, 2)
    assert (frame.weapon, frame.weapon_level, frame.weapon_levels) == ("Guns", 2, 3)
    assert frame.progress == 0.25
    assert frame.score == 500
    assert frame.bombs == 3
    assert frame.boss is None


def test_p11_r02_the_high_score_is_at_least_the_score_of_the_run() -> None:
    assert hud_frame(run(), 10, texts(), high_score=100).high_score == 500
    assert hud_frame(run(), 10, texts(), high_score=900).high_score == 900


def test_p11_r02_without_a_hull_the_max_health_stands_in() -> None:
    frame = hud_frame(run(hull=None), 7, texts())
    assert (frame.health, frame.lives) == (7, 0)


def test_p11_r06_without_bombs_no_bomb_count_is_shown() -> None:
    assert hud_frame(run(bombs=None), 10, texts()).bombs is None


def test_p11_r02_a_level_without_a_length_is_complete_on_the_bar() -> None:
    frame = hud_frame(run(track=SimpleNamespace(progress=0, length_=0)), 10, texts())
    assert frame.progress == 1


def hud_texts() -> SimpleNamespace:
    return SimpleNamespace(
        hudHealth="HEALTH",
        hudWeapon=lambda name, level, levels: f"{name} {level}/{levels}",
        hudLives=lambda lives: f"x{lives}",
        hudBombs=lambda bombs: f"B{bombs}",
        hudScore=lambda score: f"SCORE {score}",
        hudHighScore=lambda score: f"HI {score}",
        hudBomb=lambda bombs: f"BOMB {bombs}",
        hudMiniBoss="MINI BOSS",
        hudBoss="BOSS",
    )


def test_p11_r02_the_level_hud_is_built_into_its_parent_with_the_ship_and_texts() -> None:

    doc = FakeDocument()
    parent = doc.createElement("div")
    hud = create_hud(doc, parent, "Ship A", hud_texts(), None)
    assert isinstance(hud, GameHud)
    assert hud.root.parentElement is parent
    assert hud.root.querySelector(".hud-ship").textContent == "Ship A"


def test_p13_r01_the_overlays_build_the_hud_and_the_debug_tile_only_in_debug_mode() -> None:

    doc = FakeDocument()
    hud_parent = doc.createElement("div")
    stats_parent = doc.createElement("div")
    hud, stats = create_level_overlays(
        LevelOverlaysOptions(doc, True, stats_parent, hud_parent), "Ship A", hud_texts(), None
    )
    assert hud is not None
    assert stats is not None
    assert stats.root.parentElement is stats_parent
    hud2, stats2 = create_level_overlays(
        LevelOverlaysOptions(doc, False, stats_parent, None), "Ship A", hud_texts(), None
    )
    assert hud2 is None
    assert stats2 is None


def test_d212_the_debug_tile_shows_as_last_chosen_with_its_key() -> None:
    from app.game_play_hud import STATS_SHOWN  # noqa: PLC0415

    doc = FakeDocument()
    parent = doc.createElement("div")
    try:
        STATS_SHOWN.chosen = True
        _, stats = create_level_overlays(
            LevelOverlaysOptions(doc, False, parent, None), "Ship A", hud_texts(), None
        )
        assert stats is not None
        STATS_SHOWN.chosen = False
        _, hidden = create_level_overlays(
            LevelOverlaysOptions(doc, True, parent, None), "Ship A", hud_texts(), None
        )
        assert hidden is None
        _, orphan = create_level_overlays(
            LevelOverlaysOptions(doc, True, None, None), "Ship A", hud_texts(), None
        )
        assert orphan is None
    finally:
        STATS_SHOWN.chosen = None
