# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/audio/sfx_player.py`."""

import itertools
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.audio_fakes import FakeContext, FakeVoice

from audio import sfx_player
from audio.audio_types import INFINITY, SoundDesign, SoundJitter
from audio.sfx_player import SfxPlayer, SfxSettings, pan_at


def sound(name: str, seconds: float = 0.2, *, priority: float = 1, **flags: bool) -> SoundDesign:
    return SoundDesign(name, [name], 0.8, priority, seconds, **flags)


class FakeSamples:
    """A `SampleBank` stand-in: every sample is ready, except the names listed as missing."""

    def __init__(self, missing: list[str] | None = None) -> None:
        self.missing = missing or []

    def get(self, name: str) -> Any | None:
        return None if name in self.missing else object()


@pytest.fixture
def voices(monkeypatch: pytest.MonkeyPatch) -> list[FakeVoice]:
    """Every voice the player starts, recorded (no sample is played)."""
    made: list[FakeVoice] = []

    def fake_play_sample(
        context: Any,
        _destination: Any,
        _buffer: Any,
        loop: bool,
        gain: float,
        rate: float = 1,
        delay: float = 0,
    ) -> FakeVoice:
        voice = FakeVoice(INFINITY if loop else context.currentTime + 0.2, "")
        voice.played = (gain, rate, delay)  # type: ignore[attr-defined]
        made.append(voice)
        return voice

    monkeypatch.setattr(sfx_player, "play_sample", fake_play_sample)
    return made


def make_player(
    context: FakeContext | None,
    clock: list[float] | None = None,
    samples: FakeSamples | None = None,
    **settings: float,
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
    # Where the sound effects go: the audio context and its sound effect bus.
    bus = SimpleNamespace(context=context, sfx=object()) if context is not None else None
    player = SfxPlayer(
        lambda: bus,
        lambda: now[0],
        SfxSettings(**base),
        samples or FakeSamples(),  # type: ignore[arg-type]
    )
    return player, context, now


def test_aud_engine_08_pan_is_zero_in_the_middle_and_reaches_the_maximum_at_the_edges() -> None:
    assert pan_at(50, 100, 0.6) == pytest.approx(0)
    assert pan_at(0, 100, 0.6) == pytest.approx(-0.6)
    assert pan_at(100, 100, 0.6) == pytest.approx(0.6)
    assert pan_at(-20, 100, 0.6) == pytest.approx(-0.6)
    assert pan_at(10, 0, 0.6) == 0


def test_aud_engine_07_a_sound_plays_and_is_counted_by_the_pool(voices: list[FakeVoice]) -> None:
    player, _, _ = make_player(FakeContext())
    assert player.play(sound("shot")) is True
    assert player.voices == 1
    assert len(voices) == 1


def test_aud_engine_07_without_a_context_the_pool_still_decides(voices: list[FakeVoice]) -> None:
    player, _, _ = make_player(None)
    assert player.play(sound("shot")) is True
    assert player.voices == 1
    assert voices == []


def test_aud_engine_07_a_sound_again_too_soon_is_boosted_not_played_twice(
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


@pytest.mark.usefixtures("voices")
def test_aud_engine_07_a_boost_is_capped_at_its_square() -> None:
    context = FakeContext()
    player, _, clock = make_player(context)
    player.play(sound("shot"))
    gain = context.of_kind("gain")[0]
    for step in range(1, 6):
        clock[0] = step * 0.001
        player.play(sound("shot"))
    assert gain.gain.value == pytest.approx(1.25**2)


def test_aud_engine_07_when_the_voices_are_all_taken_a_higher_priority_replaces_the_oldest(
    voices: list[FakeVoice],
) -> None:
    player, _, clock = make_player(FakeContext(), max_voices=1)
    player.play(sound("tick", priority=1))
    clock[0] = 0.1
    assert player.play(sound("boom", priority=2)) is True
    assert voices[0].stops  # the evicted sound is stopped
    assert player.voices == 1


@pytest.mark.usefixtures("voices")
def test_aud_engine_07_a_lower_priority_sound_is_dropped_when_the_voices_are_taken() -> None:
    player, _, clock = make_player(FakeContext(), max_voices=1)
    player.play(sound("boom", priority=5))
    clock[0] = 0.1
    assert player.play(sound("tick", priority=1)) is False


def test_aud_engine_07_a_looping_sound_plays_once_until_it_is_stopped(
    voices: list[FakeVoice],
) -> None:
    player, _, clock = make_player(FakeContext())
    laser = sound("laser", loop=True)
    assert player.play(laser) is True
    clock[0] = 1.0
    assert player.play(laser) is False
    assert player.looping("laser") is True
    player.stop_loop("laser")
    assert player.looping("laser") is False
    assert voices[0].stops


@pytest.mark.usefixtures("voices")
def test_aud_engine_07_stopping_a_loop_that_is_not_playing_does_nothing() -> None:
    player, _, _ = make_player(FakeContext())
    player.stop_loop("laser")
    assert player.looping("laser") is False


@pytest.mark.usefixtures("voices")
def test_aud_engine_08_a_positional_sound_is_panned_when_it_is_off_centre() -> None:
    context = FakeContext()
    player, _, _ = make_player(context)
    player.play(sound("hit", positional=True), pan=0.9)
    panners = context.of_kind("panner")
    assert len(panners) == 1
    assert panners[0].pan.value == pytest.approx(0.9)
    gain = context.of_kind("gain")[0]
    assert gain.connections == [panners[0]]


@pytest.mark.usefixtures("voices")
def test_aud_engine_08_a_positional_sound_in_the_middle_is_not_panned() -> None:
    context = FakeContext()
    player, _, _ = make_player(context)
    player.play(sound("hit", positional=True), pan=0)
    assert context.of_kind("panner") == []


def test_aud_engine_10_stop_all_stops_every_sound_and_forgets_the_loops(
    voices: list[FakeVoice],
) -> None:
    player, _, _ = make_player(FakeContext())
    player.play(sound("shot"))
    player.play(sound("laser", loop=True))
    player.stop_all()
    assert player.voices == 0
    assert player.looping("laser") is False
    assert all(voice.stops for voice in voices)


@pytest.mark.usefixtures("voices")
def test_aud_engine_07_a_sound_that_is_over_is_forgotten_so_its_name_can_play_again() -> None:
    player, _, clock = make_player(FakeContext())
    player.play(sound("shot", seconds=0.1))
    clock[0] = 5.0
    assert player.play(sound("shot")) is True
    assert player.voices == 1


@pytest.mark.usefixtures("voices")
def test_aud_engine_07_each_looping_sound_is_kept_by_its_name() -> None:
    player, _, _ = make_player(FakeContext())
    player.play(sound("laser", loop=True))
    player.play(sound("engine", loop=True))
    assert player.looping("engine") is True
    player.stop_loop("engine")
    assert player.looping("engine") is False
    assert player.looping("laser") is True


def test_aud_engine_07_a_loop_let_go_and_started_again_too_soon_is_neither_played_nor_boosted(
    voices: list[FakeVoice],
) -> None:
    context = FakeContext()
    player, _, clock = make_player(context)
    laser = sound("laser", loop=True)
    player.play(laser)
    gain = context.of_kind("gain")[0]
    player.stop_loop("laser")
    clock[0] = 0.01
    assert player.play(laser) is False
    assert gain.gain.value == 1
    assert len(voices) == 1
    assert player.voices == 0


def test_aud_engine_10_stop_all_without_a_context_forgets_every_sound(
    voices: list[FakeVoice],
) -> None:
    player, _, _ = make_player(None)
    player.play(sound("shot"))
    player.play(sound("laser", loop=True))
    player.stop_all()
    assert player.voices == 0
    assert player.looping("laser") is False
    assert voices == []


def test_aud_engine_04_a_sample_that_is_not_ready_is_silent_but_the_pool_still_decides(
    voices: list[FakeVoice],
) -> None:
    """The sample failed to load or is still decoding: nothing plays, nothing throws."""
    player, _, _ = make_player(FakeContext(), samples=FakeSamples(["shot"]))
    assert player.play(sound("shot")) is True
    assert player.voices == 1
    assert voices == []
    player.stop_all()
    assert player.voices == 0


@pytest.mark.usefixtures("voices")
def test_aud_sfx_09_variants_all_play_and_never_the_same_twice_in_a_row() -> None:
    names: list[str] = []

    class Recording(FakeSamples):
        def get(self, name: str) -> Any | None:
            names.append(name)
            return super().get(name)

    context = FakeContext()
    player, _, clock = make_player(context, samples=Recording(), max_voices=100)
    boom = SoundDesign("boom", ["boom-1", "boom-2", "boom-3"], 0.8, 1, 0.2)
    for step in range(60):
        clock[0] = step
        player.play(boom)
    assert set(names) == {"boom-1", "boom-2", "boom-3"}
    assert all(a != b for a, b in itertools.pairwise(names))


@pytest.mark.usefixtures("voices")
def test_aud_sfx_09_the_same_game_picks_the_same_variants() -> None:
    def picks() -> list[str]:
        names: list[str] = []

        class Recording(FakeSamples):
            def get(self, name: str) -> Any | None:
                names.append(name)
                return super().get(name)

        player, _, clock = make_player(FakeContext(), samples=Recording(), max_voices=100)
        boom = SoundDesign("boom", ["a", "b", "c"], 0.8, 1, 0.2)
        for step in range(10):
            clock[0] = step
            player.play(boom)
        return names

    assert picks() == picks()


def test_aud_sfx_10_a_sound_with_jitter_varies_its_pitch_level_and_start_within_its_spread(
    voices: list[FakeVoice],
) -> None:
    player, _, clock = make_player(FakeContext(), max_voices=100)
    boom = SoundDesign("boom", ["boom"], 0.5, 1, 0.2, jitter=SoundJitter(0.2, 0.3, 0.08))
    for step in range(40):
        clock[0] = step
        player.play(boom)
    plays = [voice.played for voice in voices]  # type: ignore[attr-defined]
    gains = [g for g, _, _ in plays]
    rates = [r for _, r, _ in plays]
    delays = [d for _, _, d in plays]
    assert all(0.35 - 1e-9 <= g <= 0.5 for g in gains)
    assert all(0.8 <= r <= 1.2 for r in rates)
    assert all(0 <= d <= 0.08 for d in delays)
    # Not the same twice: the plays differ from one another.
    assert len(set(rates)) > 30
    assert len(set(gains)) > 30
    assert len(set(delays)) > 30


def test_aud_sfx_10_a_sound_without_jitter_is_played_the_same_each_time(
    voices: list[FakeVoice],
) -> None:
    player, _, clock = make_player(FakeContext(), max_voices=100)
    for step in range(5):
        clock[0] = step
        player.play(sound("click"))
    assert {voice.played for voice in voices} == {(0.8, 1, 0)}  # type: ignore[attr-defined]
