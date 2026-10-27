/**
 * Engine tunables of the audio layer and the volume settings (P12-R04, P12-R05, P12-R10).
 * The music, the sounds and their own levels are game data (`src/game/view/audio/`).
 */
export const AUDIO_CONFIG = {
  /** `volume_steps`: the sliders go from 0 (silent) to this step. */
  volumeSteps: 10,
  /** `music_volume_default`, `sfx_volume_default`: before anything is saved. */
  defaultVolumes: { music: 6, sfx: 8 },
  /** `master_peak`: the limiter keeps the output under this level, in dBFS. */
  masterPeakDb: -1,
  /** Master limiter: a fast compressor with a high ratio just under the peak. */
  limiter: { kneeDb: 0, ratio: 20, attackSeconds: 0.003, releaseSeconds: 0.25 },
  /** `scheduler lookahead`: notes are scheduled this far ahead, checked this often. */
  lookaheadSeconds: 0.1,
  scheduleIntervalSeconds: 0.025,
  /** P13-R03: music scheduled this far ahead before each level loading step, which may stall. */
  stallCoverSeconds: 1.5,
  /** `music_fade`, `music_crossfade`. */
  fadeSeconds: 1,
  crossfadeSeconds: 1,
  /** How fast the music goes quiet when the game pauses, and comes back. */
  pauseFadeSeconds: 0.05,
  /** `sfx_voices_max`, `sfx_retrigger_min`. */
  maxVoices: 16,
  retriggerSeconds: 0.03,
  /** A sound started again within `retriggerSeconds` is made this much louder instead (×). */
  retriggerBoost: 1.25,
  /** `sfx_pan_max`: sounds at the playfield's edges are panned this far. */
  panMax: 0.6,
  /** How many sound effect names the e2e test API keeps (P12-R12). */
  recentSounds: 32,
} as const;
