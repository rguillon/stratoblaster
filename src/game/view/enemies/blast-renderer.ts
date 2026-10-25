import type { Scene } from '@babylonjs/core/scene';
import { Constants } from '@babylonjs/core/Engines/constants';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import '@babylonjs/core/Meshes/thinInstanceMesh';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { createRng } from '../../../core/math/rng';
import type { ColoredGeometry } from '../../../render/geometry/gradient-shapes';
import type { BlastRenderer } from '../../../render/game-view';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildGlowDisc } from '../shot-geometry';
import { BLAST_LAYERS, BlastParticles, type BlastLayer, type BlastSpot } from './blast-particles';

const LOOK = ENEMY_LOOK.blasts;

type Rgb = readonly [number, number, number];

/** A soft white disc, fading to its rim. */
const soft = (segments: number): ColoredGeometry =>
  buildGlowDisc(segments, [
    [1, 1, 1],
    [0.85, 0.85, 0.85],
    [0.4, 0.4, 0.4],
    [0, 0, 0],
  ]);

/** A thin white ring at the rim of a disc, black (nothing, added on) inside and out. */
const ring = (segments: number): ColoredGeometry => {
  const inside: Rgb[] = Array.from({ length: 7 }, (): Rgb => [0, 0, 0]);
  return buildGlowDisc(segments, [...inside, [0.5, 0.5, 0.5], [1, 1, 1], [0, 0, 0]]);
};

/** A soft disc for smoke: white, its opacity fading to the rim. */
function puff(segments: number): ColoredGeometry {
  const geo = soft(segments);
  const colors: number[] = [];
  for (let i = 0; i < geo.colors.length; i += 4) colors.push(1, 1, 1, geo.colors[i] ?? 0);
  return { ...geo, colors };
}

/** Each layer: its disc, whether it is added on (fire) or laid over (smoke), and its depth. */
const LAYERS: Readonly<
  Record<BlastLayer, { geo: () => ColoredGeometry; add: boolean; z: number }>
> = {
  smoke: { geo: () => puff(LOOK.smoke.segments), add: false, z: -2.8 },
  rings: { geo: () => ring(LOOK.ring.segments), add: true, z: -3 },
  fireballs: { geo: () => puff(LOOK.fireball.segments), add: false, z: -3.2 },
  debris: { geo: () => soft(LOOK.debris.segments), add: true, z: -3.4 },
  embers: { geo: () => soft(LOOK.debris.segments), add: true, z: -3.5 },
  flashes: { geo: () => soft(LOOK.flash.segments), add: true, z: -3.6 },
};

/** One mesh drawing a whole layer as thin instances, tinted one by one. */
class LayerMesh {
  readonly mesh: Mesh;
  #matrices = new Float32Array(0);
  #colors = new Float32Array(0);

  constructor(
    name: string,
    geo: ColoredGeometry,
    add: boolean,
    private readonly z: number,
    order: number,
    scene: Scene,
  ) {
    this.mesh = new Mesh(name, scene);
    const data = new VertexData();
    data.positions = geo.positions;
    data.indices = geo.indices;
    data.colors = geo.colors;
    data.applyToMesh(this.mesh);
    const material = new StandardMaterial(name, scene);
    material.emissiveColor = Color3.White();
    material.diffuseColor = Color3.Black();
    material.specularColor = Color3.Black();
    material.disableLighting = true;
    material.backFaceCulling = false;
    material.alphaMode = add ? Constants.ALPHA_ADD : Constants.ALPHA_COMBINE;
    // Below 1, so the material goes through the blended pass.
    material.alpha = 0.999;
    material.disableDepthWrite = true;
    this.mesh.material = material;
    this.mesh.hasVertexAlpha = !add;
    this.mesh.isPickable = false;
    // Drawn in layer order (smoke under fire), and never culled: instances spread anywhere.
    this.mesh.alphaIndex = order;
    this.mesh.alwaysSelectAsActiveMesh = true;
    this.mesh.setEnabled(false);
  }

  show(spots: readonly BlastSpot[]): void {
    const n = spots.length;
    this.mesh.setEnabled(n > 0);
    if (n === 0) return;
    const grow = n > this.#colors.length / 4;
    if (grow) {
      const capacity = Math.max(16, 2 ** Math.ceil(Math.log2(n)));
      this.#matrices = new Float32Array(capacity * 16);
      this.#colors = new Float32Array(capacity * 4);
    }
    spots.forEach((s, i) => {
      const m = i * 16;
      this.#matrices.set(
        [s.radius, 0, 0, 0, 0, s.radius, 0, 0, 0, 0, 1, 0, s.x, s.y, this.z, 1],
        m,
      );
      this.#colors.set([s.r, s.g, s.b, s.a], i * 4);
    });
    if (grow) {
      this.mesh.thinInstanceSetBuffer('matrix', this.#matrices, 16, false);
      this.mesh.thinInstanceSetBuffer('color', this.#colors, 4, false);
    }
    // Before the update: Babylon uploads only the first `thinInstanceCount` matrices, and new
    // instances would show for a frame where older ones were, in their new colours (phase 6
    // review: stray glows when an enemy blew up).
    this.mesh.thinInstanceCount = n;
    if (!grow) {
      this.mesh.thinInstanceBufferUpdated('matrix');
      this.mesh.thinInstanceBufferUpdated('color');
    }
  }

  dispose(): void {
    this.mesh.material?.dispose();
    this.mesh.dispose();
  }
}

/**
 * GD-62: explosions where enemies and missiles were destroyed, in playfield space. Each layer
 * (smoke, shock rings, fireballs, debris, embers, flashes) is one mesh of thin instances, so a
 * big blast costs no more draw calls than a small one.
 */
export function createBlastRenderer(scene: Scene): BlastRenderer {
  const layers = BLAST_LAYERS.map((layer, order) => {
    const { geo, add, z } = LAYERS[layer];
    return [layer, new LayerMesh(`blast-${layer}`, geo(), add, z, order, scene)] as const;
  });
  const particles = new BlastParticles(createRng(LOOK.seed));
  return {
    sync: (blasts, dt) => {
      for (const blast of blasts) particles.emit(blast);
      const spots = particles.step(dt);
      // In front of the ships (towards the camera, -Z).
      for (const [layer, mesh] of layers) mesh.show(spots[layer]);
    },
    dispose: () => {
      for (const [, mesh] of layers) mesh.dispose();
    },
  };
}
