import type { SoundDesign, ToneLayer } from '../../../audio/audio-types';
import { blast, boom, chime, env, minigun, MINIGUN, tone } from './sound-recipes';

/**
 * The game's sound effects (P12-R09, GD-71), all synthesised, keyed by the engine's cue
 * (`SoundCue`). Priorities (P12-R10): the player's and the bombs' sounds highest, the enemy shots
 * lowest. The player's gun shots and the laser hum are mixed quieter than hits and explosions.
 */

/** Priorities (P12-R10). */
const PRIORITY = {
  enemyShot: 0,
  enemy: 1,
  hit: 2,
  weapon: 3,
  blast: 4,
  part: 5,
  player: 6,
  top: 7,
};

const sound = (
  name: string,
  priority: number,
  gain: number,
  layers: readonly ToneLayer[],
  rest: Partial<SoundDesign> = {},
): SoundDesign => ({ name, priority, gain, layers, hold: 0, ...rest });

const PLAYER_WEAPONS: Readonly<Record<string, SoundDesign>> = {
  'fire:bullet': sound('gun-shot', PRIORITY.weapon, 0.14, minigun(MINIGUN), { positional: true }),
  'fire:missile': sound(
    'missile-launch',
    PRIORITY.weapon,
    0.3,
    [
      tone('noise', 1, 0.8, env(0.01, 0.3, 0, 0.08), {
        filter: { type: 'bandpass', frequency: 2600, from: 500, sweepSeconds: 0.3, q: 2 },
      }),
      tone('sawtooth', 220, 0.3, env(0.005, 0.2), { glideTo: 90, glideSeconds: 0.2 }),
    ],
    { positional: true },
  ),
  'beam-start:laser': sound(
    'laser-start',
    PRIORITY.weapon,
    0.3,
    [
      tone('sawtooth', 300, 0.6, env(0.005, 0.18, 0, 0.05), {
        glideTo: 1300,
        glideSeconds: 0.15,
        filter: { type: 'lowpass', frequency: 3000 },
      }),
    ],
    { positional: true },
  ),
  'beam:laser': sound(
    'laser-hum',
    PRIORITY.weapon,
    0.1,
    [
      tone('sawtooth', 110, 0.6, env(0.05, 0.1, 0.8, 0.12), {
        filter: { type: 'lowpass', frequency: 900, q: 3 },
      }),
      tone('square', 220, 0.3, env(0.05, 0.1, 0.8, 0.12), {
        detuneCents: 9,
        filter: { type: 'lowpass', frequency: 1400 },
      }),
    ],
    { loop: true },
  ),
  'weapon-switch': sound(
    'weapon-switch',
    PRIORITY.player,
    0.3,
    chime('square', [660, 990], 0.06, 0.5),
  ),
  'weapon-up': sound(
    'weapon-level-up',
    PRIORITY.player,
    0.35,
    chime('triangle', [523, 659, 784, 1047], 0.07, 0.6),
  ),
};

const ENEMY_WEAPONS: Readonly<Record<string, SoundDesign>> = {
  'enemy-bullet': sound(
    'enemy-shot',
    PRIORITY.enemyShot,
    0.14,
    [tone('triangle', 760, 0.7, env(0.001, 0.08), { glideTo: 340, glideSeconds: 0.08 })],
    { positional: true },
  ),
  'enemy-missile': sound(
    'enemy-missile',
    PRIORITY.enemyShot,
    0.22,
    [
      tone('noise', 1, 0.7, env(0.02, 0.35, 0, 0.06), {
        filter: { type: 'bandpass', frequency: 900, from: 300, sweepSeconds: 0.35, q: 3 },
      }),
    ],
    { positional: true },
  ),
  'laser-warning': sound(
    'laser-warning',
    PRIORITY.enemy,
    0.2,
    [
      tone('square', 880, 0.5, env(0.002, 0.07, 0, 0.02)),
      tone('square', 880, 0.5, env(0.002, 0.07, 0, 0.02), { delay: 0.16 }),
    ],
    { positional: true },
  ),
  'laser-fire': sound(
    'enemy-laser',
    PRIORITY.enemy,
    0.3,
    [
      tone('sawtooth', 170, 0.6, env(0.01, 0.4, 0.3, 0.15), {
        glideTo: 90,
        glideSeconds: 0.5,
        filter: { type: 'lowpass', frequency: 1800 },
      }),
      tone('noise', 1, 0.3, env(0.01, 0.4, 0.2, 0.15), {
        filter: { type: 'bandpass', frequency: 1200 },
      }),
    ],
    { positional: true, hold: 0.3 },
  ),
};

const HITS: Readonly<Record<string, SoundDesign>> = {
  hit: sound(
    'hit',
    PRIORITY.hit,
    0.3,
    [
      tone('noise', 1, 0.6, env(0.001, 0.05), { filter: { type: 'highpass', frequency: 1800 } }),
      tone('square', 320, 0.4, env(0.001, 0.06), { glideTo: 140, glideSeconds: 0.06 }),
    ],
    { positional: true },
  ),
  'hit-blocked': sound(
    'hit-shield',
    PRIORITY.hit,
    0.28,
    [
      tone('square', 1480, 0.4, env(0.001, 0.12, 0, 0.06), {
        filter: { type: 'bandpass', frequency: 2400, q: 6 },
      }),
      tone('triangle', 2210, 0.3, env(0.001, 0.15, 0, 0.08)),
    ],
    { positional: true },
  ),
  'player-hit': sound(
    'player-hit',
    PRIORITY.player,
    0.5,
    [
      tone('sawtooth', 240, 0.6, env(0.002, 0.25, 0, 0.06), { glideTo: 70, glideSeconds: 0.25 }),
      tone('noise', 1, 0.5, env(0.001, 0.15), { filter: { type: 'lowpass', frequency: 2500 } }),
    ],
    { positional: true },
  ),
};

const DESTRUCTION: Readonly<Record<string, SoundDesign>> = {
  'blast-small': sound('explosion-small', PRIORITY.blast, 0.4, boom(0.22, 900, 150), {
    positional: true,
  }),
  'blast-large': sound('explosion-large', PRIORITY.blast, 0.5, boom(0.5, 1200, 110), {
    positional: true,
  }),
  'part-destroyed': sound(
    'boss-part-destroyed',
    PRIORITY.part,
    0.55,
    [
      ...blast(0.7, 2800, 110),
      tone('square', 1200, 0.25, env(0.001, 0.4, 0, 0.1), { glideTo: 300, glideSeconds: 0.4 }),
    ],
    { positional: true },
  ),
  'boss-destroyed': sound('boss-destroyed', PRIORITY.top, 0.6, [
    ...blast(2, 2000, 80),
    tone('sawtooth', 400, 0.3, env(0.01, 1.4, 0, 0.2), {
      glideTo: 40,
      glideSeconds: 1.4,
      filter: { type: 'lowpass', frequency: 900 },
    }),
  ]),
};

const PLAYER: Readonly<Record<string, SoundDesign>> = {
  'life-lost': sound('life-lost', PRIORITY.top, 0.5, [
    tone('square', 660, 0.5, env(0.005, 0.6, 0, 0.1), {
      glideTo: 110,
      glideSeconds: 0.6,
      filter: { type: 'lowpass', frequency: 2000 },
    }),
    ...blast(0.6, 2000, 90),
  ]),
  'extra-life': sound(
    'extra-life',
    PRIORITY.top,
    0.4,
    chime('triangle', [784, 988, 1175, 1568], 0.08, 0.7),
  ),
  bomb: sound('bomb', PRIORITY.top, 0.6, [
    ...blast(1.3, 4000, 75),
    tone('sawtooth', 800, 0.25, env(0.005, 0.8, 0, 0.1), {
      glideTo: 60,
      glideSeconds: 0.8,
      filter: { type: 'lowpass', frequency: 1500 },
    }),
  ]),
  'bonus:bomb': sound('bomb-bonus', PRIORITY.player, 0.35, chime('square', [523, 784], 0.07, 0.45)),
  'bonus:weapon': sound('weapon-bonus', PRIORITY.player, 0.35, [
    tone('triangle', 440, 0.7, env(0.003, 0.16, 0.2, 0.1), { glideTo: 1320, glideSeconds: 0.14 }),
    tone('sine', 1760, 0.3, env(0.003, 0.1, 0, 0.1), { delay: 0.1 }),
  ]),
  'bonus:life': sound(
    'life-bonus',
    PRIORITY.player,
    0.35,
    chime('sine', [784, 1175, 1568], 0.06, 0.7),
  ),
};

const MENUS: Readonly<Record<string, SoundDesign>> = {
  'menu-move': sound('menu-move', PRIORITY.top, 0.18, [
    tone('square', 1200, 0.5, env(0.001, 0.03)),
  ]),
  'menu-confirm': sound('menu-confirm', PRIORITY.top, 0.25, chime('square', [660, 990], 0.05, 0.5)),
  'menu-back': sound('menu-back', PRIORITY.top, 0.25, chime('square', [660, 440], 0.05, 0.5)),
  pause: sound('pause', PRIORITY.top, 0.3, [
    tone('sine', 880, 0.7, env(0.003, 0.15, 0, 0.05), { glideTo: 440, glideSeconds: 0.15 }),
  ]),
  resume: sound('resume', PRIORITY.top, 0.3, [
    tone('sine', 440, 0.7, env(0.003, 0.15, 0, 0.05), { glideTo: 880, glideSeconds: 0.15 }),
  ]),
  slider: sound('slider-step', PRIORITY.top, 0.4, [tone('triangle', 1000, 0.6, env(0.002, 0.07))]),
};

/** Every sound effect, by cue. */
export const SOUND_DESIGNS: Readonly<Record<string, SoundDesign>> = {
  ...PLAYER_WEAPONS,
  ...ENEMY_WEAPONS,
  ...HITS,
  ...DESTRUCTION,
  ...PLAYER,
  ...MENUS,
};
