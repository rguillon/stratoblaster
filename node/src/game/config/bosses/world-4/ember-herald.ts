import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P10-R11, 4-5's mini boss: the Ember Herald. Offsets in px from the boss's centre, X right and
 * Y up (its nose points down, at -Y). Stage patterns as for the earlier mini bosses (P07-R04,
 * D-055): its three ember lances fire spirals from their tips while they stand, the core fires
 * aimed bursts that change at every stage, and twin spirals of its own, used by no earlier
 * stage, once it stands alone.
 */

const MAGENTA = bullet('magenta', 215);
const PURPLE = bullet('purple', 190);
const BLUE = bullet('blue', 205);

/**
 * The turning ring's ember lances (P10-R11): each points out of the ring, its centre `orbit` px
 * from the core, its tip (where its spiral leaves from) `tip` px out, `height` above the
 * playfield. The model draws them from these numbers.
 */
export const EMBER_LANCE = { orbit: 40, tip: 61, height: 12 } as const;

/** The lances' turns around the core at a spin of 0, from the nose (radians, clockwise on screen). */
const LANCE_TURNS = [0, (2 * Math.PI) / 3, (4 * Math.PI) / 3] as const;

/** Where a point `r` px out along the turn `turn` is on the playfield, at a spin of 0. */
const outAlong = (turn: number, r: number): [number, number] => [
  r * Math.sin(turn),
  -r * Math.cos(turn),
];

/** The tip of the lance turned by `turn`: where its bullets leave from. */
const lanceTip = (turn: number): Muzzle[] => [
  [...outAlong(turn, EMBER_LANCE.tip), EMBER_LANCE.height],
];

/** The twin ember cannons under the nose (aimed bursts). */
export const EMBER_GUNS: Muzzle[] = twin(5, -57, 3);
/** The core's spiral emitter: the lit crown of the spire over the ring's hub. */
export const EMBER_CROWN: Muzzle = [0, 0, 24];

/**
 * 4-5: a fast, spiky interceptor wreathed in embers, gold neon (P10-R11); three ember lances on
 * a turning ring fire spirals and shield the core, which fires aimed bursts from its nose. It
 * chases the ship down the volcano's slope (ground ×1.4).
 */
export const EMBER_HERALD: BossDesign = {
  id: 'ember-herald',
  /** Angry after each destroyed part (phase 7 review): the hottest mini boss so far. */
  rage: rage.spirals(13.5, 'magenta', 'purple'),
  stats: stats({
    id: 'ember-herald',
    name: 'Ember Herald',
    size: 3.5,
    coreRadius: 21,
    coreHealth: 1950,
    points: 9000,
    groundSpeed: 1.4,
    parts: LANCE_TURNS.map((turn, i) =>
      part(`lance-${String(i + 1)}`, outAlong(turn, EMBER_LANCE.orbit), 14, 1200, {
        orbits: true,
      }),
    ),
  }),
  stopFraction: 0.74,
  sway: { amplitude: 60, period: 6 },
  bob: { amplitude: 8, period: 2.8 },
  spinRate: 0.9,
  guns: {
    core: { gun: EMBER_GUNS, ring: [EMBER_CROWN] },
    'lance-1': { gun: lanceTip(LANCE_TURNS[0]) },
    'lance-2': { gun: lanceTip(LANCE_TURNS[1]) },
    'lance-3': { gun: lanceTip(LANCE_TURNS[2]) },
  },
  stages: stages(
    [
      volley.ring('lance-1', 0.85, 3, 23, PURPLE, 0.4),
      volley.ring('lance-2', 0.85, 3, 23, PURPLE, 0.68),
      volley.ring('lance-3', 0.85, 3, 23, PURPLE, 0.96),
    ],
    [
      [volley.burst('core', 2.4, 4, 0.13, MAGENTA, 1.4)],
      [volley.burst('core', 2.2, 5, 0.11, MAGENTA, 0.8)],
      [
        volley.burst('core', 2.1, 5, 0.1, MAGENTA, 0.6),
        volley.aimed('core', 3.1, 3, 13, BLUE, 1.6),
      ],
      [
        volley.ring('core', 0.5, 5, 17, PURPLE, 0.4),
        volley.ring('core', 0.5, 5, -19, BLUE, 0.65),
        volley.burst('core', 2.4, 4, 0.11, MAGENTA, 1.2),
      ],
    ],
  ),
};
