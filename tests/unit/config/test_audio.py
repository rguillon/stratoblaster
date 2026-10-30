"""Unit tests of `src/config/audio.py`."""

from config.audio import AUDIO_CONFIG


def test_p12_r04_default_volumes_are_within_the_volume_steps() -> None:
    volumes = AUDIO_CONFIG.default_volumes
    assert 0 <= volumes.music <= AUDIO_CONFIG.volume_steps
    assert 0 <= volumes.sfx <= AUDIO_CONFIG.volume_steps


def test_p12_r05_the_limiter_is_a_high_ratio_fast_compressor() -> None:
    limiter = AUDIO_CONFIG.limiter
    assert limiter.ratio >= 10
    assert 0 < limiter.attack_seconds < limiter.release_seconds
    assert AUDIO_CONFIG.master_peak_db < 0


def test_p12_r10_timings_are_positive_and_the_scheduler_looks_ahead_of_its_tick() -> None:
    assert AUDIO_CONFIG.lookahead_seconds > AUDIO_CONFIG.schedule_interval_seconds > 0
    assert AUDIO_CONFIG.fade_seconds > 0
    assert AUDIO_CONFIG.crossfade_seconds > 0
    assert AUDIO_CONFIG.pause_fade_seconds > 0


def test_p12_r10_pan_stays_within_the_stereo_field_and_voices_are_capped() -> None:
    assert 0 < AUDIO_CONFIG.pan_max <= 1
    assert AUDIO_CONFIG.max_voices > 0
    assert AUDIO_CONFIG.recent_sounds > 0
    assert AUDIO_CONFIG.retrigger_boost >= 1
