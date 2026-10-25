import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { Scene } from '@babylonjs/core/scene';
import { EnemyShots } from '../../../../../src/core/systems/enemy-shots';
import { createBlastRenderer } from '../../../../../src/game/view/enemies/blast-renderer';
import { createEnemyShotRenderer } from '../../../../../src/game/view/enemies/enemy-shot-renderer';
import { ENEMY_BINDINGS } from '../../../../../src/game/view/enemies/enemy-bindings';
import { Dropper } from '../../../../fixtures/sample-enemies';

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
  it('GD-43: draws each bullet in its colour, where it is', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createEnemyShotRenderer(scene);
    const shots = new EnemyShots({ width: 480, height: 640, cullMargin: 20 });
    shots.fireBullet(10, 20, 0, { speed: 0, radius: 4, style: 'red' });
    shots.fireBullet(30, 40, 0, { speed: 0, radius: 4, style: 'blue' });
    shots.fireBullet(50, 60, 0, { speed: 0, radius: 4, style: 'unknown' });
    renderer.sync(frame(shots));
    const red = enabled(scene, 'enemy-bullet-red-');
    expect(red).toHaveLength(2);
    expect(red[0]?.position.x).toBe(10);
    expect(enabled(scene, 'enemy-bullet-blue-')).toHaveLength(1);
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
    for (const name of ['fireballs', 'debris', 'embers', 'flashes', 'rings']) {
      expect(layer(name)?.isEnabled(), name).toBe(true);
      expect(layer(name)?.thinInstanceCount, name).toBeGreaterThan(0);
    }
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
    const flashes = scene.getMeshByName('blast-flashes') as Mesh;
    const uploaded: number[] = [];
    const update = flashes.thinInstanceBufferUpdated.bind(flashes);
    flashes.thinInstanceBufferUpdated = (kind) => {
      if (kind === 'matrix') uploaded.push(flashes.thinInstanceCount);
      update(kind);
    };
    // A second flash while the first one lasts: the buffers have room, they are updated.
    renderer.sync([{ kind: 'enemy', x: 200, y: 20, radius: 15 }], 0.01);
    expect(flashes.thinInstanceCount).toBe(2);
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
