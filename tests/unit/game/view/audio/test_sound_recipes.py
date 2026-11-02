# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/audio/sound_recipes.py`."""

import pytest

from audio.audio_types import Envelope, FilterSpec, ToneLayer
from game.view.audio.sound_recipes import (
    BELL_PARTIAL,
    MINIGUN,
    ExplosionSize,
    MinigunBurst,
    bell,
    click,
    env,
    explosion,
    flatten_layers,
    minigun,
    ring,
    rumble,
    thump,
    tone,
    whoosh,
)


def test_aud_sfx_02_the_minigun_fires_six_rounds_about_48_a_second() -> None:
    assert isinstance(MINIGUN, MinigunBurst)
    assert MINIGUN.rounds == 6
    assert 1 / MINIGUN.gap == pytest.approx(47.6, abs=0.5)


def test_aud_sfx_02_a_minigun_burst_is_a_crack_and_a_thump_per_round() -> None:
    layers = minigun(MinigunBurst(3, 0.02))
    assert len(layers) == 6
    assert [layer_.wave for layer_ in layers[:2]] == ["noise", "triangle"]
    assert [layer_.delay for layer_ in layers[::2]] == pytest.approx([0, 0.02, 0.04])


def test_aud_sfx_02_alternate_rounds_are_quieter() -> None:
    layers = minigun(MinigunBurst(2, 0.02))
    crack_gains = [layer_.gain for layer_ in layers if layer_.wave == "noise"]
    assert crack_gains == [1, 0.75]


def test_aud_sfx_02_the_thump_glides_down_from_its_pitch() -> None:
    round_thump = minigun(MinigunBurst(1, 0.02))[1]
    assert round_thump.pitch == 150
    assert round_thump.glide_to == 55
    assert round_thump.glide_seconds == 0.018
    assert round_thump.filter.type == "lowpass"


def test_eng_155_flatten_layers_spreads_recipes_and_keeps_single_layers() -> None:
    a = tone("sine", 1, 1, env(0.1, 0.1), {})
    b = tone("noise", 1, 1, env(0.1, 0.1), {})
    c = tone("square", 1, 1, env(0.1, 0.1), {})
    assert flatten_layers([a, [b, c]]) == [a, b, c]
    assert flatten_layers([]) == []


def test_env_defaults_to_zero_sustain_and_a_short_release() -> None:
    e = env(0.01, 0.2)
    assert isinstance(e, Envelope)
    assert (e.attack, e.decay, e.sustain, e.release) == (0.01, 0.2, 0, 0.03)
    assert env(0.01, 0.2, 0.5, 0.4).sustain == 0.5


def test_tone_takes_the_pitch_and_optional_fields_from_its_rest() -> None:
    base = env(0.01, 0.1)
    plain = tone("sine", 440, 0.5, base, {})
    assert isinstance(plain, ToneLayer)
    assert plain.pitch == 440
    assert plain.glide_to is None
    assert plain.delay is None
    assert plain.envelope is base
    custom_env = env(0.2, 0.3)
    layer_ = tone(
        "sawtooth",
        440,
        0.5,
        base,
        {
            "pitch": 220,
            "glide_to": 110,
            "glide_seconds": 0.1,
            "detune_cents": 4,
            "envelope": custom_env,
            "filter": FilterSpec("lowpass", 900),
            "delay": 0.5,
        },
    )
    assert layer_.pitch == 220
    assert (layer_.glide_to, layer_.glide_seconds, layer_.detune_cents) == (110, 0.1, 4)
    assert layer_.envelope is custom_env
    assert layer_.filter.frequency == 900
    assert layer_.delay == 0.5


def test_aud_sfx_04_explosion_layers_a_crack_a_body_a_thump_and_debris() -> None:
    size = ExplosionSize(seconds=0.3, body=2600, thump=120, tail=0, debris=3)
    layers = explosion(size)
    # Crack, body, thump, then one crackle per piece of debris; no rumble without a tail.
    assert len(layers) == 3 + 3
    assert layers[2].glide_to == pytest.approx(120 * 0.45)
    assert all(layer_.delay == 0 for layer_ in layers[:3])


def test_aud_sfx_04_a_big_explosion_rolls_a_rumble_on_after_it() -> None:
    size = ExplosionSize(seconds=1.1, body=3400, thump=70, tail=2, debris=8)
    layers = explosion(size)
    assert len(layers) == 3 + 1 + 8
    rumble = layers[3]
    assert rumble.filter.frequency == 260
    assert rumble.envelope.decay == 2


def test_aud_sfx_04_debris_crackles_come_later_and_fade() -> None:
    size = ExplosionSize(seconds=0.6, body=3000, thump=90, tail=0, debris=5)
    debris = explosion(size)[3:]
    delays = [layer_.delay for layer_ in debris]
    assert delays == sorted(delays)
    assert delays[0] > 0.6 * 0.2
    gains = [layer_.gain for layer_ in debris]
    assert gains == sorted(gains, reverse=True)


def test_aud_sfx_04_explosion_starts_after_its_delay() -> None:
    size = ExplosionSize(seconds=0.3, body=2600, thump=120, tail=0, debris=0)
    layers = explosion(size, delay=0.5)
    assert all(layer_.delay == 0.5 for layer_ in layers)


def test_aud_sfx_01_a_bell_strikes_its_pitches_one_after_the_other() -> None:
    """D-239: each a sine fundamental under a quieter, shorter inharmonic partial."""
    layers = bell([523, 659, 784], 0.07, 0.6)
    assert [layer_.pitch for layer_ in layers[::2]] == [523, 659, 784]
    assert [layer_.pitch for layer_ in layers[1::2]] == pytest.approx([
        523 * BELL_PARTIAL,
        659 * BELL_PARTIAL,
        784 * BELL_PARTIAL,
    ])
    assert [layer_.delay for layer_ in layers] == pytest.approx([0, 0, 0.07, 0.07, 0.14, 0.14])
    assert all(layer_.wave == "sine" for layer_ in layers)
    assert [layer_.gain for layer_ in layers[:2]] == pytest.approx([0.6, 0.18])
    assert layers[0].envelope.decay > layers[1].envelope.decay


def test_d239_the_realistic_recipes_are_filtered_noise_and_sines() -> None:
    """A click, a whoosh, a rumble and a ring are noise through a filter; a thump a falling sine."""
    tick = click(2000, 0.5, 0.01, 0.2)
    assert (tick.wave, tick.delay, tick.filter.type, tick.filter.frequency) == (
        "noise",
        0.2,
        "bandpass",
        2000,
    )
    sweep = whoosh(400, 2600, 0.8, 0.5, 0.1, 0.8)
    assert (sweep.wave, sweep.delay, sweep.filter.q) == ("noise", 0.1, 0.8)
    assert (sweep.filter.from_, sweep.filter.frequency, sweep.filter.sweep_seconds) == (
        400,
        2600,
        0.5,
    )
    assert sweep.envelope.attack == pytest.approx(0.075)
    low = rumble(200, 0.4, 1.0)
    assert (low.wave, low.filter.type, low.filter.frequency, low.envelope.decay) == (
        "noise",
        "lowpass",
        200,
        1.0,
    )
    plate = ring(2900, 0.5, 0.25)
    assert (plate.wave, plate.filter.type, plate.filter.q) == ("noise", "bandpass", 30)
    low_tone = thump(180, 0.5, 0.06, 0.09)
    assert (low_tone.wave, low_tone.pitch, low_tone.glide_to, low_tone.delay) == (
        "sine",
        180,
        90,
        0.09,
    )
    assert low_tone.glide_seconds == 0.06
