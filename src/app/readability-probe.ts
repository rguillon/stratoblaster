import type { Scene } from '@babylonjs/core/scene';
import { Matrix, Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import {
  boxContrast,
  brightestBut,
  type PixelBox,
  type Pixels,
  type ReadabilityReport,
} from '../core/math/pixel-contrast';
import type { LevelRun } from '../core/systems/level-run';
import { GAME_PLAY_CONFIG } from '../config/game-play';

const CFG = GAME_PLAY_CONFIG.readabilityProbe;

/** A playfield circle: centre and radius, in logical pixels. */
interface Spot {
  readonly x: number;
  readonly y: number;
  readonly radius: number;
}

/** The first of `items` wholly in view (a margin round it), as a spot of its `radius`. */
function firstInView<T extends { x: number; y: number }>(
  items: readonly T[],
  inView: (x: number, y: number) => boolean,
  radius: (item: T) => number,
): Spot | null {
  const inside = (i: T) => {
    const m = radius(i) + CFG.margin;
    return inView(i.x - m, i.y - m) && inView(i.x + m, i.y + m);
  };
  const item = items.find(inside);
  return item ? { x: item.x, y: item.y, radius: radius(item) } : null;
}

/**
 * Where each kind of object is on the playfield, if any is in view: player shots away from
 * the ship (not over it, nor leaving its guns).
 */
function spotsOf(run: LevelRun, inView: (x: number, y: number) => boolean) {
  const { ship, enemies, shots } = run;
  const ahead = shots.projectiles.filter((p) => p.alive && p.y > ship.y + CFG.shotAhead);
  return {
    player: { x: ship.x, y: ship.y, radius: CFG.shipRadius },
    enemy: firstInView(enemies.enemies, inView, (e) => e.radius),
    enemyBullet: firstInView(
      enemies.shots.bullets.filter((b) => b.alive),
      inView,
      (b) => b.radius,
    ),
    playerShot: firstInView(ahead, inView, () => CFG.shotRadius),
  };
}

/** Reads the canvas back, row 0 at the bottom (as WebGL reads it). */
async function readFrame(scene: Scene): Promise<Pixels> {
  const engine = scene.getEngine();
  const width = engine.getRenderWidth();
  const height = engine.getRenderHeight();
  scene.render();
  const data = await engine.readPixels(0, 0, width, height);
  return { width, height, data: data as Uint8Array };
}

/** The box of pixels (WebGL rows, bottom up) that `spot` covers on screen. */
function pixelBox(scene: Scene, root: TransformNode, spot: Spot): PixelBox {
  const engine = scene.getEngine();
  const camera = scene.activeCamera;
  if (!camera) throw new Error('The level has no camera');
  const width = engine.getRenderWidth();
  const height = engine.getRenderHeight();
  const world = root.getWorldMatrix();
  const viewport = camera.viewport.toGlobal(width, height);
  const project = (x: number, y: number) =>
    Vector3.Project(
      Vector3.TransformCoordinates(new Vector3(x, y, 0), world),
      Matrix.IdentityReadOnly,
      scene.getTransformMatrix(),
      viewport,
    );
  const centre = project(spot.x, spot.y);
  const edge = project(spot.x + spot.radius, spot.y);
  const radius = Math.max(1, Math.hypot(edge.x - centre.x, edge.y - centre.y));
  return { x: centre.x, y: height - 1 - centre.y, radius };
}

/**
 * Measures how readable the level's current frame is (P14-R08): draws it once as it is and
 * once without the playfield (the background alone), and compares the two around each object.
 */
export async function probeReadability(
  scene: Scene,
  playfield: TransformNode,
  run: LevelRun,
  inView: (x: number, y: number) => boolean,
  brightShare: number,
): Promise<ReadabilityReport> {
  const spots = spotsOf(run, inView);
  const frame = await readFrame(scene);
  playfield.setEnabled(false);
  const background = await readFrame(scene).finally(() => {
    playfield.setEnabled(true);
  });
  scene.render();
  const contrast = (spot: Spot | null) =>
    spot ? boxContrast(frame, background, pixelBox(scene, playfield, spot)) : null;
  return {
    player: contrast(spots.player),
    enemy: contrast(spots.enemy),
    enemyBullet: contrast(spots.enemyBullet),
    playerShot: contrast(spots.playerShot),
    backgroundLuminance: brightestBut(background, brightShare),
  };
}
