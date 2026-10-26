import type { MenuState } from '../../src/app/menu-flow';
import type { AudioBindings, MusicRequest } from '../../src/audio/audio-bindings';
import type { SoundDesign, Track } from '../../src/audio/audio-types';

/** A sample game's audio and the state the audio reads, for the `GameAudio` tests. */

export const track = (id: string, loop = true): Track => ({
  id,
  bpm: 120,
  beats: 8,
  loop,
  notes: [{ beat: 0, beats: 1, pitch: 60, velocity: 1, instrument: 'tone' }],
});

export const sound = (name: string, rest: Partial<SoundDesign> = {}): SoundDesign => ({
  name,
  priority: 1,
  gain: 0.5,
  hold: 0,
  layers: [
    {
      wave: 'sine',
      gain: 1,
      pitch: 440,
      envelope: { attack: 0, decay: 0.1, sustain: 0, release: 0 },
    },
  ],
  ...rest,
});

/** A sample game's audio: its requests are recorded. */
export function bindings(requests: MusicRequest[] = []): AudioBindings {
  return {
    music: (request) => {
      requests.push(request);
      switch (request.kind) {
        case 'menu':
          return track('menu');
        case 'level':
          return track(`level-${request.levelId}`);
        case 'boss':
          return track(`boss-${request.levelId}`);
        case 'jingle':
          return track(`jingle-${request.jingle}`, false);
      }
    },
    instruments: {
      tone: {
        gain: 1,
        layers: [
          {
            wave: 'sine',
            gain: 1,
            pitch: 1,
            envelope: { attack: 0, decay: 0.1, sustain: 0, release: 0 },
          },
        ],
      },
    },
    sounds: {
      'fire:gun': sound('gun-shot', { positional: true }),
      'beam:laser': sound('hum', { loop: true }),
      'menu-move': sound('move'),
      'menu-confirm': sound('confirm'),
      'menu-back': sound('back'),
      pause: sound('pause'),
      resume: sound('resume'),
      slider: sound('slider'),
    },
    largeBlastRadius: 18,
    mix: { music: 0.5, sfx: 0.8 },
  };
}

export const MENU: MenuState = {
  screen: 'title',
  selection: 0,
  selectedId: 'start',
  highlightedShipId: 'a',
  chosenShipId: null,
  chosenLevelId: null,
  transitioning: false,
  levelResult: null,
  choice: 0,
  attempt: 0,
  resume: null,
  paused: false,
  leaving: false,
  volumes: { music: 6, sfx: 8 },
};

/** A level run seen by the audio: its boss fight and shots, as plain data. */
export function run() {
  return {
    ship: { x: 240 },
    shots: {
      volleys: 0,
      beam: [] as unknown[],
      weapon: { id: 'gun' },
      level: 1,
    },
    enemies: { shots: { bullets: [], missiles: [], lasers: [] }, brokenParts: [] },
    impacts: [],
    blasts: [],
    hits: [],
    bonuses: { picked: [] },
    hull: { lives: 3 },
    bombs: { fired: 0 },
    fights: {
      bar: undefined as object | undefined,
      finalDefeated: false,
      defeated: [] as { rank: 'mini' | 'final' }[],
    },
  };
}
