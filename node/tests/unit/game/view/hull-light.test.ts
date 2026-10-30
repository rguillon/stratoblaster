import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { READABILITY } from '../../../../src/game/config/readability';
import { enemyMaterials } from '../../../../src/game/view/enemies/enemy-mesh';
import { getShipMaterials } from '../../../../src/game/view/ship-materials';

describe('hull light (reviewer, 2026-10-28)', () => {
  it('the player ship, enemy and boss metal is lit brighter', () => {
    const scene = new Scene(new NullEngine());
    const { direct, environment } = READABILITY.hullLight;
    expect(direct).toBeGreaterThan(1);
    expect(environment).toBeGreaterThan(1);
    for (const mat of [getShipMaterials(scene).hull, enemyMaterials(scene).hull]) {
      expect(mat.directIntensity, mat.name).toBe(direct);
      expect(mat.environmentIntensity, mat.name).toBe(environment);
    }
  });
});
