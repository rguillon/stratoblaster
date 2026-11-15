# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/loop/quality_governor.py` (D-410)."""

from config.engine import ENGINE_CONFIG, QualityConfig, QualityLevel
from core.loop.quality_governor import QualityGovernor

CONFIG = QualityConfig(
    [QualityLevel(1.0, "medium"), QualityLevel(0.75, "low"), QualityLevel(0.5, "low")],
    1000,
    1000 / 55,
    0.1,
    1.5,
    500,
    3000,
    17.5,
    9,
    1,
    2,
    0.8,
)


def _frames(governor: QualityGovernor, count: int, ms: float, work: float = 4.0) -> list[int]:
    """Feed `count` frames `ms` apart; return the levels after each change."""
    return [governor.level for _ in range(count) if governor.sample(ms, work, None)]


def _slow(governor: QualityGovernor, count: int) -> list[int]:
    """Frames at 40 FPS on a 60 Hz display: one 16.7 ms, one 33.3 ms, and so on."""
    return [
        governor.level
        for i in range(count)
        if governor.sample(1000 / 60 if i % 2 == 0 else 1000 / 30, 4.0, None)
    ]


def test_d410_frames_at_60_fps_keep_the_full_look() -> None:
    governor = QualityGovernor(CONFIG, 0)
    assert _frames(governor, 600, 1000 / 60) == []
    assert governor.level == 0


def test_d410_late_frames_lower_the_level_one_window_at_a_time() -> None:
    governor = QualityGovernor(CONFIG, 0)
    # A window of late frames: one level down, then the next frames settle before being judged.
    assert _slow(governor, 40) == [1]
    assert _slow(governor, 120) == [2]
    # The lowest level stays the lowest.
    assert _slow(governor, 200) == []
    assert governor.level == 2


def test_d410_a_display_slower_than_60_hz_is_not_a_slow_machine() -> None:
    governor = QualityGovernor(CONFIG, 0)
    # Every frame 20 ms apart on a 50 Hz display: none is late for it.
    assert _frames(governor, 500, 20) == []


def test_d410_frames_slowed_by_the_processor_keep_the_level() -> None:
    governor = QualityGovernor(CONFIG, 0)
    # The main thread's work fills the frames: fewer pixels would not help.
    changes = []
    for i in range(200):
        ms = 1000 / 60 if i % 2 == 0 else 1000 / 30
        if governor.sample(ms, ms * 0.9, None):
            changes.append(governor.level)
    assert changes == []


def test_d410_a_long_run_of_quick_frames_tries_a_better_level() -> None:
    governor = QualityGovernor(CONFIG, 2)
    # Quick, light frames for longer than `clean_ms`: one level up, to try; once the try has held
    # as long again, the next one.
    assert _frames(governor, 400, 1000 / 60) == [1]
    assert _frames(governor, 300, 1000 / 60) == [0]


def test_d410_a_failed_try_goes_back_down_and_stays() -> None:
    governor = QualityGovernor(CONFIG, 1)
    assert _frames(governor, 300, 1000 / 60) == [0]
    # The try is slow: back down, and no other try in the session.
    assert _slow(governor, 60) == [1]
    # Leave the window the slow frames started (play paused), then quick frames for long.
    governor.restart()
    assert _frames(governor, 2000, 1000 / 60) == []
    assert governor.level == 1


def test_d410_a_try_holds_once_it_has_run_as_long_as_it_took_to_earn() -> None:
    governor = QualityGovernor(CONFIG, 1)
    assert _frames(governor, 600, 1000 / 60) == [0]
    # Slow frames after the trial: down again, but the next long quick run may try again.
    assert _slow(governor, 60) == [1]
    governor.restart()
    assert _frames(governor, 400, 1000 / 60) == [0]


def test_d410_a_busy_gpu_or_main_thread_holds_the_try() -> None:
    governor = QualityGovernor(CONFIG, 1)
    for _ in range(600):
        assert not governor.sample(1000 / 60, 4.0, 12.0)
    assert _frames(governor, 600, 1000 / 60, work=12.0) == []
    assert governor.level == 1


def test_d410_a_restart_forgets_the_frames_and_settles() -> None:
    governor = QualityGovernor(CONFIG, 0)
    _slow(governor, 30)
    governor.restart()
    # Within `settle_ms` nothing is judged; a frame of no length is ignored.
    assert not governor.sample(0, 0, None)
    assert _slow(governor, 30) == []
    assert _slow(governor, 40) == [1]


def test_d410_the_level_starts_within_the_levels() -> None:
    assert QualityGovernor(CONFIG, 9).level == 2
    assert QualityGovernor(CONFIG, -3).level == 0
    assert QualityGovernor(ENGINE_CONFIG.quality, 0).ceiling == 4
