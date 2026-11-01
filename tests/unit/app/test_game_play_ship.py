"""Unit tests of the ship's bank and blink in `src/app/game_play.py` (GAME-SHIP-05,
GFX-SHIP-08, GAME-LIFE-07). The level and its ship are not built: a `GamePlay` with only the
fields these read."""

import math
from types import SimpleNamespace

import pytest

from app.game_play import GamePlay
from config.game_play import GAME_PLAY_CONFIG as CFG


def _play(speed: float = 300.0, roll: float = 0.0, phase: str = "playing", hull=None) -> GamePlay:
    play = GamePlay.__new__(GamePlay)
    play._speed = speed
    play._roll = roll
    play.run = SimpleNamespace(phase=phase, hull=hull)
    return play


def _hull(invincible: float) -> SimpleNamespace:
    return SimpleNamespace(invincible=invincible)


def test_game_ship_05_the_ship_banks_at_full_sideways_speed_up_to_max_deg() -> None:
    """Flying right, the ship dips to the right's negative bank; flying left, the other way."""
    max_bank = math.radians(CFG.roll.max_deg)
    play = _play(speed=300.0)
    assert play._bank(300.0, 10.0) == pytest.approx(-max_bank)
    assert play._bank(-300.0, 10.0) == pytest.approx(max_bank)


def test_game_ship_05_the_bank_is_proportional_to_the_sideways_speed() -> None:
    max_bank = math.radians(CFG.roll.max_deg)
    play = _play(speed=300.0)
    assert play._bank(150.0, 10.0) == pytest.approx(-max_bank / 2)


def test_gfx_ship_08_the_bank_eases_towards_its_target_and_back_to_level() -> None:
    """Each step closes a share `ease_per_sec * dt` of the gap (capped at the whole gap); with no
    sideways speed the bank goes back to level."""
    max_bank = math.radians(CFG.roll.max_deg)
    play = _play(speed=300.0)
    step = 0.05
    share = min(1, CFG.roll.ease_per_sec * step)
    banked = play._bank(300.0, step)
    assert banked == pytest.approx(-max_bank * share)
    settled = banked
    for _ in range(200):
        settled = play._bank(0.0, step)
    assert settled == pytest.approx(0.0, abs=1e-9)


def test_game_life_07_the_ship_is_hidden_once_the_game_is_over() -> None:
    assert _play(phase="over", hull=_hull(1.0))._ship_shown() is False


def test_game_life_07_the_ship_shows_when_it_is_not_invincible() -> None:
    assert _play(hull=_hull(0.0))._ship_shown() is True
    assert _play(hull=None)._ship_shown() is True


def test_game_life_07_the_ship_blinks_every_0_05_seconds_while_invincible() -> None:
    """Blinking at `blink_hz` (10): shown and hidden alternately every 0.05 s over the 2 s of
    invincibility, sampled in the middle of each 0.05 s step."""
    step = 1 / (2 * CFG.damage.blink_hz)
    assert step == pytest.approx(0.05)
    shown = []
    for i in range(40):
        invincible = 2.0 - (i + 0.5) * step
        shown.append(_play(hull=_hull(invincible))._ship_shown())
    assert all(a != b for a, b in zip(shown, shown[1:], strict=False))
    assert shown[0] is False
