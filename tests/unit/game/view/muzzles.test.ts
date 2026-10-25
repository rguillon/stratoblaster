import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Muzzle } from '../../../../src/core/entities/muzzle';
import { volleyMuzzles } from '../../../../src/game/config/bosses/boss-kit';
import { ENEMY_CONFIG } from '../../../../src/game/config/enemies';
import { createRng } from '../../../../src/core/math/rng';
import { BOSS_DESIGNS, BOSS_KINDS } from '../../../../src/game/sim/boss-kinds';
import type { WorldBoss } from '../../../../src/game/sim/bosses/world-boss';
import { RecordingContext, runUntil } from '../../../helpers/enemy-context';
import { BOSS_MODELS } from '../../../../src/game/view/bosses/boss-models';
import { ENEMY_MODELS } from '../../../../src/game/view/enemies/enemy-models';
import type { EnemyModelFactory } from '../../../../src/render/game-view';

/** The muzzles marked in a model, by `<piece> <kind>`, as `Muzzle`s (from the model's centre). */
function marked(factory: EnemyModelFactory, prefix: string): Map<string, Muzzle[]> {
  return markers(factory(new Scene(new NullEngine())).root, prefix);
}

/** The muzzles marked under `root`, by `<piece> <kind>` (see {@link marked}). */
function markers(root: TransformNode, prefix: string): Map<string, Muzzle[]> {
  root.computeWorldMatrix(true);
  const found = new Map<string, Muzzle[]>();
  for (const node of root.getDescendants<TransformNode>(false)) {
    const match = /^(.*)-muzzle-(\w+)-\d+$/.exec(node.name);
    if (!match) continue;
    node.computeWorldMatrix(true);
    const p = node.getAbsolutePosition();
    // Model space (nose +Z, Y up) to a Muzzle (facing down the screen: X right, Y up, height).
    // A piece's turret is its own model, `<piece>-turret`.
    const piece = (match[1] ?? '').slice(prefix.length).replace(/-turret$/, '');
    const key = `${piece || 'body'} ${match[2] ?? ''}`;
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

/** A boss of `id` in place, level, its turrets turned (each by its own angle). */
function turnedBoss(id: string): WorldBoss {
  const area = { width: 480, height: 640, random: createRng(1) };
  const boss = BOSS_KINDS.find((k) => k.id === id)?.spawn(area) as WorldBoss;
  runUntil(boss, new RecordingContext(), () => boss.state === 'fighting');
  boss.roll = 0;
  [boss.core, ...boss.parts].forEach((piece, i) => {
    if (piece.turret) piece.turret.aim = 0.4 + i * 0.3;
  });
  return boss;
}

/** Where the muzzles of `boss`'s turrets are now, by piece, from its centre. */
function turretMuzzles(boss: WorldBoss): Map<string, Muzzle[]> {
  const found = new Map<string, Muzzle[]>();
  for (const [name, guns] of Object.entries(boss.design.guns)) {
    const piece = name === 'core' ? boss.core : boss.parts.find((p) => p.spec.id === name);
    if (!guns.turret || !piece?.turret) continue;
    const placed = (guns.gun ?? []).map((m): Muzzle => {
      const p = piece.place(m, true);
      return [p.x - boss.x, p.y - boss.y, p.height];
    });
    found.set(name, placed);
  }
  return found;
}

describe('Muzzles', () => {
  it.each(BOSS_DESIGNS.map((d) => [d.id, d] as const))(
    'phase 7 review: the %s fires from the tips of the barrels its model draws',
    (id, design) => {
      const factory = BOSS_MODELS[id];
      if (!factory) throw new Error(id);
      const drawn = marked(factory, `${id}-`);
      for (const [piece, guns] of Object.entries(design.guns)) {
        // Its `turret` is a pivot, not muzzles.
        for (const [kind, muzzles] of Object.entries(
          guns as Partial<Record<string, readonly Muzzle[]>>,
        ).filter(([kind]) => kind !== 'turret')) {
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

  const TURRETED = BOSS_DESIGNS.filter((d) => Object.values(d.guns).some((g) => g.turret));

  it.each(TURRETED.map((d) => [d.id] as const))(
    'phase 7 review: the %s turrets turn the barrels its model draws, its shots leaving their tips',
    (id) => {
      const boss = turnedBoss(id);
      const model = BOSS_MODELS[id]?.(new Scene(new NullEngine()));
      if (!model) throw new Error(id);
      model.sync(boss, 1 / 60);
      const drawn = markers(model.root, `${id}-`);
      for (const [name, placed] of turretMuzzles(boss)) {
        expectSame(placed, drawn.get(`${name} gun`) ?? [], `${id} ${name}`);
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
