import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SolidBuilder } from '../../../render/geometry/solids';
import type { EnemyModel } from '../../../render/game-view';
import { ENEMY_CONFIG } from '../../config/enemies';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import { CANOPY_SECTION, flipX, HULL_SECTION, sideStripe, SIDES } from './enemy-shapes';

// P05-R12: the Carrier. Logical pixels, nose +Z, Y up (towards the camera).
const H = ENEMY_LOOK.hull;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;

type Vec3 = [number, number, number];

/** P05-R12: the Carrier's fat hull (loft stations) and the spine along its back. */
const CARRIER_HULL = [
  [-28, 12, -3, 4.5],
  [-18, 17, -4, 7.5],
  [0, 19, -4.5, 8.5],
  [16, 15.5, -4, 7],
  [25, 8, -3, 4.5],
  [30, 0, -1.5, 1.5],
] as const;
const CARRIER_SPINE = [
  [-25, 3, 4, 7],
  [-12, 6, 7, 11],
  [8, 5, 7.5, 10.5],
  [20, 0, 5.5, 6],
] as const;
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

/** P05-R12: a fat flying carrier with a spine along its back and two launch ports a side. */
export function buildCarrier(scene: Scene): EnemyModel {
  return buildEnemyModel('carrier', scene, N.carrier, ({ hull, neon, charge, reactor }) => {
    hull.loft(HULL_SECTION, CARRIER_HULL, H.base);
    hull.loft(CANOPY_SECTION, CARRIER_SPINE, H.panel, {}, { open: true });
    // Amber stripes along both flanks of the spine.
    for (const side of [0, 3]) {
      const stripe = sideStripe(CANOPY_SECTION, side, [0.35, 0.75]);
      neon.loft(stripe, CARRIER_SPINE.slice(1, 3), N.carrier, {}, { open: true });
    }
    for (const s of SIDES) {
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
      reactor([s * 7, 0.5, -28.5], 2.4);
    }
  });
}
