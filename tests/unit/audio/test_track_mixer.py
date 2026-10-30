"""Unit tests of `src/audio/track_mixer.py`."""

from unittest.mock import MagicMock

import pytest

from audio.audio_types import Envelope, Instrument, MusicEffects, ToneLayer
from audio.track_mixer import SILENT, MusicBus, TrackMixer


def make_context() -> MagicMock:
    """A Web Audio context whose gain nodes have a real `value` to fade from."""
    context = MagicMock()

    def new_gain() -> MagicMock:
        node = MagicMock()
        node.gain.value = 1.0
        return node

    context.createGain.side_effect = new_gain
    return context


def make_mixer(reverb: bool = True, effects: MusicEffects | None = None) -> tuple:
    context = make_context()
    music = MagicMock()
    reverb_node = MagicMock() if reverb else None
    bus = MusicBus(context, music, reverb_node)
    mixer = TrackMixer(bus, effects, 120)
    return mixer, context, music, reverb_node


def instrument(echo: float | None = None, reverb: float | None = None) -> Instrument:
    layer = ToneLayer("sine", 1, 1, None, None, None, Envelope(0, 0, 1, 0), None, None)
    return Instrument([layer], 1, echo, reverb)


def test_p12_r06_the_track_fader_feeds_the_music_bus() -> None:
    mixer, _, music, _ = make_mixer(reverb=False)
    mixer.output.connect.assert_called_once_with(music)


def test_p12_r06_the_track_has_a_reverb_send_only_with_a_reverb_and_effects() -> None:
    effects = MusicEffects(0.75, 0.3, 2.0)
    mixer, _, _, _ = make_mixer(reverb=True, effects=effects)
    assert mixer._reverb is not None
    mixer_no_effects, _, _, _ = make_mixer(reverb=True, effects=None)
    assert mixer_no_effects._reverb is None


def test_p12_r06_an_instrument_input_is_made_once_per_name() -> None:
    mixer, _, _, _ = make_mixer(reverb=False)
    first = mixer.input("lead", instrument())
    second = mixer.input("lead", instrument())
    other = mixer.input("bass", instrument())
    assert first is second
    assert other is not first


def test_p12_r06_an_echo_send_is_made_only_when_the_instrument_asks_for_one() -> None:
    effects = MusicEffects(0.75, 0.3, 2.0)
    mixer, context, _, _ = make_mixer(reverb=False, effects=effects)
    node = mixer.input("dry", instrument())
    node.connect.assert_called_once_with(mixer.output)
    mixer.input("wet", instrument(echo=0.5))
    assert mixer._echo is not None
    # The echo delay is a dotted eighth at 120 bpm: 0.75 beats of 0.5 s.
    delay = context.createDelay.call_args.args[0]
    assert delay == pytest.approx(1.0)
    assert context.createDelay.return_value.delayTime.value == pytest.approx(0.375)


def test_p12_r06_an_echo_without_effects_is_not_sent() -> None:
    mixer, context, _, _ = make_mixer(reverb=False, effects=None)
    mixer.input("wet", instrument(echo=0.5))
    assert mixer._echo is None
    context.createDelay.assert_not_called()


def test_p12_r06_fade_to_zero_is_an_immediate_set() -> None:
    mixer, _, _, _ = make_mixer(reverb=False)
    mixer.fade_to(0, 3.0, 0)
    mixer.output.gain.setValueAtTime.assert_called_with(0, 3.0)
    mixer.output.gain.exponentialRampToValueAtTime.assert_not_called()


def test_p12_r06_fade_to_a_level_ramps_both_the_track_and_its_reverb() -> None:
    mixer, _, _, _ = make_mixer(reverb=True, effects=MusicEffects(0.75, 0.3, 2))
    mixer.fade_to(0.5, 1.0, 2.0)
    mixer.output.gain.exponentialRampToValueAtTime.assert_called_with(0.5, 3.0)
    mixer._reverb.gain.exponentialRampToValueAtTime.assert_called_with(0.5, 3.0)


def test_p12_r06_a_fade_in_starts_silent_then_rises_to_full() -> None:
    mixer, _, _, _ = make_mixer(reverb=False)
    mixer.fade_in(0.0, 1.0)
    mixer.output.gain.setValueAtTime.assert_any_call(SILENT, 0.0)
    mixer.output.gain.exponentialRampToValueAtTime.assert_called_with(1, 1.0)


def test_p12_r06_a_fade_in_of_zero_seconds_is_at_full_level_at_once() -> None:
    mixer, _, _, _ = make_mixer(reverb=False)
    mixer.fade_in(2.0, 0)
    mixer.output.gain.setValueAtTime.assert_called_with(1, 2.0)


def test_p12_r06_disconnect_cuts_the_track_off_the_bus() -> None:
    mixer, _, _, _ = make_mixer(reverb=True, effects=MusicEffects(0.75, 0.3, 2))
    mixer.input("wet", instrument(echo=0.5))
    mixer.disconnect()
    mixer.output.disconnect.assert_called_once()
    mixer._reverb.disconnect.assert_called_once()
    mixer._echo.disconnect.assert_called_once()
