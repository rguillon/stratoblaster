import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { Scene } from '@babylonjs/core/scene';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { JointedEnemy } from '../../../../../src/core/entities/jointed-enemy';
import type { Muzzle } from '../../../../../src/core/entities/muzzle';
import { ENEMY_UNIT } from '../../../../../src/game/config/enemies';
import { ELITE_CONFIG as C } from '../../../../../src/game/config/enemies-elite';
import { Hive } from '../../../../../src/game/sim/enemies/hive';
import { Hydra } from '../../../../../src/game/sim/enemies/hydra';
import { Juggernaut } from '../../../../../src/game/sim/enemies/juggernaut';
import { Orbiter } from '../../../../../src/game/sim/enemies/orbiter';
import { Scissor } from '../../../../../src/game/sim/enemies/scissor';
import { bossPoint } from '../../../../../src/game/view/bosses/boss-limbs';
import { ELITE_MODELS } from '../../../../../src/game/view/enemies/elite-models';
import { ENEMY_MODELS } from '../../../../../src/game/view/enemies/enemy-models';
import type { EnemyModel } from '../../../../../src/render/game-view';
import { RecordingContext, run, runUntil } from '../../../../helpers/enemy-context';

const KEYS = ['hydra', 'orbiter', 'scissor', 'juggernaut', 'hive'] as const;
type Key = (typeof KEYS)[number];

const build = (key: Key): EnemyModel => {
  const factory = ELITE_MODELS[key];
  if (!factory) throw new Error(key);
  return factory(new Scene(new NullEngine()));
};

/** Width across X, length along Z and height of a model's body (reactor flames left out). */
function extent(model: EnemyModel) {
  model.root.computeWorldMatrix(true);
  const boxes = model.root
    .getChildMeshes()
    .filter((m) => !m.name.includes('-reactor-'))
    .map((m) => {
      m.computeWorldMatrix(true);
      return m.getBoundingInfo().boundingBox;
    });
  const span = (axis: 'x' | 'y' | 'z'): number =>
    Math.max(...boxes.map((b) => b.maximumWorld[axis])) -
    Math.min(...boxes.map((b) => b.minimumWorld[axis]));
  return { width: span('x'), length: span('z'), height: span('y') };
}

/** The node of `model` named `name`, its world matrix up to date. */
function node(model: EnemyModel, name: string): TransformNode {
  const found = model.root.getDescendants<TransformNode>(false).find((n) => n.name === name);
  if (!found) throw new Error(name);
  found.computeWorldMatrix(true);
  return found;
}

/** Where a model point is now, as a `Muzzle` (facing down the screen: X right, Y up, height). */
const asMuzzle = (p: Vector3): Muzzle => [-p.x, -p.z, p.y];

/** The muzzles marked in a model, by kind, as `Muzzle`s from its centre. */
function marked(model: EnemyModel): Map<string, Muzzle[]> {
  model.root.computeWorldMatrix(true);
  const found = new Map<string, Muzzle[]>();
  for (const n of model.root.getDescendants<TransformNode>(false)) {
    const kind = /-muzzle-(\w+)-\d+$/.exec(n.name)?.[1];
    if (!kind) continue;
    n.computeWorldMatrix(true);
    found.set(kind, [...(found.get(kind) ?? []), asMuzzle(n.getAbsolutePosition())]);
  }
  return found;
}

/** Whether every muzzle of `config` is one of `drawn` (to 0.1 px), and as many. */
function expectSame(config: readonly Muzzle[], drawn: readonly Muzzle[], what: string): void {
  const near = (a: Muzzle) => (b: Muzzle) => a.every((v, i) => Math.abs(v - (b[i] ?? NaN)) < 0.1);
  expect(drawn.length, what).toBe(config.length);
  for (const m of config) expect(drawn.some(near(m)), `${what} ${m.join(', ')}`).toBe(true);
}

/** The muzzles each elite kind fires from, by kind of muzzle, at rest. */
const MUZZLES: Readonly<Record<Key, Readonly<Record<string, readonly Muzzle[]>>>> = {
  hydra: { gun: C.hydra.heads.map((h) => h.muzzle) },
  orbiter: { ring: C.orbiter.ringMuzzles, gun: C.orbiter.drones.map((d) => d.muzzle) },
  scissor: { laser: C.scissor.arms.map((a) => a.muzzle) },
  juggernaut: { gun: [...C.juggernaut.muzzles, ...C.juggernaut.cannons.map((c) => c.muzzle)] },
  hive: { ring: C.hive.ringMuzzles, launch: [C.hive.port] },
};

/** The muzzle on each moving part, by part id. */
const PART_MUZZLES: Readonly<Record<string, Muzzle>> = Object.fromEntries(
  [...C.hydra.heads, ...C.orbiter.drones, ...C.scissor.arms, ...C.juggernaut.cannons].map(
    (p): [string, Muzzle] => [p.id, p.muzzle],
  ),
);

/** Each jointed kind, its moving parts swung (or turned) away from rest. */
function swung(key: Exclude<Key, 'hive'>): JointedEnemy {
  const ctx = new RecordingContext();
  if (key === 'scissor') {
    const scissor = new Scissor(240, 512, 512);
    runUntil(scissor, ctx, () => scissor.state === 'fire');
    run(scissor, ctx, 1.2);
    return scissor;
  }
  const enemy =
    key === 'hydra'
      ? new Hydra(240, 470, 470)
      : key === 'orbiter'
        ? new Orbiter(240, 500, 500)
        : new Juggernaut(240, 500, 500);
  run(enemy, ctx, 0.7);
  return enemy;
}

describe('ELITE_MODELS (P05-R19 to P05-R23)', () => {
  it('P05-R24: a model for each elite kind, among the enemy models', () => {
    expect(Object.keys(ELITE_MODELS).sort()).toEqual([...KEYS].sort());
    for (const key of KEYS) {
      expect(ENEMY_MODELS[key], key).toBe(ELITE_MODELS[key]);
      expect(C[key].stats.model).toBe(key);
    }
  });

  it('P05-R19..R23: each model is as big as the spec says (L = the medium player ship)', () => {
    for (const key of KEYS) {
      const { width, length } = extent(build(key));
      const measured = Math.max(width, length) / ENEMY_UNIT;
      expect(Math.abs(measured / C[key].size - 1), key).toBeLessThan(0.15);
    }
  });

  it('GD-61: dark metallic hulls with neon lights', () => {
    for (const key of KEYS) {
      const names = build(key)
        .root.getChildMeshes()
        .map((m) => m.material?.name);
      expect(names, key).toContain('enemy-hull');
      expect(names, key).toContain('enemy-neon');
    }
  });

  it('P05-R19..R23: light models, in the range of the other enemies', () => {
    for (const key of KEYS) {
      const triangles = build(key)
        .root.getChildMeshes()
        .reduce((n, m) => n + m.getTotalIndices() / 3, 0);
      expect(triangles, key).toBeGreaterThan(200);
      expect(triangles, key).toBeLessThan(1500);
    }
  });

  it('phase 7 review: each elite kind fires from the muzzles its model draws, at rest', () => {
    for (const key of KEYS) {
      const drawn = marked(build(key));
      const muzzles = MUZZLES[key];
      expect([...drawn.keys()].sort(), key).toEqual(Object.keys(muzzles).sort());
      for (const [kind, config] of Object.entries(muzzles)) {
        expectSame(config, drawn.get(kind) ?? [], `${key} ${kind}`);
      }
    }
  });

  it('P05-R13: the moving parts are drawn where the simulation puts them, with their muzzles', () => {
    for (const key of ['hydra', 'orbiter', 'scissor', 'juggernaut'] as const) {
      const enemy = swung(key);
      const model = build(key);
      model.sync(enemy, 0);
      let moved = 0;
      for (const part of enemy.parts) {
        const root = node(model, `${key}-${part.spec.id}`);
        const rest = Vector3.FromArray(bossPoint(part.spec.x, part.spec.y));
        const [x, y] = asMuzzle(Vector3.TransformCoordinates(rest, root.getWorldMatrix()));
        expect(x, `${key} ${part.spec.id}`).toBeCloseTo(part.x - enemy.x, 1);
        expect(y, `${key} ${part.spec.id}`).toBeCloseTo(part.y - enemy.y, 1);
        moved += Math.hypot(part.x - enemy.x - part.spec.x, part.y - enemy.y - part.spec.y);
      }
      expect(moved, key).toBeGreaterThan(1);
      // Each part's gun: its muzzle drawn where the part fires from now.
      for (const part of enemy.parts) {
        const muzzle = PART_MUZZLES[part.spec.id];
        if (!muzzle) continue;
        const prefix = `${key}-${part.spec.id}-muzzle-`;
        const drawn = model.root
          .getDescendants<TransformNode>(false)
          .find((n) => n.name.startsWith(prefix));
        drawn?.computeWorldMatrix(true);
        const at = asMuzzle(drawn?.getAbsolutePosition() ?? new Vector3(NaN, NaN, NaN));
        const p = part.place(muzzle);
        expect(at[0], prefix).toBeCloseTo(p.x - enemy.x, 1);
        expect(at[1], prefix).toBeCloseTo(p.y - enemy.y, 1);
        expect(at[2], prefix).toBeCloseTo(p.height, 1);
      }
    }
  });

  it('P05-R13: a destroyed part disappears from the model', () => {
    const jug = new Juggernaut(240, 500, 500);
    const model = build('juggernaut');
    const plate = jug.parts.find((p) => p.spec.id === 'plate-left');
    if (plate) plate.health = 0;
    model.sync(jug, 0);
    expect(node(model, 'juggernaut-plate-left').isEnabled()).toBe(false);
    expect(node(model, 'juggernaut-plate-right').isEnabled()).toBe(true);
  });

  it("P05-R23: the Hive's launch ring turns, its hatch drawn where the Wasps come out", () => {
    const hive = new Hive(240, 600);
    const ctx = new RecordingContext();
    run(hive, ctx, 2.3);
    expect(hive.spin).toBeGreaterThan(1);
    const model = build('hive');
    model.sync(hive, 0);
    const [x, y] = asMuzzle(node(model, 'hive-ring-muzzle-launch-0').getAbsolutePosition());
    const hatch = hive.hatch(ctx);
    expect(x).toBeCloseTo(hatch.x - hive.x, 1);
    expect(y).toBeCloseTo(hatch.y - hive.y, 1);
  });
});
