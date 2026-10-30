"""Unit tests of `src/audio/sfx_player.py`."""

import pytest
from helpers.audio_fakes import FakeContext, FakeVoice

from audio import sfx_player
from audio.audio_types import INFINITY, Envelope, SoundDesign, ToneLayer
from audio.sfx_player import SfxBus, SfxPlayer, SfxSettings, pan_at


def sound(name: str, hold: float = 0.2, *, priority: float = 1, **flags: bool) -> SoundDesign:
    layer = ToneLayer("square", 1, 440, None, None, None, Envelope(0, 0, 1, 0.1), None, None)
    return SoundDesign(name, [layer], 0.8, priority, hold, **flags)


@pytest.fixture
def voices(monkeypatch: pytest.MonkeyPatch) -> list[FakeVoice]:
    """Every voice the player starts, recorded (the synth is not run)."""
    made: list[FakeVoice] = []

    def fake_play_voice(context, destination, layers, options) -> FakeVoice:  # noqa: ANN001
        voice = FakeVoice(options.when + options.hold, "")
        made.append(voice)
        return voice

    monkeypatch.setattr(sfx_player, "play_voice", fake_play_voice)
    return made


def make_player(
    context: FakeContext | None, clock: list[float] | None = None, **settings: float
) -> tuple[SfxPlayer, FakeContext | None, list[float]]:
    now = clock if clock is not None else [0.0]
    base = {
        "max_voices": 4,
        "retrigger_seconds": 0.03,
        "retrigger_boost": 1.25,
        "pan_max": 0.6,
        "stop_fade_seconds": 0.05,
    }
    base.update(settings)
    bus = SfxBus(context, object()) if context is not None else None
    player = SfxPlayer(lambda: bus, lambda: now[0], SfxSettings(**base))
    return player, context, now


def test_p12_r09_pan_is_zero_in_the_middle_and_reaches_the_maximum_at_the_edges() -> None:
    assert pan_at(50, 100, 0.6) == pytest.approx(0)
    assert pan_at(0, 100, 0.6) == pytest.approx(-0.6)
    assert pan_at(100, 100, 0.6) == pytest.approx(0.6)
    assert pan_at(-20, 100, 0.6) == pytest.approx(-0.6)
    assert pan_at(10, 0, 0.6) == 0


def test_p12_r10_a_sound_plays_and_is_counted_by_the_pool(voices: list[FakeVoice]) -> None:
    player, _, _ = make_player(FakeContext())
    assert player.play(sound("shot")) is True
    assert player.voices == 1
    assert len(voices) == 1


def test_p12_r10_without_a_context_the_pool_still_decides(voices: list[FakeVoice]) -> None:
    player, _, _ = make_player(None)
    assert player.play(sound("shot")) is True
    assert player.voices == 1
    assert voices == []


def test_p12_r10_a_sound_again_too_soon_is_boosted_not_played_twice(
    voices: list[FakeVoice],
) -> None:
    context = FakeContext()
    player, _, clock = make_player(context)
    player.play(sound("shot"))
    gain = context.of_kind("gain")[0]
    clock[0] = 0.01
    assert player.play(sound("shot")) is False
    assert gain.gain.value == pytest.approx(1.25)
    assert len(voices) == 1


def test_p12_r10_a_boost_is_capped_at_its_square(voices: list[FakeVoice]) -> None:
    context = FakeContext()
    player, _, clock = make_player(context)
    player.play(sound("shot"))
    gain = context.of_kind("gain")[0]
    for step in range(1, 6):
        clock[0] = step * 0.001
        player.play(sound("shot"))
    assert gain.gain.value == pytest.approx(1.25**2)


def test_p12_r10_when_the_voices_are_all_taken_a_higher_priority_replaces_the_oldest(
    voices: list[FakeVoice],
) -> None:
    player, _, clock = make_player(FakeContext(), max_voices=1)
    player.play(sound("tick", priority=1))
    clock[0] = 0.1
    assert player.play(sound("boom", priority=2)) is True
    assert voices[0].stops  # the evicted sound is stopped
    assert player.voices == 1


def test_p12_r10_a_lower_priority_sound_is_dropped_when_the_voices_are_taken(
    voices: list[FakeVoice],
) -> None:
    player, _, clock = make_player(FakeContext(), max_voices=1)
    player.play(sound("boom", priority=5))
    clock[0] = 0.1
    assert player.play(sound("tick", priority=1)) is False


def test_p12_r09_a_looping_sound_plays_once_until_it_is_stopped(voices: list[FakeVoice]) -> None:
    player, _, clock = make_player(FakeContext())
    laser = sound("laser", hold=INFINITY, loop=True)
    assert player.play(laser) is True
    clock[0] = 1.0
    assert player.play(laser) is False
    assert player.looping("laser") is True
    player.stop_loop("laser")
    assert player.looping("laser") is False
    assert voices[0].stops


def test_p12_r09_stopping_a_loop_that_is_not_playing_does_nothing(
    voices: list[FakeVoice],
) -> None:
    player, _, _ = make_player(FakeContext())
    player.stop_loop("laser")
    assert player.looping("laser") is False


def test_p12_r09_a_positional_sound_is_panned_when_it_is_off_centre(
    voices: list[FakeVoice],
) -> None:
    context = FakeContext()
    player, _, _ = make_player(context)
    player.play(sound("hit", positional=True), pan=0.9)
    panners = context.of_kind("panner")
    assert len(panners) == 1
    assert panners[0].pan.value == pytest.approx(0.9)
    gain = context.of_kind("gain")[0]
    assert gain.connections == [panners[0]]


def test_p12_r09_a_positional_sound_in_the_middle_is_not_panned(
    voices: list[FakeVoice],
) -> None:
    context = FakeContext()
    player, _, _ = make_player(context)
    player.play(sound("hit", positional=True), pan=0)
    assert context.of_kind("panner") == []


def test_p12_r11_stop_all_stops_every_sound_and_forgets_the_loops(
    voices: list[FakeVoice],
) -> None:
    player, _, _ = make_player(FakeContext())
    player.play(sound("shot"))
    player.play(sound("laser", hold=INFINITY, loop=True))
    player.stop_all()
    assert player.voices == 0
    assert player.looping("laser") is False
    assert all(voice.stops for voice in voices)


def test_p12_r10_a_sound_that_is_over_is_forgotten_so_its_name_can_play_again(
    voices: list[FakeVoice],
) -> None:
    player, _, clock = make_player(FakeContext())
    player.play(sound("shot", hold=0.1))
    clock[0] = 5.0
    assert player.play(sound("shot")) is True
    assert player.voices == 1
