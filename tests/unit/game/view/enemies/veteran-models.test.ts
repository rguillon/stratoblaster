import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Muzzle } from '../../../../../src/core/entities/muzzle';
import { ENEMY_UNIT } from '../../../../../src/game/config/enemies';
import { VETERAN_CONFIG as C, VETERAN_NEON } from '../../../../../src/game/config/enemies-veteran';
import { ENEMY_LOOK } from '../../../../../src/game/config/enemy-look';
import { Mantis } from '../../../../../src/game/sim/enemies/mantis';
import { Phantom } from '../../../../../src/game/sim/enemies/phantom';
import { ENEMY_MODELS } from '../../../../../src/game/view/enemies/enemy-models';
import { VETERAN_MODELS } from '../../../../../src/game/view/enemies/veteran-models';
import type { EnemyModel } from '../../../../../src/render/game-view';
import { RecordingContext, run, runUntil } from '../../../../helpers/enemy-context';

const KEYS = ['wasp', 'mortar', 'mantis', 'phantom', 'minelayer'] as const;

function build(key: string): EnemyModel {
  const model = VETERAN_MODELS[key]?.(new Scene(new NullEngine()));
  if (!model) throw new Error(key);
  model.root.computeWorldMatrix(true);
  return model;
}

/** Width across X, length along Z and height of a model's body (reactor flames left out). */
function extent(model: EnemyModel) {
  const body = model.root
    .getChildMeshes()
    .filter((m) => !m.name.includes('-reactor-'))
    .map((m) => {
      m.computeWorldMatrix(true);
      return m.getBoundingInfo().boundingBox;
    });
  const span = (axis: 'x' | 'y' | 'z'): number =>
    Math.max(...body.map((b) => b.maximumWorld[axis])) -
    Math.min(...body.map((b) => b.minimumWorld[axis]));
  return { width: span('x'), length: span('z'), height: span('y') };
}

/** The muzzles marked in a model (`<name>-muzzle-<kind>-<i>`), as `Muzzle`s from its centre. */
function marked(model: EnemyModel): Muzzle[] {
  return model.root
    .getDescendants<TransformNode>(false)
    .filter((n) => /-muzzle-\w+-\d+$/.test(n.name))
    .map((node): Muzzle => {
      node.computeWorldMatrix(true);
      const p = node.getAbsolutePosition();
      return [-p.x, -p.z, p.y];
    });
}

/** Whether every muzzle of `config` is one of `drawn` (to 0.1 px), and the other way round. */
function expectSame(config: readonly Muzzle[], drawn: readonly Muzzle[], what: string): void {
  const near = (a: Muzzle) => (b: Muzzle) => a.every((v, i) => Math.abs(v - (b[i] ?? NaN)) < 0.1);
  expect(drawn.length, what).toBe(config.length);
  for (const m of config) expect(drawn.some(near(m)), `${what} ${m.join(', ')}`).toBe(true);
}

const triangles = (model: EnemyModel): number =>
  model.root.getChildMeshes().reduce((n, m) => n + m.getTotalIndices() / 3, 0);

describe('VETERAN_MODELS (P05-R14 to P05-R18)', () => {
  it('P05-R14..R18: a model per veteran kind, among the enemy models', () => {
    expect(Object.keys(VETERAN_MODELS).sort()).toEqual([...KEYS].sort());
    expect(Object.values(C).map((c) => c.stats.model)).toEqual([...KEYS]);
    for (const key of KEYS) expect(ENEMY_MODELS[key], key).toBe(VETERAN_MODELS[key]);
  });

  it.each(KEYS)('P05-R14..R18: the %s is as big as the spec says, a flat ship', (key) => {
    const { width, length, height } = extent(build(key));
    const measured = Math.max(width, length) / ENEMY_UNIT;
    expect(Math.abs(measured / C[key].size - 1)).toBeLessThan(0.15);
    expect(height).toBeLessThan(Math.max(width, length) / 2);
  });

  it.each(KEYS)('GD-61: the %s is dark metal with its own neon colour', (key) => {
    const names = build(key)
      .root.getChildMeshes()
      .map((m) => m.material?.name);
    expect(names).toContain('enemy-hull');
    expect(names).toContain('enemy-neon');
    const colours = new Set(Object.values(VETERAN_NEON).map((c) => c.join()));
    const first = new Set(Object.values(ENEMY_LOOK.neon).map((c) => c.join()));
    expect(colours.size).toBe(KEYS.length);
    expect([...colours].some((c) => first.has(c))).toBe(false);
  });

  it.each(KEYS)('P05-R14..R18: the %s costs as many triangles as the first enemies', (key) => {
    const count = triangles(build(key));
    expect(count).toBeGreaterThan(150);
    expect(count).toBeLessThan(550);
  });

  it('phase 7 review: each veteran kind fires from the tips of the barrels its model draws', () => {
    const arms = C.mantis.arm.muzzles;
    const expected: Readonly<Record<(typeof KEYS)[number], readonly Muzzle[]>> = {
      wasp: C.wasp.muzzles,
      mortar: C.mortar.muzzles,
      mantis: [...C.mantis.head.muzzles, ...arms.left, ...arms.right],
      phantom: C.phantom.muzzles,
      minelayer: C.minelayer.muzzles,
    };
    for (const key of KEYS) expectSame(expected[key], marked(build(key)), key);
  });

  it('P05-R13, P05-R16: the Mantis arms move their barrels as the simulation does, and go when shot off', () => {
    const ctx = new RecordingContext();
    const mantis = new Mantis(0, 600, 400);
    runUntil(mantis, ctx, () => mantis.state === 'stay');
    run(mantis, ctx, 0.7);
    mantis.x = 0;
    mantis.y = 0;
    run(mantis, ctx, 0); // places the parts at the new centre
    const model = build('mantis');
    model.sync(mantis, 1 / 60);
    const drawn = marked(model).filter((m) => m[1] < -15);
    const placed = (['left', 'right'] as const).flatMap((side) => {
      const arm = mantis.part(`${side}-arm`);
      return C.mantis.arm.muzzles[side].map((m): Muzzle => {
        const p = arm?.place(m) ?? { x: NaN, y: NaN, height: NaN };
        return [p.x, p.y, p.height];
      });
    });
    expectSame(placed, drawn, 'mantis arms');
    const left = mantis.parts.find((p) => p.spec.id === 'left-arm');
    if (left) left.health = 0;
    model.sync(mantis, 1 / 60);
    const enabled = model.root
      .getChildren((n) => n.name === 'mantis-left-arm', false)
      .map((n) => n.isEnabled(false));
    expect(enabled).toEqual([false]);
  });

  it('P05-R17: the Phantom model fades out and in with the Phantom', () => {
    const model = build('phantom');
    const ctx = new RecordingContext();
    const phantom = new Phantom(240, 700, 500);
    const visibility = (): number[] => [
      ...new Set(model.root.getChildMeshes().map((m) => (m.isVisible ? m.visibility : 0))),
    ];
    model.sync(phantom, 1 / 60);
    expect(visibility()).toEqual([1]);
    runUntil(phantom, ctx, () => phantom.state === 'fadeOut');
    run(phantom, ctx, C.phantom.fade / 2);
    model.sync(phantom, 1 / 60);
    const half = visibility();
    expect(half).toHaveLength(1);
    expect(half[0]).toBeGreaterThan(0.2);
    expect(half[0]).toBeLessThan(0.8);
    runUntil(phantom, ctx, () => phantom.state === 'hidden');
    model.sync(phantom, 1 / 60);
    expect(visibility()).toEqual([0]);
  });
});
