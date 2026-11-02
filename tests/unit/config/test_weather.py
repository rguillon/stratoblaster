# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/config/weather.py`."""

import itertools

from config.weather import LIGHTNING
from core.scenery.lightning import LightningSchedule


def test_gfx_weather_10_strikes_come_every_gap_seconds_at_least() -> None:
    schedule = LightningSchedule(11)
    strikes = schedule.strikes_before(300)
    starts = [s.flashes[0] for s in strikes]
    assert starts == sorted(starts)
    gaps = [b - a for a, b in itertools.pairwise(starts)]
    assert gaps
    assert all(LIGHTNING.gap[0] - 1e-9 <= g <= LIGHTNING.gap[1] + 1e-9 for g in gaps)
