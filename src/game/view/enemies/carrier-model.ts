import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import { decal, flipX, HULL_SECTION, SIDES } from './enemy-shapes';

// P05-R12: the Carrier. Logical pixels, nose +Z, Y up (towards the camera).
const H = ENEMY_LOOK.hull;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;

/** P05-R12: the Carrier's fat hull (loft stations), its flight deck and its island. */
const CARRIER_HULL = [
  [-28, 12, -3, 4.5],
  [-18, 17, -4, 7.5],
  [0, 19, -4.5, 8.5],
  [16, 15.5, -4, 7],
  [25, 8, -3, 4.5],
  [30, 0, -1.5, 1.5],
] as const;
const CARRIER_DECK = [
  [-6, 20],
  [6, 24],
  [10, 12],
  [10, -24],
  [-10, -24],
  [-10, 10],
] as const;
const CARRIER_ISLAND = [
  [3.5, 4],
  [8.5, 2],
  [8.5, -10],
  [3.5, -12],
] as const;
/** The right sponson along the hull's side, its top sloping out to the hangar vents. */
const CARRIER_SPONSON = [
  [12, 15],
  [20, 11],
  [23.5, 4],
  [23.5, -10],
  [20, -16],
  [12, -20],
] as const;
/** A vent on the right sponson, glowing as the next launch comes, and its louvres. */
const CARRIER_VENT = [
  [16.5, 6],
  [20.5, 4],
  [20.5, -10],
  [16.5, -12],
] as const;
const VENT_LOUVRES = [-9, -5.5, -2, 1.5] as const;
/** A runway light, and the island's bridge window along its front. */
const DASH = [
  [-0.6, -1.6],
  [0.6, -1.6],
  [0.6, 1.6],
  [-0.6, 1.6],
] as const;
const ISLAND_WINDOW = [
  [4.8, 2.4],
  [7.2, 1.4],
  [7.2, 0.6],
  [4.8, 1.6],
] as const;

/** P05-R12: a fat flying carrier with a flight deck, an island and glowing hangar vents. */
export function buildCarrier(scene: Scene): EnemyModel {
  return buildEnemyModel('carrier', scene, N.carrier, ({ hull, neon, charge, reactor }) => {
    hull.loft(HULL_SECTION, CARRIER_HULL, H.base);
    hull.bevelSlab(CARRIER_DECK, [4.5, 7.6, 8.9], [0, 0.6], H.dark, {}, H.panel);
    // Runway lights along the deck's centre line.
    for (let z = -20; z <= 16; z += 7.2) {
      decal(
        neon,
        DASH.map(([x, dz]): OutlinePoint => [x, z + dz]),
        8.95,
        N.carrier,
      );
    }
    hull.bevelSlab(CARRIER_ISLAND, [8, 8.5, 12.5], [0, 1], H.panel, {}, H.base);
    decal(neon, ISLAND_WINDOW, 12.55, N.carrier);
    for (const s of SIDES) {
      const side = (o: readonly OutlinePoint[]): readonly OutlinePoint[] => (s > 0 ? o : flipX(o));
      hull.bevelSlab(side(CARRIER_SPONSON), [-3, 0, 4.5], [1, 2.5], H.base, {}, H.panel);
      decal(charge, side(CARRIER_VENT), 4.55, WHITE);
      for (const z of VENT_LOUVRES) {
        hull.box([4.6, 0.6, 0.8], H.dark, { at: [s * 18.5, 4.6, z] });
      }
      reactor([s * 7, 0.5, -28.5], 2.4);
    }
  });
}
