import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SolidBuilder } from '../../../render/geometry/solids';
import type { EnemyModel } from '../../../render/game-view';
import { ENEMY_CONFIG } from '../../config/enemies';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import { curve, organ, segmentedBody, tendril, vein } from '../../../render/geometry/organic';
import { decal, flipX, LOBE_SECTION, shiftX, SIDES } from './enemy-shapes';

// P05-R12, P16-R03: the Carrier, Cyber-Organic (P16-R01). Logical pixels, nose +Z, Y up (towards the camera).
const H = ENEMY_LOOK.hull;
const F = ENEMY_LOOK.flesh;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/**
 * The right sponson along the hull's side. Its outer wall slopes from `SPONSON_EDGE` at the waist
 * up to its top, inset `SPONSON_SLOPE`, so the launch ports in it face out and up, to the camera.
 */
const CARRIER_SPONSON = [
  [12, 16],
  [21, 12],
  [24, 6],
  [24, -14],
  [21, -19],
  [12, -22],
] as const;
const SPONSON_EDGE = 24;
const SPONSON_SLOPE = [5.5, 5] as const;
/** A port's frame and its glowing mouth: across the slope and along the side. */
const PORT_FRAME = [5.2, 7] as const;
const PORT_MOUTH = [3.4, 5.2] as const;

/**
 * A quad `[across, along]` big on the right sponson's sloped wall, centred on the port at
 * `z`, `lift` off the wall; `side` -1 mirrors it to the left.
 */
function portQuad(
  side: number,
  z: number,
  [across, along]: readonly [number, number],
  lift: number,
): Vec3[] {
  const [inset, rise] = SPONSON_SLOPE;
  const len = Math.hypot(inset, rise);
  // The wall's outward normal (n) and the direction down it (d), on the right side.
  const [nx, ny] = [rise / len, inset / len];
  const [dx, dy] = [ny, -nx];
  const [cx, cy] = [SPONSON_EDGE - inset / 2 + nx * lift, rise / 2 + ny * lift];
  const corner = (u: number, v: number): Vec3 => [side * (cx + dx * u), cy + dy * u, z + v];
  const [u, v] = [across / 2, along / 2];
  const quad = [corner(-u, -v), corner(-u, v), corner(u, v), corner(u, -v)];
  // Mirrored, the corners turn the other way round: keep the face towards the outside.
  return side > 0 ? quad : quad.reverse();
}

/** A launch port: a dark frame on the sponson's wall and a mouth glowing as a launch comes. */
function port(hull: SolidBuilder, charge: SolidBuilder, side: number, z: number): void {
  hull.face(portQuad(side, z, PORT_FRAME, 0.08), H.dark);
  charge.face(portQuad(side, z, PORT_MOUTH, 0.16), WHITE);
}

/** P16-R03: the brood sac's ribs, arched over its back, and the gnat larvae glowing inside. */
const CARRIER_RIBS = [-10, 10];
/** A larva glowing through the sac (8 triangles), and the neon band along each side of its spine. */
const LARVA = [
  [0, -0.6],
  [1.4, 0],
  [0, 0.8],
] as const;
const CARRIER_BAND = [
  [-0.4, -13],
  [0.4, -13],
  [0.4, 13],
  [-0.4, 13],
] as const;
const CARRIER_LARVAE: readonly Vec3[] = [
  [-5, 8.6, -9],
  [5, 8.6, -4],
  [-4, 9, 5],
  [4, 8.6, 10],
];

/**
 * P05-R12, P16-R03: a brood sac that releases Gnats: a fat swollen sac of three segments under
 * bone ribs, larvae glowing through its back, a metal sponson grafted on each flank with two
 * launch ports, amber neon bands along its spine, its reactors set in flesh sacs.
 */
export function buildCarrier(scene: Scene): EnemyModel {
  return buildEnemyModel('carrier', scene, N.carrier, (p) => {
    const { flesh, hull, neon, charge } = p;
    const sac = { tail: -28, nose: 30, segments: 3, width: 19, bottom: -4.5, top: 9 };
    segmentedBody(flesh, sac, F.purple, {}, LOBE_SECTION);
    for (const z of CARRIER_RIBS) {
      const arch = curve([-16, 1, z], [16, 1, z], [0, 10, 0], 4);
      tendril(flesh, arch, [0.9, 0.9], 3, F.bone);
    }
    for (const at of CARRIER_LARVAE) p.vein.lathe(LARVA, 4, N.carrier, { at });
    for (const s of SIDES) {
      decal(neon, shiftX(CARRIER_BAND, s * 3.5), 9.1, N.carrier);
      const side = (o: readonly OutlinePoint[]): readonly OutlinePoint[] => (s > 0 ? o : flipX(o));
      const [inset] = SPONSON_SLOPE;
      hull.bevelSlab(
        side(CARRIER_SPONSON),
        [-3, 0, SPONSON_SLOPE[1]],
        [1, inset],
        H.base,
        {},
        H.panel,
      );
      // Model Z is down the screen's Y: a port `py` up the screen sits at Z = -py.
      for (const [, py] of ENEMY_CONFIG.carrier.ports) port(hull, charge, s, -py);
      // Its reactor, set in a flesh sac with a vein running into the body (P16-R01).
      const nozzle: Vec3 = [s * 7, 0.5, -28.5];
      organ(flesh, 3.2, 4, F.crimson, { at: [s * 7, 0.5, -28], pitch: QUARTER }, 0.9);
      p.reactor(nozzle, 2.4);
      vein(p.vein, curve([s * 7, 3, -25], [s * 5, 6, -17], [0, 1, 0], 2), 1, N.carrier);
    }
  });
}
