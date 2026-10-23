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

/** Cars stand in the middle of a lane, on the road surface (`roads.lift`). */
export const CAR_RULES: CarRules = {
  kinds: Object.values(CAR_IDS),
  density: 0.3,
  lift: 0.6,
  scale: 0.6,
  length: 4,
};
