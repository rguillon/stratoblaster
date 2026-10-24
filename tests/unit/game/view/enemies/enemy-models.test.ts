import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { ENEMY_CONFIG, ENEMY_UNIT } from '../../../../../src/game/config/enemies';
import { ENEMY_LOOK } from '../../../../../src/game/config/enemy-look';
import { ENEMY_MODELS } from '../../../../../src/game/view/enemies/enemy-models';
import { Dropper } from '../../../../fixtures/sample-enemies';

const scene = (): Scene => new Scene(new NullEngine());

/** Width across X and length along Z of a model's body (its meshes, reactor flames left out). */
function extent(key: string) {
  const model = ENEMY_MODELS[key]?.(scene());
  if (!model) throw new Error(key);
  model.root.computeWorldMatrix(true);
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
  return { width: span('x'), length: span('z'), height: span('y'), model };
}

/** The spec size (in L) of each model, across its biggest side seen from above. */
const SIZES: Readonly<Record<string, number>> = {
  gnat: ENEMY_CONFIG.gnat.size,
  hornet: ENEMY_CONFIG.hornet.size,
  scout: ENEMY_CONFIG.scout.size,
  strafer: ENEMY_CONFIG.strafer.size,
  weaver: ENEMY_CONFIG.weaver.size,
  spinner: ENEMY_CONFIG.spinner.size,
  lancer: ENEMY_CONFIG.lancer.size,
  rocketeer: ENEMY_CONFIG.rocketeer.size,
  bulwark: ENEMY_CONFIG.bulwark.size,
  splitter: ENEMY_CONFIG.splitter.size,
  'splitter-pod': ENEMY_CONFIG.splitterPod.size,
  carrier: ENEMY_CONFIG.carrier.size,
};

describe('ENEMY_MODELS', () => {
  it('P05-R01..R10: a model per enemy model key', () => {
    const keys = Object.values(ENEMY_CONFIG).map((c) => c.stats.model);
    expect(Object.keys(ENEMY_MODELS).sort()).toEqual([...keys].sort());
  });

  it('P05-R01..R10, P05-R12: each model is as big as the spec says (L = the medium player ship)', () => {
    for (const [key, size] of Object.entries(SIZES)) {
      const { width, length, height } = extent(key);
      const measured = Math.max(width, length) / ENEMY_UNIT;
      expect(Math.abs(measured / size - 1), key).toBeLessThan(0.15);
      // Flat ships, seen from above.
      expect(height, key).toBeLessThan(Math.max(width, length) / 2);
    }
  });

  it('GD-61: dark metallic hulls with neon lights', () => {
    for (const key of Object.keys(ENEMY_MODELS)) {
      const { model } = extent(key);
      const meshes = model.root.getChildMeshes();
      const names = meshes.map((m) => m.material?.name);
      expect(names, key).toContain('enemy-hull');
      expect(names, key).toContain('enemy-neon');
    }
    expect(Math.max(...ENEMY_LOOK.hull.base)).toBeLessThan(0.2);
  });

  it('P05-R07, P05-R08: charging lights brighten with the enemy charge', () => {
    const { model } = extent('rocketeer');
    const light = model.root.getChildMeshes().find((m) => m.name === 'rocketeer-charge');
    const mat = light?.material as StandardMaterial | undefined;
    const enemy = new Dropper(0, 0);
    enemy.charge = 0;
    model.sync(enemy, 0);
    const dim = mat?.emissiveColor.r ?? 0;
    enemy.charge = 1;
    model.sync(enemy, 0);
    expect(mat?.emissiveColor.r).toBeCloseTo(ENEMY_LOOK.neon.rocketeer[0]);
    expect(dim).toBeLessThan(mat?.emissiveColor.r ?? 0);
  });

  it('P05-R06, P05-R10: the pods sit where the simulation fires from or splits them', () => {
    const spinner = extent('spinner');
    expect(spinner.width / 2).toBeGreaterThan(ENEMY_CONFIG.spinner.podRadius);
    const lancer = extent('lancer');
    expect(lancer.length / 2).toBeGreaterThanOrEqual(ENEMY_CONFIG.lancer.emitterOffset);
  });

  it('phase 5 review: reactors with animated flames, the same light blue on every enemy', () => {
    const counts: Readonly<Record<string, number>> = {
      gnat: 1,
      hornet: 1,
      scout: 2,
      strafer: 4,
      weaver: 2,
      spinner: 0,
      lancer: 3,
      rocketeer: 2,
      bulwark: 3,
      splitter: 1,
      'splitter-pod': 1,
      carrier: 2,
    };
    for (const [key, count] of Object.entries(counts)) {
      const { model } = extent(key);
      const reactors = model.root.getChildren((n) => n.name.startsWith(`${key}-reactor-`), true);
      expect(reactors, key).toHaveLength(count);
    }
    const exhaust = (key: string): StandardMaterial | undefined =>
      extent(key)
        .model.root.getChildMeshes()
        .find((m) => m.name.endsWith('reactor-0-exhaust'))?.material as
        StandardMaterial | undefined;
    for (const key of ['gnat', 'rocketeer', 'bulwark', 'splitter']) {
      expect(exhaust(key)?.emissiveColor.asArray(), key).toEqual([...ENEMY_LOOK.reactor.color]);
    }
    const { model } = extent('bulwark');
    const flame = model.root.getChildMeshes().find((m) => m.name.endsWith('reactor-0-exhaust'));
    const pivot = flame?.parent as TransformNode | undefined;
    const before = pivot?.scaling.z;
    model.sync(new Dropper(0, 0), 0.13);
    expect(pivot?.scaling.z).not.toBe(before);
  });

  it('P05-R01, phase 5 review: the Gnat is a drone with three ducted fans that spin', () => {
    const { model } = extent('gnat');
    const rotors = model.root.getChildren((n) => n.name.startsWith('gnat-rotor-'), false);
    expect(rotors).toHaveLength(3);
    const rotor = rotors[0] as TransformNode | undefined;
    const before = rotor?.rotation.y ?? 0;
    model.sync(new Dropper(0, 0), 0.1);
    expect(rotor?.rotation.y).toBeCloseTo(before + ENEMY_LOOK.rotor.spinRadPerSec * 0.1);
  });

  it('phase 5 review: a reactor costs about 40 triangles', () => {
    const s = scene();
    const withReactors = ENEMY_MODELS.bulwark?.(s);
    const flames = withReactors?.root.getChildMeshes().filter((m) => m.name.includes('-reactor-'));
    const triangles = (flames ?? []).reduce((n, m) => n + m.getTotalIndices() / 3, 0);
    // 3 reactors: 2 capless 4-sided cones and 2 tetrahedra each (the nozzle and core are in
    // the hull and neon meshes: a 6-sided band and a hexagon, 16 triangles).
    expect(triangles / 3).toBeLessThanOrEqual(24);
  });
});
