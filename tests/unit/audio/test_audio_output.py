"""Unit tests of `src/audio/audio_output.py`."""

import pytest
from helpers.audio_fakes import FakeContext

from audio.audio_bindings import AudioMix
from audio.audio_output import (
    BUS_RAMP_SECONDS,
    AudioOutput,
    AudioOutputOptions,
    reverb_impulse,
    volume_gain,
)
from config.audio import AudioLimiter


def options(
    context: FakeContext | None,
    *,
    reverb: float | None = None,
    fail: bool = False,
) -> AudioOutputOptions:
    def create() -> FakeContext:
        if fail:
            raise RuntimeError("no Web Audio")
        assert context is not None
        return context

    factory = create if context is not None or fail else None
    return AudioOutputOptions(
        factory,
        AudioMix(0.5, 0.8),
        -1,
        AudioLimiter(0, 20, 0.003, 0.25),
        reverb,
    )


def test_p12_r04_volume_steps_follow_a_square_law_and_stay_in_range() -> None:
    assert volume_gain(0, 10) == 0
    assert volume_gain(5, 10) == pytest.approx(0.25)
    assert volume_gain(10, 10) == 1
    assert volume_gain(20, 10) == 1
    assert volume_gain(-3, 10) == 0
    assert volume_gain(3, 0) == 0


def test_p12_r05_without_web_audio_everything_stays_silent() -> None:
    output = AudioOutput(AudioOutputOptions(None, AudioMix(1, 1), -1, AudioLimiter(0, 20, 0, 0)))
    assert output.state == "none"
    assert output.unlock() is None
    assert output.buses is None
    output.set_hidden(True)
    output.set_volumes(0.5, 0.5)


def test_p12_r05_the_context_is_created_on_the_first_unlock_only() -> None:
    context = FakeContext()
    output = AudioOutput(options(context))
    buses = output.unlock()
    assert buses is not None
    assert output.unlock() is buses
    assert output.buses is buses
    assert output.state == "running"


def test_p12_r05_a_suspended_context_is_resumed_on_unlock() -> None:
    context = FakeContext()
    context.state = "suspended"
    output = AudioOutput(options(context))
    output.unlock()
    assert context.resumed == 1


def test_p12_r05_both_buses_feed_a_compressor_into_the_destination() -> None:
    context = FakeContext()
    output = AudioOutput(options(context))
    buses = output.unlock()
    assert buses is not None
    master = context.of_kind("compressor")[0]
    assert master.connections == [context.destination]
    assert buses.music.connections == [master]
    assert buses.sfx.connections == [master]
    assert master.threshold.value == -1
    assert master.ratio.value == 20
    assert master.attack.value == pytest.approx(0.003)
    assert master.release.value == pytest.approx(0.25)


def test_p12_r04_the_bus_levels_are_the_volumes_times_the_mix() -> None:
    context = FakeContext()
    output = AudioOutput(options(context))
    output.set_volumes(1, 0.5)
    buses = output.unlock()
    assert buses is not None
    assert buses.music.gain.value == pytest.approx(0.5)
    assert buses.sfx.gain.value == pytest.approx(0.4)


def test_p12_r04_volume_changes_ramp_the_buses_without_a_click() -> None:
    context = FakeContext()
    output = AudioOutput(options(context))
    buses = output.unlock()
    assert buses is not None
    context.currentTime = 2.0
    output.set_volumes(0, 1)
    assert buses.music.gain.names() == [
        "cancelScheduledValues",
        "setValueAtTime",
        "linearRampToValueAtTime",
    ]
    assert buses.music.gain.events[-1] == ("linearRampToValueAtTime", (0, 2.0 + BUS_RAMP_SECONDS))


def test_p12_r04_volumes_set_before_the_context_apply_when_it_is_created() -> None:
    context = FakeContext()
    output = AudioOutput(options(context))
    output.set_volumes(0.5, 0.5)
    buses = output.unlock()
    assert buses is not None
    assert buses.music.gain.value == pytest.approx(0.25)


def test_p12_r11_hiding_the_page_suspends_and_showing_it_resumes_the_audio() -> None:
    context = FakeContext()
    output = AudioOutput(options(context))
    output.unlock()
    output.set_hidden(True)
    assert context.suspended == 1
    output.set_hidden(False)
    assert context.resumed == 1


def test_p12_r11_hiding_a_closed_context_does_nothing() -> None:
    context = FakeContext()
    output = AudioOutput(options(context))
    output.unlock()
    context.state = "closed"
    output.set_hidden(True)
    assert context.suspended == 0


def test_p12_r11_hiding_before_any_unlock_does_nothing() -> None:
    output = AudioOutput(options(FakeContext()))
    output.set_hidden(True)
    assert output.buses is None


def test_p12_r05_a_failing_context_stays_silent_and_is_not_retried() -> None:
    output = AudioOutput(options(None, fail=True))
    assert output.unlock() is None
    assert output.unlock() is None
    assert output.buses is None


def test_p12_r06_a_reverb_is_a_convolver_into_the_music_bus() -> None:
    context = FakeContext(sample_rate=100)
    output = AudioOutput(options(context, reverb=0.5))
    buses = output.unlock()
    assert buses is not None
    convolver = context.of_kind("convolver")[0]
    assert buses.reverb is convolver
    assert convolver.connections == [buses.music]
    assert convolver.buffer.channels[0]
    assert len(convolver.buffer.channels) == 2


def test_p12_r06_no_reverb_is_made_unless_asked() -> None:
    context = FakeContext()
    buses = AudioOutput(options(context)).unlock()
    assert buses is not None
    assert buses.reverb is None
    assert context.of_kind("convolver") == []


def test_p12_r05_the_reverb_impulse_decays_and_is_the_same_on_every_run() -> None:
    first = reverb_impulse(FakeContext(sample_rate=1000), 0.2)
    second = reverb_impulse(FakeContext(sample_rate=1000), 0.2)
    assert first.channels == second.channels
    left = first.channels[0]
    assert len(left) == 200
    early = max(abs(sample) for sample in left[:20])
    late = max(abs(sample) for sample in left[-20:])
    assert late < early / 10
