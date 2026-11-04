# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/audio/audio_types.py`."""

import math

import pytest

from audio.audio_types import (
    INFINITY,
    Envelope,
    Note,
    SoundDesign,
    ToneLayer,
    Track,
    beat_seconds,
    is_finite,
    midi_to_hz,
    sound_seconds,
    track_seconds,
    xorshift,
)


def layer(envelope: Envelope, delay: float | None = None) -> ToneLayer:
    return ToneLayer("sine", 1, 440, None, None, None, envelope, None, delay)


def test_aud_engine_01_is_finite_is_false_for_infinity_and_nan() -> None:
    assert is_finite(1.5) is True
    assert is_finite(0) is True
    assert is_finite(INFINITY) is False
    assert is_finite(float("nan")) is False


def test_aud_engine_06_xorshift_matches_marsaglia_reference_values() -> None:
    # Marsaglia's xorshift32 (13, 17, 5) from seed 1: 270369 is its first output.
    assert xorshift(1) == 270369
    assert xorshift(0x9E3779B9) != 0x9E3779B9


def test_aud_engine_06_xorshift_is_deterministic_and_stays_32_bit() -> None:
    seed = 0x2545F491
    for _ in range(100):
        seed = xorshift(seed)
        assert 0 < seed < 2**32


def test_aud_engine_05_beat_seconds_and_track_seconds() -> None:
    assert beat_seconds(120) == pytest.approx(0.5)
    track = Track("menu", 120, 8, [], loop=True)
    assert track_seconds(track) == pytest.approx(4.0)


def test_aud_engine_01_midi_pitch_69_is_concert_a() -> None:
    assert midi_to_hz(69) == pytest.approx(440)
    assert midi_to_hz(81) == pytest.approx(880)
    assert midi_to_hz(57) == pytest.approx(220)


def test_aud_engine_07_a_looping_sound_lasts_forever() -> None:
    sound = SoundDesign("hum", ["hum"], 1, 1, 4.7, loop=True)
    assert sound_seconds(sound) == INFINITY


def test_aud_engine_07_a_sound_lasts_as_long_as_its_sample() -> None:
    assert sound_seconds(SoundDesign("boom", ["boom"], 1, 1, 1.26)) == pytest.approx(1.26)


def test_aud_engine_13_notes_keep_their_fields() -> None:
    note = Note(2, 0.5, 60, 0.8, "lead")
    assert (note.beat, note.beats, note.pitch, note.velocity, note.instrument) == (
        2,
        0.5,
        60,
        0.8,
        "lead",
    )


def test_aud_engine_01_nan_is_not_finite() -> None:
    assert not is_finite(math.nan)
