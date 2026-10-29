import type { OutlinePoint } from '../../../../render/geometry/outline';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal, SIDES } from '../../enemies/enemy-shapes';
import { dish, grille, mast, rod, studs } from '../final-boss-greebles';
import { AURORA, CITADEL_DECK, FROST, rect, VIOLET } from './boreal-citadel-city';
import { ICE_FLESH, sinew } from './w2-organic';

// P08-R10, 2-5: the Boreal Citadel's details: armour skirts on its deck's sides, snow drifts,
// dishes and masts, lamps along its avenue, buttresses round its keep, heating pipes, the
// engine block's grilles and fins. Model space: logical pixels, nose +Z, Y up.
const H = ENEMY_LOOK.hull;

type Vec3 = [number, number, number];

/** The armour skirts along the right side of the deck (+X), between the bow and the outrigger. */
const SKIRTS: readonly OutlinePoint[][] = [
  [
    [52, 52],
    [57.5, 42],
    [55, 40],
    [49.5, 50],
  ],
  [
    [58.5, 34],
    [60.5, 28],
    [58, 27.5],
    [56, 33],
  ],
];
/** Snow drifts on the deck (right half): where, and how wide. */
const DRIFTS = [
  [46, -16, 4.5],
  [14, -76, 4],
  [44, 34, 3.5],
  [27, 72, 3.5],
] as const;
/** A drift's mound (lathe profile, in units of its width). */
const DRIFT = [
  [1, 0],
  [0.75, 0.25],
  [0.35, 0.42],
  [0, 0.45],
] as const;
/** The keep's buttresses (around it at these turns from the nose, mirrored), and their size. */
const BUTTRESSES = [Math.PI / 4, (3 * Math.PI) / 4] as const;
const BUTTRESS: Vec3 = [4, 13, 7];

/** Armour skirts lit by violet slits, and snow drifts piled on the deck. */
function drawDeckEdges({ hull, flesh, neon }: EnemyParts): void {
  const top = CITADEL_DECK.top;
  for (const s of SIDES) {
    for (const skirt of SKIRTS) {
      const outline = skirt.map(([x, z]): OutlinePoint => [s * x, z]);
      hull.bevelSlab(outline, [top - 0.4, top, top + 2], [0, 0.8], H.panel, {}, FROST.frosted);
    }
    neon.box([0.5, 0.8, 9], VIOLET, { at: [s * 55, top + 1.2, 46], yaw: s * 0.5 });
    for (const [x, z, w] of DRIFTS) {
      const mound = DRIFT.map(([r, y]) => [r * w, y * w] as const);
      flesh.lathe(mound, 6, ICE_FLESH.crystal, { at: [s * x, top, z], yaw: x });
    }
  }
}

/** Buttresses round the keep, snowed on top, and heating pipes from the domes to the keep. */
function drawKeepDetail({ hull, flesh, neon }: EnemyParts): void {
  const top = CITADEL_DECK.top;
  for (const s of SIDES) {
    for (const a of BUTTRESSES) {
      const turn = s * a;
      const at: Vec3 = [Math.sin(turn) * 21, top, Math.cos(turn) * 21];
      flesh.box(BUTTRESS, ICE_FLESH.sinew, { at, yaw: turn }, ICE_FLESH.rime);
      neon.box([0.4, 6, 0.4], s > 0 ? AURORA : VIOLET, {
        at: [Math.sin(turn) * 24.2, top + 3, Math.cos(turn) * 24.2],
        yaw: turn,
      });
    }
    // Arteries from the blisters to the heart, a metal pipe grafted along them.
    sinew(flesh, [s * 30, top + 1, 32], [s * 17, top + 1, 15], 1.2, ICE_FLESH.crimson);
    rod(hull, [s * 27, top + 1, 35], [s * 14, top + 1, 18], 0.6, H.dark);
  }
}

/** Masts and dishes over the city, lamps along the avenue. */
function drawRoofs(p: EnemyParts): void {
  const { top, avenue } = CITADEL_DECK;
  for (const s of SIDES) {
    dish(p, [s * 50, top, 26], 4, [0.6, s * 0.8]);
    mast(p, [s * 36, top + 19, 2], 7, s > 0 ? AURORA : VIOLET);
    mast(p, [s * 24, top + 25, -24], 8, VIOLET);
    studs(
      p.neon,
      [
        [s * 13, -60],
        [s * 13, -26],
      ],
      [6, 1.2],
      avenue + 0.05,
      AURORA,
    );
  }
}

/** The engine block's grilles and heat-sink fins. */
function drawEngineBlock({ hull, flesh }: EnemyParts): void {
  for (const s of SIDES) {
    grille(hull, [s * 19, -86], [10, 8], [4, 5.05]);
    for (const dx of [4, 7, 10]) {
      flesh.box([1, 3, 9], ICE_FLESH.bone, { at: [s * (dx + 22), 5, -86] }, ICE_FLESH.rime);
    }
  }
  decal(hull, rect(8, 8, [0, -86]), 5.05, H.dark);
}

/** The Boreal Citadel's details (P08-R10), on its core body. */
export function drawDetails(p: EnemyParts): void {
  drawDeckEdges(p);
  drawKeepDetail(p);
  drawRoofs(p);
  drawEngineBlock(p);
}
