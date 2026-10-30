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
    layer_seconds,
    midi_to_hz,
    sound_seconds,
    track_seconds,
    xorshift,
)


def layer(envelope: Envelope, delay: float | None = None) -> ToneLayer:
    return ToneLayer("sine", 1, 440, None, None, None, envelope, None, delay)


def test_p12_r05_is_finite_is_false_for_infinity_and_nan() -> None:
    assert is_finite(1.5) is True
    assert is_finite(0) is True
    assert is_finite(INFINITY) is False
    assert is_finite(float("nan")) is False


def test_p12_r09_xorshift_matches_marsaglia_reference_values() -> None:
    # Marsaglia's xorshift32 (13, 17, 5) from seed 1: 270369 is its first output.
    assert xorshift(1) == 270369
    assert xorshift(0x9E3779B9) != 0x9E3779B9


def test_p12_r09_xorshift_is_deterministic_and_stays_32_bit() -> None:
    seed = 0x2545F491
    for _ in range(100):
        seed = xorshift(seed)
        assert 0 < seed < 2**32


def test_p12_r05_beat_seconds_and_track_seconds() -> None:
    assert beat_seconds(120) == pytest.approx(0.5)
    track = Track("menu", 120, 8, [], True)
    assert track_seconds(track) == pytest.approx(4.0)


def test_p12_r05_midi_pitch_69_is_concert_a() -> None:
    assert midi_to_hz(69) == pytest.approx(440)
    assert midi_to_hz(81) == pytest.approx(880)
    assert midi_to_hz(57) == pytest.approx(220)


def test_p12_r09_a_layer_lasts_its_delay_plus_hold_or_attack_decay_plus_release() -> None:
    env = Envelope(0.01, 0.2, 0.5, 0.3)
    assert layer_seconds(layer(env), 0.1) == pytest.approx(0 + 0.21 + 0.3)
    assert layer_seconds(layer(env), 1.0) == pytest.approx(1.0 + 0.3)
    assert layer_seconds(layer(env, delay=0.5), 1.0) == pytest.approx(0.5 + 1.0 + 0.3)


def test_p12_r09_a_looping_sound_lasts_forever() -> None:
    sound = SoundDesign("hum", [layer(Envelope(0, 0, 1, 0))], 1, 1, 0.1, loop=True)
    assert sound_seconds(sound) == INFINITY


def test_p12_r09_a_sound_lasts_as_long_as_its_longest_layer() -> None:
    short = layer(Envelope(0, 0, 1, 0.1))
    long = layer(Envelope(0, 0, 1, 0.1), delay=0.4)
    sound = SoundDesign("chime", [short, long], 1, 1, 0.2)
    assert sound_seconds(sound) == pytest.approx(0.4 + 0.2 + 0.1)


def test_p12_r09_a_sound_without_layers_lasts_no_time() -> None:
    assert sound_seconds(SoundDesign("silence", [], 1, 1, 0.2)) == 0


def test_p12_r05_notes_keep_their_fields() -> None:
    note = Note(2, 0.5, 60, 0.8, "lead")
    assert (note.beat, note.beats, note.pitch, note.velocity, note.instrument) == (
        2,
        0.5,
        60,
        0.8,
        "lead",
    )


def test_p12_r05_nan_is_not_finite() -> None:
    assert not is_finite(math.nan)
