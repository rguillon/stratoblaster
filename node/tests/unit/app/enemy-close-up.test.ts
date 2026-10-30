import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { JointedEnemy } from '../../../src/core/entities/jointed-enemy';
import { createRng } from '../../../src/core/math/rng';
import { EnemyCloseUp } from '../../../src/app/enemy-close-up';
import { ENEMY_KINDS } from '../../../src/game/sim/enemy-kinds';
import { ENEMY_MODELS } from '../../../src/game/view/enemies/enemy-models';

const GLOW = { intensity: 1, blurKernelSize: 16 };

/** The first enemy of kind `id`, just spawned. */
function spawned(id: string) {
  const kind = ENEMY_KINDS.find((k) => k.id === id);
  const enemy = kind?.spawn({ width: 480, height: 640, random: createRng(1) })[0];
  if (!enemy) throw new Error(id);
  return enemy;
}

/** How many hit circles the wireframe view draws for `id`. */
function circles(id: string): number {
  const closeUp = new EnemyCloseUp(new NullEngine(), false, GLOW);
  closeUp.wireframe = true;
  const enemy = spawned(id);
  const build = ENEMY_MODELS[enemy.model];
  if (!build) throw new Error(enemy.model);
  closeUp.show(build, enemy);
  return closeUp.scene.meshes.filter((m) => m.name.startsWith('close-up-hitbox-')).length;
}

describe('EnemyCloseUp', () => {
  it('P05-R11: the wireframe view draws a plain enemy’s hit circle', () => {
    expect(circles('scout')).toBe(1);
  });

  it('P05-R24: the wireframe view also draws the hit circles of the moving parts', () => {
    const enemy = spawned('juggernaut');
    if (!(enemy instanceof JointedEnemy)) throw new Error('juggernaut has no parts');
    expect(enemy.parts.length).toBeGreaterThan(0);
    expect(circles('juggernaut')).toBe(1 + enemy.parts.length);
  });
});
