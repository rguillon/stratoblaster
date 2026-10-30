"""Unit tests of `src/game/sim/enemies/hornet.py`."""

import pytest
from helpers.enemy_steps import run, run_until
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.hornet import Hornet, HornetOptions, hornet_options

CFG = ENEMY_CONFIG.hornet


def _options(stop_y: float | None = 300.0, pause: float = 1.0) -> HornetOptions:
    return HornetOptions(CFG.stats, stop_y, 200.0, 50.0, pause, 100.0, 400.0)


def test_p05_r02_hornet_options_read_the_config_entry_and_its_stop_height() -> None:
    options = hornet_options(CFG, 250.0)
    assert options.stop_y == 250.0
    assert options.pause == CFG.pause
    assert options.dive_max_speed == CFG.diveMaxSpeed
    assert options.entry_brake == (CFG.entryBrake or 1.7976931348623157e308)


def test_p05_r02_a_hornet_without_a_stop_height_starts_with_its_pause() -> None:
    hornet = Hornet(100, 300, _options(stop_y=None))
    assert hornet.state == "aim"


def test_p05_r02_a_hornet_brakes_into_its_stop_height_then_aims() -> None:
    hornet = Hornet(100, 500, _options(stop_y=300.0))
    assert hornet.state == "enter"
    run_until(hornet, FakeContext(), lambda: hornet.state != "enter", limit=10.0)
    assert hornet.state == "aim"
    assert hornet.y == pytest.approx(300.0)


def test_p05_r02_a_hornet_dives_at_the_player_after_its_pause() -> None:
    ctx = FakeContext()
    hornet = Hornet(100, 300, _options(stop_y=None, pause=0.5))
    run(hornet, ctx, 0.6)
    assert hornet.state == "dive"
    assert hornet.dive_heading is not None
    before = hornet.y
    run(hornet, ctx, 0.5)
    assert hornet.y < before


def test_p05_r02_a_hornet_does_not_shoot() -> None:
    ctx = FakeContext()
    run(Hornet(100, 300, _options(stop_y=None, pause=0.2)), ctx, 3.0)
    assert ctx.bullets == [] and ctx.missiles == []
