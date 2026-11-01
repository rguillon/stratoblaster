"""Unit tests of `src/config/audio.py`."""

from config.audio import AUDIO_CONFIG


def test_ui_set_05_default_volumes_are_within_the_volume_steps() -> None:
    """Also UI-SET-02 (the 0 to 10 sliders)."""
    volumes = AUDIO_CONFIG.default_volumes
    assert 0 <= volumes.music <= AUDIO_CONFIG.volume_steps
    assert 0 <= volumes.sfx <= AUDIO_CONFIG.volume_steps


def test_aud_engine_02_the_limiter_is_a_high_ratio_fast_compressor() -> None:
    limiter = AUDIO_CONFIG.limiter
    assert limiter.ratio >= 10
    assert 0 < limiter.attack_seconds < limiter.release_seconds
    assert AUDIO_CONFIG.master_peak_db < 0


def test_aud_engine_05_timings_are_positive_and_the_scheduler_looks_ahead_of_its_tick() -> None:
    assert AUDIO_CONFIG.lookahead_seconds > AUDIO_CONFIG.schedule_interval_seconds > 0
    assert AUDIO_CONFIG.fade_seconds > 0
    assert AUDIO_CONFIG.crossfade_seconds > 0
    assert AUDIO_CONFIG.pause_fade_seconds > 0


def test_aud_engine_07_pan_stays_within_the_stereo_field_and_voices_are_capped() -> None:
    """Also AUD-ENGINE-08 (panning) and DEV-API-02 (the last sounds kept for the tests)."""
    assert 0 < AUDIO_CONFIG.pan_max <= 1
    assert AUDIO_CONFIG.max_voices > 0
    assert AUDIO_CONFIG.recent_sounds > 0
    assert AUDIO_CONFIG.retrigger_boost >= 1
