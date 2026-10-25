import { describe, expect, it } from 'vitest';
import type { BossPatternSpec } from '../../../../src/core/systems/boss-pattern';
import { withOwnLasers } from '../../../../src/game/config/bosses/boss-kit';
import { BOSS_DESIGNS } from '../../../../src/game/sim/boss-kinds';

const volleys = (patterns: readonly BossPatternSpec[]) => patterns.flat();

describe('boss lasers', () => {
  it('phase 8 review: every boss fires its lasers in its own style, the rest unchanged', () => {
    const styles = new Set<string>();
    for (const design of BOSS_DESIGNS) {
      const own = withOwnLasers(design);
      const before = volleys([...design.stages, ...(design.rage ? [design.rage] : [])]);
      const after = volleys([...own.stages, ...(own.rage ? [own.rage] : [])]);
      expect(after).toHaveLength(before.length);
      after.forEach((v, i) => {
        if (v.shape.kind !== 'laser') {
          expect(v).toBe(before[i]);
          return;
        }
        const was = before[i]?.shape;
        expect(v.shape.laser).toEqual({
          ...(was?.kind === 'laser' ? was.laser : {}),
          style: design.id,
        });
        styles.add(v.shape.laser.style);
      });
    }
    // Lasers of many colours (one per boss with lasers).
    expect(styles.size).toBeGreaterThanOrEqual(8);
  });
});
