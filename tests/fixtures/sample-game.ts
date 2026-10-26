import type { Scene } from '@babylonjs/core/scene';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import { CreatePlane } from '@babylonjs/core/Meshes/Builders/planeBuilder';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { GameDefinition } from '../../src/core/content/game-definition';
import type { MenuScreen } from '../../src/core/menu/menu-screen';
import type {
  BombFrame,
  BombRenderer,
  BonusFrame,
  BonusRenderer,
  GameView,
  MenuBackdrop,
  ShotFrame,
  ShotRenderer,
} from '../../src/render/game-view';
import { SAMPLE_SCENERY, SAMPLE_SCENERY_LEVEL } from './sample-scenery';
import { SAMPLE_ENEMIES, SAMPLE_ENEMY_KINDS } from './sample-enemies';
import { SAMPLE_BOSS_KINDS } from './sample-boss';

const box = (scene: Scene) => CreateBox('sample-ship', { size: 1 }, scene);

/** The frames the sample bonus renderer was given, most recent last. */
export const bonusFrames: BonusFrame[] = [];

/** A bonus renderer that records its frames. */
function sampleBonusRenderer(): BonusRenderer {
  return {
    sync: (frame) => {
      bonusFrames.push(frame);
    },
    dispose: () => undefined,
  };
}

/** The frames the sample bomb renderer was given, most recent last. */
export const bombFrames: BombFrame[] = [];

/** A bomb renderer that records its frames. */
function sampleBombRenderer(): BombRenderer {
  return {
    sync: (frame) => {
      bombFrames.push(frame);
    },
    dispose: () => undefined,
  };
}

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

/** A shot renderer that records the frames it is given. */
export interface SampleShotRenderer extends ShotRenderer {
  readonly weaponId: string;
  readonly frames: ShotFrame[];
  disposed: boolean;
}

/** Shot renderers built by the sample game, most recent last. */
export const SAMPLE_SHOT_RENDERERS: SampleShotRenderer[] = [];

function sampleShotRenderer(weaponId: string) {
  return (): SampleShotRenderer => {
    const renderer: SampleShotRenderer = {
      weaponId,
      frames: [],
      disposed: false,
      sync: (frame) => {
        renderer.frames.push(frame);
      },
      dispose: () => {
        renderer.disposed = true;
      },
    };
    SAMPLE_SHOT_RENDERERS.push(renderer);
    return renderer;
  };
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
  playerWeapons: [
    {
      kind: 'projectile',
      id: 'pea',
      name: 'Pea',
      launchPoint: 'muzzle',
      shotsPerSecond: 2,
      launchSpeed: 100,
      acceleration: 0,
      maxSpeed: 100,
      homingTurnRateDeg: 0,
      homingRange: 0,
      radius: 2,
      damage: 1,
      blastRadius: 0,
      levels: [
        [{ offsetX: 0, angleDeg: 0 }],
        [
          { offsetX: -5, angleDeg: 0 },
          { offsetX: 5, angleDeg: 0 },
        ],
      ],
    },
    {
      kind: 'beam',
      id: 'ray',
      name: 'Ray',
      levels: [
        { damagePerSecond: 2, width: 2 },
        { damagePerSecond: 4, width: 4 },
      ],
    },
  ],
  levels: {
    columns: 2,
    levels: [
      { id: 'a', label: 'A', world: 1, level: 1, unlocked: true },
      { id: 'b', label: 'B', world: 1, level: 2, unlocked: false },
      { id: 'c', label: 'C', world: 2, level: 1, unlocked: true },
    ],
  },
  gameLevels: [
    {
      id: 'a',
      scenery: SAMPLE_SCENERY_LEVEL,
      waves: [
        { at: 0, kind: 'dropper', count: 1, interval: 0, entry: { side: 'top', position: 0.5 } },
        { at: 100, kind: 'pair', count: 2, interval: 1, entry: { side: 'top', position: 0.5 } },
      ],
      difficulty: { bulletSpeed: 1, fireRate: 1 },
    },
    {
      id: 'c',
      scenery: SAMPLE_SCENERY_LEVEL,
      waves: [],
      difficulty: { bulletSpeed: 1.5, fireRate: 2 },
    },
  ],
  sceneryLevels: [SAMPLE_SCENERY_LEVEL],
  enemyKinds: SAMPLE_ENEMY_KINDS,
  bossKinds: SAMPLE_BOSS_KINDS,
  bossFights: { speedEaseSeconds: 1, barFillSeconds: 0.5 },
  // No drops unless a test asks for them.
  bonuses: { chance: { perHealth: 0, min: 0, max: 0 }, fallSpeed: 20, pickupRadius: 15 },
  bombs: { start: 2, max: 3, damage: 50, seconds: 0.5 },
  hull: {
    lives: 2,
    invincibleSeconds: 1,
    hitRadius: 4,
    damage: { bullet: 1, missile: 2, laser: 2, collision: 3 },
    ramDamage: 10,
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
    gameLevel: (level) => `L${level}`,
    fire: 'Pew',
    levelComplete: 'Done',
    gameOver: 'Lost',
    enemiesDestroyed: (destroyed, spawned) => `${String(destroyed)}/${String(spawned)}`,
    finalScore: (score) => `Pts ${String(score)}`,
    newHighScore: 'Record!',
    continueHint: 'Go on',
    continueFromCheckpoint: 'Again',
    toLevelSelect: 'Levels',
    hudHealth: 'Life',
    hudLives: (lives) => `L${String(lives)}`,
    hudWeapon: (weapon, level, levels) => `${weapon} ${String(level)}/${String(levels)}`,
    hudDestroyed: (count) => `x${String(count)}`,
    hudScore: (score) => String(score),
    hudHighScore: (score) => `Top ${String(score)}`,
    hudBomb: (bombs) => `B${String(bombs)}`,
    hudMiniBoss: 'Mini',
    hudBoss: 'Big',
    unsupported: 'No WebGL2',
  },
  view: {
    playerShipModels: { cube: box, brick: box },
    playerShipScale: 10,
    playerShotRenderers: { pea: sampleShotRenderer('pea'), ray: sampleShotRenderer('ray') },
    menuBackdrop: sampleBackdrop,
    scenery: SAMPLE_SCENERY,
    enemies: SAMPLE_ENEMIES,
    bonuses: sampleBonusRenderer,
    bombs: sampleBombRenderer,
  },
};
