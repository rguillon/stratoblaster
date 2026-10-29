"""Engine tunables of the audio layer and the volume settings (P12-R04, P12-R05, P12-R10), ported
from `config/audio.ts`.

The music, the sounds and their own levels are game data (`src/game/view/audio/`).
"""


class AudioVolumes:
    """`defaultVolumes`: the music and sound effect levels before anything is saved."""

    def __init__(self, music: float, sfx: float) -> None:
        self.music = music
        self.sfx = sfx


class AudioLimiter:
    """Master limiter: a fast compressor with a high ratio just under the peak."""

    def __init__(
        self, knee_db: float, ratio: float, attack_seconds: float, release_seconds: float
    ) -> None:
        self.knee_db = knee_db
        self.ratio = ratio
        self.attack_seconds = attack_seconds
        self.release_seconds = release_seconds


class AudioConfig:
    """The audio tunables, in the order of `AUDIO_CONFIG`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        volume_steps: float,
        default_volumes: AudioVolumes,
        master_peak_db: float,
        limiter: AudioLimiter,
        lookahead_seconds: float,
        schedule_interval_seconds: float,
        fade_seconds: float,
        crossfade_seconds: float,
        pause_fade_seconds: float,
        max_voices: float,
        retrigger_seconds: float,
        retrigger_boost: float,
        pan_max: float,
        recent_sounds: float,
    ) -> None:
        # `volume_steps`: the sliders go from 0 (silent) to this step.
        self.volume_steps = volume_steps
        # `music_volume_default`, `sfx_volume_default`: before anything is saved.
        self.default_volumes = default_volumes
        # `master_peak`: the limiter keeps the output under this level, in dBFS.
        self.master_peak_db = master_peak_db
        self.limiter = limiter
        # `scheduler lookahead`: notes are scheduled this far ahead, checked this often (D-120).
        self.lookahead_seconds = lookahead_seconds
        self.schedule_interval_seconds = schedule_interval_seconds
        # `music_fade`, `music_crossfade`.
        self.fade_seconds = fade_seconds
        self.crossfade_seconds = crossfade_seconds
        # How fast the music goes quiet when the game pauses, and comes back.
        self.pause_fade_seconds = pause_fade_seconds
        # `sfx_voices_max`, `sfx_retrigger_min`.
        self.max_voices = max_voices
        self.retrigger_seconds = retrigger_seconds
        # A sound started again within `retrigger_seconds` is made this much louder instead (x).
        self.retrigger_boost = retrigger_boost
        # `sfx_pan_max`: sounds at the playfield's edges are panned this far.
        self.pan_max = pan_max
        # How many sound effect names the e2e test API keeps (P12-R12).
        self.recent_sounds = recent_sounds


AUDIO_CONFIG = AudioConfig(
    10,
    AudioVolumes(6, 8),
    -1,
    AudioLimiter(0, 20, 0.003, 0.25),
    1.5,
    0.025,
    1,
    1,
    0.05,
    16,
    0.03,
    1.25,
    0.6,
    32,
)
