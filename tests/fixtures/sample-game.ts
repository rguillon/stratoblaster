import type { GameDefinition } from '../../src/core/content/game-definition';

/** Minimal game used to test the engine independently of `src/game/` (ENG-145). */
export const SAMPLE_GAME: GameDefinition = {
  id: 'sample',
  title: 'Sample Game',
};
