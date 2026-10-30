import type { PropRules } from '../../../core/scenery/scenery-level';
import { tileKinds } from '../tile-buildings';
import { CAR_RULES } from '../cars';
import { WORLD_3_GROUPS, WORLD_3_PROPS } from '../world-3/props';

/** Building groups of World 4 (reviewer's rework, 2026-10-27); each section lists its own. */
export const WORLD_4_GROUPS = {
  /** World 3's garden villages and suburbs, where World 3 ended. */
  villages: WORLD_3_GROUPS.villages,
  residences: WORLD_3_GROUPS.residences,
  workerFlats: WORLD_3_GROUPS.workerFlats,
  /** A town centre: flats and terraces, the first mid-rise blocks. */
  townCentre: 'w4-town-centre',
  /** Mid-rise blocks of flats and offices. */
  midrise: 'w4-midrise',
  /** Office blocks and the city towers. */
  offices: 'w4-offices',
  /** City towers among the last office blocks. */
  towers: 'w4-towers',
  /** Skyscrapers among the last towers. */
  skyscrapers: 'w4-skyscrapers',
  /** Downtown: skyscrapers only. */
  downtown: 'w4-downtown',
} as const;

const G = WORLD_4_GROUPS;

/** World 3's rules for the home groups World 4 starts with. */
const homeGroups = WORLD_3_PROPS.groups.filter((g) =>
  [G.villages, G.residences, G.workerFlats].some((id) => id === g.id),
);

/**
 * The props of World 4 (P10-R03, R08; reworked at the reviewer's request, 2026-10-27): World 3's
 * houses, terraces and flats, then Level Zero's city blocks and towers made of parts, then the
 * skyscrapers; each section picks the groups that stand on it, so the buildings slowly grow
 * from the houses to the skyscrapers. World 3's plants (Level Zero's trees).
 */
export const WORLD_4_PROPS: PropRules = {
  ...WORLD_3_PROPS,
  groups: [
    ...homeGroups,
    {
      id: G.townCentre,
      weight: 3,
      kinds: tileKinds('townCentre'),
    },
    {
      id: G.midrise,
      weight: 3,
      kinds: tileKinds('midrise'),
    },
    {
      id: G.offices,
      weight: 3,
      kinds: tileKinds('offices'),
    },
    {
      id: G.towers,
      weight: 3,
      kinds: tileKinds('towers'),
    },
    {
      id: G.skyscrapers,
      weight: 3,
      kinds: tileKinds('skyscrapers'),
    },
    { id: G.downtown, weight: 3, kinds: tileKinds('downtown') },
  ],
  cars: CAR_RULES,
};
