import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { Scene } from '@babylonjs/core/scene';
import { EnemyShots } from '../../../../../src/core/systems/enemy-shots';
import { ENEMY_LOOK } from '../../../../../src/game/config/enemy-look';
import { createEnemyShotRenderer } from '../../../../../src/game/view/enemies/enemy-shot-renderer';
import { WORLD_1 } from '../../../../../src/game/sim/world-1';
import { WORLD_2 } from '../../../../../src/game/sim/world-2';
import { WORLD_3 } from '../../../../../src/game/sim/world-3';
import { WORLD_4 } from '../../../../../src/game/sim/world-4';
import { SCENERY_BINDINGS } from '../../../../../src/game/view/scenery-bindings';
import { Dropper } from '../../../../fixtures/sample-enemies';

const LASER = { warningSeconds: 1, firingSeconds: 1, width: 10, style: 'l' };

/** A renderer in `style` after one frame with a red bullet and a laser's warning line. */
function drawn(style?: string) {
  const scene = new Scene(new NullEngine());
  const renderer = createEnemyShotRenderer(scene, style);
  const shots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });
  shots.fireBullet(10, 20, 0, { speed: 0, radius: 4, style: 'red' });
  shots.fireLaser(new Dropper(200, 500), LASER);
  renderer.sync({
    bullets: shots.bullets.filter((b) => b.alive),
    missiles: [],
    lasers: shots.lasers,
    dtSeconds: 1 / 60,
  });
  const mesh = (name: string) => scene.getMeshByName(name) as Mesh | null;
  const warning = scene.meshes.find(
    (m) => m.name.startsWith('enemy-laser-warning-l-') && m.isEnabled(),
  );
  return { mesh, warning };
}

const lookOf = (id: string) => SCENERY_BINDINGS.looks[id];

describe('Enemy shots over fire (P10-R07)', () => {
  it('P10-R07: World 4 levels draw their shots in the contrast style; the other worlds are unchanged', () => {
    for (const level of WORLD_4)
      expect(lookOf(level.scenery.id)?.shotStyle, level.id).toBe(ENEMY_LOOK.contrast.style);
    for (const level of [...WORLD_1, ...WORLD_2, ...WORLD_3])
      expect(lookOf(level.scenery.id)?.shotStyle, level.id).toBeUndefined();
  });

  it('P10-R07: in the contrast style a bullet gets a dark rim behind it and a white spark at its heart', () => {
    const plain = drawn();
    expect(plain.mesh('enemy-bullet-red-rim')).toBeNull();
    expect(plain.mesh('enemy-bullet-red-spark')).toBeNull();
    const contrast = drawn(ENEMY_LOOK.contrast.style);
    const rim = contrast.mesh('enemy-bullet-red-rim');
    const spark = contrast.mesh('enemy-bullet-red-spark');
    expect(rim?.thinInstanceCount).toBe(1);
    expect(spark?.thinInstanceCount).toBe(1);
    // The rim is drawn behind the body, the spark in front of everything.
    const body = contrast.mesh('enemy-bullet-red');
    expect(rim?.alphaIndex).toBeLessThan(body?.alphaIndex ?? -Infinity);
    expect(spark?.alphaIndex).toBeGreaterThan(
      contrast.mesh('enemy-bullet-red-core')?.alphaIndex ?? 0,
    );
    // Dark, so it shows on lava; white at the heart.
    const rgb = (m: Mesh | null) => Array.from(m?.getVerticesData('color')?.slice(0, 3) ?? []);
    expect(Math.max(...rgb(rim))).toBeLessThan(0.1);
    expect(Math.min(...rgb(spark))).toBeGreaterThan(0.9);
  });

  it('P10-R07: in the contrast style a laser’s warning line is wider, with a white core', () => {
    const plain = drawn();
    const contrast = drawn(ENEMY_LOOK.contrast.style);
    const width = (m: typeof plain.warning) => m?.scaling.x ?? 0;
    expect(width(contrast.warning) / width(plain.warning)).toBeCloseTo(
      ENEMY_LOOK.contrast.warningWidth,
    );
    const centre = (m: typeof plain.warning) => {
      const data = Array.from(m?.getVerticesData('color') ?? []);
      // The middle column of the bar is its core.
      const mid = Math.floor(data.length / 8) * 4;
      return data.slice(mid, mid + 3);
    };
    expect(Math.min(...centre(contrast.warning))).toBeGreaterThan(
      Math.min(...centre(plain.warning)),
    );
  });
});
