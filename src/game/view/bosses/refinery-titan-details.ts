import type { LoftStation, SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal, POD_SECTION, sideStripe, SIDES } from '../enemies/enemy-shapes';
import { TITAN_WEAR } from './refinery-titan-armour';
import { cutStations } from './refinery-titan-hull';
import { rect, TITAN_NEON } from './refinery-titan-parts';

// P07-R05 (phase 7 review: more detail): the Refinery Titan's surface, armour plates and their
// seams, a patched plate, hazard stripes, grilles, rivets and beacons. Model space: logical
// pixels, nose +Z (down the screen), Y up towards the camera; +X is the screen's left.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;

type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/**
 * Stripes on the sponson's front chamfer (from `(x, 0, 40)` up to `(x, 8, 37)`), from `x0` to
 * `x1`: slanted bands of hazard paint, some of them worn off where `worn` says so.
 */
function hazardStripes(
  hull: SolidBuilder,
  [x0, x1]: readonly [number, number],
  worn: (i: number) => boolean,
): void {
  const width = 2.4;
  // The chamfer's normal (0, 3, 8), normalised: the stripes stand just off it.
  const [ny, nz] = [0.35 * 0.1, 0.94 * 0.1];
  for (let i = 0, x = x0; x + 2 * width <= x1; i++, x += 2 * width) {
    if (worn(i)) continue;
    const at = (dx: number, y: number, z: number): Vec3 => [x + dx, y + ny, z + nz];
    const corners = [at(0, 0, 40), at(width, 0, 40), at(width + 2, 8, 37), at(2, 8, 37)];
    hull.face(corners, TITAN_WEAR.hazard);
  }
}

/** The sponson: hazard stripes on its front corners, a grille and rivets on its top. */
function drawSponsonDeck({ hull, neon }: EnemyParts): void {
  // Left (+X): fresh paint; right: worn, half the bands gone.
  hazardStripes(hull, [20, 40], () => false);
  hazardStripes(hull, [-40, -20], (i) => i % 3 === 1 || i === 3);
  // An exhaust grille under the twin cannon, its slats across.
  decal(hull, rect(22, 8, [0, 31]), 8.03, H.dark);
  for (let k = -2; k <= 2; k++) decal(hull, rect(0.9, 7, [k * 4, 31]), 8.06, H.panel);
  decal(neon, rect(22, 0.7, [0, 35.6]), 8.06, TITAN_NEON);
  // Rivet strips along its back edge, beside the hull.
  for (const s of SIDES) {
    for (let k = 0; k < 5; k++) decal(hull, rect(1, 1, [s * (37 + k * 2.4), 8.5]), 8.05, H.dark);
  }
}

/** The engine nacelles at the tail (loft stations), drawn in the model file. */
export const NACELLE: readonly LoftStation[] = [
  [-62, 7.5, -3, 11],
  [-52, 8.5, -3.5, 13],
  [-36, 6, -2, 12.5],
  [-28, 0, 9, 9],
];

/** Exhaust grilles on the nacelles' backs: a dark vent crossed by slats. */
function drawNacelleVents({ hull }: EnemyParts): void {
  const top = sideStripe(POD_SECTION, 2, [0.1, 0.9], 1);
  for (const s of SIDES) {
    const vent = { at: [s * 11, 0.08, 0] as Vec3 };
    hull.loft(top, cutStations(NACELLE, [-58, -42]), H.dark, vent, { open: true });
    for (const z of [-56, -52.5, -49, -45.5]) {
      const slat = { at: [s * 11, 0.2, 0] as Vec3 };
      hull.loft(top, cutStations(NACELLE, [z, z + 1]), H.panel, slat, { open: true });
    }
  }
}

/** A beacon: a dark stub with a neon cap, standing at (x, y, z). */
function beacon({ hull, neon }: EnemyParts, [x, y, z]: Vec3, color: Rgb = TITAN_NEON): void {
  hull.cylinder(1.2, 1.5, 6, H.dark, { at: [x, y, z] });
  neon.cylinder(0.9, 1.2, 6, color, { at: [x, y + 1.5, z] });
}

/** Beacons on the cradle arms' ends: orange, but white at the back of the right one. */
function drawBeamEnds(parts: EnemyParts): void {
  for (const s of SIDES) {
    beacon(parts, [s * 87, 13, 0.5]);
    if (s < 0) beacon(parts, [s * 87, 13, -36.5], WHITE);
  }
}

/** P07-R05 (phase 7 review): the surface details of the Refinery Titan's core. */
export function drawTitanDetails(parts: EnemyParts): void {
  drawSponsonDeck(parts);
  drawNacelleVents(parts);
  drawBeamEnds(parts);
}
