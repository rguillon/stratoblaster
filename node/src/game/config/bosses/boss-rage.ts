import type { BossPatternSpec } from '../../../core/systems/boss-pattern';
import { bullet, volley } from './boss-kit';

/**
 * The bosses' angry patterns (phase 7 review): the bullet hell a boss fires from its core for
 * `BOSS_TIMING.rageSeconds` after the pause that follows each destroyed part. `heat` goes from 0
 * (1-1's mini boss) to 4.5 (1-5's final boss): about 20 → 56 bullets a second, a little faster
 * each level, but slower than the stages' bullets (120 → 156 px/s) and with lanes between them,
 * so a kid in 1-1 can still weave through. `share` is the part of that rate a pattern fires,
 * for a boss firing two of them.
 */

/** Bullets a second at `heat`. */
const rate = (heat: number, share: number): number => (20 + 8 * heat) * share;
/** Bullets in a ring at `heat`. */
const arms = (heat: number): number => 5 + Math.round(heat * 0.7);
/** A slow bullet of `style` for the angry patterns, at `heat`. */
const angry = (style: string, heat: number) => bullet(style, 120 + 8 * heat, 4);

export const rage = {
  /** Two spirals turning opposite ways from the core, crossing as they go. */
  spirals: (heat: number, a: string, b: string, share = 1): BossPatternSpec => {
    const every = (2 * arms(heat)) / rate(heat, share);
    return [
      volley.ring('core', every, arms(heat), 13, angry(a, heat), 0.05),
      volley.ring('core', every, arms(heat), -17, angry(b, heat), 0.05 + every / 2),
    ];
  },
  /** A dense, slowly turning ring blooming from the core, and small fans at the player. */
  flower: (heat: number, a: string, b: string, share = 1): BossPatternSpec => {
    const petals = arms(heat) * 2 + 2;
    const every = (petals + 1.5) / rate(heat, share);
    return [
      volley.ring('core', every, petals, 9, angry(a, heat), 0.05),
      volley.aimed('core', every * 2, 3, 14, angry(b, heat), 0.3),
    ];
  },
  /** Fans sweeping across the screen and back, a ring under them. */
  curtain: (heat: number, a: string, b: string, share = 1): BossPatternSpec => {
    const ring = arms(heat) + 3;
    const sweep = (24 + 2 * ring) / rate(heat, share);
    return [
      ...[-40, -20, 0, 20, 40, 20, 0, -20].map((heading, i) =>
        volley.fan('core', sweep, 3, 7, angry(a, heat), 0.05 + (sweep * i) / 8, heading),
      ),
      volley.ring('core', sweep / 2, ring, 11, angry(b, heat), 0.2),
    ];
  },
  /** One fast-turning spiral, and bursts at the player. */
  vortex: (heat: number, a: string, b: string, share = 1): BossPatternSpec => {
    const spiral = Math.max(3, arms(heat) - 2);
    const every = (spiral + 0.5) / rate(heat, share);
    return [
      volley.ring('core', every, spiral, 23, angry(a, heat), 0.05),
      volley.burst('core', every * 6, 3, 0.12, angry(b, heat), 0.5),
    ];
  },
};
