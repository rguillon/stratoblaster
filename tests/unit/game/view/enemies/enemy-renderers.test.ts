import { describe, expect, it } from 'vitest';
import { Constants } from '@babylonjs/core/Engines/constants';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { Scene } from '@babylonjs/core/scene';
import { EnemyShots } from '../../../../../src/core/systems/enemy-shots';
import { createBlastRenderer } from '../../../../../src/game/view/enemies/blast-renderer';
import { createEnemyShotRenderer } from '../../../../../src/game/view/enemies/enemy-shot-renderer';
import { ENEMY_BINDINGS } from '../../../../../src/game/view/enemies/enemy-bindings';
import { Dropper } from '../../../../fixtures/sample-enemies';
import { BOSS_LOOK } from '../../../../../src/game/config/boss-look';
import { ENEMY_LOOK } from '../../../../../src/game/config/enemy-look';

const enabled = (scene: Scene, prefix: string) =>
  scene.meshes.filter(
    (m) => m.name.startsWith(prefix) && m.isEnabled() && !m.name.endsWith(prefix),
  );

function frame(shots: EnemyShots, dtSeconds = 1 / 60) {
  return {
    bullets: shots.bullets.filter((b) => b.alive),
    missiles: shots.missiles.filter((m) => m.alive),
    lasers: shots.lasers,
    dtSeconds,
  };
}

describe('createEnemyShotRenderer', () => {
  /** Each instance's position, scale and angle in a bullet layer mesh, from its matrices. */
  const instances = (scene: Scene, name: string) => {
    const mesh = scene.getMeshByName(name) as Mesh | null;
    if (!mesh?.isEnabled()) return [];
    const data = (mesh as unknown as { _thinInstanceDataStorage: { matrixData: Float32Array } })
      ._thinInstanceDataStorage.matrixData;
    return Array.from({ length: mesh.thinInstanceCount }, (_, i) => {
      const [c = 0, s = 0] = data.subarray(i * 16, i * 16 + 2);
      return {
        x: data[i * 16 + 12] ?? 0,
        y: data[i * 16 + 13] ?? 0,
        scale: Math.hypot(c, s),
        angle: Math.atan2(s, c),
      };
    });
  };

  it('GD-43: draws each bullet in its colour, where it is, a few draw calls for them all', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createEnemyShotRenderer(scene);
    const shots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });
    shots.fireBullet(10, 20, 0, { speed: 0, radius: 4, style: 'red' });
    shots.fireBullet(30, 40, 0, { speed: 0, radius: 4, style: 'blue' });
    shots.fireBullet(50, 60, 0, { speed: 0, radius: 4, style: 'unknown' });
    renderer.sync(frame(shots));
    const red = instances(scene, 'enemy-bullet-red');
    expect(red).toHaveLength(2);
    expect(red[0]?.x).toBe(10);
    expect(red[0]?.scale).toBeCloseTo(4 * ENEMY_LOOK.bullets.scale);
    expect(instances(scene, 'enemy-bullet-blue')).toHaveLength(1);
    expect(instances(scene, 'enemy-bullet-green')).toHaveLength(0);
    renderer.dispose();
  });

  it('a bullet is a ball of plasma: an aura, a body, swirls spinning opposite ways, a core', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createEnemyShotRenderer(scene);
    const shots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });
    shots.fireBullet(10, 20, 0, { speed: 0, radius: 4, style: 'red' });
    const angles = (i: number) =>
      [0, 1].map(() => {
        shots.step(0.05, 0, 0);
        renderer.sync(frame(shots));
        return instances(scene, `enemy-bullet-red-swirl-${String(i)}`)[0]?.angle ?? 0;
      });
    const [a0, a1] = angles(0);
    const [b0, b1] = angles(1);
    expect(instances(scene, 'enemy-bullet-red-halo')[0]?.scale).toBeGreaterThan(
      4 * ENEMY_LOOK.bullets.scale,
    );
    expect(Math.sign((a1 ?? 0) - (a0 ?? 0))).toBe(-Math.sign((b1 ?? 0) - (b0 ?? 0)));
    renderer.dispose();
  });

  it('phase 8 review: each bullet has a white-hot core that pulses as it flies', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createEnemyShotRenderer(scene);
    const shots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });
    shots.fireBullet(10, 20, 0, { speed: 0, radius: 4, style: 'red' });
    const r = 4 * ENEMY_LOOK.bullets.scale;
    const sizes = [0, 0.1, 0.2].map(() => {
      shots.step(0.1, 0, 0);
      renderer.sync(frame(shots));
      return (instances(scene, 'enemy-bullet-red-core')[0]?.scale ?? 0) / r;
    });
    expect(sizes.every((size) => size > 0 && size < 1)).toBe(true);
    expect(new Set(sizes).size).toBe(3);
    renderer.dispose();
  });

  it('phase 8 review: a beam has a flare at its base as the player laser, both over the models', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createEnemyShotRenderer(scene);
    const shots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });
    const laser = { warningSeconds: 1, firingSeconds: 1, width: 10, style: 'l' };
    shots.fireLaser(new Dropper(200, 500), laser);
    shots.step(1.1, 0, 0);
    renderer.sync(frame(shots));
    const [beam] = enabled(scene, 'enemy-laser-beam-');
    const [flare] = enabled(scene, 'enemy-laser-emitter-');
    const { radius, baseScale, widthDivisor, stretch, pulse } = ENEMY_LOOK.laser.flare;
    const size = radius * (baseScale + 10 / widthDivisor);
    expect(flare?.scaling.x).toBeGreaterThanOrEqual(size * (1 - pulse) - 1e-6);
    expect(flare?.scaling.x).toBeLessThanOrEqual(size * (1 + pulse) + 1e-6);
    expect(flare?.scaling.y).toBeCloseTo((flare?.scaling.x ?? 0) * stretch);
    // Drawn over the models, so a beam is seen leaving its emitter's lens.
    for (const mesh of [beam, flare]) {
      expect(mesh?.material?.depthFunction).toBe(Constants.ALWAYS);
    }
    renderer.dispose();
  });

  it("phase 8 review: a boss's lasers are drawn in its neon colour, the others in red", () => {
    const scene = new Scene(new NullEngine());
    const renderer = createEnemyShotRenderer(scene);
    const shots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });
    const laser = { warningSeconds: 1, firingSeconds: 1, width: 10 };
    shots.fireLaser(new Dropper(100, 500), { ...laser, style: 'sentinel' });
    shots.fireLaser(new Dropper(200, 500), { ...laser, style: 'lancer' });
    renderer.sync(frame(shots));
    expect(enabled(scene, 'enemy-laser-warning-sentinel-')).toHaveLength(1);
    expect(enabled(scene, 'enemy-laser-warning-lancer-')).toHaveLength(1);
    const colors = (style: string) => {
      const beam = scene.getMeshByName(`enemy-laser-beam-${style}`);
      const data = beam?.getVerticesData('color') ?? [];
      return Array.from({ length: data.length / 4 }, (_, i) => data.slice(4 * i, 4 * i + 3));
    };
    const has = (style: string, rgb: readonly number[]) =>
      colors(style).some((c) => c.every((v, k) => Math.abs(v - (rgb[k] ?? 0)) < 1e-6));
    expect(has('sentinel', BOSS_LOOK.neon.sentinel ?? [])).toBe(true);
    expect(has('lancer', ENEMY_LOOK.laser.color)).toBe(true);
    renderer.dispose();
  });

  it('P05-R07, P05-R08: draws missiles, and lasers as a warning line then a beam', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createEnemyShotRenderer(scene);
    const shots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });
    shots.fireMissile(100, 300, Math.PI, {
      speed: 0,
      turnRateDeg: 0,
      homingSeconds: 0,
      radius: 4,
      health: 1,
      style: 'r',
    });
    shots.fireLaser(new Dropper(200, 500), {
      warningSeconds: 1,
      firingSeconds: 1,
      width: 10,
      style: 'l',
    });
    renderer.sync(frame(shots));
    const missile = scene.getTransformNodeByName('enemy-missile-0');
    expect(missile?.isEnabled()).toBe(true);
    expect(missile?.rotation.z).toBeCloseTo(-Math.PI);
    expect(enabled(scene, 'enemy-laser-warning-')).toHaveLength(1);
    expect(enabled(scene, 'enemy-laser-beam-')).toHaveLength(0);
    shots.step(1.1, 0, 0);
    renderer.sync(frame(shots));
    expect(enabled(scene, 'enemy-laser-warning-')).toHaveLength(0);
    const [beam] = enabled(scene, 'enemy-laser-beam-');
    expect(beam?.scaling.y).toBeCloseTo(510);
    renderer.dispose();
  });
});

describe('createBlastRenderer', () => {
  it('GD-62, phase 5 review: draws each layer of a blast as one mesh of thin instances', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createBlastRenderer(scene);
    const layer = (name: string): Mesh | undefined =>
      (scene.getMeshByName(`blast-${name}`) as Mesh | null) ?? undefined;
    expect(layer('fireballs')?.isEnabled()).toBe(false);
    renderer.sync([{ kind: 'enemy', x: 10, y: 20, radius: 15 }], 0.05);
    for (const name of ['fireballs', 'debris', 'embers', 'rings']) {
      expect(layer(name)?.isEnabled(), name).toBe(true);
      expect(layer(name)?.thinInstanceCount, name).toBeGreaterThan(0);
    }
    // No flash, and the ring laid over the ground: a blast does not light it (reviewer, 2026-10-28).
    expect(layer('flashes')).toBeUndefined();
    expect(layer('rings')?.material?.alphaMode).toBe(Constants.ALPHA_COMBINE);
    // Two blasts: more instances, not more meshes.
    const meshes = scene.meshes.length;
    const debris = layer('debris')?.thinInstanceCount ?? 0;
    renderer.sync([{ kind: 'enemy', x: 200, y: 20, radius: 15 }], 0.01);
    expect(scene.meshes).toHaveLength(meshes);
    expect(layer('debris')?.thinInstanceCount).toBeGreaterThan(debris);
    renderer.dispose();
    expect(layer('debris')).toBeUndefined();
  });

  it('phase 6 review: uploads the positions of every instance, new ones included', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createBlastRenderer(scene);
    renderer.sync([{ kind: 'enemy', x: 10, y: 20, radius: 15 }], 0.01);
    const rings = scene.getMeshByName('blast-rings') as Mesh;
    const uploaded: number[] = [];
    const update = rings.thinInstanceBufferUpdated.bind(rings);
    rings.thinInstanceBufferUpdated = (kind) => {
      if (kind === 'matrix') uploaded.push(rings.thinInstanceCount);
      update(kind);
    };
    // A second ring while the first one lasts: the buffers have room, they are updated.
    renderer.sync([{ kind: 'enemy', x: 200, y: 20, radius: 15 }], 0.01);
    expect(rings.thinInstanceCount).toBe(2);
    expect(uploaded).toEqual([2]);
    renderer.dispose();
  });
});

describe('ENEMY_BINDINGS', () => {
  it('P05: binds the models, the shot and blast renderers, and the glow', () => {
    expect(ENEMY_BINDINGS.shots).toBe(createEnemyShotRenderer);
    expect(ENEMY_BINDINGS.blasts).toBe(createBlastRenderer);
    expect(ENEMY_BINDINGS.glow.intensity).toBeGreaterThan(0);
  });
});
