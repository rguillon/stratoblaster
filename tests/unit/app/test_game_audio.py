"""Unit tests of `src/app/game_audio.py`."""
# (P12-R05..R11): which music and sounds play when.

from types import SimpleNamespace

import pytest
from helpers.audio_fakes import FakeContext, FakeVoice

from app.game_audio import GameAudio, GameAudioOptions
from app.menu_state import MenuState
from app.settings_menu import Volumes
from audio import music_player, sfx_player
from audio.audio_bindings import AudioBindings, AudioMix, MusicRequest
from audio.audio_types import INFINITY, Envelope, SoundDesign, ToneLayer, Track
from audio.level_cues import SoundCue
from core.systems.level_run_types import LevelResult


def layer() -> ToneLayer:
    return ToneLayer("sine", 1, 440, None, None, None, Envelope(0, 0, 1, 0.1), None, None)


def sound(name: str, **flags: bool) -> SoundDesign:
    hold = INFINITY if flags.get("loop") else 0.2
    return SoundDesign(name, [layer()], 0.8, 1, hold, **flags)


class FakeMusic:
    """The track of each request: the ids name the request, as the e2e test API does."""

    def __init__(self) -> None:
        self.requests: list[MusicRequest] = []

    def __call__(self, request: MusicRequest) -> Track | None:
        self.requests.append(request)
        if request.kind == "menu":
            return Track("menu", 120, 4, [], True)
        if request.kind == "level":
            return Track(f"level-{request.level_id}", 120, 4, [], True)
        if request.kind == "boss":
            return Track(f"boss-{request.level_id}", 120, 4, [], True)
        return Track(f"jingle-{request.jingle}", 120, 4, [], False)


@pytest.fixture
def voices(monkeypatch: pytest.MonkeyPatch) -> list[FakeVoice]:
    made: list[FakeVoice] = []

    def fake_play_voice(context, destination, layers, options) -> FakeVoice:  # noqa: ANN001
        voice = FakeVoice(options.when + options.hold)
        made.append(voice)
        return voice

    monkeypatch.setattr(music_player, "play_voice", fake_play_voice)
    monkeypatch.setattr(sfx_player, "play_voice", fake_play_voice)
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


def test_p12_r05_before_a_gesture_the_audio_is_not_started() -> None:
    audio, _, ctx = make(can_start=False)
    audio.unlock()
    assert audio.state.context == "none"
    assert ctx.resumed == 0


def test_p12_r05_a_gesture_starts_the_audio_when_it_may() -> None:
    audio, _, _ = make(can_start=True)
    audio.unlock()
    assert audio.state.context == "running"


def test_p12_r05_without_a_context_the_game_is_silent_but_still_runs() -> None:
    audio, music, _ = make(with_bindings=False, web_audio=False)
    audio.menu_changed(menu_state("title"))
    audio.unlock()
    assert audio.state.music is None
    assert audio.state.context == "none"


def test_p12_r11_hiding_the_page_suspends_the_audio() -> None:
    audio, _, ctx = make()
    audio.unlock()
    audio.set_hidden(True)
    assert ctx.suspended == 1


def test_p12_r08_the_menus_play_their_music_and_the_loading_plays_none() -> None:
    audio, music, _ = make()
    audio.menu_changed(menu_state("loading"))
    assert audio.state.music is None
    audio.menu_changed(menu_state("title"))
    assert music.requests[-1].kind == "menu"
    assert audio.state.music == "menu"


def test_p12_r11_the_menu_music_is_not_asked_for_again_while_it_plays() -> None:
    audio, music, _ = make()
    audio.menu_changed(menu_state("title"))
    audio.menu_changed(menu_state("settings"))
    assert [r.kind for r in music.requests].count("menu") == 2


def test_p12_r11_pausing_the_game_pauses_the_music_and_stops_the_sounds(
    voices: list[FakeVoice],
) -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-1")
    audio.menu_changed(menu_state("pause", paused=True))
    assert audio.music.position == 0
    audio.menu_changed(menu_state("game"))
    assert audio.music.track is not None


def test_p12_r07_a_level_plays_its_own_track_from_the_start() -> None:
    audio, _, _ = make()
    audio.level_started("2-3")
    assert audio.state.music == "level-2-3"


def test_p12_r07_a_completed_level_fades_out_and_its_jingle_plays_once() -> None:
    audio, music, _ = make()
    audio.level_started("1-1")
    audio.level_ended(LevelResult("1-1", 9, 9, "complete", 10, False, None))
    assert music.requests[-1].kind == "jingle"
    assert music.requests[-1].jingle == "complete"
    assert audio.state.music == "level-1-1" or audio.state.music is None


def test_p12_r07_a_lost_level_plays_the_game_over_jingle() -> None:
    audio, music, _ = make()
    audio.level_started("1-1")
    audio.level_ended(LevelResult("1-1", 1, 9, "over", 10, False, None))
    assert music.requests[-1].jingle == "over"


def test_p12_r09_a_menu_move_plays_the_menu_sound_at_the_new_volumes(
    voices: list[FakeVoice],
) -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.menu_feedback("down", "moved", Volumes(10, 10))
    assert audio.state.sounds == ["menu-move"]


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
def test_p12_r09_each_menu_feedback_has_its_sound(
    voices: list[FakeVoice], command: str, feedback: str, sound_name: str | None
) -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.menu_feedback(command, feedback, Volumes(5, 5))
    expected = [] if sound_name is None else [sound_name]
    assert audio.state.sounds == expected


def test_p12_r10_the_recent_sounds_are_kept_to_the_last_few(voices: list[FakeVoice]) -> None:
    audio, _, _ = make()
    audio.unlock()
    for _ in range(12):
        audio.menu_feedback("x", "moved", Volumes(5, 5))
        audio.menu_feedback("x", "paused", Volumes(5, 5))
    assert len(audio.state.sounds) <= 32
    assert audio.state.sounds[-1] == "pause"


def test_p12_r09_a_level_cue_plays_its_sound_panned_to_where_it_happened(
    voices: list[FakeVoice], monkeypatch: pytest.MonkeyPatch
) -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-1")

    class Cues:
        beam = None

        def observe(self, run: object) -> list[SoundCue]:
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


def test_p07_r02_a_boss_bar_switches_the_music_to_the_boss_track(voices: list[FakeVoice]) -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-2")
    cues = SimpleNamespace(observe=lambda run: [], beam=None)
    audio._cues = cues  # type: ignore[assignment]
    boss_run = SimpleNamespace(
        fights=SimpleNamespace(bar=object(), defeated=[], final_defeated=False)
    )
    audio.level_step(boss_run)
    assert audio.state.music == "boss-1-2"


def test_p07_r08_a_mini_boss_kill_plays_the_checkpoint_jingle_and_resumes_the_level(
    voices: list[FakeVoice],
) -> None:
    audio, music, _ = make()
    audio.unlock()
    audio.level_started("1-2")
    audio._cues = SimpleNamespace(observe=lambda run: [], beam=None)  # type: ignore[assignment]
    mini = SimpleNamespace(rank="mini")
    run = SimpleNamespace(fights=SimpleNamespace(bar=None, defeated=[mini], final_defeated=False))
    audio.level_step(run)
    assert music.requests[-2].jingle == "checkpoint"
    assert music.requests[-1].kind == "level"


def test_p12_r09_a_laser_hum_plays_while_it_fires_and_stops_when_it_lets_go(
    voices: list[FakeVoice],
) -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-1")
    audio._beam("guns")
    assert audio.state.sounds == ["beam:guns"]
    audio._beam("guns")
    assert audio.state.sounds == ["beam:guns"]
    audio._beam(None)
    assert audio._hum is None


def test_p12_r04_the_volume_settings_reach_the_output(voices: list[FakeVoice]) -> None:
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


def test_p12_r05_the_game_is_silent_before_its_context_exists() -> None:
    audio, _, _ = make(web_audio=False)
    assert audio.state.context == "none"
    audio.update()
    audio.set_volumes(Volumes(3, 3))
    audio.set_hidden(True)
    audio.level_ended(LevelResult("1-1", 0, 0, "over", 0, False, None))


def test_p12_r11_a_sound_that_plays_only_in_a_level_is_not_played_after_it_ends(
    voices: list[FakeVoice],
) -> None:
    audio, _, _ = make()
    audio.unlock()
    audio.level_started("1-1")
    audio.level_ended(LevelResult("1-1", 1, 1, "complete", 0, False, None))
    audio._cues = SimpleNamespace(observe=lambda run: [SoundCue("hit", None)], beam=None)  # type: ignore[assignment]
    audio.level_step(
        SimpleNamespace(fights=SimpleNamespace(bar=None, defeated=[], final_defeated=False))
    )
    assert "hit" not in audio.state.sounds
