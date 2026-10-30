"""The game's audio (P12-R05..R11): which music plays on which
screen, the level and boss tracks following the boss bar, the jingles, the sound effects of the
level's cues and of the menus, and pausing it all with the game. It only reads the menu and core
state (ENG-11).

Options are a plain class (`GameAudioOptions`), passed by position (Transcrypt has no keyword
arguments). `create_context` and `can_start` are None when omitted.
"""

from org.transcrypt.stubs.browser import __pragma__

from audio.audio_bindings import AudioBindings, AudioMix, MusicRequest
from audio.audio_output import AudioOutput, AudioOutputOptions, volume_gain
from audio.audio_types import INFINITY
from audio.level_cues import LevelCues
from audio.music_player import MusicPlayer, MusicTimings
from audio.sfx_player import SfxPlayer, SfxSettings, pan_at
from config.audio import AUDIO_CONFIG

__pragma__("skip")
from typing import Any  # noqa: E402

from app.menu_state import MenuFeedback, MenuState  # noqa: E402
from app.settings_menu import Volumes  # noqa: E402
from core.systems.level_run import LevelRun  # noqa: E402
from core.systems.level_run_types import LevelResult  # noqa: E402
from input.menu_action import MenuCommand  # noqa: E402

__pragma__("noskip")


class GameAudioOptions:
    """Browser pieces the audio needs."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        create_context: Any | None,
        can_start: Any | None,
        clock: Any,
        screen_width: float,
    ) -> None:
        # Creates the Web Audio context; None without Web Audio (the game is silent).
        self.create_context = create_context
        # Whether the page may start audio now (a user gesture is going on). Always when None.
        self.can_start = can_start
        # Seconds, for the sound effect limits (P12-R10).
        self.clock = clock
        # Width of the playfield, to pan sounds with their position (P12-R09).
        self.screen_width = screen_width


class GameAudioState:
    """What the e2e test API reports about the audio (P12-R12)."""

    def __init__(self, music: str | None, sounds: list[str], context: str) -> None:
        # Id of the music playing (`menu`, `level-2-3`, `boss-2`), or None.
        self.music = music
        # Names of the last sound effects played, most recent last.
        self.sounds = sounds
        # The audio context's state: `none` before the first user gesture.
        self.context = context


# The sound of a menu feedback (P12-R09); `screen` depends on the command, see `_menu_cue`.
_MENU_CUES = {
    "moved": "menu-move",
    "locked": "menu-back",
    "paused": "pause",
    "resumed": "resume",
    "adjusted": "slider",
}


def _menu_cue(command: MenuCommand, feedback: MenuFeedback) -> str | None:
    """Menu sounds by what a command did (P12-R09)."""
    if feedback == "screen":
        return "menu-back" if command in ["back", "cancel"] else "menu-confirm"
    return _MENU_CUES.get(feedback)


class GameAudio:
    """The game's audio (see the module doc)."""

    def __init__(self, bindings: AudioBindings | None, options: GameAudioOptions) -> None:
        self._bindings = bindings
        self._options = options
        self._recent: list[str] = []
        self._cues: LevelCues | None = None
        self._level_id: str | None = None
        self._paused = False
        self._ended = False
        self._defeated = 0
        # Name of the beam hum playing, if any.
        self._hum: str | None = None
        mix = bindings.mix if bindings is not None else AudioMix(1, 1)
        effects = bindings.effects if bindings is not None else None
        reverb_seconds = effects.reverb_seconds if effects is not None else None
        self._output = AudioOutput(
            AudioOutputOptions(
                options.create_context,
                mix,
                AUDIO_CONFIG.master_peak_db,
                AUDIO_CONFIG.limiter,
                reverb_seconds,
            )
        )
        instruments = bindings.instruments if bindings is not None else {}
        self._music = MusicPlayer(
            lambda: self._output.buses,
            instruments,
            MusicTimings(AUDIO_CONFIG.lookahead_seconds, AUDIO_CONFIG.pause_fade_seconds),
            effects,
        )
        self._sfx = SfxPlayer(
            lambda: self._output.buses,
            options.clock,
            SfxSettings(
                AUDIO_CONFIG.max_voices,
                AUDIO_CONFIG.retrigger_seconds,
                AUDIO_CONFIG.retrigger_boost,
                AUDIO_CONFIG.pan_max,
                AUDIO_CONFIG.pause_fade_seconds,
            ),
        )

    @property
    def state(self) -> GameAudioState:
        track = self._music.track
        music = track.id if track is not None else None
        return GameAudioState(music, self._recent[:], self._output.state)

    @property
    def music(self) -> MusicPlayer:
        """The music player, for its position (tests)."""
        return self._music

    def unlock(self) -> None:
        """A user gesture: the audio may start (P12-R05)."""
        can_start = self._options.can_start
        if can_start is not None and not can_start():
            return
        self._output.unlock()

    def set_hidden(self, hidden: bool) -> None:
        """The page is hidden or shown again (P12-R11)."""
        self._output.set_hidden(hidden)

    def set_volumes(self, volumes: Volumes) -> None:
        steps = AUDIO_CONFIG.volume_steps
        self._output.set_volumes(volume_gain(volumes.music, steps), volume_gain(volumes.sfx, steps))

    def update(self) -> None:
        """Schedules the music ahead (every frame, and on a timer)."""
        self._music.update()

    def menu_changed(self, state: MenuState) -> None:
        """The menus changed (P12-R08, P12-R11): the music of their screen, pausing with the
        game."""
        self.set_volumes(state.volumes)
        if state.paused != self._paused:
            self._set_paused(state.paused)
        if state.paused:
            return
        if state.screen == "loading":
            return
        if state.screen == "game":
            if state.level_result is not None:
                self._want(None, AUDIO_CONFIG.fade_seconds)
            return
        self._level_id = None
        self._want(MusicRequest("menu", None, None), AUDIO_CONFIG.crossfade_seconds)

    def menu_feedback(self, command: MenuCommand, feedback: MenuFeedback, volumes: Volumes) -> None:
        """What a menu command did: its sound, at the volumes it may have just set (P12-R04)."""
        self.set_volumes(volumes)
        cue = _menu_cue(command, feedback)
        if cue is not None:
            self._cue(cue, None)

    def level_started(self, level_id: str) -> None:
        """A level starts, or starts again from its checkpoint: its track from the start
        (P12-R07)."""
        self._level_id = level_id
        bindings = self._bindings
        radius = bindings.large_blast_radius if bindings is not None else INFINITY
        self._cues = LevelCues(radius)
        self._ended = False
        self._defeated = 0
        self._stop_beam()
        self._play(MusicRequest("level", level_id, None), AUDIO_CONFIG.crossfade_seconds)

    def level_step(self, run: LevelRun) -> None:
        """A level step was run: its sounds, and the music following the boss fights."""
        cues = self._cues
        if cues is None or self._paused or self._ended:
            return
        for cue in cues.observe(run):
            self._cue(cue.cue, cue.x)
        self._beam(cues.beam)
        self._boss_music(run)

    def level_ended(self, result: LevelResult) -> None:
        """The level is complete or over (P12-R07): the music fades, its jingle plays once."""
        self._ended = True
        self._stop_beam()
        self._want(None, AUDIO_CONFIG.fade_seconds)
        self._jingle("complete" if result.outcome == "complete" else "over")

    def _set_paused(self, paused: bool) -> None:
        self._paused = paused
        if paused:
            self._music.pause()
            self._sfx.stop_all()
        else:
            self._music.resume()

    def _boss_music(self, run: LevelRun) -> None:
        """The boss track while a boss bar shows, the level track (from its start) after it."""
        level_id = self._level_id
        if level_id is None:
            return
        defeated = run.fights.defeated
        count = len(defeated)
        if count > self._defeated and defeated[count - 1].rank == "mini":
            self._jingle("checkpoint")
        self._defeated = count
        # After the final boss, its track goes on until the level ends.
        if run.fights.bar is not None:
            self._want(MusicRequest("boss", level_id, None), AUDIO_CONFIG.crossfade_seconds)
        elif not run.fights.final_defeated:
            self._want(MusicRequest("level", level_id, None), AUDIO_CONFIG.crossfade_seconds)

    def _beam(self, weapon: str | None) -> None:
        """The laser's hum plays while it fires."""
        hum = None
        if weapon is not None and self._bindings is not None:
            hum = self._bindings.sounds.get("beam:" + weapon)
        hum_name = hum.name if hum is not None else None
        if self._hum is not None and self._hum != hum_name:
            self._sfx.stop_loop(self._hum)
            self._hum = None
        if hum is None or self._sfx.looping(hum.name):
            return
        self._played(hum.name, self._sfx.play(hum, 0))
        self._hum = hum.name

    def _stop_beam(self) -> None:
        self._beam(None)

    def _cue(self, cue: str, x: float | None) -> None:
        if self._bindings is None:
            return
        sound = self._bindings.sounds.get(cue)
        if sound is None:
            return
        pan = 0.0
        if x is not None:
            pan = pan_at(x, self._options.screen_width, AUDIO_CONFIG.pan_max)
        self._played(sound.name, self._sfx.play(sound, pan))

    def _played(self, name: str, played: bool) -> None:
        if not played:
            return
        self._recent.append(name)
        if len(self._recent) > AUDIO_CONFIG.recent_sounds:
            self._recent.pop(0)

    def _track_of(self, request: MusicRequest | None) -> Any:
        """The track for `request` (None: silence, or no bindings)."""
        if request is None or self._bindings is None:
            return None
        return self._bindings.music(request)

    def _want(self, request: MusicRequest | None, fade: float) -> None:
        """Plays the request's track unless it already plays."""
        track = self._track_of(request)
        wanted = track.id if track is not None else None
        current = self._music.track
        current_id = current.id if current is not None else None
        if wanted == current_id:
            return
        self._music.play(track, fade)

    def _play(self, request: MusicRequest, fade: float) -> None:
        """Plays the request's track from its start, even if it already plays."""
        self._music.play(self._track_of(request), fade)

    def _jingle(self, jingle: str) -> None:
        if self._bindings is None:
            return
        track = self._bindings.music(MusicRequest("jingle", None, jingle))
        if track is not None:
            self._music.jingle(track)
