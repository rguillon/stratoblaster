import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { LoftStation } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import { ASH_WRAITH, WRAITH_VENT } from '../../../config/bosses/world-4/ash-wraith';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { canopyPaint, FIGHTER_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { edgeStrips, mirrored, strip } from '../final-boss-shapes';
import { vent } from '../mini-boss-greebles';
import { H, offset, socket, WHITE } from '../mini-boss-shapes';
import { ASH, ashDrift, ASH_THIN, moltenSeam, SCORCH, sootStreaks } from './ash-plains-soot';
import { eyeMount, eyeTurret, shroudPod, WRAITH_CYAN } from './ash-wraith-parts';
import { backRibs, glands, magmaVein, reactorSacs, SKIN } from './living-forge';

// P10-R11, 4-2: the Ash Wraith. Logical pixels, nose +Z, Y up (towards the camera). A ragged
// stealth flying wing: a thin faceted wing, its trailing edge torn into tatters, a low fuselage
// with a dark canopy, the two shroud pods on the wings, the eye cannon on the nose.
// P16-R05: a living ash ray, its wing a scorched membrane veined with cyan, its body flesh under
// ribs, a great eye on its brow, metal only on its grafts (vents, plates, guns, reactors).

/**
 * The wing seen from above (right half, nose to tail): a sharp delta, its trailing edge torn
 * into ragged points, as if it had flown through fire.
 */
const WING_HALF: readonly OutlinePoint[] = [
  [0, 44],
  [7, 34],
  [20, 14],
  [34, 1],
  [47, -9],
  [51, -15],
  [45, -17],
  [41, -25],
  [35, -19],
  [29, -28],
  [23, -21],
  [17, -31],
  [11, -24],
  [6, -36],
  [0, -30],
];
const WING = mirrored(WING_HALF);

/** The fuselage along the centre line, tail to nose (loft stations: z, half width, bottom, top). */
const FUSELAGE: readonly LoftStation[] = [
  [-33, 4, 0, 3.5],
  [-22, 9, -1, 7.5],
  [-6, 12, -1.5, 10],
  [10, 10, -1, 9],
  [24, 5, 0, 4.6],
];
/** The dark glass of its canopy, on the back of the fuselage's front bands. */
const CANOPY_GLASS: readonly [number, number, number] = [0.03, 0.05, 0.06];

/** P16-R05, P16-R06: its living flesh: veins, glands and ribs. */
function wingVeins(p: EnemyParts, s: number): void {
  magmaVein(
    p,
    [
      [s * 8, 3.2, 12],
      [s * 24, 3.1, 2],
      [s * 40, 3, -8],
    ],
    0.9,
    WRAITH_CYAN,
  );
  magmaVein(
    p,
    [
      [s * 9, 3.2, 0],
      [s * 22, 3.1, -14],
    ],
    0.8,
    WRAITH_CYAN,
  );
}

/** The wing: grey, bevelled plates, pale cyan neon along its leading edges, ash and soot on it. */
function drawWing(p: EnemyParts): void {
  const { hull, neon } = p;
  p.flesh.bevelSlab(WING, [-1, 0.6, 3], [0.8, 1], SKIN.dark, {}, SKIN.base);
  for (const s of SIDES) {
    wingVeins(p, s);
    edgeStrips(
      neon,
      [
        [s * 8.5, 30],
        [s * 20.5, 11.5],
        [s * 34, -1.5],
        [s * 44, -9],
      ],
      0.8,
      [2.7, 3.2],
      WRAITH_CYAN,
    );
    edgeStrips(
      neon,
      [
        [s * 47, -12],
        [s * 43, -15],
      ],
      0.7,
      [2.4, 2.9],
      WRAITH_CYAN,
    );
    sootStreaks(
      hull,
      [
        [
          [s * 8, -20],
          [s * 14, -30],
        ],
        [
          [s * 20, -12],
          [s * 27, -24],
        ],
        [
          [s * 44, -4],
          [s * 46, -14],
        ],
      ],
      3,
    );
    moltenSeam(p, [s * 14, 4], [s * 22, -10], 3);
    ashDrift(hull, [s * 22, 3, 10], 3.6, s * 1.3);
    ashDrift(hull, [s * 46, 2.6, -10], 2.4, s * 2.2);
  }
}

/** The fuselage: a low faceted spine, its dark canopy, vents and scorched plates by the engines. */
function drawFuselage(p: EnemyParts): void {
  const { hull, neon } = p;
  p.flesh.loft(
    FIGHTER_SECTION,
    FUSELAGE,
    SKIN.base,
    {},
    { paint: canopyPaint([2, 3], CANOPY_GLASS) },
  );
  backRibs(p, [-12, -4, 4], { halfWidth: 8, y: 3, height: 6.6, thickness: 0.7 });
  glands(
    p,
    [
      [0, 8.6, -9],
      [0, 8.8, 0],
    ],
    1.2,
    WRAITH_CYAN,
  );
  strip(neon, [0, 21], [0, 14], 0.6, [9.4, 9.8], WRAITH_CYAN);
  for (const s of SIDES) {
    vent(hull, [s * 7, 7.2, -16], [3, 6], 3, s * 0.15);
    hull.box([5, 1.4, 8], SCORCH, { at: [s * 6, 2.6, -30] }, H.dark);

    strip(neon, [s * 10.6, 2], [s * 8.4, -18], 0.6, [5.6, 6.2], WRAITH_CYAN);
  }
  reactorSacs(
    p,
    [
      [5.5, 2.2, -34],
      [-5.5, 2.2, -34],
    ],
    2.6,
    WRAITH_CYAN,
  );
}

/** Flakes of ash trailing off its torn wing (x, z, size, turn): it sheds ash as it flies. */
const ASH_TRAIL = [
  [41, -30, 2.2, 0.4],
  [29, -34, 1.8, 1.1],
  [17, -37, 2, 2],
  [6, -42, 1.6, 0.7],
  [36, -38, 1.4, 1.6],
] as const;
/** A flake of ash seen from above: a small ragged diamond. */
const FLAKE: readonly OutlinePoint[] = [
  [0, 1],
  [0.7, 0.1],
  [0.2, -1],
  [-0.8, -0.2],
];

/** The ash it sheds: grey flakes drifting behind the trailing edge, either side. */
function drawAshTrail({ hull }: EnemyParts): void {
  for (const s of SIDES) {
    for (const [x, z, size, turn] of ASH_TRAIL) {
      const flake = FLAKE.map(([fx, fz]): OutlinePoint => [fx * size, fz * size]);
      hull.slab(flake, [0, 0.3], ASH_THIN, { at: [s * x, 1 + size * 0.3, z], yaw: s * turn }, ASH);
    }
  }
}

/** The ash vent on its back (the core's spirals): a squat stack, a cyan ring, a lit grate. */
function drawVent(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  const [top] = WRAITH_VENT.map((m) => bossPoint(...m));
  if (!top) return;
  socket(hull, offset(top, 0, -5.6, 0), 4.6, 1.6);
  hull.cylinder(4, 4.4, 8, H.panel, { at: offset(top, 0, -5, 0), yaw: Math.PI / 8 }, 3.2);
  neon.ring(3.3, 0.5, 8, WRAITH_CYAN, { at: offset(top, 0, -1.2, 0), yaw: Math.PI / 8 });
  hull.cylinder(2.6, 0.6, 8, ASH, { at: offset(top, 0, -1.2, 0) });
  charge.cylinder(2, 0.6, 8, WHITE, { at: offset(top, 0, -0.6, 0) });
  muzzle(top, 'ring');
}

/**
 * P10-R11: the Ash Wraith, a ragged grey stealth gunship trailing ash, pale cyan neon, soot and
 * molten seams on its torn wing.
 */
export function buildAshWraith(scene: Scene): EnemyModel {
  return buildBossModel(ASH_WRAITH, scene, WRAITH_CYAN, {
    core: (p) => {
      drawWing(p);
      drawFuselage(p);
      drawVent(p);
      drawAshTrail(p);
    },
    parts: { 'pod-left': shroudPod, 'pod-right': shroudPod, eye: eyeMount },
    turrets: { eye: eyeTurret },
  });
}
