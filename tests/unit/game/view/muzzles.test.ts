import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Muzzle } from '../../../../src/core/entities/muzzle';
import { volleyMuzzles } from '../../../../src/game/config/bosses/boss-kit';
import { ENEMY_CONFIG } from '../../../../src/game/config/enemies';
import { BOSS_DESIGNS } from '../../../../src/game/sim/boss-kinds';
import { BOSS_MODELS } from '../../../../src/game/view/bosses/boss-models';
import { ENEMY_MODELS } from '../../../../src/game/view/enemies/enemy-models';
import type { EnemyModelFactory } from '../../../../src/render/game-view';

/** The muzzles marked in a model, by `<piece> <kind>`, as `Muzzle`s (from the model's centre). */
function marked(factory: EnemyModelFactory, prefix: string): Map<string, Muzzle[]> {
  const model = factory(new Scene(new NullEngine()));
  model.root.computeWorldMatrix(true);
  const found = new Map<string, Muzzle[]>();
  for (const node of model.root.getDescendants<TransformNode>(false)) {
    const match = /^(.*)-muzzle-(\w+)-\d+$/.exec(node.name);
    if (!match) continue;
    node.computeWorldMatrix(true);
    const p = node.getAbsolutePosition();
    // Model space (nose +Z, Y up) to a Muzzle (facing down the screen: X right, Y up, height).
    const key = `${(match[1] ?? '').slice(prefix.length) || 'body'} ${match[2] ?? ''}`;
    found.set(key, [...(found.get(key) ?? []), [-p.x, -p.z, p.y]]);
  }
  return found;
}

/** Whether every muzzle of `config` is one of `drawn` (to 0.1 px), and the other way round. */
function expectSame(config: readonly Muzzle[], drawn: readonly Muzzle[], what: string): void {
  const near = (a: Muzzle) => (b: Muzzle) => a.every((v, i) => Math.abs(v - (b[i] ?? NaN)) < 0.1);
  expect(config.length, what).toBe(drawn.length);
  for (const m of config) expect(drawn.some(near(m)), `${what} ${m.join(', ')}`).toBe(true);
}

describe('Muzzles', () => {
  it.each(BOSS_DESIGNS.map((d) => [d.id, d] as const))(
    'phase 7 review: the %s fires from the tips of the barrels its model draws',
    (id, design) => {
      const factory = BOSS_MODELS[id];
      if (!factory) throw new Error(id);
      const drawn = marked(factory, `${id}-`);
      for (const [piece, guns] of Object.entries(design.guns)) {
        for (const [kind, muzzles] of Object.entries(
          guns as Partial<Record<string, readonly Muzzle[]>>,
        )) {
          const model = drawn.get(`${piece} ${kind}`) ?? [];
          expectSame(muzzles ?? [], model, `${id} ${piece} ${kind}`);
        }
      }
      // Every bullet, missile and laser leaves from a muzzle.
      for (const volley of design.stages.flat()) {
        const fires = volley.shape.kind !== 'launch';
        expect(volleyMuzzles(design, volley).length > 0, `${id} ${volley.from}`).toBe(fires);
      }
    },
  );

  const ENEMIES = [
    ['scout', ENEMY_CONFIG.scout.muzzles],
    ['strafer', ENEMY_CONFIG.strafer.muzzles],
    ['weaver', ENEMY_CONFIG.weaver.muzzles],
    ['spinner', ENEMY_CONFIG.spinner.muzzles],
    ['lancer', [ENEMY_CONFIG.lancer.muzzle]],
    ['rocketeer', ENEMY_CONFIG.rocketeer.muzzles],
    ['bulwark', ENEMY_CONFIG.bulwark.muzzles],
    ['splitter', ENEMY_CONFIG.splitter.muzzles],
  ] as const;

  it.each(ENEMIES)(
    'phase 7 review: the %s fires from the tips of the barrels its model draws',
    (id, muzzles) => {
      const factory = ENEMY_MODELS[id];
      if (!factory) throw new Error(id);
      const drawn = [...marked(factory, id).values()].flat();
      expectSame(muzzles, drawn, id);
    },
  );
});
