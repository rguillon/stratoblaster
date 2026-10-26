import type { LevelRun, LevelResult } from '../core/systems/level-run';
import type { AudioBindings, MusicRequest } from '../audio/audio-bindings';
import { AudioOutput, volumeGain } from '../audio/audio-output';
import { LevelCues, type SoundCue } from '../audio/level-cues';
import { MusicPlayer } from '../audio/music-player';
import { panAt, SfxPlayer } from '../audio/sfx-player';
import { AUDIO_CONFIG } from '../config/audio';
import type { MenuCommand } from '../input/menu-action';
import type { MenuFeedback, MenuState } from './menu-flow';
import type { Volumes } from './settings-menu';

/** Browser pieces the audio needs, injected so tests can use fakes. */
export interface GameAudioOptions {
  /** Creates the Web Audio context; none without Web Audio (the game is silent). */
  readonly createContext?: () => AudioContext;
  /** Whether the page may start audio now (a user gesture is going on). Always when omitted. */
  readonly canStart?: () => boolean;
  /** Seconds, for the sound effect limits (P12-R10). */
  readonly clock: () => number;
  /** Width of the playfield, to pan sounds with their position (P12-R09). */
  readonly screenWidth: number;
}

/** What the e2e test API reports about the audio (P12-R12). */
export interface GameAudioState {
  /** Id of the music playing (`menu`, `level-2-3`, `boss-2`), or null. */
  readonly music: string | null;
  /** Names of the last sound effects played, most recent last. */
  readonly sounds: readonly string[];
  /** The audio context's state: `none` before the first user gesture. */
  readonly context: AudioContextState | 'none';
}

/** Menu sounds by what a command did (P12-R09). */
function menuCue(command: MenuCommand, feedback: MenuFeedback): string | undefined {
  const back = command === 'back' || command === 'cancel';
  const cues: Partial<Record<MenuFeedback, string>> = {
    moved: 'menu-move',
    screen: back ? 'menu-back' : 'menu-confirm',
    locked: 'menu-back',
    paused: 'pause',
    resumed: 'resume',
    adjusted: 'slider',
  };
  return cues[feedback];
}

/**
 * The game's audio (P12-R05..R11): which music plays on which screen, the level and boss tracks
 * following the boss bar, the jingles, the sound effects of the level's cues and of the menus,
 * and pausing it all with the game. It only reads the menu and core state (ENG-11).
 */
export class GameAudio {
  readonly #output: AudioOutput;
  readonly #music: MusicPlayer;
  readonly #sfx: SfxPlayer;
  readonly #recent: string[] = [];
  #cues: LevelCues | undefined;
  #levelId: string | null = null;
  #paused = false;
  #ended = false;
  #defeated = 0;
  /** Name of the beam hum playing, if any. */
  #hum: string | undefined;

  constructor(
    private readonly bindings: AudioBindings | undefined,
    private readonly options: GameAudioOptions,
  ) {
    const mix = bindings?.mix ?? { music: 1, sfx: 1 };
    const effects = bindings?.effects;
    this.#output = new AudioOutput({
      ...(options.createContext ? { createContext: options.createContext } : {}),
      mix,
      peakDb: AUDIO_CONFIG.masterPeakDb,
      limiter: AUDIO_CONFIG.limiter,
      ...(effects ? { reverbSeconds: effects.reverbSeconds } : {}),
    });
    const buses = () => this.#output.buses;
    this.#music = new MusicPlayer(buses, bindings?.instruments ?? {}, AUDIO_CONFIG, effects);
    this.#sfx = new SfxPlayer(buses, options.clock, {
      ...AUDIO_CONFIG,
      stopFadeSeconds: AUDIO_CONFIG.pauseFadeSeconds,
    });
  }

  get state(): GameAudioState {
    return {
      music: this.#music.track?.id ?? null,
      sounds: [...this.#recent],
      context: this.#output.state,
    };
  }

  /** The music player, for its position (tests). */
  get music(): MusicPlayer {
    return this.#music;
  }

  /** A user gesture: the audio may start (P12-R05). */
  unlock(): void {
    if (this.options.canStart?.() === false) return;
    this.#output.unlock();
  }

  /** The page is hidden or shown again (P12-R11). */
  setHidden(hidden: boolean): void {
    this.#output.setHidden(hidden);
  }

  setVolumes({ music, sfx }: Volumes): void {
    const steps = AUDIO_CONFIG.volumeSteps;
    this.#output.setVolumes(volumeGain(music, steps), volumeGain(sfx, steps));
  }

  /** Schedules the music ahead (every frame, and on a timer). */
  update(): void {
    this.#music.update();
  }

  /** The menus changed (P12-R08, P12-R11): the music of their screen, pausing with the game. */
  menuChanged(state: MenuState): void {
    this.setVolumes(state.volumes);
    if (state.paused !== this.#paused) this.#setPaused(state.paused);
    if (state.paused) return;
    switch (state.screen) {
      case 'loading':
        return;
      case 'game':
        if (state.levelResult) this.#want(undefined, AUDIO_CONFIG.fadeSeconds);
        return;
      default:
        this.#levelId = null;
        this.#want({ kind: 'menu' }, AUDIO_CONFIG.crossfadeSeconds);
    }
  }

  /** What a menu command did: its sound, at the volumes it may have just set (P12-R04). */
  menuFeedback(command: MenuCommand, feedback: MenuFeedback, volumes: Volumes): void {
    this.setVolumes(volumes);
    const cue = menuCue(command, feedback);
    if (cue) this.#cue({ cue });
  }

  /** A level starts, or starts again from its checkpoint: its track from the start (P12-R07). */
  levelStarted(levelId: string): void {
    this.#levelId = levelId;
    this.#cues = new LevelCues(this.bindings?.largeBlastRadius ?? Infinity);
    this.#ended = false;
    this.#defeated = 0;
    this.#stopBeam();
    this.#play({ kind: 'level', levelId }, AUDIO_CONFIG.crossfadeSeconds);
  }

  /** A level step was run: its sounds, and the music following the boss fights. */
  levelStep(run: LevelRun): void {
    const cues = this.#cues;
    if (!cues || this.#paused || this.#ended) return;
    for (const cue of cues.observe(run)) this.#cue(cue);
    this.#beam(cues.beam);
    this.#bossMusic(run);
  }

  /** The level is complete or over (P12-R07): the music fades, its jingle plays once. */
  levelEnded(result: LevelResult): void {
    this.#ended = true;
    this.#stopBeam();
    this.#want(undefined, AUDIO_CONFIG.fadeSeconds);
    this.#jingle(result.outcome === 'complete' ? 'complete' : 'over');
  }

  #setPaused(paused: boolean): void {
    this.#paused = paused;
    if (paused) {
      this.#music.pause();
      this.#sfx.stopAll();
    } else {
      this.#music.resume();
    }
  }

  /** The boss track while a boss bar shows, the level track (from its start) after it. */
  #bossMusic(run: LevelRun): void {
    const levelId = this.#levelId;
    if (levelId === null) return;
    const { defeated } = run.fights;
    if (defeated.length > this.#defeated && defeated.at(-1)?.rank === 'mini') {
      this.#jingle('checkpoint');
    }
    this.#defeated = defeated.length;
    // After the final boss, its track goes on until the level ends.
    if (run.fights.bar) this.#want({ kind: 'boss', levelId }, AUDIO_CONFIG.crossfadeSeconds);
    else if (!run.fights.finalDefeated) {
      this.#want({ kind: 'level', levelId }, AUDIO_CONFIG.crossfadeSeconds);
    }
  }

  /** The laser's hum plays while it fires. */
  #beam(weapon: string | undefined): void {
    const hum = weapon === undefined ? undefined : this.bindings?.sounds[`beam:${weapon}`];
    if (this.#hum !== undefined && this.#hum !== hum?.name) {
      this.#sfx.stopLoop(this.#hum);
      this.#hum = undefined;
    }
    if (!hum || this.#sfx.looping(hum.name)) return;
    this.#played(hum.name, this.#sfx.play(hum));
    this.#hum = hum.name;
  }

  #stopBeam(): void {
    this.#beam(undefined);
  }

  #cue({ cue, x }: SoundCue): void {
    const sound = this.bindings?.sounds[cue];
    if (!sound) return;
    const pan = x === undefined ? 0 : panAt(x, this.options.screenWidth, AUDIO_CONFIG.panMax);
    this.#played(sound.name, this.#sfx.play(sound, pan));
  }

  #played(name: string, played: boolean): void {
    if (!played) return;
    this.#recent.push(name);
    if (this.#recent.length > AUDIO_CONFIG.recentSounds) this.#recent.shift();
  }

  /** Plays the request's track unless it already plays. */
  #want(request: MusicRequest | undefined, fade: number): void {
    const track = request && this.bindings?.music(request);
    if ((track?.id ?? null) === (this.#music.track?.id ?? null)) return;
    this.#music.play(track ?? null, fade);
  }

  /** Plays the request's track from its start, even if it already plays. */
  #play(request: MusicRequest, fade: number): void {
    this.#music.play(this.bindings?.music(request) ?? null, fade);
  }

  #jingle(jingle: 'complete' | 'over' | 'checkpoint'): void {
    const track = this.bindings?.music({ kind: 'jingle', jingle });
    if (track) this.#music.jingle(track);
  }
}
