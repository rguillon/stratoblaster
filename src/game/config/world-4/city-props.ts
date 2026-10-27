import type { PropRules } from '../../../core/scenery/scenery-level';
import {
  CITY_VARIANTS,
  SKYSCRAPER_VARIANTS,
  familyRules,
  type PartFamily,
} from '../building-families';
import { CAR_RULES } from '../cars';
import { WORLD_3_GROUPS, WORLD_3_PROPS } from '../world-3/props';

/** Building groups of World 4 (reviewer's rework, 2026-10-27); each section lists its own. */
export const WORLD_4_GROUPS = {
  /** World 3's garden villages and suburbs, where World 3 ended. */
  villages: WORLD_3_GROUPS.villages,
  suburbs: WORLD_3_GROUPS.suburbs,
  terraces: WORLD_3_GROUPS.terraces,
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

/** Props are drawn small next to the ships, as in Worlds 1 to 3. */
const BUILDING_SCALE = [0.5, 0.65] as const;

/** The variants of `family`, sharing `weight` between them (not `weight` each). */
const variants = (family: PartFamily, weight: number) => {
  const count = family === 'skyscraper' ? SKYSCRAPER_VARIANTS : CITY_VARIANTS;
  return familyRules(family, count, weight / count, BUILDING_SCALE);
};

/** World 3's rules for the home groups World 4 starts with. */
const homeGroups = WORLD_3_PROPS.groups.filter((g) =>
  [G.villages, G.suburbs, G.terraces, G.workerFlats].some((id) => id === g.id),
);
/** The kinds of World 3's group `id`, with their weights shared out as `weight`. */
const kindsOf = (id: string, weight: number) => {
  const kinds = WORLD_3_PROPS.groups.find((g) => g.id === id)?.kinds ?? [];
  const total = kinds.reduce((sum, k) => sum + k.weight, 0);
  return kinds.map((k) => ({ ...k, weight: (k.weight / total) * weight }));
};

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
      kinds: [
        ...kindsOf(G.workerFlats, 4),
        ...kindsOf(G.terraces, 3),
        ...variants('city-block', 1),
      ],
    },
    {
      id: G.midrise,
      weight: 3,
      kinds: [
        ...variants('city-block', 6),
        ...kindsOf(G.workerFlats, 2),
        ...variants('city-tower', 1),
      ],
    },
    {
      id: G.offices,
      weight: 3,
      kinds: [...variants('city-block', 4), ...variants('city-tower', 4)],
    },
    {
      id: G.towers,
      weight: 3,
      kinds: [...variants('city-tower', 6), ...variants('city-block', 2)],
    },
    {
      id: G.skyscrapers,
      weight: 3,
      kinds: [...variants('skyscraper', 6), ...variants('city-tower', 2)],
    },
    { id: G.downtown, weight: 3, kinds: variants('skyscraper', 1) },
  ],
  cars: CAR_RULES,
};
