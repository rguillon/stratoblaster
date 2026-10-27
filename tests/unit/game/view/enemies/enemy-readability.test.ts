import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { inFamily, type Rgb } from '../../../../../src/core/math/color';
import { READABILITY } from '../../../../../src/game/config/readability';
import { GAME } from '../../../../../src/game';
import { buildEnemyModel, enemyColor } from '../../../../../src/game/view/enemies/enemy-mesh';
import { outlineOf } from '../../../../../src/render/outline';

const ENEMY = READABILITY.families.enemy;

describe('enemies stand out (P14-R02, R04)', () => {
  it('P14-R02: an enemy drawn with cyan neon gets lights in the enemy family', () => {
    const scene = new Scene(new NullEngine());
    const model = buildEnemyModel('test', scene, [0.1, 0.95, 1], (p) => {
      p.hull.box([4, 4, 4], [0.1, 0.1, 0.12]);
      p.neon.box([2, 2, 2], [0.1, 0.95, 1], { at: [0, 3, 0] });
      p.reactor([0, 0, -2], 1);
    });
    const neon = model.root.getChildMeshes().find((m) => m.name === 'test-enemy-neon');
    const colors = Array.from(neon?.getVerticesData('color') ?? []);
    expect(colors.length).toBeGreaterThan(0);
    for (let i = 0; i < colors.length; i += 4) {
      const c: Rgb = [colors[i] ?? 0, colors[i + 1] ?? 0, colors[i + 2] ?? 0];
      expect(inFamily(c, ENEMY)).toBe(true);
    }
    expect(inFamily(enemyColor([0.1, 0.95, 1]), ENEMY)).toBe(true);
  });

  it('P14-R04: its hull asks for a rim in a light shade of its neon', () => {
    const scene = new Scene(new NullEngine());
    const model = buildEnemyModel('rimmed', scene, [1, 0.1, 0.85], (p) => {
      p.hull.box([4, 4, 4], [0.1, 0.1, 0.12]);
    });
    const hull = model.root.getChildMeshes().find((m) => m.name.startsWith('rimmed-enemy-hull'));
    const rim = hull ? outlineOf(hull) : undefined;
    expect(rim).toBeDefined();
    // Lighter than the neon itself, so a violet rim still shows on a dark ground.
    expect(Math.min(...(rim ?? [0]))).toBeGreaterThanOrEqual(
      READABILITY.enemyOutline.whiten - 1e-9,
    );
  });

  it('P14-R04: every enemy kind and boss part model has a rim', () => {
    const scene = new Scene(new NullEngine());
    for (const [key, build] of Object.entries(GAME.view.enemies.models)) {
      const rims = build(scene)
        .root.getChildMeshes()
        .filter((m) => outlineOf(m));
      expect(rims.length, key).toBeGreaterThan(0);
    }
  });
});
