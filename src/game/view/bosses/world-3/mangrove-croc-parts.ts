import type { OutlinePoint } from '../../../../render/geometry/outline';
import { mirror } from '../../../config/bosses/boss-kit';
import {
  CROC_JAW,
  CROC_JAW_CANNON,
  CROC_JAW_SWING,
  CROC_PONTOON_GUNS,
} from '../../../config/bosses/world-3/mangrove-croc';
import { BOSS_LOOK } from '../../../config/boss-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { flipX, POD_SECTION, sideStripe } from '../../enemies/enemy-shapes';
import { bossPoint, type LimbDrawing } from '../boss-limbs';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { barrelTo, moss, vine } from './mangrove-croc-jungle';
import { ribs } from '../../../../render/geometry/organic';
import { F, gland, JUNGLE_FLESH, sac, veinTo } from './jungle-flesh';

// P09-R09, 3-1: the Mangrove Croc's jaws (on their hinges, D-061), its jaw cannon and its side
// pontoons. Logical pixels, nose +Z, Y up; the left jaw and pontoon (the screen's left, -X on
// the playfield) are drawn at +X.
type Vec3 = [number, number, number];

/** The Mangrove Croc's green neon (P09-R09). */
export const CROC_GREEN = BOSS_LOOK.neon['mangrove-croc'] ?? [0.25, 1, 0.3];

/**
 * The left jaw seen from above, from its hinge (x across, z along), as it is shut: wide at the
 * hinge, its inner edge along the croc's centre line, tapering to the tip.
 */
const JAW: readonly OutlinePoint[] = [
  [-6.5, 0],
  [4, 0],
  [5, 6],
  [3.5, 16],
  [0, 24.5],
  [-2, 26.5],
  [-4.5, 25],
  [-6.5, 14],
];
/** The jaw's heights: its bottom, its waist and its top. */
const JAW_Y = [0, 2, 5] as const;
/** How far along the jaw (z from the hinge) its teeth stand on the inner edge. */
const TEETH = [5, 10, 15, 20, 24] as const;

/**
 * A jaw (side `s`, +1 the left one at +X), drawn half open as at rest: an armoured wedge with a
 * row of teeth along its inner edge, green neon along its outer edge and moss on its back.
 */
function drawJaw(s: number) {
  return ({ hull, flesh, neon }: EnemyParts): void => {
    const [hx, hy] = CROC_JAW.hinge;
    const at: Vec3 = bossPoint(s * -Math.abs(hx), hy);
    const place = { at, yaw: (s * CROC_JAW_SWING.amplitudeDeg * Math.PI) / 180 };
    const outline = s > 0 ? JAW : flipX(JAW);
    // P16-R05: a fleshy jaw, bone fangs along it, a metal plate grafted on its back.
    flesh.bevelSlab(outline, JAW_Y, [0.8, 1.2], F.sinew, place, JUNGLE_FLESH);
    hull.box(
      [5, 0.8, 8],
      H.panel,
      { at: turnAbout(at, [s * -1.5, JAW_Y[2], 4], place.yaw), yaw: place.yaw },
      H.base,
    );
    for (const z of TEETH) {
      const edge = -6.6 + Math.max(0, z - 14) * 0.25;
      flesh.box([2.2, 2.4, 1.6], F.bone, {
        at: turnAbout(at, [s * edge, 0.4, z], place.yaw),
        yaw: place.yaw,
      });
    }
    const outer = (s > 0 ? JAW : flipX(JAW)).slice(1, 4);
    for (let i = 0; i < outer.length - 1; i++) {
      const [a, b] = [outer[i], outer[i + 1]];
      if (!a || !b) continue;
      const [dx, dz] = [b[0] - a[0], b[1] - a[1]];
      neon.box([0.9, 0.6, Math.hypot(dx, dz)], CROC_GREEN, {
        at: turnAbout(at, [(a[0] + b[0]) / 2, JAW_Y[2] - 0.8, (a[1] + b[1]) / 2], place.yaw),
        yaw: place.yaw + Math.atan2(dx, dz),
      });
    }
    moss(hull, scaledAbout(outline, 0.45, [s * -1.5, 6]), JAW_Y[2]);
  };
}

/** `p` (from `at`) turned by `yaw` around +Y, then moved to `at`. */
function turnAbout(at: Vec3, [x, y, z]: Vec3, yaw: number): Vec3 {
  const [c, k] = [Math.cos(yaw), Math.sin(yaw)];
  return [at[0] + x * c + z * k, at[1] + y, at[2] - x * k + z * c];
}

/** `outline` shrunk by `k` around `[cx, cz]`. */
function scaledAbout(
  outline: readonly OutlinePoint[],
  k: number,
  [cx, cz]: readonly [number, number],
): OutlinePoint[] {
  return outline.map(([x, z]): OutlinePoint => [cx + (x - cx) * k, cz + (z - cz) * k]);
}

/** The jaws (D-061): each drawn on its hinge, they open and close with it; they go with the core. */
export const CROC_JAWS: Readonly<Record<string, LimbDrawing>> = {
  'jaw-left': { draw: drawJaw(1) },
  'jaw-right': { draw: drawJaw(-1) },
};

/**
 * The jaw cannon (P09-R09) in the croc's throat between the jaws: a ribbed housing with a neon
 * collar, its barrel reaching for the jaws' tips, a charge light glowing in its maw.
 */
export function jawCannon(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge } = p;
  const [tip] = CROC_JAW_CANNON;
  if (!tip) return;
  const axis = bossPoint(...tip)[1];
  const back = offset(at, 0, axis, -8);
  // P16-R05: a throat gland swelling behind the grafted cannon, veins feeding it.
  sac(p, offset(back, 0, 0, -2), 5, F.crimson);
  gland(p, offset(back, 0, 2.6, -2), 1.8, CROC_GREEN);
  hull.cylinder(4.4, 9, 8, H.panel, { at: back, pitch: QUARTER }, 3.4);
  hull.cylinder(5, 1.6, 8, H.dark, { at: offset(back, 0, 0, 1), pitch: QUARTER });
  neon.ring(3.6, 0.9, 8, CROC_GREEN, { at: offset(back, 0, 0, 7.4), pitch: QUARTER });
  charge.box([4, 0.5, 3], WHITE, { at: offset(at, 0, axis + 3.3, -4) });
  barrelTo(p, tip, [1.8, 8]);
}

/** A pontoon's float (loft stations from its centre: z, half width, bottom, top). */
const FLOAT = [
  [-22, 3, 1, 4],
  [-16, 7.5, -2, 7],
  [2, 8.5, -2, 7.5],
  [11, 6.5, -1, 6.5],
  [14, 3, 1, 4.5],
] as const;

/**
 * A side pontoon (P09-R09): a long armoured float with its twin fan guns at its bow, a green
 * light along its outer side, moss on its back and a vine trailing from it.
 */
export function pontoon(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, neon } = p;
  const s = Math.sign(at[0]);
  const stations = FLOAT.map(([z, w, b, t]) => [z + at[2], w, b, t] as const);
  // P16-R05: a swollen float-bladder, ridged like a croc's flank, plated at its bow.
  flesh.loft(POD_SECTION, stations, JUNGLE_FLESH, { at: [at[0], 0, 0] });
  ribs(
    flesh,
    [at[2] - 12, at[2] - 6, at[2]],
    { halfWidth: 8, y: 2, height: 5.6, thickness: 0.6 },
    F.bone,
    { at: [at[0], 0, 0] },
  );
  veinTo(p, [offset(at, 0, 7.6, -16), offset(at, 0, 7.6, 8)], [0, 0.8, 0], CROC_GREEN);
  const side = s > 0 ? 1 : 3;
  neon.loft(
    sideStripe(POD_SECTION, side, [0.15, 0.45], 1.04),
    stations.slice(1, 4),
    CROC_GREEN,
    {
      at: [at[0], 0, 0],
    },
    { open: true },
  );
  hull.box([12, 1.6, 6], H.dark, { at: offset(at, 0, 7.2, -4) }, SHADE.edge);
  moss(
    hull,
    [
      [at[0] - 4, at[2] - 14],
      [at[0] + 4, at[2] - 12],
      [at[0] + 3, at[2] - 4],
      [at[0] - 3, at[2] - 6],
    ],
    7.2,
  );
  vine(hull, offset(at, s * 7, 5, -10), offset(at, s * 6, 4, 4), 4);
  const guns = s < 0 ? CROC_PONTOON_GUNS : mirror(CROC_PONTOON_GUNS);
  for (const tip of guns) barrelTo(p, tip, [1.3, 7]);
  hull.box([8, 3, 4], H.dark, { at: offset(at, 0, 2.6, 8.5) }, H.panel);
}
