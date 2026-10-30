"""Unit tests of `src/config/engine.py`."""

from config.engine import ENGINE_CONFIG


def test_eng17_the_simulation_runs_at_60_hz_with_a_bounded_catch_up() -> None:
    assert ENGINE_CONFIG.simulation_hz == 60
    assert ENGINE_CONFIG.max_steps_per_frame >= 1


def test_eng17_device_pixel_ratio_is_capped() -> None:
    assert ENGINE_CONFIG.max_device_pixel_ratio >= 1


def test_eng52_the_e2e_build_renders_fewer_pixels_without_antialiasing() -> None:
    assert 0 < ENGINE_CONFIG.e2e.render_scale < 1
    assert ENGINE_CONFIG.e2e.antialias is False


def test_p13_r01_the_perf_overlay_refreshes_and_toggles_with_a_key() -> None:
    assert ENGINE_CONFIG.perf_overlay.refresh > 0
    assert ENGINE_CONFIG.perf_overlay.key == "F3"
    assert ENGINE_CONFIG.long_frame_ms > 1000 / ENGINE_CONFIG.simulation_hz
