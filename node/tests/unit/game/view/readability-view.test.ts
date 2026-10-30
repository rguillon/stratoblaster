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
  toned,
} from '../../../../src/game/view/readability-view';
import { outlineOf } from '../../../../src/render/outline';
import { SAMPLE_GAME } from '../../../fixtures/sample-game';
import { at } from '../../../helpers/at';

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

  it('P14-R01 (reviewer, 2026-10-28): every level darkens its ground, props, haze and clouds', () => {
    const tones = Object.values(READABILITY.tones);
    for (const [id, look] of Object.entries(GAME.view.scenery.looks)) {
      expect(tones, id).toContain(look.tone);
    }
    const look = at(Object.values(SAMPLE_GAME.view.scenery.looks), 0);
    const dark = toned(look, 0.5);
    expect(dark.tone).toBe(0.5);
    expect(dark.terrain.ground.colors[1]).toEqual(look.terrain.ground.colors[1].map((v) => v / 2));
    expect(dark.terrain.shore.deep).toEqual(look.terrain.shore.deep.map((v) => v / 2));
    expect(dark.sea.color).toEqual(look.sea.color.map((v) => v / 2));
    expect(dark.roads.main).toEqual(look.roads.main.map((v) => v / 2));
    // Tint factors stay as they were; the engine dims the haze and the clouds.
    expect(dark.terrain.tints).toEqual(look.terrain.tints);
    expect(dark.sky).toEqual(look.sky);
  });
});
