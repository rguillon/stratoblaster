"""Unit tests of `src/core/scenery/lightning.py`."""

import pytest
from helpers.sample_level import sample_atmosphere

from config.weather import LightningRules
from core.scenery.lightning import (
    Bolt,
    LightningSchedule,
    Strike,
    _brighter,
    _envelope,
    _max_of,
    flashed,
)


def rules(**overrides: object) -> LightningRules:
    """The engine's lightning, with some values replaced."""
    values: dict[str, object] = {
        "gap": [4, 10],
        "flash": 0.15,
        "rise": 0.03,
        "double_chance": 0,
        "double_after": 0.25,
        "brightness": 2,
        "max_haze": 0.85,
        "bolt_chance": 0,
        "max_per_second": 3,
    }
    values.update(overrides)
    return LightningRules(**values)  # type: ignore[arg-type]


def test_p09_r05_the_same_seed_flashes_at_the_same_times() -> None:
    first = LightningSchedule(11).flashes_between(0, 200)
    second = LightningSchedule(11).flashes_between(0, 200)
    assert first == second
    assert first
    assert LightningSchedule(12).flashes_between(0, 200) != first


def test_p09_r05_flashes_between_are_the_flashes_in_the_range() -> None:
    schedule = LightningSchedule(3)
    everything = schedule.flashes_between(0, 500)
    middle = schedule.flashes_between(100, 200)
    assert middle == [t for t in everything if 100 <= t < 200]
    assert schedule.flashes_between(50, 50) == []


def test_p09_r05_a_strike_can_flash_twice_and_draw_a_bolt() -> None:
    schedule = LightningSchedule(5, rules(double_chance=1, bolt_chance=1))
    strikes = schedule.strikes_before(60)
    assert strikes
    for strike in strikes:
        assert len(strike.flashes) == 2
        assert strike.flashes[1] - strike.flashes[0] == pytest.approx(0.25)
        assert isinstance(strike.bolt, Bolt)
        assert 0 <= strike.bolt.x < 1
        assert 0 <= strike.bolt.z < 1


def test_p09_r05_strikes_without_bolts_or_doubles() -> None:
    strikes = LightningSchedule(5, rules()).strikes_before(60)
    assert strikes
    assert all(len(s.flashes) == 1 and s.bolt is None for s in strikes)


def test_strike_at_finds_the_strike_lit_at_a_time() -> None:
    schedule = LightningSchedule(5, rules(double_chance=1))
    first = schedule.strikes_before(100)[0]
    start = first.flashes[0]
    assert schedule.strike_at(start + 0.01) is first
    assert schedule.strike_at(start - 0.01) is None
    assert schedule.strike_at(-1) is None


def test_strike_at_skips_a_strike_without_flashes() -> None:
    schedule = LightningSchedule(5, rules())
    lit = schedule.strikes_before(100)[0]
    schedule._strikes.append(Strike([], None))
    assert schedule.strike_at(lit.flashes[0] + 0.01) is lit
    assert schedule.strike_at(1000) is None


def test_flash_at_rises_to_full_and_fades_to_nothing() -> None:
    schedule = LightningSchedule(5, rules(flash=1.0, rise=0.2))
    start = schedule.strikes_before(100)[0].flashes[0]
    assert schedule.flash_at(start - 0.5) == 0
    assert schedule.flash_at(start + 0.2) == pytest.approx(1)
    assert 0 < schedule.flash_at(start + 0.6) < 1
    assert schedule.flash_at(start + 1.5) == 0


def test_envelope_rises_then_fades() -> None:
    assert _envelope(-0.1, 0.1, 1) == 0
    assert _envelope(1, 0.1, 1) == 0
    assert _envelope(0.05, 0.1, 1) == pytest.approx(0.5)
    assert _envelope(0.1, 0.1, 1) == pytest.approx(1)
    assert _envelope(0.55, 0.1, 1) == pytest.approx(0.25)


def test_max_of_is_javascripts_math_max() -> None:
    assert _max_of([]) == float("-inf")
    assert _max_of([0.2, 0.7, 0.1]) == 0.7


def test_brighter_caps_channels_but_never_dims_them() -> None:
    assert _brighter((0.2, 0.5, 1.0), 2, 0.8) == pytest.approx((0.4, 0.8, 1.0))
    assert _brighter((0.9, 0.1, 0.1), 3, 0.5) == pytest.approx((0.9, 0.3, 0.3))


def test_a_flash_brightens_the_scene_and_keeps_the_haze_in_range() -> None:
    atmosphere = sample_atmosphere(lightning=1.0, haze=(0.5, 0.5, 0.6))
    lit = flashed(atmosphere, 1.0, rules(brightness=2, max_haze=0.85))
    assert lit.ambient.intensity == pytest.approx(1.0)
    assert lit.sky.environment_intensity == pytest.approx(2)
    assert lit.sky.haze == pytest.approx((0.85, 0.85, 0.85))


def test_no_flash_or_no_storm_leaves_the_atmosphere_as_it_is() -> None:
    no_storm = sample_atmosphere(lightning=0.0)
    assert flashed(no_storm, 1.0) is no_storm
    storm = sample_atmosphere(lightning=1.0)
    assert flashed(storm, 0.0) is storm


def test_a_flash_is_clamped_to_its_range() -> None:
    atmosphere = sample_atmosphere(lightning=2.0)
    over = flashed(atmosphere, 5.0, rules(brightness=2))
    full = flashed(sample_atmosphere(lightning=1.0), 1.0, rules(brightness=2))
    assert over.ambient.intensity == pytest.approx(full.ambient.intensity)
