import { SAMPLE_GAME } from '../../fixtures/sample-game';

/** The sample game where hits and rams do no damage, for tests of other things on level a. */
export const HARMLESS = {
  ...SAMPLE_GAME,
  hull: {
    ...SAMPLE_GAME.hull,
    damage: { bullet: 0, missile: 0, laser: 0, collision: 0 },
    ramDamage: 0,
  },
};

/** The harmless sample game whose level a has a mini boss at 5 s and a final boss at its end. */
export const BOSSY = {
  ...HARMLESS,
  gameLevels: HARMLESS.gameLevels.map((level) =>
    level.id === 'a'
      ? {
          ...level,
          runout: 5,
          bosses: [
            { kind: 'big-cube', rank: 'mini', at: 100 },
            { kind: 'big-cube', rank: 'final', at: 400 },
          ] as const,
        }
      : level,
  ),
};

/** Runs `seconds` of frames of 0.1 s. */
