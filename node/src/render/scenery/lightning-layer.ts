import type { Scene } from '@babylonjs/core/scene';
import { Constants } from '@babylonjs/core/Engines/constants';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { createRng, type Random } from '../../core/math/rng';
import type { Atmosphere } from '../../core/scenery/atmosphere';
import { LightningSchedule, type Strike } from '../../core/scenery/lightning';
import { BELOW_CLOUDS_GROUP } from './cloud-layers';
import type { GroundWindow } from './playfield-framing';

/** How a bolt is drawn in the clouds (P09-R05): a pale violet-white zigzag with a few forks. */
export const BOLT_LOOK = {
  color: [0.86, 0.86, 1] as const,
  /** Length of the main bolt, and of its forks, as shares of the view's width. */
  length: 0.55,
  fork: 0.22,
  forks: 2,
  /** Pieces of the main bolt, their widest sideways jag (world units), and the line's width. */
  pieces: 12,
  jag: 14,
  width: 1.4,
  /** Draw order among the see-through meshes above the ground: before the weather. */
  alphaIndex: 3,
} as const;

type Point = readonly [number, number];

/** A jagged line of `pieces` from `start`, `length` long, heading `angle` (radians from +X). */
function zigzag(random: Random, start: Point, [length, angle, pieces]: readonly number[]): Point[] {
  const n = pieces ?? 1;
  const step = (length ?? 0) / n;
  const [dx, dz] = [Math.cos(angle ?? 0), Math.sin(angle ?? 0)];
  const points: Point[] = [start];
  for (let i = 1; i <= n; i++) {
    const jag = (random() - 0.5) * 2 * BOLT_LOOK.jag * (i === n ? 0.3 : 1);
    points.push([start[0] + dx * step * i - dz * jag, start[1] + dz * step * i + dx * jag]);
  }
  return points;
}

/** Flat ribbons along `lines`, `width` wide, in the XZ plane. */
function ribbons(lines: readonly Point[][], width: number): VertexData {
  const positions: number[] = [];
  const indices: number[] = [];
  for (const line of lines) {
    for (let i = 1; i < line.length; i++) {
      const [a, b] = [line[i - 1], line[i]];
      if (!a || !b) continue;
      const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
      const [nx, nz] = [(-(b[1] - a[1]) / len) * width, ((b[0] - a[0]) / len) * width];
      const v = positions.length / 3;
      positions.push(a[0] - nx, 0, a[1] - nz, a[0] + nx, 0, a[1] + nz);
      positions.push(b[0] + nx, 0, b[1] + nz, b[0] - nx, 0, b[1] - nz);
      indices.push(v, v + 1, v + 2, v, v + 2, v + 3);
    }
  }
  const data = new VertexData();
  data.positions = positions;
  data.indices = indices;
  return data;
}

/** The lines of the bolt of seed `seed`, across a view `span` wide, from its centre. */
export function boltLines(seed: number, span: number): Point[][] {
  const random = createRng(seed);
  const angle = random() * Math.PI * 2;
  const main = zigzag(random, [0, 0], [span * BOLT_LOOK.length, angle, BOLT_LOOK.pieces]);
  const forks = Array.from({ length: BOLT_LOOK.forks }, () => {
    const from = main[1 + Math.floor(random() * (main.length - 2))] ?? [0, 0];
    const turn = angle + (random() < 0.5 ? -1 : 1) * (0.4 + random() * 0.6);
    return zigzag(random, from, [span * BOLT_LOOK.fork, turn, BOLT_LOOK.pieces / 2]);
  });
  return [main, ...forks];
}

/**
 * The lightning of a storm (P09-R05): the flashes drawn from the level's seed and, for some
 * strikes, a bolt drawn in the clouds while its flashes last, added over what is behind it. The
 * flash itself lights the scene through the atmosphere (`flashed`), not here. It is only a
 * look: nothing in the simulation reads it.
 */
export class LightningLayer {
  readonly schedule: LightningSchedule;
  readonly #material: StandardMaterial;
  #bolt: Mesh | undefined;
  #strike: Strike | undefined;
  #flash = 0;

  constructor(
    private readonly scene: Scene,
    seed: number,
    private readonly place: readonly [window: GroundWindow, altitude: number],
  ) {
    this.schedule = new LightningSchedule(seed);
    const material = new StandardMaterial('lightning-bolt', scene);
    material.disableLighting = true;
    material.emissiveColor = new Color3(...BOLT_LOOK.color);
    material.alphaMode = Constants.ALPHA_ADD;
    material.backFaceCulling = false;
    material.disableDepthWrite = true;
    this.#material = material;
  }

  /** The flash (0..1) on the last frame, before the storm's lightning strength. */
  get flash(): number {
    return this.#flash;
  }

  /** Whether a bolt was drawn on the last frame. */
  get boltShown(): boolean {
    return this.#bolt?.isEnabled() ?? false;
  }

  /** The flash at `time` for `atmosphere`'s lightning, the bolt drawn around the view at `z`. */
  update(atmosphere: Atmosphere, time: number, z: number): number {
    const strength = atmosphere.lightning;
    this.#flash = strength > 0 ? this.schedule.flashAt(time) : 0;
    const strike = this.#flash > 0 ? this.schedule.strikeAt(time) : undefined;
    if (strike?.bolt && strike !== this.#strike) this.#build(strike.bolt, z);
    this.#strike = strike;
    const shown = strike?.bolt !== undefined;
    this.#bolt?.setEnabled(shown);
    if (shown) this.#material.alpha = Math.min(1, this.#flash * strength);
    return this.#flash;
  }

  #build(bolt: NonNullable<Strike['bolt']>, z: number): void {
    const [window, altitude] = this.place;
    const span = window.halfWidth * 2;
    this.#bolt?.dispose();
    const mesh = new Mesh('lightning-bolt', this.scene);
    ribbons(boltLines(bolt.seed, span), BOLT_LOOK.width).applyToMesh(mesh);
    mesh.material = this.#material;
    mesh.isPickable = false;
    mesh.renderingGroupId = BELOW_CLOUDS_GROUP + 1;
    mesh.alphaIndex = BOLT_LOOK.alphaIndex;
    mesh.position.set(
      (bolt.x - 0.5) * span,
      altitude,
      z + window.zNear + bolt.z * (window.zFar - window.zNear),
    );
    this.#bolt = mesh;
  }
}
