import type { Scene } from '@babylonjs/core/scene';
import { Constants } from '@babylonjs/core/Engines/constants';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { EnemyBullet, EnemyMissile } from '../../../core/systems/enemy-shots';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { EnemyShotRenderer } from '../../../render/game-view';
import { NodePool } from '../../../render/node-pool';
import { setOutline } from '../../../render/outline';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { READABILITY } from '../../config/readability';
import '@babylonjs/core/Meshes/thinInstanceMesh';
import { buildGlowDisc, buildSwirl } from '../shot-geometry';
import { additiveTemplate, blendedTemplate } from '../shots/shot-meshes';
import { enemyMaterials, meshOf } from './enemy-mesh';
import { EnemyLasers } from './enemy-lasers';

const LOOK = ENEMY_LOOK;
/** Draw order of the bullets: after every other see-through mesh of the playfield (P14-R05). */
const ON_TOP = 1_000_000;
type Style = keyof typeof LOOK.bullets.styles;
const STYLES = Object.keys(LOOK.bullets.styles) as Style[];

/** Opacity of each vertex of a bullet's disc: its centre, then each ring's. */
function discAlphas(segments: number, fade: readonly number[]): number[] {
  return fade.flatMap((alpha, ring) => Array<number>(ring === 0 ? 1 : segments).fill(alpha));
}

/** Where, how big and how turned one bullet layer is drawn. */
interface Spot {
  readonly x: number;
  readonly y: number;
  readonly radius: number;
  readonly angle: number;
}

/**
 * One layer of the bullets of one colour, drawn as thin instances of a template (as the blasts,
 * D-034): one draw call however many bullets are flying.
 */
class BulletLayer {
  #matrices = new Float32Array(0);

  constructor(
    readonly mesh: Mesh,
    private readonly z: number,
    order: number,
  ) {
    // P14-R05: over everything else on the playfield (blasts, player shots, models), in layer
    // order; never culled: instances spread anywhere.
    mesh.alphaIndex = ON_TOP + order;
    mesh.alwaysSelectAsActiveMesh = true;
    if (mesh.material) mesh.material.depthFunction = Constants.ALWAYS;
  }

  show(spots: readonly Spot[]): void {
    const n = spots.length;
    this.mesh.setEnabled(n > 0);
    if (n === 0) return;
    const grow = n > this.#matrices.length / 16;
    if (grow) this.#matrices = new Float32Array(Math.max(16, 2 ** Math.ceil(Math.log2(n))) * 16);
    spots.forEach(({ x, y, radius, angle }, i) => {
      const c = Math.cos(angle) * radius;
      const s = Math.sin(angle) * radius;
      this.#matrices.set([c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, x, y, this.z, 1], i * 16);
    });
    if (grow) this.mesh.thinInstanceSetBuffer('matrix', this.#matrices, 16, false);
    // Before the update, as the blasts (Babylon uploads only `thinInstanceCount` matrices).
    this.mesh.thinInstanceCount = n;
    if (!grow) this.mesh.thinInstanceBufferUpdated('matrix');
  }

  dispose(): void {
    this.mesh.material?.dispose();
    this.mesh.dispose();
  }
}

/** How big and how turned one layer of a bullet is drawn. */
type Placement = (b: EnemyBullet, r: number) => { radius: number; angle: number };

/** The dark rim and white spark of a bullet in the contrast style (P10-R07). */
function contrastLayers(name: string, scene: Scene): { rim: Mesh; spark: Mesh } {
  const { segments } = LOOK.bullets;
  const { rim, spark } = LOOK.contrast;
  const dark = rim.fade.map(() => rim.color);
  return {
    rim: blendedTemplate(
      `${name}-rim`,
      buildGlowDisc(segments, dark),
      discAlphas(segments, rim.fade),
      scene,
    ),
    spark: additiveTemplate(`${name}-spark`, buildGlowDisc(segments, spark.colors), scene),
  };
}

/**
 * A ball of plasma (GD-43), back to front: a faint flickering aura, a solid body, two curled
 * swirls of brighter plasma spinning opposite ways, and a pulsing white-hot core. In the
 * contrast style (P10-R07), a dark rim behind the body and a white spark over the core.
 */
function bulletLayers(style: Style, scene: Scene, contrast: boolean): [BulletLayer, Placement][] {
  const { segments, swirlSegments, fade, swirls } = LOOK.bullets;
  const colors = LOOK.bullets.styles[style];
  const name = `enemy-bullet-${style}`;
  const body = buildGlowDisc(segments, colors.body);
  const layers: [Mesh, Placement][] = [
    [
      additiveTemplate(`${name}-halo`, buildGlowDisc(segments, colors.halo), scene),
      (b, r) => ({ radius: r * haloScale(b.age), angle: 0 }),
    ],
    [
      blendedTemplate(name, body, discAlphas(segments, fade), scene),
      (_b, r) => ({ radius: r, angle: 0 }),
    ],
    ...swirls.map((swirl, i): [Mesh, Placement] => [
      additiveTemplate(
        `${name}-swirl-${String(i)}`,
        buildSwirl(swirlSegments, colors.swirls[i] ?? colors.halo, swirl),
        scene,
      ),
      (b, r) => ({ radius: r * swirl.size, angle: b.heading * 3 + swirl.spinRadPerSec * b.age }),
    ]),
    [
      additiveTemplate(`${name}-core`, buildGlowDisc(segments, colors.core), scene),
      (b, r) => ({ radius: r * coreScale(b.age), angle: 0 }),
    ],
  ];
  if (contrast) {
    const extra = contrastLayers(name, scene);
    const { rim, spark } = LOOK.contrast;
    layers.splice(1, 0, [extra.rim, (_b, r) => ({ radius: r * rim.size, angle: 0 })]);
    layers.push([extra.spark, (_b, r) => ({ radius: r * spark.size, angle: 0 })]);
  }
  // Back to front, towards the camera (-Z).
  return layers.map(([mesh, place], order) => [
    new BulletLayer(mesh, -1 - 0.05 * order, order),
    place,
  ]);
}

/** One set of plasma layers per bullet colour (GD-43). */
function bulletPools(scene: Scene, contrast: boolean): Map<string, [BulletLayer, Placement][]> {
  return new Map(STYLES.map((style) => [style, bulletLayers(style, scene, contrast)]));
}

/** Size of a bullet's core, relative to the bullet, `age` seconds after it was fired. */
function coreScale(age: number): number {
  const { size, pulse } = LOOK.bullets.core;
  return size * (1 + pulse.amount * Math.sin(2 * Math.PI * pulse.hz * age));
}

/** Size of a bullet's aura, relative to the bullet, flickering as it flies. */
function haloScale(age: number): number {
  const { size, flicker, flickerHz } = LOOK.bullets.halo;
  return size * (1 + flicker * Math.sin(2 * Math.PI * flickerHz * age));
}

/** A bullet's drawn radius: never under half `minEnemyBulletSize` (P14-R05); its hitbox is kept. */
function drawnRadius(b: EnemyBullet): number {
  return Math.max(b.radius * LOOK.bullets.scale, READABILITY.minEnemyBulletSize / 2);
}

function syncBullets(
  pools: Map<string, [BulletLayer, Placement][]>,
  bullets: readonly EnemyBullet[],
): void {
  for (const [style, layers] of pools) {
    const own = bullets.filter((b) => (pools.has(b.style) ? b.style : STYLES[0]) === style);
    for (const [layer, place] of layers) {
      layer.show(own.map((b) => ({ x: b.x, y: b.y, ...place(b, drawnRadius(b)) })));
    }
  }
}

/**
 * A small dark missile pointing +Y with an orange tip and a flame behind it, and (P14-R05) a
 * rim glow in the enemy shots' colour, so it shows over blasts and bright ground.
 */
function buildMissile(scene: Scene, flame: Mesh, i: number): TransformNode {
  const look = LOOK.missile;
  const root = new TransformNode(`enemy-missile-${String(i)}`, scene);
  const body = new SolidBuilder().cylinder(look.radius, look.length, 6, LOOK.hull.panel, {
    at: [0, -look.length / 2, 0],
  });
  const tip = new SolidBuilder().cylinder(
    look.radius,
    3,
    6,
    look.tip,
    { at: [0, look.length / 2, 0] },
    0,
  );
  const mats = enemyMaterials(scene);
  const hull = meshOf(`${root.name}-body`, body.geometry, mats.hull, scene);
  hull.parent = root;
  setOutline(hull, look.tip);
  meshOf(`${root.name}-tip`, tip.geometry, mats.neon, scene).parent = root;
  const glow = flame.clone(`${root.name}-flame`);
  glow.parent = root;
  glow.setEnabled(true);
  const [w, h] = look.flameSize;
  glow.position.set(0, -look.length / 2 - h * 0.6, 0.5);
  glow.scaling.set(w, h, 1);
  return root;
}

function syncMissiles(pool: NodePool<TransformNode>, missiles: readonly EnemyMissile[]): void {
  pool.show(missiles.length).forEach((node, i) => {
    const m = missiles[i];
    if (!m) return;
    node.position.set(m.x, m.y, -0.5);
    node.rotation.z = -m.heading;
  });
}

/**
 * GD-43: the enemies' shots in playfield space: glowing bullets, small orange-tipped missiles
 * with a flame, and lasers ({@link EnemyLasers}). The contrast look (P10-R07: a dark rim and a
 * white spark, wider laser warning lines) is used in every level since phase 14 (P14-R05),
 * whatever style a level names.
 */
export function createEnemyShotRenderer(scene: Scene): EnemyShotRenderer {
  const contrast = true;
  const bullets = bulletPools(scene, contrast);
  const flame = additiveTemplate(
    'enemy-missile-flame',
    buildGlowDisc(8, LOOK.missile.flame),
    scene,
  );
  const missiles = new NodePool((i) => buildMissile(scene, flame, i));
  const lasers = new EnemyLasers(scene, contrast);
  let time = 0;
  return {
    sync: (frame) => {
      time += frame.dtSeconds;
      syncBullets(bullets, frame.bullets);
      syncMissiles(missiles, frame.missiles);
      lasers.sync(frame.lasers, time);
    },
    dispose: () => {
      for (const layers of bullets.values()) for (const [layer] of layers) layer.dispose();
      lasers.dispose();
      missiles.dispose();
      flame.dispose();
    },
  };
}
