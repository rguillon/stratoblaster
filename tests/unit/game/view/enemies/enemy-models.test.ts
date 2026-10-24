import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { ENEMY_CONFIG, ENEMY_UNIT } from '../../../../../src/game/config/enemies';
import { ENEMY_LOOK } from '../../../../../src/game/config/enemy-look';
import { ENEMY_MODELS } from '../../../../../src/game/view/enemies/enemy-models';
import { Dropper } from '../../../../fixtures/sample-enemies';

const scene = (): Scene => new Scene(new NullEngine());

/** Width across X and length along Z of a model, from its meshes. */
function extent(key: string) {
  const model = ENEMY_MODELS[key]?.(scene());
  if (!model) throw new Error(key);
  model.root.computeWorldMatrix(true);
  const { min, max } = model.root.getHierarchyBoundingVectors(true);
  return { width: max.x - min.x, length: max.z - min.z, height: max.y - min.y, model };
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
};

describe('ENEMY_MODELS', () => {
  it('P05-R01..R10: a model per enemy model key', () => {
    const keys = Object.values(ENEMY_CONFIG).map((c) => c.stats.model);
    expect(Object.keys(ENEMY_MODELS).sort()).toEqual([...keys].sort());
  });

  it('P05-R01..R10: each model is as big as the spec says (L = the medium player ship)', () => {
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
    const lancer = extent('lancer').model;
    lancer.root.computeWorldMatrix(true);
    const { max } = lancer.root.getHierarchyBoundingVectors(true);
    expect(max.z).toBeGreaterThanOrEqual(ENEMY_CONFIG.lancer.emitterOffset);
  });
});
