import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Constants } from '@babylonjs/core/Engines/constants';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { Scene } from '@babylonjs/core/scene';
import { READABILITY } from '../../../../src/game/config/readability';
import { GAME } from '../../../../src/game';
import {
  buildHitboxMarker,
  outlinedShips,
  tonedShots,
  withVeil,
} from '../../../../src/game/view/readability-view';
import { outlineOf } from '../../../../src/render/outline';

const scene = () => new Scene(new NullEngine());

describe('readability views (phase 14)', () => {
  it('P14-R03: the player ships get a rim in the player colour', () => {
    const s = scene();
    for (const [id, build] of Object.entries(GAME.view.playerShipModels)) {
      const root = build(s);
      const rims = root.getChildMeshes().filter((m) => outlineOf(m));
      expect(rims.length, id).toBeGreaterThan(0);
      for (const m of rims) expect(outlineOf(m)).toEqual(READABILITY.playerOutline.color);
    }
    const plain = outlinedShips({ cube: (sc) => CreateBox('cube', {}, sc) });
    expect(Object.keys(plain)).toEqual(['cube']);
    expect(outlineOf(plain.cube?.(s).getChildMeshes()[0] ?? CreateBox('x', {}, s))).toBeUndefined();
  });

  it('P14-R03: the hitbox marker is a disc of the hitbox radius, drawn over the ship', () => {
    const s = scene();
    const root = buildHitboxMarker(s, 5);
    const [disc] = root.getChildMeshes<Mesh>();
    expect(disc?.isEnabled()).toBe(true);
    expect(disc?.scaling.x).toBe(5);
    expect(disc?.position.z).toBeLessThan(0);
    expect(disc?.material?.depthFunction).toBe(Constants.ALWAYS);
    const extent = disc?.getBoundingInfo().boundingBox.extendSize.x ?? 0;
    expect(extent).toBeCloseTo(1);
  });

  it('P14-R06: player shots are toned down, other materials untouched', () => {
    const s = scene();
    const before = new StandardMaterial('before', s);
    before.alphaMode = Constants.ALPHA_ADD;
    before.alpha = 1;
    let solid: StandardMaterial | undefined;
    const [create] = Object.values(
      tonedShots({
        test: (sc) => {
          const glow = new StandardMaterial('glow', sc);
          glow.alphaMode = Constants.ALPHA_ADD;
          glow.alpha = 0.999;
          solid = new StandardMaterial('solid', sc);
          return { sync: () => undefined, dispose: () => undefined };
        },
      }),
    );
    create?.(s);
    expect(s.getMaterialByName('glow')?.alpha).toBe(READABILITY.playerShotMaxOpacity);
    expect(solid?.alpha).toBe(1);
    expect(before.alpha).toBe(1);
    for (const shots of Object.values(GAME.view.playerShotRenderers)) {
      const sc = scene();
      shots(sc).dispose();
    }
  });

  it('P14-R01: every level of the game has its world’s veil', () => {
    const looks = GAME.view.scenery.looks;
    for (const [id, look] of Object.entries(looks)) expect(look.veil, id).toBeDefined();
    const veiled = withVeil({ a: { shotStyle: 'x' } as never }, READABILITY.veils.world1);
    expect(veiled.a?.veil).toBe(READABILITY.veils.world1);
    expect(veiled.a?.shotStyle).toBe('x');
  });
});
