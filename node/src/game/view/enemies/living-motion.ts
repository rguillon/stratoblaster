import { ENEMY_LOOK } from '../../config/enemy-look';

// The living motion of the enemy models (P16-R07), visual only.

/**
 * The breathing of a creature (P16-R07): every model of one creature (a boss's core, parts and
 * limbs) shares one, so it breathes as one body.
 */
export interface Breath {
  readonly phase: number;
  readonly period: number;
}

let breaths = 0;
let livingMotion = true;

/** A new breath, its period and phase spread from one creature to the next (P16-R07). */
export function newBreath(): Breath {
  const { period, spread } = ENEMY_LOOK.living.breathing;
  // A golden-ratio sequence: deterministic, evenly spread.
  const k = (breaths++ * 0.618034) % 1;
  return { phase: 2 * Math.PI * k, period: period * (1 + spread * (2 * k - 1)) };
}

/** Turns the living motion on or off (P16-R10, debug pages): off, bodies hold still at rest. */
export function setLivingMotion(on: boolean): void {
  livingMotion = on;
}

export function isLivingMotion(): boolean {
  return livingMotion;
}

/** The body's scale at `time` (P16-R07). */
export function breathScale(breath: Breath, time: number): number {
  const a = ENEMY_LOOK.living.breathing.amplitude;
  return 1 + a * Math.sin((2 * Math.PI * time) / breath.period + breath.phase);
}

/** The veins' brightness at `time` (P16-R07), from `low` to 1. */
export function glowLevel(breath: Breath, time: number): number {
  const { period, low } = ENEMY_LOOK.living.glow;
  const wave = 0.5 + 0.5 * Math.sin((2 * Math.PI * time) / period + breath.phase);
  return low + (1 - low) * wave;
}

/** A wing's roll at `time` (P16-R07): `side` up then down, slower for big wings. */
export function flutterAngle(side: number, span: number, time: number, phase = 0): number {
  const { hz, bigHz, bigSpan, angle } = ENEMY_LOOK.living.flutter;
  const f = span > bigSpan ? bigHz : hz;
  return -side * angle * Math.sin(2 * Math.PI * f * time + phase);
}
