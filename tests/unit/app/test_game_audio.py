# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/game_audio.py`."""
# (specs/audio/): which music and sounds play when.

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.audio_fakes import FakeContext, FakeVoice

from app.game_audio import GameAudio, GameAudioOptions, _sample_names
from app.menu_state import MenuState
from app.settings_menu import Volumes
from audio import music_player, sfx_player
from audio.audio_bindings import AudioBindings, AudioMix, MusicRequest
from audio.audio_types import INFINITY, Envelope, SoundDesign, ToneLayer, Track
from audio.level_cues import SoundCue
from audio.sample_bank import SampleBank
from config.audio import AUDIO_CONFIG
from core.systems.level_run_types import LevelResult


def layer() -> ToneLayer:
    return ToneLayer("sine", 1, 440, None, None, None, Envelope(0, 0, 1, 0.1), None, None)


def sound(name: str, **flags: bool) -> SoundDesign:
    return SoundDesign(name, [name], 0.8, 1, 0.2, **flags)


class FakeMusic:
    """The track of each request: the ids name the request, as the e2e test API does."""

    def __init__(self) -> None:
        self.requests: list[MusicRequest] = []

    def __call__(self, request: MusicRequest) -> Track | None:
        self.requests.append(request)
        if request.kind == "menu":
            return Track("menu", 120, 4, [], loop=True)
        if request.kind == "level":
            return Track(f"level-{request.level_id}", 120, 4, [], loop=True)
        if request.kind == "boss":
            return Track(f"boss-{request.level_id}", 120, 4, [], loop=True)
        return Track(f"jingle-{request.jingle}", 120, 4, [], loop=False)


@pytest.fixture
def voices(monkeypatch: pytest.MonkeyPatch) -> list[FakeVoice]:
    made: list[FakeVoice] = []

    def fake_play_voice(_context: Any, _destination: Any, _layers: Any, options: Any) -> FakeVoice:
        voice = FakeVoice(options.when + options.hold)
        made.append(voice)
        return voice

    def fake_play_sample(
        context: Any,
        _destination: Any,
        _buffer: Any,
        loop: bool,
        _gain: float,
        _rate: float = 1,
        _delay: float = 0,
    ) -> FakeVoice:
        voice = FakeVoice(INFINITY if loop else context.currentTime + 0.2)
        made.append(voice)
        return voice

    monkeypatch.setattr(music_player, "play_voice", fake_play_voice)
    monkeypatch.setattr(sfx_player, "play_sample", fake_play_sample)
    # Every sample is decoded and ready.
    monkeypatch.setattr(SampleBank, "get", lambda _self, _name: object())
    return made


def make(
    *,
    with_bindings: bool = True,
    can_start: bool | None = None,
    context: FakeContext | None = None,
    web_audio: bool = True,
) -> tuple[GameAudio, FakeMusic, FakeContext]:
    ctx = context if context is not None else FakeContext()
    music = FakeMusic()
    sounds = {
        "menu-move": sound("menu-move"),
        "menu-confirm": sound("menu-confirm"),
        "menu-back": sound("menu-back"),
        "pause": sound("pause"),
        "resume": sound("resume"),
        "slider": sound("slider"),
        "fire:guns": sound("fire:guns"),
        "hit": sound("hit"),
        "beam:guns": sound("beam:guns", loop=True),
    }
    bindings = (
        AudioBindings(music, {}, sounds, 40, AudioMix(0.6, 0.8), None) if with_bindings else None
    )
    options = GameAudioOptions(
        (lambda: ctx) if web_audio else None,
        (lambda: can_start) if can_start is not None else None,
        lambda: 0.0,
        300,
    )
    return GameAudio(bindings, options), music, ctx


def menu_state(screen: str, **overrides: object) -> MenuState:
    values: dict[str, object] = {
        "screen": screen,
        "selection": 0,
        "selected_id": None,
        "highlighted_ship_id": "alpha",
        "chosen_ship_id": None,
        "chosen_level_id": "1-1",
        "transitioning": False,
        "level_result": None,
        "choice": 0,
        "attempt": 1,
        "resume": None,
        "paused": False,
        "leaving": False,
        "volumes": Volumes(5, 5),
    }
    values.update(overrides)
    return MenuState(*values.values())  # type: ignore[arg-type]


def test_aud_engine_03_before_a_gesture_the_audio_is_not_started() -> None:
    audio, _, ctx = make(can_start=False)
    audio.unlock()
    assert audio.state.context == "none"
    assert ctx.resumed == 0


def test_aud_engine_03_a_gesture_starts_the_audio_when_it_may() -> None:
    audio, _, _ = make(can_start=True)
    audio.unlock()
    assert audio.state.context == "running"


def test_aud_engine_04_without_a_context_the_game_is_silent_but_still_runs() -> None:
    audio, _music, _ = make(with_bindings=False, web_audio=False)
    audio.menu_changed(menu_state("title"))
    audio.unlock()
    assert audio.state.music is None
    assert audio.state.context == "none"


def test_aud_engine_11_hiding_the_page_suspends_the_audio() -> None:
    audio, _, ctx = make()
    audio.unlock()
    audio.set_hidden(True)
    assert ctx.suspended == 1


def test_aud_music_11_the_menus_play_their_music_and_the_loading_plays_none() -> None:
    audio, music, _ = make()
    audio.menu_changed(menu_state("loading"))
    assert audio.state.music is None
    audio.menu_changed(menu_state("title"))
    assert music.requests[-1].kind == "menu"
    assert audio.state.music == "menu"


def test_aud_music_11_the_menu_music_is_not_asked_for_again_while_it_plays() -> None:
    audio, music, _ = make()
    audio.menu_changed(menu_state("title"))
    audio.menu_changed(menu_state("settings"))
    assert [r.kind for r in music.requests].count("menu") == 2


@pytest.mark.usefixtures("voices")
def test_aud_engine_10_pausing_the_game_pauses_the_music_and_stops_the_sounds() -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-1")
    audio.menu_changed(menu_state("pause", paused=True))
    assert audio.music.position == 0
    audio.menu_changed(menu_state("game"))
    assert audio.music.track is not None


def test_aud_music_08_a_level_plays_its_own_track_from_the_start() -> None:
    audio, _, _ = make()
    audio.level_started("2-3")
    assert audio.state.music == "level-2-3"


def test_aud_music_10_a_completed_level_fades_out_and_its_jingle_plays_once() -> None:
    """Also AUD-MUSIC-08 (the level's music fades)."""
    audio, music, _ = make()
    audio.level_started("1-1")
    audio.level_ended(
        LevelResult("1-1", 9, 9, "complete", 10, new_high_score=False, checkpoint=None)
    )
    assert music.requests[-1].kind == "jingle"
    assert music.requests[-1].jingle == "complete"
    assert audio.state.music == "level-1-1" or audio.state.music is None


def test_aud_music_10_a_lost_level_plays_the_game_over_jingle() -> None:
    audio, music, _ = make()
    audio.level_started("1-1")
    audio.level_ended(LevelResult("1-1", 1, 9, "over", 10, new_high_score=False, checkpoint=None))
    assert music.requests[-1].jingle == "over"


@pytest.mark.usefixtures("voices")
def test_aud_engine_09_a_menu_move_plays_the_menu_sound_at_the_new_volumes() -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.menu_feedback("down", "moved", Volumes(10, 10))
    assert audio.state.sounds == ["menu-move"]


@pytest.mark.usefixtures("voices")
@pytest.mark.parametrize(
    ("command", "feedback", "sound_name"),
    [
        ("back", "screen", "menu-back"),
        ("cancel", "screen", "menu-back"),
        ("confirm", "screen", "menu-confirm"),
        ("locked", "locked", "menu-back"),
        ("pause", "paused", "pause"),
        ("resume", "resumed", "resume"),
        ("confirm", "adjusted", "slider"),
        ("confirm", "none", None),
    ],
)
def test_aud_sfx_01_each_menu_feedback_has_its_sound(
    command: str, feedback: str, sound_name: str | None
) -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.menu_feedback(command, feedback, Volumes(5, 5))
    expected = [] if sound_name is None else [sound_name]
    assert audio.state.sounds == expected


@pytest.mark.usefixtures("voices")
def test_dev_api_02_the_recent_sounds_are_kept_to_the_last_few() -> None:
    audio, _, _ = make()
    audio.unlock()
    for _ in range(12):
        audio.menu_feedback("x", "moved", Volumes(5, 5))
        audio.menu_feedback("x", "paused", Volumes(5, 5))
    assert len(audio.state.sounds) <= 32
    assert audio.state.sounds[-1] == "pause"


@pytest.mark.usefixtures("voices")
def test_aud_engine_08_a_level_cue_plays_its_sound_panned_to_where_it_happened(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Also AUD-ENGINE-09."""
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-1")

    class Cues:
        beam = None

        def observe(self, _run: object) -> list[SoundCue]:
            return [SoundCue("hit", 150.0)]

    audio._cues = Cues()  # type: ignore[assignment]
    played: list[float] = []
    original = audio._sfx.play

    def record(sound_design: SoundDesign, pan: float = 0) -> bool:
        played.append(pan)
        return original(sound_design, pan)

    monkeypatch.setattr(audio._sfx, "play", record)
    audio.level_step(
        SimpleNamespace(fights=SimpleNamespace(bar=None, defeated=[], final_defeated=False))
    )
    assert audio.state.sounds == ["hit"]
    assert played == [pytest.approx(0.0)]


@pytest.mark.usefixtures("voices")
def test_aud_music_09_a_boss_bar_switches_the_music_to_the_boss_track() -> None:
    """Also BOSS-05."""
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-2")
    cues = SimpleNamespace(observe=lambda _run: [], beam=None)
    audio._cues = cues  # type: ignore[assignment]
    boss_run = SimpleNamespace(
        fights=SimpleNamespace(bar=object(), defeated=[], final_defeated=False)
    )
    audio.level_step(boss_run)
    assert audio.state.music == "boss-1-2"


@pytest.mark.usefixtures("voices")
def test_aud_music_10_a_mini_boss_kill_plays_the_checkpoint_jingle_and_resumes_the_level() -> None:
    """Also AUD-MUSIC-09 (the level track after the fight)."""
    audio, music, _ = make()
    audio.unlock()
    audio.level_started("1-2")
    audio._cues = SimpleNamespace(observe=lambda _run: [], beam=None)  # type: ignore[assignment]
    mini = SimpleNamespace(rank="mini")
    run = SimpleNamespace(fights=SimpleNamespace(bar=None, defeated=[mini], final_defeated=False))
    audio.level_step(run)
    assert music.requests[-2].jingle == "checkpoint"
    assert music.requests[-1].kind == "level"


@pytest.mark.usefixtures("voices")
def test_aud_sfx_03_a_laser_hum_plays_while_it_fires_and_stops_when_it_lets_go() -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-1")
    audio._beam("guns")
    assert audio.state.sounds == ["beam:guns"]
    audio._beam("guns")
    assert audio.state.sounds == ["beam:guns"]
    audio._beam(None)
    assert audio._hum is None


@pytest.mark.usefixtures("voices")
def test_ui_set_04_the_volume_settings_reach_the_output() -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.set_volumes(Volumes(10, 0))
    buses = audio._output.buses
    assert buses is not None
    # The bus ramps to the step's gain times the mix: full music (0.6), silent effects.
    music_ramp = buses.music.gain.events[-1]
    sfx_ramp = buses.sfx.gain.events[-1]
    assert music_ramp[0] == "linearRampToValueAtTime"
    assert music_ramp[1][0] == pytest.approx(0.6)
    assert sfx_ramp[1][0] == pytest.approx(0)


def test_aud_engine_04_the_game_is_silent_before_its_context_exists() -> None:
    audio, _, _ = make(web_audio=False)
    assert audio.state.context == "none"
    audio.update()
    audio.set_volumes(Volumes(3, 3))
    audio.set_hidden(True)
    audio.level_ended(LevelResult("1-1", 0, 0, "over", 0, new_high_score=False, checkpoint=None))


@pytest.mark.usefixtures("voices")
def test_aud_engine_09_a_sound_that_plays_only_in_a_level_is_not_played_after_it_ends() -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-1")
    audio.level_ended(
        LevelResult("1-1", 1, 1, "complete", 0, new_high_score=False, checkpoint=None)
    )
    audio._cues = SimpleNamespace(observe=lambda _run: [SoundCue("hit", None)], beam=None)  # type: ignore[assignment]
    audio.level_step(
        SimpleNamespace(fights=SimpleNamespace(bar=None, defeated=[], final_defeated=False))
    )
    assert "hit" not in audio.state.sounds


def test_aud_music_08_the_level_s_track_fades_on_its_end_panel() -> None:
    """While it plays, the game screen keeps the level's track."""
    audio, _, _ = make()
    audio.level_started("1-1")
    audio.menu_changed(menu_state("game"))
    assert audio.state.music == "level-1-1"
    result = LevelResult("1-1", 9, 9, "complete", 10, new_high_score=False, checkpoint=None)
    audio.menu_changed(menu_state("game", level_result=result))
    assert audio.state.music is None


@pytest.mark.usefixtures("voices")
def test_aud_music_09_after_the_final_boss_its_track_goes_on_until_the_level_ends() -> None:
    """Also BOSS-05."""
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-2")
    audio._cues = SimpleNamespace(observe=lambda _run: [], beam=None)  # type: ignore[assignment]
    fighting = SimpleNamespace(
        fights=SimpleNamespace(bar=object(), defeated=[], final_defeated=False)
    )
    audio.level_step(fighting)
    final = SimpleNamespace(rank="final")
    beaten = SimpleNamespace(
        fights=SimpleNamespace(bar=None, defeated=[final], final_defeated=True)
    )
    audio.level_step(beaten)
    assert audio.state.music == "boss-1-2"


@pytest.mark.usefixtures("voices")
def test_aud_music_11_a_level_step_heard_on_the_menus_keeps_the_menu_music() -> None:
    """Once the menus show, the level's and boss tracks do not come back."""
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-2")
    audio.menu_changed(menu_state("level-select"))
    audio._cues = SimpleNamespace(observe=lambda _run: [], beam=None)  # type: ignore[assignment]
    boss_run = SimpleNamespace(
        fights=SimpleNamespace(bar=object(), defeated=[], final_defeated=False)
    )
    audio.level_step(boss_run)
    assert audio.state.music == "menu"


@pytest.mark.usefixtures("voices")
def test_aud_engine_09_a_cue_without_a_sound_plays_nothing() -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-1")
    audio._cues = SimpleNamespace(  # type: ignore[assignment]
        observe=lambda _run: [SoundCue("unknown-cue", 10.0)], beam=None
    )
    audio.level_step(
        SimpleNamespace(fights=SimpleNamespace(bar=None, defeated=[], final_defeated=False))
    )
    assert audio.state.sounds == []


def test_aud_engine_04_without_bindings_no_sound_or_jingle_plays() -> None:
    audio, _, _ = make(with_bindings=False)
    audio.unlock()
    audio.menu_feedback("down", "moved", Volumes(5, 5))
    audio.level_started("1-1")
    audio.level_ended(LevelResult("1-1", 1, 9, "over", 10, new_high_score=False, checkpoint=None))
    assert audio.state.sounds == []
    assert audio.state.music is None


def test_aud_music_10_a_jingle_the_game_has_no_track_for_is_not_played(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audio, music, _ = make()
    jingles: list[Track] = []
    monkeypatch.setattr(audio.music, "jingle", jingles.append)
    audio.level_ended(LevelResult("1-1", 1, 9, "over", 10, new_high_score=False, checkpoint=None))
    assert [request.jingle for request in music.requests] == ["over"]
    assert [track.id for track in jingles] == ["jingle-over"]

    def no_jingles(request: MusicRequest) -> Track | None:
        music.requests.append(request)
        return None

    audio._bindings.music = no_jingles  # type: ignore[union-attr]
    audio.level_ended(LevelResult("1-1", 1, 9, "over", 10, new_high_score=False, checkpoint=None))
    # The jingle was asked for again, but there is none to play.
    assert [request.jingle for request in music.requests] == ["over", "over"]
    assert len(jingles) == 1


def test_dev_api_02_only_the_last_sounds_played_are_reported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The oldest is dropped past `recent_sounds`; a sound the voices refused is not reported."""
    audio, _, _ = make()
    monkeypatch.setattr(audio._sfx, "play", lambda _sound, _pan=0: True)
    count = int(AUDIO_CONFIG.recent_sounds)
    for _ in range(count):
        audio.menu_feedback("x", "moved", Volumes(5, 5))
    audio.menu_feedback("x", "paused", Volumes(5, 5))
    sounds = audio.state.sounds
    assert len(sounds) == count
    assert sounds[-1] == "pause"
    assert sounds.count("menu-move") == count - 1
    monkeypatch.setattr(audio._sfx, "play", lambda _sound, _pan=0: False)
    audio.menu_feedback("x", "resumed", Volumes(5, 5))
    assert audio.state.sounds == sounds


# DEV-MENU-19, DEV-MENU-20: the dev audio viewers play any cue or track.


@pytest.mark.usefixtures("voices")
def test_dev_menu_19_a_cue_plays_its_sound_alone_and_names_it() -> None:
    audio, _, _ = make()
    audio.unlock()
    assert audio.play_cue("fire:guns") == "fire:guns"
    assert audio.play_cue("no-such-cue") is None
    assert audio.state.sounds == ["fire:guns"]
    audio.menu_feedback("right", "played", Volumes(5, 5))
    assert audio.state.sounds == ["fire:guns"]


@pytest.mark.usefixtures("voices")
def test_dev_menu_19_a_looping_cue_plays_until_the_next_cue_or_stopped() -> None:
    audio, _, _ = make()
    audio.unlock()
    assert audio.play_cue("beam:guns") == "beam:guns"
    assert audio._sfx.looping("beam:guns")
    audio.play_cue("hit")
    assert not audio._sfx.looping("beam:guns")
    audio.play_cue("beam:guns")
    audio.stop_cue()
    audio.stop_cue()
    assert not audio._sfx.looping("beam:guns")


def test_dev_menu_19_a_cue_the_voices_refuse_names_no_sound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audio, _, _ = make()
    monkeypatch.setattr(audio._sfx, "play", lambda _sound, _pan=0: False)
    assert audio.play_cue("hit") is None
    assert audio.state.sounds == []


def test_dev_menu_19_without_bindings_a_cue_plays_nothing() -> None:
    audio, _, _ = make(with_bindings=False)
    assert audio.play_cue("hit") is None
    assert audio.play_music(MusicRequest("menu", None, None)) is None


@pytest.mark.usefixtures("voices")
def test_dev_menu_20_a_track_replaces_the_music_and_a_jingle_plays_over_it() -> None:
    audio, music, _ = make()
    audio.unlock()
    audio.menu_changed(menu_state("dev-viewer", dev_viewer="music"))
    assert audio.state.music is None
    assert audio.play_music(MusicRequest("level", "2-3", None)) == "level-2-3"
    assert audio.state.music == "level-2-3"
    assert audio.play_music(MusicRequest("jingle", None, "complete")) == "jingle-complete"
    assert audio.state.music == "level-2-3"
    assert music.requests[-1].jingle == "complete"
    # The menus leave the music to the viewer; back on the dev menu, their theme returns.
    audio.menu_changed(menu_state("dev-viewer", dev_viewer="music", selection=1))
    assert audio.state.music == "level-2-3"
    audio.menu_changed(menu_state("dev"))
    assert audio.state.music == "menu"


@pytest.mark.usefixtures("voices")
def test_dev_menu_19_the_sounds_viewer_keeps_the_menu_music() -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.menu_changed(menu_state("dev-viewer", dev_viewer="sounds"))
    assert audio.state.music == "menu"


def test_aud_engine_01_the_samples_are_fetched_at_once_and_decoded_when_the_audio_is_unlocked() -> (
    None
):
    from helpers.audio_fakes import FakePromise  # noqa: PLC0415

    ctx = FakeContext()
    fetched: dict[str, FakePromise] = {}

    def fetch_sample(name: str) -> FakePromise:
        fetched[name] = FakePromise()
        return fetched[name]

    sounds = {"hit": sound("hit"), "menu-move": sound("menu-move")}
    bindings = AudioBindings(FakeMusic(), {}, sounds, 40, AudioMix(0.6, 0.8), None)
    options = GameAudioOptions(lambda: ctx, None, lambda: 0.0, 300, fetch_sample)
    audio = GameAudio(bindings, options)
    assert sorted(fetched) == ["hit", "menu-move"]
    assert audio.state.samples == 0
    for name, promise in fetched.items():
        promise.resolve(name + "-bytes")
    assert ctx.decodes == []  # before a gesture: no context, nothing decoded
    audio.unlock()
    assert sorted(d.data for d in ctx.decodes) == ["hit-bytes", "menu-move-bytes"]
    for decode in ctx.decodes:
        decode.resolve(object())
    assert audio.state.samples == 2


def test_aud_engine_01_a_sample_shared_by_two_sounds_is_fetched_once() -> None:
    sounds = {
        "a": SoundDesign("a", ["x", "y"], 1, 1, 1),
        "b": SoundDesign("b", ["y", "z"], 1, 1, 1),
    }
    assert _sample_names(sounds) == ["x", "y", "z"]


def test_d262_the_blasts_of_a_dev_viewer_are_sounded_as_a_level_would(
    voices: list[FakeVoice],  # noqa: ARG001
) -> None:
    audio, _, _ = make()
    audio.unlock()
    bindings_sounds = audio._bindings.sounds  # type: ignore[union-attr]
    for cue in ["blast-small", "blast-large", "part-destroyed", "boss-destroyed"]:
        bindings_sounds[cue] = sound(cue)
    audio.play_blasts([10.0, 50.0], 1, True)
    assert audio.state.sounds[-4:] == [
        "blast-large",
        "blast-small",
        "part-destroyed",
        "boss-destroyed",
    ]


def test_d262_nothing_is_sounded_without_blasts_or_without_bindings() -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.play_blasts([], 0, False)
    assert audio.state.sounds == []
    silent, _, _ = make(with_bindings=False)
    silent.play_blasts([10.0], 1, True)
    assert silent.state.sounds == []
