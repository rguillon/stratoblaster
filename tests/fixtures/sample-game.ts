import type { Scene } from '@babylonjs/core/scene';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import type { GameDefinition } from '../../src/core/content/game-definition';
import type { GameView } from '../../src/render/game-view';

const box = (scene: Scene) => CreateBox('sample-ship', { size: 1 }, scene);

/** Minimal game used to test the engine independently of `src/game/` (ENG-145). */
export const SAMPLE_GAME: GameDefinition<GameView> = {
  id: 'sample',
  title: 'Sample Game',
  playerShips: {
    baseSpeedPxPerSec: 50,
    ships: [
      { id: 'cube', name: 'Cube', maxSpeedFactor: 1, maxHealth: 3 },
      { id: 'brick', name: 'Brick', maxSpeedFactor: 0.5, maxHealth: 6 },
    ],
  },
  view: { playerShipModels: { cube: box, brick: box } },
};
