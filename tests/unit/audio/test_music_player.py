"""Unit tests of `src/audio/music_player.py`."""

import pytest
from helpers.audio_fakes import FakeContext, FakeVoice

from audio import music_player
from audio.audio_types import Envelope, Instrument, Note, ToneLayer, Track
from audio.music_player import MusicPlayer, MusicTimings
from audio.track_mixer import MusicBus


class Stage:
    """The bus the player reads: `bus` is None until the context exists."""

    def __init__(self, context: FakeContext | None) -> None:
        self.context = context
        self.bus = MusicBus(context, context.createGain(), None) if context else None

    def get(self) -> MusicBus | None:
        return self.bus


def track(track_id: str, loop: bool = True) -> Track:
    # 120 bpm (0.5 s a beat), 4 beats (2 s): notes on beats 0, 1 and 3.
    notes = [
        Note(0, 1, 60, 1, "lead"),
        Note(1, 1, 62, 1, "lead"),
        Note(3, 1, 64, 1, "lead"),
    ]
    return Track(track_id, 120, 4, notes, loop)


def instrument() -> Instrument:
    layer = ToneLayer("sine", 1, 1, None, None, None, Envelope(0, 0, 1, 0), None, None)
    return Instrument([layer], 1)


@pytest.fixture
def voices(monkeypatch: pytest.MonkeyPatch) -> list[FakeVoice]:
    made: list[FakeVoice] = []

    def fake_play_voice(context, destination, layers, options) -> FakeVoice:  # noqa: ANN001
        voice = FakeVoice(options.when + options.hold, "")
        voice.hold = options.hold
        made.append(voice)
        return voice

    monkeypatch.setattr(music_player, "play_voice", fake_play_voice)
    return made


def make(context: FakeContext | None) -> tuple[MusicPlayer, Stage]:
    stage = Stage(context)
    player = MusicPlayer(
        stage.get,
        {"lead": instrument()},
        MusicTimings(1.5, 0.05),
    )
    return player, stage


def test_p12_r05_nothing_is_scheduled_before_the_audio_context_exists(
    voices: list[FakeVoice],
) -> None:
    player, _ = make(None)
    player.play(track("menu"), 0.5)
    player.update()
    assert voices == []
    assert player.position == 0


def test_p12_r05_notes_inside_the_lookahead_are_scheduled_on_the_clock(
    voices: list[FakeVoice],
) -> None:
    context = FakeContext()
    player, _ = make(context)
    player.play(track("menu"), 0)
    player.update()
    # The lookahead is 1.5 s: the notes at 0 s and 0.5 s, not the one at 1.5 s.
    assert [v.hold for v in voices] == [0.5, 0.5]
    assert player.track is not None
    assert player.track.id == "menu"


def test_p12_r05_the_notes_of_an_unknown_instrument_are_skipped(
    voices: list[FakeVoice],
) -> None:
    context = FakeContext()
    stage = Stage(context)
    player = MusicPlayer(stage.get, {}, MusicTimings(1.5, 0.05))
    player.play(track("menu"), 0)
    player.update()
    assert voices == []


def test_p12_r05_the_position_follows_the_audio_clock(voices: list[FakeVoice]) -> None:
    context = FakeContext()
    player, _ = make(context)
    player.play(track("menu"), 0)
    player.update()
    context.currentTime = 1.25
    assert player.position == pytest.approx(1.25)
    context.currentTime = 2.5  # past the first loop of 2 s
    assert player.position == pytest.approx(2.5)


def test_p12_r11_pausing_keeps_the_position_and_resuming_goes_on_from_it(
    voices: list[FakeVoice],
) -> None:
    context = FakeContext()
    player, _ = make(context)
    player.play(track("menu"), 0)
    player.update()
    context.currentTime = 1.0
    player.pause()
    assert player.position == pytest.approx(1.0)
    assert all(voice.stops for voice in voices)
    context.currentTime = 5.0
    assert player.position == pytest.approx(1.0)
    player.update()  # nothing is scheduled while paused
    player.resume()
    context.currentTime = 6.0
    assert player.position == pytest.approx(2.0)


def test_p12_r11_pause_and_resume_are_idempotent(voices: list[FakeVoice]) -> None:
    context = FakeContext()
    player, _ = make(context)
    player.resume()  # not paused: nothing to do
    player.play(track("menu"), 0)
    player.update()
    player.pause()
    player.pause()
    player.resume()
    player.resume()
    assert player.position == pytest.approx(0)


def test_p12_r11_pausing_before_the_context_exists_is_harmless(voices: list[FakeVoice]) -> None:
    player, _ = make(None)
    player.play(track("menu"), 0)
    player.pause()
    player.resume()
    assert player.position == 0


def test_p12_r06_a_new_track_cross_fades_the_old_one_out(voices: list[FakeVoice]) -> None:
    context = FakeContext()
    player, _ = make(context)
    player.play(track("level-1"), 0)
    player.update()
    context.currentTime = 1.0
    player.play(track("boss-1"), 2.0)
    assert player.track is not None
    assert player.track.id == "boss-1"
    # The old track is fading out over 2 s: it is still in the mix until then.
    context.currentTime = 2.5
    player.update()
    context.currentTime = 3.5
    player.update()
    assert player.track is not None


def test_p12_r06_playing_none_fades_the_music_out(voices: list[FakeVoice]) -> None:
    context = FakeContext()
    player, _ = make(context)
    player.play(track("menu"), 0)
    player.update()
    player.play(None, 0.5)
    assert player.track is None
    assert player.position == 0


def test_p12_r07_a_jingle_plays_over_the_music_and_is_dropped_when_over(
    voices: list[FakeVoice],
) -> None:
    context = FakeContext()
    player, _ = make(context)
    player.play(track("menu"), 0)
    player.jingle(track("complete", loop=False))
    player.update()
    jingle_voices = len(voices)
    assert jingle_voices > 2  # the menu notes and the jingle's first notes
    context.currentTime = 100.0
    player.update()
    assert player.track is not None  # the jingle does not replace the track


def test_p12_r11_stop_silences_everything_and_clears_the_track(
    voices: list[FakeVoice],
) -> None:
    context = FakeContext()
    player, _ = make(context)
    player.play(track("menu"), 0)
    player.update()
    player.stop()
    assert player.track is None
    assert player.position == 0
    assert all(voice.stops for voice in voices)


def test_p12_r11_stop_without_a_context_clears_the_track(voices: list[FakeVoice]) -> None:
    player, _ = make(None)
    player.play(track("menu"), 0)
    player.stop()
    assert player.track is None


def test_p12_r05_update_without_a_context_does_nothing(voices: list[FakeVoice]) -> None:
    player, _ = make(None)
    player.update()
    assert voices == []
