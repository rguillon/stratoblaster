"""Unit tests of `src/game/view/audio/instruments.py`."""

import pytest

from audio.audio_types import Instrument, ToneLayer
from game.view.audio.instruments import DRUM_PITCH, INSTRUMENTS, _instrument, env, layer, saws
from game.view.audio.jingles import JINGLES
from game.view.audio.music_styles import MENU_STYLE, WORLD_STYLES


def test_p12_r06_every_instrument_is_an_instrument_with_layers():
    assert INSTRUMENTS
    for name, instrument in INSTRUMENTS.items():
        assert isinstance(instrument, Instrument), name
        assert instrument.layers, name
        assert all(isinstance(layer_, ToneLayer) for layer_ in instrument.layers), name
        assert instrument.gain > 0, name


def test_p12_r06_every_instrument_a_track_names_exists():
    named = set()
    for style in [*WORLD_STYLES.values(), MENU_STYLE]:
        i = style.instruments
        named.update([i.kick, i.snare, i.hat, i.perc, i.bass, i.pad, i.arp, i.lead])
    for track in JINGLES.values():
        named.update(n.instrument for n in track.notes)
    # The boss parts and the fills of the tracks name these voices too.
    named.update(["stab", "riser", "tom"])
    assert sorted(name for name in named if name not in INSTRUMENTS) == []


def test_p12_r06_drum_pitch_is_a_midi_note():
    assert DRUM_PITCH == 36


def test_p12_r06_saws_detunes_one_sawtooth_per_cent():
    layers = saws([-7, 7], 0.3, {"glide_to": 500, "glide_seconds": 0.1})
    assert [layer_.wave for layer_ in layers] == ["sawtooth", "sawtooth"]
    assert [layer_.detune_cents for layer_ in layers] == [-7, 7]
    assert all(layer_.gain == 0.3 for layer_ in layers)
    assert all(layer_.glide_to == 500 for layer_ in layers)


def test_p12_r06_layer_defaults_to_a_plucked_envelope_at_pitch_one():
    default = layer("square", 0.5, {})
    assert default.pitch == 1
    assert default.envelope.attack == pytest.approx(0.002)
    assert default.filter is None and default.delay is None


def test_p12_r06_layer_takes_its_optional_fields_from_the_rest():
    own = env(0.1, 0.2, 0.3, 0.4)
    custom = layer("sine", 0.2, {"pitch": 0.5, "envelope": own, "delay": 0.25})
    assert custom.pitch == 0.5
    assert custom.envelope is own
    assert custom.delay == 0.25


def test_env_stores_the_four_stages():
    e = env(0.01, 0.2, 0.5, 0.3)
    assert (e.attack, e.decay, e.sustain, e.release) == (0.01, 0.2, 0.5, 0.3)


def test_p12_r06_instrument_shares_its_echo_and_reverb():
    plain = _instrument(0.5, [[layer("sine", 1, {})]], {})
    assert plain.echo is None and plain.reverb is None
    sent = _instrument(0.5, [layer("sine", 1, {})], {"echo": 0.4, "reverb": 0.2})
    assert (sent.echo, sent.reverb) == (0.4, 0.2)
    assert len(sent.layers) == 1
