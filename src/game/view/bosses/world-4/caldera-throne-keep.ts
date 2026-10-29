import type { OutlinePoint } from '../../../../render/geometry/outline';
import { CALDERA_CROWN } from '../../../config/bosses/world-4/caldera-throne';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { around, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-limbs';
import { studs } from '../final-boss-greebles';
import { armour, conduit } from '../final-boss-mechanism';
import { H, SHADE, WHITE } from '../mini-boss-shapes';
import { SKIN } from './living-forge';
import { edgeLights } from '../overlord-city';
import { CRIMSON, DECK_TOP, GOLD, HEAT } from './caldera-throne-parts';

// P10-R11, 4-5: the Caldera Throne's keep over its core: three armoured tiers lit crimson, molten
// slits in their walls, battlements, and the throne tower crowned in gold whose crown fires the
// core's rings; the smokestacks aft, glowing at their mouths; watchtowers and lamps. Model space: logical pixels, nose
// +Z (down the screen), Y up towards the camera.
type Vec3 = [number, number, number];
// P16-R06: the keep's lowest tier is the flesh of its back swelling up, the upper ones armour
// grafted on; its stacks are flesh spiracles, its watchtowers bone horns.

/** An octagon of `radius` (to its corners) around `[x, z]`, its faces square to the axes. */
function octagon(radius: number, [x, z]: OutlinePoint = [0, 0]): OutlinePoint[] {
  return around(8).map((a): OutlinePoint => {
    const turn = a + Math.PI / 8;
    return [x + Math.sin(turn) * radius, z + Math.cos(turn) * radius];
  });
}

/** The keep's tiers: radius, base and top heights. */
const TIERS = [
  [38, DECK_TOP - 1, 18],
  [29, 18, 28],
  [20, 28, 36],
] as const;
/** The throne tower on top of the keep: where (model z), its radius and top. */
const TOWER = { z: bossPoint(...CALDERA_CROWN)[2], radius: 8, top: 43 } as const;
/** The crown's charge light (lathe profile), up to the ring emitter. */
const CROWN_LIGHT = [
  [3, 0],
  [2.4, 3],
  [0, CALDERA_CROWN[2] - TOWER.top],
] as const;
/** The smokestacks aft: where (model x, z), their radius and top. */
const STACKS = [
  [24, -74, 4.6, 27],
  [40, -82, 3.8, 23],
] as const;

/** The three tiers, their edges lit crimson, molten slits in the lowest, battlements on it. */
function drawTiers({ hull, neon, flesh }: EnemyParts): void {
  TIERS.forEach(([radius, y0, y1], i) => {
    const outline = octagon(radius);
    if (i === 0) armour(flesh, outline, [y0, y1], SKIN.base, 1.6, SKIN.dark);
    else armour(hull, outline, [y0, y1], H.base, 1.6, H.panel);
    const all = outline.map((_, k) => k);
    edgeLights(neon, outline, all, [y1 - 3.2, y1 - 2.2], i === 1 ? GOLD : CRIMSON);
  });
  const [r0, , y1] = TIERS[0];
  const face = r0 * Math.cos(Math.PI / 8);
  for (const a of around(8)) {
    const [s, c] = [Math.sin(a), Math.cos(a)];
    neon.box([2.2, 6, 0.4], HEAT.molten, {
      at: [s * (face + 0.3), DECK_TOP + 1.5, c * (face + 0.3)],
      yaw: a,
    });
    for (const d of [-0.28, 0.28]) {
      const along = face * Math.tan(Math.PI / 8) * d * 2;
      const at: Vec3 = [s * (face - 1.6) + c * along, y1, c * (face - 1.6) - s * along];
      hull.box([3.6, 2.6, 2.2], H.dark, { at, yaw: a }, SHADE.edge);
    }
  }
  neon.box([10, 2.4, 0.5], GOLD, { at: [0, 22, TIERS[1][0] * Math.cos(Math.PI / 8) + 0.3] });
}

/** The throne tower: an armoured drum, a gold crown of spikes, its charge light on top. */
function drawTower({ hull, neon, charge, muzzle }: EnemyParts): void {
  const { z, radius, top } = TOWER;
  const base = TIERS[2][2];
  hull.cylinder(radius + 2, 2, 8, H.panel, { at: [0, base, z], yaw: Math.PI / 8 }, radius + 1);
  hull.cylinder(radius, top - base, 8, H.base, { at: [0, base, z], yaw: Math.PI / 8 }, radius - 1);
  neon.ring(radius - 0.2, 0.9, 8, CRIMSON, { at: [0, top - 4, z], yaw: Math.PI / 8 });
  for (const a of around(6)) {
    const at: Vec3 = [Math.sin(a) * (radius - 2.4), top, z + Math.cos(a) * (radius - 2.4)];
    neon.lathe(
      [
        [1.3, 0],
        [0, 6],
      ],
      4,
      GOLD,
      { at, pitch: 0.25, yaw: a },
    );
  }
  hull.cylinder(radius - 1.5, 0.8, 8, H.dark, { at: [0, top, z] });
  charge.lathe(CROWN_LIGHT, 6, WHITE, { at: [0, top, z] });
  muzzle(bossPoint(...CALDERA_CROWN), 'ring');
}

/** The smokestacks aft: soot-black, banded crimson, their mouths glowing with the furnaces. */
function drawStacks({ hull, neon, flesh }: EnemyParts): void {
  for (const s of SIDES) {
    for (const [x, z, radius, top] of STACKS) {
      const at: Vec3 = [s * x, DECK_TOP, z];
      flesh.cylinder(radius, top - DECK_TOP, 6, SKIN.panel, { at }, radius * 0.85);
      hull.ring(radius * 0.9, 2, 6, HEAT.soot, { at: [s * x, top - 2, z] });
      neon.ring(radius * 0.95, 0.8, 6, CRIMSON, { at: [s * x, DECK_TOP + 6, z] });
      neon.cylinder(radius * 0.7, 0.4, 6, HEAT.molten, { at: [s * x, top - 0.3, z] });
    }
    conduit(flesh, [s * 18, DECK_TOP + 3, -36], [s * 24, DECK_TOP + 3, -68], [1.6, 3]);
  }
}

/** The watchtowers flanking the prow: where (model x, z), their radius and top. */
const WATCHTOWER = { x: 26, z: 76, radius: 5, top: 22 } as const;
/** The gold lamps along the deck's flanks (right half, `[x, z]` from and to). */
const LAMP_ROWS = [
  [
    [50, 46],
    [60, 20],
  ],
  [
    [60, -36],
    [52, -66],
  ],
] as const satisfies readonly (readonly [OutlinePoint, OutlinePoint])[];

/** The watchtowers by the prow, gold beacons on their roofs, and the deck's rows of lamps. */
function drawWatch({ hull, neon, flesh }: EnemyParts): void {
  const { x, z, radius, top } = WATCHTOWER;
  for (const s of SIDES) {
    const at: Vec3 = [s * x, DECK_TOP, z];
    flesh.cylinder(radius, top - DECK_TOP, 6, SKIN.bone, { at }, radius * 0.8);
    hull.cylinder(radius * 1.25, 2, 6, H.panel, { at: [s * x, top, z] }, radius * 0.9);
    neon.ring(radius * 0.95, 0.7, 6, CRIMSON, { at: [s * x, top - 4, z] });
    neon.box([1.6, 1.6, 1.6], GOLD, { at: [s * x, top + 2.2, z] });
    for (const [a, b] of LAMP_ROWS) {
      studs(
        neon,
        [
          [s * a[0], a[1]],
          [s * b[0], b[1]],
        ],
        [5, 1.6],
        DECK_TOP + 0.06,
        GOLD,
      );
    }
  }
}

/** The keep over the core, its throne tower, the smokestacks and watchtowers (P10-R11). */
export function drawKeep(p: EnemyParts): void {
  drawTiers(p);
  drawTower(p);
  drawStacks(p);
  drawWatch(p);
}
