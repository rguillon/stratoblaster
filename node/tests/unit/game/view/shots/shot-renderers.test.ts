import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { Constants } from '@babylonjs/core/Engines/constants';
import type { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import type { Projectile } from '../../../../../src/core/systems/projectile-motion';
import type { BeamSegment } from '../../../../../src/core/systems/beam';
import type { ShotFrame } from '../../../../../src/render/game-view';
import { BULLET, LASER, MISSILE } from '../../../../../src/game/config/player-weapons';
import { SHOT_LOOK } from '../../../../../src/game/config/shot-look';
import { PLAYER_SHOT_RENDERERS } from '../../../../../src/game/view/shots/player-shot-renderers';
import { createBulletRenderer } from '../../../../../src/game/view/shots/bullet-renderer';
import { createLaserRenderer } from '../../../../../src/game/view/shots/laser-renderer';
import { createMissileRenderer } from '../../../../../src/game/view/shots/missile-renderer';
import { buildMissile } from '../../../../../src/game/view/shots/missile-model';
import { flashScale } from '../../../../../src/game/view/shots/impact-flashes';
import { buildGlowDisc, buildTracer } from '../../../../../src/game/view/shot-geometry';

function frame(overrides: Partial<ShotFrame> = {}): ShotFrame {
  return { projectiles: [], beam: [], impacts: [], dtSeconds: 1 / 60, ...overrides };
}

function bullet(x: number, y: number, heading = 0): Projectile {
  return { alive: true, weapon: BULLET, x, y, heading, speed: 600, age: 0 };
}

function enabledMeshes(scene: Scene, prefix: string): string[] {
  return scene.meshes.filter((m) => m.name.startsWith(prefix) && m.isEnabled()).map((m) => m.name);
}

describe('player shot renderers', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
    scene = undefined;
  });
  const newScene = (): Scene => (scene = new Scene(new NullEngine()));

  it('has a renderer for every player weapon', () => {
    expect(Object.keys(PLAYER_SHOT_RENDERERS).sort()).toEqual(['bullet', 'laser', 'missile']);
  });

  it('P03-R01, phase 5 review: draws one additive tracer per bullet, along its heading', () => {
    const s = newScene();
    const renderer = createBulletRenderer(s);
    renderer.sync(frame({ projectiles: [bullet(10, 20), bullet(30, 40, 0.3)] }));
    const blobs = s.meshes.filter((m) => /^bullet-\d+$/.test(m.name) && m.isEnabled());
    expect(blobs).toHaveLength(2);
    const [a, b] = blobs;
    // Under the ship, which is drawn over the tracers leaving from inside it.
    expect(a?.position.asArray()).toEqual([10, 20, SHOT_LOOK.bullet.depth]);
    expect(SHOT_LOOK.bullet.depth).toBeGreaterThan(0);
    expect(b?.rotation.z).toBeCloseTo(-0.3);
    // Just fired (age 0): a short streak, growing to its full length from the muzzle.
    expect(b?.scaling.y).toBeCloseTo(SHOT_LOOK.bullet.width);
    renderer.sync(frame({ projectiles: [{ ...bullet(0, 0), age: 1 }] }));
    const tracer = s.meshes.find((m) => /^bullet-\d+$/.test(m.name) && m.isEnabled());
    expect(tracer?.scaling.y).toBe(SHOT_LOOK.bullet.length);
    expect((a?.material as StandardMaterial).alphaMode).toBe(Constants.ALPHA_ADD);
    renderer.sync(frame({ projectiles: [bullet(1, 1)] }));
    expect(s.meshes.filter((m) => /^bullet-\d+$/.test(m.name) && m.isEnabled())).toHaveLength(1);
    renderer.dispose();
  });

  it('P03 review: a bullet hit throws metal sparks, which then die out', () => {
    const s = newScene();
    const renderer = createBulletRenderer(s);
    const impact = { weaponId: 'bullet', x: 5, y: 6, blastRadius: 0 };
    renderer.sync(frame({ impacts: [impact] }));
    expect(enabledMeshes(s, 'bullet-spark-')).toHaveLength(SHOT_LOOK.impact.bullet.count);
    // No green flash any more.
    expect(s.meshes.some((m) => m.name.startsWith('bullet-hit'))).toBe(false);
    renderer.sync(frame({ dtSeconds: 1 }));
    expect(enabledMeshes(s, 'bullet-spark-')).toHaveLength(0);
  });

  it('P03-R02: draws each beam segment at its own width, contact glows and particles', () => {
    const s = newScene();
    const renderer = createLaserRenderer(s);
    const beam: BeamSegment[] = [
      { x: 50, y0: 10, y1: 100, level: 2, width: 6, hit: true },
      { x: 50, y0: 100, y1: 640, level: 1, width: 4, hit: false },
    ];
    renderer.sync(frame({ beam }));
    const bars = s.meshes.filter((m) => /^laser-\d+$/.test(m.name) && m.isEnabled());
    expect(bars).toHaveLength(2);
    expect(bars[0]?.scaling.y).toBeCloseTo(90);
    expect(bars[0]?.scaling.x ?? 0).toBeGreaterThan(bars[1]?.scaling.x ?? Infinity);
    expect(enabledMeshes(s, 'laser-contact-')).toHaveLength(1);
    // P03 review: a glow at the base of the beam, where it leaves the ship.
    const muzzle = s.getMeshByName('laser-muzzle-0');
    expect(muzzle?.isEnabled()).toBe(true);
    expect(muzzle?.position.x).toBe(50);
    expect(muzzle?.position.y).toBe(10);
    expect(enabledMeshes(s, 'laser-muzzle-')).toHaveLength(1);
    expect(enabledMeshes(s, 'laser-particle-')).toHaveLength(SHOT_LOOK.laser.particles.count);
    renderer.sync(frame());
    expect(s.meshes.filter((m) => m.name.startsWith('laser') && m.isEnabled())).toEqual([]);
    renderer.dispose();
  });

  it('P03-R03: draws a missile with a flame per projectile, and an explosion per impact', () => {
    const s = newScene();
    const renderer = createMissileRenderer(s);
    const missile: Projectile = { ...bullet(10, 20, 0.5), weapon: MISSILE };
    renderer.sync(
      frame({
        projectiles: [missile],
        impacts: [{ weaponId: 'missile', x: 1, y: 2, blastRadius: 10 }],
      }),
    );
    const node = s.getTransformNodeByName('missile-0');
    expect(node?.isEnabled()).toBe(true);
    expect(node?.rotation.z).toBeCloseTo(-0.5);
    // Phase 3 review: drawn behind the ship (Z = 0, the camera looks from -Z).
    expect(node?.position.z).toBe(SHOT_LOOK.missile.depth);
    expect(SHOT_LOOK.missile.depth).toBeGreaterThan(0);
    expect(s.meshes.some((m) => m.name.startsWith('missile-0-flame'))).toBe(true);
    expect(enabledMeshes(s, 'missile-blast-')).toHaveLength(1);
    renderer.dispose();
  });

  it('phase 5 review: a motor flare and an exhaust trail behind each missile, at its nozzle', () => {
    const s = newScene();
    const renderer = createMissileRenderer(s);
    const missile: Projectile = { ...bullet(10, 20, 0.5), weapon: MISSILE, age: 1 };
    renderer.sync(frame({ projectiles: [missile] }));
    const flare = s.getMeshByName('missile-flare-0');
    const trail = s.getMeshByName('missile-trail-0');
    expect(flare?.isEnabled()).toBe(true);
    expect(trail?.isEnabled()).toBe(true);
    expect(flare?.position.x).toBeLessThan(missile.x);
    expect(flare?.position.y).toBeLessThan(missile.y);
    expect(trail?.position.asArray()).toEqual(flare?.position.asArray());
    expect(trail?.rotation.z).toBeCloseTo(-0.5);
    expect(trail?.scaling.y).toBe(SHOT_LOOK.missile.trail.length);
    renderer.dispose();
    expect(s.meshes.some((m) => m.name.startsWith('missile-trail'))).toBe(false);
  });

  it('P03-R03: a missile points to +Y when its heading is 0, its top facing the camera', () => {
    const s = newScene();
    const pivot = buildMissile('m', s);
    const model = s.getTransformNodeByName('m-model');
    pivot.computeWorldMatrix(true);
    model?.computeWorldMatrix(true);
    const nose = Vector3.TransformNormal(
      new Vector3(0, 0, 1),
      model?.getWorldMatrix() ?? pivot.getWorldMatrix(),
    );
    const [nx, ny, nz] = nose.normalize().asArray();
    expect(nx).toBeCloseTo(0);
    expect(ny).toBeCloseTo(1);
    expect(nz).toBeCloseTo(0);
    const top = Vector3.TransformNormal(
      new Vector3(0, 1, 0),
      model?.getWorldMatrix() ?? pivot.getWorldMatrix(),
    );
    expect(top.normalize().z).toBeCloseTo(-1);
  });

  it('P03 review, phase 5 review: a tracer is 48 triangles and a spark 12', () => {
    const { colors, rows } = SHOT_LOOK.bullet;
    // 7 columns across (3 colours each side of the centre line) by 5 rows along: 6 × 4 quads.
    expect(buildTracer(colors, rows).indices.length / 3).toBe(48);
    const spark = SHOT_LOOK.impact.bullet;
    expect(buildGlowDisc(spark.segments, spark.colors).indices.length / 3).toBe(12);
  });

  it('P03 review: the glow at the base of the laser is round and smooth (24 sides, 6 rings)', () => {
    const { segments, colors } = SHOT_LOOK.laser.muzzle;
    expect(segments).toBeGreaterThanOrEqual(24);
    expect(colors.length - 1).toBeGreaterThanOrEqual(6);
    expect(buildGlowDisc(segments, colors).indices.length / 3).toBe(24 * 11);
  });

  it('a flash grows then shrinks to nothing over its duration', () => {
    expect(flashScale(0, 1)).toBe(0);
    expect(flashScale(0.25, 1)).toBeCloseTo(1);
    expect(flashScale(0.5, 1)).toBeGreaterThan(0);
    expect(flashScale(1, 1)).toBe(0);
  });

  it('every player weapon renderer is a function of the scene', () => {
    expect(PLAYER_SHOT_RENDERERS[LASER.id]).toBe(createLaserRenderer);
  });
});
