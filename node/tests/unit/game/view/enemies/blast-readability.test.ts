import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../../src/core/math/rng';
import { GAME_CONFIG } from '../../../../../src/game/config/game';
import { READABILITY } from '../../../../../src/game/config/readability';
import {
  BLAST_LAYERS,
  BlastParticles,
  type BlastSpots,
} from '../../../../../src/game/view/enemies/blast-particles';

const { width, height } = GAME_CONFIG.screen;
/** Cells of the coverage grid, in logical pixels. */
const CELL = 4;

/** Share of the screen covered by the spots of `frame` (each drawn as a disc). */
function coverage(frame: BlastSpots): number {
  const cols = Math.ceil(width / CELL);
  const rows = Math.ceil(height / CELL);
  const covered = new Uint8Array(cols * rows);
  for (const layer of BLAST_LAYERS) {
    for (const s of frame[layer]) {
      const r = Math.ceil(s.radius / CELL);
      const cx = Math.floor(s.x / CELL);
      const cy = Math.floor(s.y / CELL);
      for (let y = Math.max(0, cy - r); y <= Math.min(rows - 1, cy + r); y++) {
        for (let x = Math.max(0, cx - r); x <= Math.min(cols - 1, cx + r); x++) {
          const d = Math.hypot((x - cx) * CELL, (y - cy) * CELL);
          if (d <= s.radius) covered[y * cols + x] = 1;
        }
      }
    }
  }
  return covered.reduce((n, c) => n + c, 0) / covered.length;
}

/** Every frame of a blast of `radius` in the middle of the screen, at 60 Hz, for 3 s. */
function frames(radius: number, seed: number): BlastSpots[] {
  const blasts = new BlastParticles(createRng(seed));
  blasts.emit({ kind: 'enemy', x: width / 2, y: height / 2, radius });
  return Array.from({ length: 180 }, () => blasts.step(1 / 60));
}

const count = (frame: BlastSpots) => BLAST_LAYERS.reduce((n, l) => n + frame[l].length, 0);

describe('P14-R07: explosions do not clutter the screen', () => {
  for (const radius of [8, 20, 60, 120]) {
    it(`P14-R07: a blast of a ${String(radius)} px ship covers at most ${String(
      READABILITY.effectMaxScreenShare * 100,
    )} % of the screen`, () => {
      for (const seed of [1, 2, 3]) {
        const largest = Math.max(...frames(radius, seed).map(coverage));
        expect(largest).toBeLessThanOrEqual(READABILITY.effectMaxScreenShare);
        expect(largest).toBeGreaterThan(0);
      }
    });

    it(`P14-R07: a blast of a ${String(radius)} px ship is over after ${String(
      READABILITY.effectMaxDuration,
    )} s`, () => {
      for (const seed of [1, 2, 3]) {
        const all = frames(radius, seed);
        const last = all.findLastIndex((f) => count(f) > 0);
        expect((last + 1) / 60).toBeLessThanOrEqual(READABILITY.effectMaxDuration);
      }
    });
  }
});
