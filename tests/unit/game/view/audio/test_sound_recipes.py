"""Unit tests of `src/game/view/audio/sound_recipes.py`."""

import pytest

from audio.audio_types import Envelope, FilterSpec, ToneLayer
from game.view.audio.sound_recipes import (
    MINIGUN,
    ExplosionSize,
    MinigunBurst,
    chime,
    env,
    explosion,
    flatten_layers,
    minigun,
    tone,
)


def test_p12_r09_the_minigun_fires_six_rounds_about_48_a_second():
    assert isinstance(MINIGUN, MinigunBurst)
    assert MINIGUN.rounds == 6
    assert 1 / MINIGUN.gap == pytest.approx(47.6, abs=0.5)


def test_p12_r09_a_minigun_burst_is_a_crack_and_a_thump_per_round():
    layers = minigun(MinigunBurst(3, 0.02))
    assert len(layers) == 6
    assert [layer_.wave for layer_ in layers[:2]] == ["noise", "square"]
    assert [layer_.delay for layer_ in layers[::2]] == pytest.approx([0, 0.02, 0.04])


def test_p12_r09_alternate_rounds_are_quieter():
    layers = minigun(MinigunBurst(2, 0.02))
    crack_gains = [layer_.gain for layer_ in layers if layer_.wave == "noise"]
    assert crack_gains == [1, 0.75]


def test_p12_r09_the_thump_glides_down_from_its_pitch():
    thump = minigun(MinigunBurst(1, 0.02))[1]
    assert thump.pitch == 150
    assert thump.glide_to == 65
    assert thump.glide_seconds == 0.018
    assert thump.filter.type == "lowpass"


def test_p12_r09_flatten_layers_spreads_recipes_and_keeps_single_layers():
    a = tone("sine", 1, 1, env(0.1, 0.1), {})
    b = tone("noise", 1, 1, env(0.1, 0.1), {})
    c = tone("square", 1, 1, env(0.1, 0.1), {})
    assert flatten_layers([a, [b, c]]) == [a, b, c]
    assert flatten_layers([]) == []


def test_env_defaults_to_zero_sustain_and_a_short_release():
    e = env(0.01, 0.2)
    assert isinstance(e, Envelope)
    assert (e.attack, e.decay, e.sustain, e.release) == (0.01, 0.2, 0, 0.03)
    assert env(0.01, 0.2, 0.5, 0.4).sustain == 0.5


def test_tone_takes_the_pitch_and_optional_fields_from_its_rest():
    base = env(0.01, 0.1)
    plain = tone("sine", 440, 0.5, base, {})
    assert isinstance(plain, ToneLayer)
    assert plain.pitch == 440
    assert plain.glide_to is None and plain.delay is None
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


def test_p12_r09_explosion_layers_a_crack_a_body_a_thump_and_debris():
    size = ExplosionSize(seconds=0.3, body=2600, thump=120, tail=0, debris=3)
    layers = explosion(size)
    # Crack, body, thump, then one crackle per piece of debris; no rumble without a tail.
    assert len(layers) == 3 + 3
    assert layers[2].glide_to == pytest.approx(120 * 0.45)
    assert all(layer_.delay == 0 for layer_ in layers[:3])


def test_p12_r09_a_big_explosion_rolls_a_rumble_on_after_it():
    size = ExplosionSize(seconds=1.1, body=3400, thump=70, tail=2, debris=8)
    layers = explosion(size)
    assert len(layers) == 3 + 1 + 8
    rumble = layers[3]
    assert rumble.filter.frequency == 260
    assert rumble.envelope.decay == 2


def test_p12_r09_debris_crackles_come_later_and_fade():
    size = ExplosionSize(seconds=0.6, body=3000, thump=90, tail=0, debris=5)
    debris = explosion(size)[3:]
    delays = [layer_.delay for layer_ in debris]
    assert delays == sorted(delays)
    assert delays[0] > 0.6 * 0.2
    gains = [layer_.gain for layer_ in debris]
    assert gains == sorted(gains, reverse=True)


def test_p12_r09_explosion_starts_after_its_delay():
    size = ExplosionSize(seconds=0.3, body=2600, thump=120, tail=0, debris=0)
    layers = explosion(size, delay=0.5)
    assert all(layer_.delay == 0.5 for layer_ in layers)


def test_p12_r09_chime_plays_its_pitches_one_after_the_other():
    layers = chime("triangle", [523, 659, 784], 0.07, 0.6)
    assert [layer_.pitch for layer_ in layers] == [523, 659, 784]
    assert [layer_.delay for layer_ in layers] == pytest.approx([0, 0.07, 0.14])
    assert all(layer_.wave == "triangle" and layer_.gain == 0.6 for layer_ in layers)
