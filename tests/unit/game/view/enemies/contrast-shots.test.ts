import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Constants } from '@babylonjs/core/Engines/constants';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { Scene } from '@babylonjs/core/scene';
import { EnemyShots } from '../../../../../src/core/systems/enemy-shots';
import { ENEMY_LOOK } from '../../../../../src/game/config/enemy-look';
import { READABILITY } from '../../../../../src/game/config/readability';
import { ENEMY_BINDINGS } from '../../../../../src/game/view/enemies/enemy-bindings';
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
  // Through the bindings, as a level calls it with its style.
  const renderer = ENEMY_BINDINGS.shots(scene, style);
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

/** The first 3 vertex colour channels of `m`. */
const rgb = (m: Mesh | null) => Array.from(m?.getVerticesData('color')?.slice(0, 3) ?? []);
const order = (m: Mesh | null) => m?.alphaIndex ?? Number.NaN;

/** A renderer after one frame with a tiny red bullet (0.5 px hit radius). */
function tinyBullet() {
  const scene = new Scene(new NullEngine());
  const renderer = createEnemyShotRenderer(scene);
  const shots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });
  shots.fireBullet(10, 20, 0, { speed: 0, radius: 0.5, style: 'red' });
  const bullets = shots.bullets.filter((b) => b.alive);
  renderer.sync({ bullets, missiles: [], lasers: [], dtSeconds: 1 / 60 });
  return { scene, body: scene.getMeshByName('enemy-bullet-red') as Mesh | null };
}

/** A red bullet drawn by `mesh` has a dark rim behind its body and a white spark over its core. */
function expectContrastBullet(mesh: (name: string) => Mesh | null): void {
  const rim = mesh('enemy-bullet-red-rim');
  const spark = mesh('enemy-bullet-red-spark');
  expect(rim?.thinInstanceCount).toBe(1);
  expect(spark?.thinInstanceCount).toBe(1);
  expect(order(rim)).toBeLessThan(order(mesh('enemy-bullet-red')));
  expect(order(spark)).toBeGreaterThan(order(mesh('enemy-bullet-red-core')));
  // Dark, so it shows on lava and snow; white at the heart.
  expect(Math.max(...rgb(rim))).toBeLessThan(0.1);
  expect(Math.min(...rgb(spark))).toBeGreaterThan(0.9);
}

describe('Enemy shots over fire (P10-R07)', () => {
  it('P10-R07: World 4 levels draw their shots in the contrast style; the other worlds are unchanged', () => {
    for (const level of WORLD_4)
      expect(lookOf(level.scenery.id)?.shotStyle, level.id).toBe(ENEMY_LOOK.contrast.style);
    for (const level of [...WORLD_1, ...WORLD_2, ...WORLD_3])
      expect(lookOf(level.scenery.id)?.shotStyle, level.id).toBeUndefined();
  });

  it('P10-R07, P14-R05: in every style a bullet gets a dark rim behind it and a white spark at its heart', () => {
    for (const style of [undefined, ENEMY_LOOK.contrast.style])
      expectContrastBullet(drawn(style).mesh);
  });

  it('P10-R07, P14-R05: in every style a laser’s warning line is wide, with a white core', () => {
    const plain = drawn();
    const contrast = drawn(ENEMY_LOOK.contrast.style);
    const width = (m: typeof plain.warning) => m?.scaling.x ?? 0;
    expect(width(plain.warning)).toBeCloseTo(width(contrast.warning));
    const centre = (m: typeof plain.warning) => {
      const data = Array.from(m?.getVerticesData('color') ?? []);
      // The middle column of the bar is its core.
      const mid = Math.floor(data.length / 8) * 4;
      return data.slice(mid, mid + 3);
    };
    expect(centre(plain.warning)).toEqual(centre(contrast.warning));
    expect(Math.min(...centre(plain.warning))).toBeGreaterThan(0.8);
  });

  it('P14-R05: bullets are drawn over everything else, at least the smallest size', () => {
    const { scene, body } = tinyBullet();
    const others = scene.meshes.filter((m) => !m.name.startsWith('enemy-bullet-'));
    for (const m of others) expect(order(body)).toBeGreaterThan(m.alphaIndex);
    expect(body?.material?.depthFunction).toBe(Constants.ALWAYS);
    // Its drawn radius (the matrix's scale) is at least half the smallest size.
    const m = body?.thinInstanceGetWorldMatrices()[0]?.m ?? [0, 0];
    const scale = Math.hypot(m[0] ?? 0, m[1] ?? 0);
    expect(2 * scale).toBeGreaterThanOrEqual(READABILITY.minEnemyBulletSize - 1e-9);
  });
});
