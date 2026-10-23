import type { Scene } from '@babylonjs/core/scene';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import { CreatePlane } from '@babylonjs/core/Meshes/Builders/planeBuilder';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { GameDefinition } from '../../src/core/content/game-definition';
import type { MenuScreen } from '../../src/core/menu/menu-screen';
import type { GameView, MenuBackdrop } from '../../src/render/game-view';

const box = (scene: Scene) => CreateBox('sample-ship', { size: 1 }, scene);

/** A backdrop that records what the engine asks of it. */
export interface SampleBackdrop extends MenuBackdrop {
  readonly screens: MenuScreen[];
  elapsed: number;
}

/** Backdrops built by the sample game, most recent last. */
export const SAMPLE_BACKDROPS: SampleBackdrop[] = [];

function sampleBackdrop(scene: Scene): SampleBackdrop {
  new FreeCamera('sample-camera', new Vector3(0, 0, -10), scene);
  const backdrop: SampleBackdrop = {
    screens: [],
    elapsed: 0,
    glowExcludedMeshes: [CreatePlane('sample-sky', { size: 10 }, scene)],
    update: (dt) => {
      backdrop.elapsed += dt;
    },
    showScreen: (screen) => {
      backdrop.screens.push(screen);
    },
  };
  SAMPLE_BACKDROPS.push(backdrop);
  return backdrop;
}

/** Minimal game used to test the engine independently of `src/game/` (ENG-145). */
export const SAMPLE_GAME: GameDefinition<GameView> = {
  id: 'sample',
  title: 'Sample Game',
  screen: { width: 300, height: 400 },
  playerShips: {
    baseSpeedPxPerSec: 50,
    ships: [
      { id: 'cube', name: 'Cube', maxSpeedFactor: 1, maxHealth: 3 },
      { id: 'brick', name: 'Brick', maxSpeedFactor: 0.5, maxHealth: 6 },
    ],
  },
  levels: {
    columns: 2,
    levels: [
      { id: 'a', label: 'A', world: 1, level: 1, unlocked: true },
      { id: 'b', label: 'B', world: 1, level: 2, unlocked: false },
      { id: 'c', label: 'C', world: 2, level: 1, unlocked: true },
    ],
  },
  texts: {
    loading: 'Wait',
    highScore: 'Best',
    start: 'Go',
    startHint: 'Press go',
    chooseShip: 'Ship?',
    chooseShipHint: 'Pick a ship',
    chooseLevel: 'Level?',
    chooseLevelHint: 'Pick a level',
    back: 'Back',
    locked: 'Nope',
    gamePlaceholder: (ship, level) => `${ship} @ ${level}`,
    gameHint: 'Esc',
    unsupported: 'No WebGL2',
  },
  view: { playerShipModels: { cube: box, brick: box }, menuBackdrop: sampleBackdrop },
};
