import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { createRng } from '../../../../../src/core/math/rng';
import { L } from '../../../../../src/game/config/bosses/boss-kit';
import { BOSS_LOOK } from '../../../../../src/game/config/boss-look';
import { BOSS_DESIGNS, BOSS_KINDS } from '../../../../../src/game/sim/boss-kinds';
import { BOSS_MODELS } from '../../../../../src/game/view/bosses/boss-models';
import { bossPoint } from '../../../../../src/game/view/bosses/boss-model';
import { ENEMY_BINDINGS } from '../../../../../src/game/view/enemies/enemy-bindings';
import { RecordingContext, runUntil } from '../../../../helpers/enemy-context';

const AREA = { width: 480, height: 640, random: createRng(1), topRange: [107, 373] as const };
const scene = (): Scene => new Scene(new NullEngine());

/** Triangles drawn by the enabled meshes under `root`. */
function triangles(root: TransformNode): number {
  return root
    .getChildMeshes<Mesh>(false)
    .filter((m) => m.isEnabled())
    .reduce((n, m) => n + m.getTotalIndices() / 3, 0);
}

/** Width and length of what is drawn, reactor flames left out. */
function extent(root: TransformNode) {
  root.computeWorldMatrix(true);
  const boxes = root
    .getChildMeshes<Mesh>(false)
    .filter((m) => m.isEnabled() && !m.name.includes('-reactor-'))
    .map((m) => {
      m.computeWorldMatrix(true);
      return m.getBoundingInfo().boundingBox;
    });
  const span = (axis: 'x' | 'z') =>
    Math.max(...boxes.map((b) => b.maximumWorld[axis])) -
    Math.min(...boxes.map((b) => b.minimumWorld[axis]));
  return { width: span('x'), length: span('z') };
}

/** A boss of `id` in place, and its model synced once. */
function shown(id: string) {
  const kind = BOSS_KINDS.find((k) => k.id === id);
  if (!kind) throw new Error(id);
  const boss = kind.spawn(AREA);
  runUntil(boss, new RecordingContext(), () => boss.state === 'fighting');
  const model = BOSS_MODELS[id]?.(scene());
  if (!model) throw new Error(id);
  model.sync(boss, 1 / 60);
  return { boss, model };
}

describe('Boss models', () => {
  it('P07-R05: a model per boss, registered with the enemy models', () => {
    expect(Object.keys(BOSS_MODELS).sort()).toEqual(BOSS_DESIGNS.map((d) => d.id).sort());
    for (const design of BOSS_DESIGNS) {
      expect(ENEMY_BINDINGS.models[design.stats.model], design.id).toBe(BOSS_MODELS[design.id]);
      expect(BOSS_LOOK.neon[design.id], design.id).toBeDefined();
    }
  });

  it.each(BOSS_DESIGNS.map((d) => [d.id, d] as const))(
    'P07-R05: the %s is about its size across, and within its triangle budget (≤ 6,000)',
    (id, design) => {
      const { model } = shown(id);
      expect(triangles(model.root), id).toBeLessThanOrEqual(6000);
      const { width, length } = extent(model.root);
      const size = (design.stats.radius * 2) / L;
      expect(Math.abs(Math.max(width, length) / L / size - 1), id).toBeLessThan(0.15);
    },
  );

  it('P07-R01: a destroyed part is replaced by a stump; a damaged one smokes', () => {
    const { boss, model } = shown('reef-warden');
    const nodes = (part: string) =>
      model.root.getDescendants(false).filter((n) => n.name.startsWith(`reef-warden-${part}`));
    const enabled = (name: string) =>
      nodes('cannon-left')
        .find((n) => n.name === name)
        ?.isEnabled(false);
    expect(enabled('reef-warden-cannon-left')).toBe(true);
    expect(enabled('reef-warden-cannon-left-stump')).toBe(false);
    expect(enabled('reef-warden-cannon-left-smoke')).toBe(false);
    const [left] = boss.parts;
    if (!left) throw new Error('no part');
    left.health = left.maxHealth * 0.4;
    model.sync(boss, 1 / 60);
    expect(enabled('reef-warden-cannon-left-smoke')).toBe(true);
    left.destroy();
    model.sync(boss, 1 / 60);
    expect(enabled('reef-warden-cannon-left')).toBe(false);
    expect(enabled('reef-warden-cannon-left-stump')).toBe(true);
    expect(enabled('reef-warden-cannon-left-smoke')).toBe(false);
  });

  it('P07-R01: a part flashes white for a moment when hit', () => {
    const { boss, model } = shown('reef-warden');
    const hullOf = () =>
      model.root
        .getChildMeshes<Mesh>(false)
        .find(
          (m) => m.name.startsWith('reef-warden-cannon-right-') && m.name.endsWith('enemy-hull'),
        );
    const [, right] = boss.parts;
    if (!right) throw new Error('no part');
    right.health -= 10;
    model.sync(boss, 0.01);
    expect(hullOf()?.material?.name).toBe('boss-flash');
    model.sync(boss, 0.1);
    right.sinceHit += 0.1;
    model.sync(boss, 0.01);
    expect(hullOf()?.material?.name).toBe('enemy-hull');
  });

  it('P07-R05: orbiting parts are drawn on a ring that turns with the boss', () => {
    const { boss, model } = shown('dust-devil');
    const ring = model.root.getDescendants(false).find((n) => n.name === 'dust-devil-ring');
    boss.spin = 1.25;
    model.sync(boss, 1 / 60);
    expect((ring as TransformNode | undefined)?.rotation.y).toBe(1.25);
  });

  it('P07-R05: a playfield offset maps to the model’s nose-down space', () => {
    expect(bossPoint(10, -20, 3)).toEqual([-10, 3, 20]);
  });
});
