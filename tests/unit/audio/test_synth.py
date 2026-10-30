"""Unit tests of `src/audio/synth.py`."""

import pytest
from helpers.audio_fakes import FakeContext, FakeNode

from audio.audio_types import INFINITY, Envelope, FilterSpec, ToneLayer
from audio.synth import NOISE_SECONDS, STOP_MARGIN, VoiceOptions, noise_buffer, play_voice


def layer(
    wave: str = "sine",
    *,
    gain: float = 1,
    pitch: float = 1,
    envelope: Envelope | None = None,
    glide_to: float | None = None,
    glide_seconds: float | None = None,
    detune: float | None = None,
    filter_spec: FilterSpec | None = None,
    delay: float | None = None,
) -> ToneLayer:
    env = envelope if envelope is not None else Envelope(0.1, 0.1, 0.5, 0.2)
    return ToneLayer(wave, gain, pitch, glide_to, glide_seconds, detune, env, filter_spec, delay)


def test_p12_r05_the_noise_buffer_is_one_second_of_noise_made_once_per_context() -> None:
    ctx = FakeContext(sample_rate=500)
    first = noise_buffer(ctx)
    assert noise_buffer(ctx) is first
    data = first.getChannelData(0)
    assert len(data) == round(500 * NOISE_SECONDS)
    assert all(-1 <= sample <= 1 for sample in data)
    assert len(set(data)) > 100  # it is noise, not a constant
    assert noise_buffer(FakeContext(sample_rate=500)) is not first


def test_p12_r05_an_oscillator_layer_is_started_at_its_pitch_and_stopped_after_its_release() -> (
    None
):
    ctx = FakeContext()
    destination = FakeNode("bus")
    voice = play_voice(ctx, destination, [layer("square")], VoiceOptions(2.0, 440, 0.5, 1))
    oscillator = ctx.of_kind("oscillator")[0]
    assert oscillator.type == "square"
    assert oscillator.frequency.value == pytest.approx(440)
    assert oscillator.started == [2.0]
    # The envelope ends at 2 + max(0.5, 0.1 + 0.1) + 0.2 = 2.7 s.
    assert oscillator.stops == [pytest.approx(2.7 + STOP_MARGIN)]
    assert voice.end == pytest.approx(2.7)


def test_p12_r05_an_instrument_layer_is_a_ratio_of_the_note_frequency() -> None:
    ctx = FakeContext()
    play_voice(ctx, FakeNode("bus"), [layer(pitch=0.5)], VoiceOptions(0, 440, 0.2, 1))
    assert ctx.of_kind("oscillator")[0].frequency.value == pytest.approx(220)


def test_p12_r09_a_gliding_layer_sweeps_its_pitch_over_its_glide_time() -> None:
    ctx = FakeContext()
    play_voice(
        ctx,
        FakeNode("bus"),
        [layer(glide_to=100, glide_seconds=0.5)],
        VoiceOptions(0, None, 0.2, 1),
    )
    oscillator = ctx.of_kind("oscillator")[0]
    assert ("exponentialRampToValueAtTime", (100, 0.5)) in oscillator.frequency.events


def test_p12_r09_detuned_layers_are_detuned() -> None:
    ctx = FakeContext()
    play_voice(ctx, FakeNode("bus"), [layer(detune=12)], VoiceOptions(0, 440, 0.2, 1))
    assert ctx.of_kind("oscillator")[0].detune.value == pytest.approx(12)


def test_p12_r09_a_noise_layer_is_a_looped_buffer_source() -> None:
    ctx = FakeContext()
    play_voice(ctx, FakeNode("bus"), [layer("noise")], VoiceOptions(0, None, 0.2, 1))
    source = ctx.of_kind("source")[0]
    assert source.loop is True
    assert source.buffer is noise_buffer(ctx)
    assert ctx.of_kind("oscillator") == []


def test_p12_r09_a_gliding_noise_layer_sets_its_playback_rate() -> None:
    ctx = FakeContext()
    play_voice(
        ctx,
        FakeNode("bus"),
        [layer("noise", pitch=1000, glide_to=500, glide_seconds=0.3)],
        VoiceOptions(1.0, None, 0.2, 1),
    )
    rate = ctx.of_kind("source")[0].playbackRate
    assert ("exponentialRampToValueAtTime", (0.5, 1.3)) in rate.events


def test_p12_r09_a_layer_filter_sits_between_the_source_and_its_gain() -> None:
    ctx = FakeContext()
    spec = FilterSpec("lowpass", 800, q=4, from_=3000, sweep_seconds=0.2)
    play_voice(ctx, FakeNode("bus"), [layer(filter_spec=spec)], VoiceOptions(0, 440, 0.2, 1))
    oscillator = ctx.of_kind("oscillator")[0]
    filter_node = ctx.of_kind("filter")[0]
    gain = ctx.of_kind("gain")[0]
    assert oscillator.connections == [filter_node]
    assert filter_node.connections == [gain]
    assert filter_node.type == "lowpass"
    assert filter_node.Q.value == 4
    assert filter_node.frequency.value == 3000
    assert ("exponentialRampToValueAtTime", (800, 0.2)) in filter_node.frequency.events


def test_p12_r09_a_filter_without_a_sweep_starts_at_its_frequency() -> None:
    ctx = FakeContext()
    spec = FilterSpec("bandpass", 1200)
    play_voice(ctx, FakeNode("bus"), [layer(filter_spec=spec)], VoiceOptions(0, 440, 0.2, 1))
    filter_node = ctx.of_kind("filter")[0]
    assert filter_node.Q.value == 1
    assert filter_node.frequency.value == 1200
    assert filter_node.frequency.names() == ["setValueAtTime"]


def test_p12_r05_a_held_voice_has_no_end_and_no_stop_scheduled() -> None:
    ctx = FakeContext()
    voice = play_voice(ctx, FakeNode("bus"), [layer()], VoiceOptions(0, 440, INFINITY, 1))
    assert voice.end == INFINITY
    assert ctx.of_kind("oscillator")[0].stops == []


def test_p12_r05_a_delayed_layer_starts_later_and_the_voice_lasts_until_the_last_layer() -> None:
    ctx = FakeContext()
    voice = play_voice(
        ctx,
        FakeNode("bus"),
        [layer(delay=0.5), layer()],
        VoiceOptions(1.0, 440, 0.2, 1),
    )
    starts = [osc.started[0] for osc in ctx.of_kind("oscillator")]
    assert starts == pytest.approx([1.5, 1.0])
    assert voice.end == pytest.approx(1.5 + 0.2 + 0.2)


def test_p12_r11_stopping_a_voice_fades_its_gain_and_stops_its_sources() -> None:
    ctx = FakeContext()
    voice = play_voice(ctx, FakeNode("bus"), [layer()], VoiceOptions(0, 440, INFINITY, 1))
    voice.stop(3.0, 0.4)
    gain = ctx.of_kind("gain")[0]
    assert gain.gain.events[-1][0] == "setTargetAtTime"
    oscillator = ctx.of_kind("oscillator")[0]
    assert oscillator.stops == [pytest.approx(3.0 + 0.4 + STOP_MARGIN)]


def test_p12_r11_stopping_a_source_that_already_ended_is_harmless() -> None:
    ctx = FakeContext()
    voice = play_voice(ctx, FakeNode("bus"), [layer()], VoiceOptions(0, 440, INFINITY, 1))
    oscillator = ctx.of_kind("oscillator")[0]

    def broken_stop(when: float = 0) -> None:
        raise RuntimeError("already stopped")

    oscillator.stop = broken_stop
    voice.stop(1.0, 0.1)  # must not raise
    assert voice.end == INFINITY


def test_p12_r05_the_layer_gain_is_its_own_times_the_voice_gain() -> None:
    ctx = FakeContext()
    play_voice(ctx, FakeNode("bus"), [layer(gain=0.5)], VoiceOptions(0, 440, 0.2, 0.8))
    gain = ctx.of_kind("gain")[0]
    assert ("linearRampToValueAtTime", (0.4, 0.1)) in gain.gain.events
