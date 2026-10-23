import type { CarRules } from '../../core/scenery/scenery-level';

/** Cars on the streets and main roads (phase 4 review). */
export const CAR_IDS = {
  red: 'car-red',
  blue: 'car-blue',
  white: 'car-white',
  grey: 'car-grey',
  van: 'van',
  truck: 'truck',
} as const;

/** One lane each way of the 6-wide roads; cars stand on the road surface (`roads.lift`). */
export const CAR_RULES: CarRules = {
  kinds: Object.values(CAR_IDS),
  density: 0.3,
  laneOffset: 1.5,
  lift: 0.6,
  scale: 0.6,
  length: 4,
};
