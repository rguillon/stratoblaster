# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/quality.py` (D-410).

Its work is JavaScript (checked in the e2e runs and by `tests/perf/measure_perf.py`); in CPython
the functions only return their defaults.
"""

from render.quality import apply_quality, gpu_frame_ms, new_gpu_timer


def test_d410_without_a_browser_the_quality_functions_do_nothing() -> None:
    apply_quality(object(), 0.5, "low")
    assert new_gpu_timer(object()) is None
    assert gpu_frame_ms(object()) is None
