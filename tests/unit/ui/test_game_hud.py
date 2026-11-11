# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/ui/game_hud.py`."""

from helpers.dom import FakeDocument, FakeEvent

from ui.boss_bar import BossBarFrame
from ui.game_hud import GameHud, HudFrame, HudSetup, HudTexts, split_lead


def texts() -> HudTexts:
    return HudTexts(
        health="HEALTH",
        lives=lambda lives: f"x{lives}",
        bombs=lambda bombs: f"B{bombs}",
        score=lambda score: f"{score:07d}",
        high_score=lambda score: f"HI {score}",
        bomb=lambda bombs: f"BOMB {bombs}",
    )


def frame(**overrides: object) -> HudFrame:
    values: dict[str, object] = {
        "health": 2.5,
        "max_health": 10,
        "lives": 3,
        "weapon": "Bullet",
        "weapon_level": 1,
        "weapon_levels": 5,
        "progress": 0.5,
        "score": 100,
        "high_score": 50,
        "bombs": 2,
    }
    values.update(overrides)
    return HudFrame(**values)  # type: ignore[arg-type]


def make_hud(on_bomb: object = None) -> tuple[GameHud, FakeDocument]:
    doc = FakeDocument()
    setup = HudSetup("Ship A", texts(), on_bomb)  # type: ignore[arg-type]
    return GameHud(doc, doc.createElement("div"), setup), doc


def test_ui_hud_04_the_hud_shows_the_health_as_a_rounded_up_count_and_a_bar() -> None:
    hud, _ = make_hud()
    hud.update(frame())
    assert hud.root.querySelector(".hud-health-text").textContent == "HEALTH 3 / 10"
    assert hud.root.querySelector(".hud-bar-fill").style.width == "25.0%"


def test_ui_hud_04_the_low_health_warning_shows_under_30_percent() -> None:
    hud, _ = make_hud()
    hud.update(frame(health=2.5))
    bar = hud.root.querySelector(".hud-bar-fill")
    assert bar.classList.contains("low")
    assert hud.root.classList.contains("hud-low")
    hud.update(frame(health=5))
    assert not bar.classList.contains("low")
    assert not hud.root.classList.contains("hud-low")


def test_ui_hud_01_the_weapon_lives_progress_and_score_are_written() -> None:
    """Each readout: UI-HUD-02, UI-HUD-03, UI-HUD-05, UI-HUD-06."""
    hud, _ = make_hud()
    hud.update(frame())
    assert hud.root.querySelector(".hud-weapon-name").textContent == "Bullet"
    assert hud.root.querySelector(".hud-lives").textContent == "x3"
    assert hud.root.querySelector(".hud-progress-fill").style.height == "50.0%"
    assert hud.root.querySelector(".hud-score-lead").textContent == "0000"
    assert hud.root.querySelector(".hud-score-digits").textContent == "100"
    assert hud.root.querySelector(".hud-high-score").textContent == "HI 100"


def test_ui_hud_05_the_padding_zeros_are_split_from_the_digits() -> None:
    assert split_lead("0012340") == ["00", "12340"]
    assert split_lead("0000000") == ["000000", "0"]
    assert split_lead("1234567") == ["", "1234567"]


def test_ui_hud_06_the_weapon_has_one_pip_per_level_lit_up_to_its_level() -> None:
    hud, _ = make_hud()
    hud.update(frame(weapon_level=2, weapon_levels=5))
    pips = hud.root.querySelectorAll(".hud-pip")
    assert [pip.classList.contains("on") for pip in pips] == [True, True, False, False, False]
    hud.update(frame(weapon_level=3, weapon_levels=5))
    pips = hud.root.querySelectorAll(".hud-pip")
    assert sum(pip.classList.contains("on") for pip in pips) == 3


def test_ui_hud_06_unchanged_pips_are_not_rebuilt() -> None:
    hud, _ = make_hud()
    hud.update(frame())
    first = hud.root.querySelector(".hud-pip")
    hud.update(frame(score=200))
    assert hud.root.querySelector(".hud-pip") is first


def test_ui_hud_05_the_high_score_line_is_the_best_of_the_two() -> None:
    hud, _ = make_hud()
    hud.update(frame(score=10, high_score=50))
    assert hud.root.querySelector(".hud-high-score").textContent == "HI 50"


def test_ui_hud_03_the_bombs_left_are_shown_beside_the_lives() -> None:
    hud, _ = make_hud()
    hud.update(frame(bombs=2))
    assert hud.root.querySelector(".hud-bombs").textContent == "B2"
    hud.update(frame(bombs=None))
    assert hud.root.querySelector(".hud-bombs").textContent == ""


def test_ui_hud_10_the_touch_bomb_button_bombs_once_per_tap_and_stops_the_event() -> None:
    fired: list[bool] = []
    hud, _ = make_hud(on_bomb=lambda: fired.append(True))
    hud.update(frame(bombs=2))
    button = hud.root.querySelector(".hud-bomb-button")
    assert button.textContent == "BOMB 2"
    assert not button.classList.contains("empty")
    event = FakeEvent()
    button.fire("pointerdown", event)
    assert fired == [True]
    assert event.stopped is True


def test_ui_hud_10_an_empty_bomb_button_is_marked_empty() -> None:
    hud, _ = make_hud(on_bomb=lambda: None)
    hud.update(frame(bombs=0))
    button = hud.root.querySelector(".hud-bomb-button")
    assert button.classList.contains("empty")
    assert button.textContent == "BOMB 0"


def test_ui_hud_10_without_a_bomb_handler_there_is_no_bomb_button() -> None:
    hud, _ = make_hud()
    hud.update(frame())
    assert hud.root.querySelector(".hud-bomb-button") is None


def test_ui_hud_14_the_boss_bar_follows_the_boss_of_the_frame() -> None:
    hud, _ = make_hud()
    hud.update(frame(boss=BossBarFrame("Warden", "BOSS", 0.4, [])))
    assert hud.root.querySelector(".boss-name").textContent == "Warden"
    hud.update(frame(boss=None))
    assert hud.root.querySelector(".boss-bar").hidden is True


def test_ui_hud_11_the_hud_takes_no_clicks_and_is_hidden_from_assistive_tech() -> None:
    hud, _ = make_hud()
    assert hud.root.getAttribute("aria-hidden") == "true"


def test_ui_hud_11_an_unchanged_frame_does_not_rewrite_the_text() -> None:
    hud, _ = make_hud()
    hud.update(frame())
    lives = hud.root.querySelector(".hud-lives")
    lives.textContent = "edited"
    hud.update(frame())
    assert lives.textContent == "edited"


def test_ui_hud_01_dispose_removes_the_hud() -> None:
    hud, _ = make_hud()
    hud.dispose()
    assert hud.root.parentElement is None


def test_ui_hud_01_the_readouts_are_in_the_corners_of_the_playfield_window() -> None:
    """D-317: no side columns; the readouts sit, panel-less, over the playfield window."""
    hud, _ = make_hud()
    assert [child.className for child in hud.root.children] == [
        "hud-score",
        "hud-stock",
        "hud-progress",
        "hud-health",
        "hud-weapon",
        "boss-bar",
    ]
    assert hud.root.querySelector(".hud-panel") is None
    assert hud.root.querySelector(".hud-ship").textContent == "Ship A"
