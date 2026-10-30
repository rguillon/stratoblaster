import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { segmentedBody } from '../../../render/geometry/organic';
import { GULL_MOTHERSHIP } from '../../config/bosses/final-bosses';
import { BOSS_LOOK } from '../../config/boss-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { SIDES } from '../enemies/enemy-shapes';
import { eyes, reactorSac } from '../enemies/organic-parts';
import { buildBossModel } from './boss-model';
import { mirrored, shift, turret } from './final-boss-shapes';
import { DECK_TOP, drawFlak, drawHangar } from './final-boss-gull';
import {
  barbs,
  F,
  gland,
  graft,
  hide,
  M,
  mantle,
  polygon,
  ribCage,
  scaleOutline,
  spine,
  tentacle,
  veinLine,
} from './world-1-organic-kit';

// P07-R05, P16-R06: the Gull Mothership, the final boss of 1-2. Logical pixels, nose +Z, Y up
// (towards the camera). A brood-mother of the sea: a wide fleshy mantle, a shelled body along
// its middle ending in a huge glowing eye (its laser), a brood pouch at each flank and two flak
// growths on its front.
const N = BOSS_LOOK.neon['gull-mothership'] ?? [0.2, 1, 0.35];
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/** The mantle seen from above (right half, front to back); the pouches sit on its flat sides. */
const DECK = mirrored([
  [0, 50],
  [24, 46],
  [40, 32],
  [47, 20],
  [47, -30],
  [34, -48],
  [14, -56],
  [0, -56],
]);
/** The laser eye's lens (a lathe profile along its axis), at the body's nose. */
const LENS = [
  [0, 0],
  [5.5, 1.2],
  [4.6, 3.4],
  [0, 4.4],
] as const;

/**
 * The body (P16-R06): a teal mantle lined with a green vein, a second fold on it, a shelled
 * body along its middle with ribs over its back and glands down its spine.
 */
function drawHull(p: EnemyParts): void {
  mantle(p, DECK, [-5, DECK_TOP], F.teal, N);
  mantle(p, scaleOutline(DECK, 0.72, 0, -4), [DECK_TOP - 1, DECK_TOP + 1.6], F.purple);
  hide(p, {
    tail: -61,
    nose: 58,
    width: 16,
    bottom: DECK_TOP - 1,
    top: 22,
    segments: 6,
    shell: [F.crimson, F.membrane],
    belly: F.sinew,
  });
  ribCage(p, [-36, -24, -12, 0, 12], { halfWidth: 20, y: DECK_TOP, height: 15, thickness: 1.2 });
  spine(p, [0, 22.5, -50], [0, 22.5, 40], { color: N, width: 1.6, bow: 3 });
  for (const z of [-30, -6, 18]) gland(p, [0, 22, z], 1.8, N);
  p.neon.box([1, 0.8, 16], N, { at: [0, 24.4, -9] });
  graft(p, polygon(6, 7, [1, 1.6]), [20.5, 22], [0, 0, 30]);
  barbs(p, [0, 21, -44], { count: 3, spacing: 0.1, size: 4, dir: [0, 1, -0.4] });
  for (const s of SIDES) {
    for (const z of [-34, -14, 6, 26]) {
      veinLine(p, [s * 15, DECK_TOP + 6, z], [s * 40, DECK_TOP + 1, z - 8], [0, 3, 0], 1.1, N);
    }
    tentacle(p, [s * 10, 0, -52], [s * 18, -1, -60], [s * 4, 0, 0], [3, 0.4], F.teal);
    graft(p, polygon(4, 5, [1.6, 0.9]), [DECK_TOP + 1.4, DECK_TOP + 2.4], [s * 30, 0, 22]);
  }
}

/** The laser eye at the nose: a socket of flesh, a grafted ring, the lens glowing as it charges. */
function drawEmitter(p: EnemyParts): void {
  const at: Vec3 = [0, DECK_TOP + 3, 58];
  p.flesh.cylinder(8, 6, 8, F.purple, { at, pitch: QUARTER }, 6.5);
  p.hull.ring(7.3, 1.4, 8, M.dark, { at: shift(at, [0, 0, 5.4]), pitch: QUARTER });
  for (const z of [1.5, 5]) {
    p.neon.ring(7.6 - z * 0.15, 1, 8, N, { at: shift(at, [0, 0, z]), pitch: QUARTER });
  }
  p.charge.lathe(LENS, 8, WHITE, { at: shift(at, [0, 0, 7.5]), pitch: QUARTER });
  eyes(p, shift(at, [0, 9, -6]), { count: 4, size: 1.1, spacing: 3 }, N);
  // The core's laser and bullets leave from the lens's front.
  const lens = shift(at, [0, 0, 11.9]);
  p.muzzle(lens, 'laser');
  p.muzzle(lens);
}

/** The swim bladders on the back of the mantle, their reactors in sacs. */
function drawEngines(p: EnemyParts): void {
  for (const s of SIDES) {
    segmentedBody(
      p.flesh,
      { tail: -51, nose: -24, segments: 2, width: 5.5, bottom: 0, top: 9.5 },
      F.crimson,
      { at: [s * 30, DECK_TOP - 1, 0] },
    );
    reactorSac(p, [s * 30, DECK_TOP + 3, -50], 3.4, N);
    reactorSac(p, [s * 6, DECK_TOP + 2.5, -60], 2.8, N);
  }
}

/** A flak growth's twin guns, on its crown. */
function flakTurret(p: EnemyParts, at: Vec3): void {
  turret(p, shift(at, [0, DECK_TOP + 2.5, 0]), 8.5, [2, N]);
}

/**
 * P07-R05, P16-R06: the Gull Mothership, a brood-mother of the sea 5 L across; green veins and
 * glands, a brood pouch on each flank (they launch the Gnats), two flak growths on its front,
 * and a huge laser eye at the nose of its body (the core).
 */
export function buildGullMothership(scene: Scene): EnemyModel {
  return buildBossModel(GULL_MOTHERSHIP, scene, N, {
    core: (p) => {
      drawHull(p);
      drawEmitter(p);
      drawEngines(p);
    },
    parts: {
      'hangar-left': drawHangar,
      'hangar-right': drawHangar,
      'flak-left': drawFlak,
      'flak-right': drawFlak,
    },
    turrets: { 'flak-left': flakTurret, 'flak-right': flakTurret },
  });
}
