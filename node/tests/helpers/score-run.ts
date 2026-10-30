/** Shared setup of the P11 `LevelRun` tests (score, bombs, bonuses). */
import type { GameLevel } from '../../src/core/content/game-level';
import { Enemy } from '../../src/core/entities/enemy';
import type { BonusRules } from '../../src/core/systems/bonus-world';
import type { LevelBoss } from '../../src/core/systems/boss-fights';
import {
  LevelRun,
  type LevelControls,
  type LevelRunOptions,
} from '../../src/core/systems/level-run';
import type { BombRules } from '../../src/core/systems/player-bombs';
import type { HullRules } from '../../src/core/systems/player-hull';
import { SAMPLE_BOSS_KINDS, SAMPLE_BOSS_STATS, SampleBoss } from '../fixtures/sample-boss';
import { SAMPLE_ENEMY_KINDS } from '../fixtures/sample-enemies';
import { SAMPLE_GAME } from '../fixtures/sample-game';
import { SAMPLE_SCENERY_LEVEL } from '../fixtures/sample-scenery';

/** An enemy that stays where it is put. */
export class Still extends Enemy {
  constructor(x: number, y: number, health: number, points: number) {
    super(x, y, { model: 'cube', radius: 10, health, points });
  }

  override update(): void {
    // stays put
  }
}

export const STILL: LevelControls = { move: { x: 0, y: 0 }, fire: false };
export const BOMB: LevelControls = { ...STILL, bomb: true };

export const BOMBS: BombRules = { start: 3, max: 5, damage: 100, seconds: 1 };
export const HULL: HullRules = {
  lives: 3,
  maxLives: 5,
  invincibleSeconds: 1,
  hitRadius: 5,
  damage: { bullet: 200, missile: 200, laser: 200, collision: 200 },
  ramDamage: 50,
};
/** Hits do no damage: boss fights cannot end the game while a test plays them. */
export const SAFE: HullRules = {
  ...HULL,
  damage: { bullet: 0, missile: 0, laser: 0, collision: 0 },
};
export const NO_DROP: BonusRules = {
  chance: { perHealth: 0, min: 0, max: 0 },
  fallSpeed: 0,
  pickupRadius: 15,
  overflowPoints: { life: 5000, bomb: 2000 },
};

/** A boss whose parts score 10 points each, and its core 100 (P11-R01). */
export const SCORED_BOSS = {
  id: 'scored-cube',
  name: 'Scored Cube',
  spawn: (area: Parameters<(typeof SAMPLE_BOSS_KINDS)[number]['spawn']>[0]) =>
    new SampleBoss(area, { ...SAMPLE_BOSS_STATS, partPoints: 10 }),
};

export const level = (bosses: readonly LevelBoss[] = []): GameLevel => ({
  id: 'a',
  scenery: SAMPLE_SCENERY_LEVEL,
  waves: [],
  difficulty: { bulletSpeed: 1, fireRate: 1 },
  bosses,
});

export function newRun(overrides: Partial<LevelRunOptions> = {}): LevelRun {
  const [weapon] = SAMPLE_GAME.playerWeapons;
  if (!weapon) throw new Error('no weapon');
  return new LevelRun({
    screen: SAMPLE_GAME.screen,
    level: level(),
    kinds: SAMPLE_ENEMY_KINDS,
    weapon,
    weaponLevel: 1,
    ship: {
      start: { x: 150, y: 50 },
      maxSpeed: 100,
      accelerationSeconds: 0.05,
      muzzleOffset: 10,
      maxHealth: 100,
    },
    bounds: { minY: 20, maxY: 300, centerX: 150, halfWidthAt: () => 120 },
    cullMargin: 40,
    maxEnemyAge: 60,
    endWait: 10,
    seed: 3,
    bombs: BOMBS,
    hull: HULL,
    bonuses: NO_DROP,
    bossKinds: [...SAMPLE_BOSS_KINDS, SCORED_BOSS],
    bossRules: SAMPLE_GAME.bossFights,
    ...overrides,
  });
}

export function play(run: LevelRun, seconds: number, controls = STILL): void {
  for (let i = 0; i < Math.round(seconds * 60) && run.phase !== 'complete'; i++) {
    run.step(1 / 60, controls);
  }
}

/** Destroys the boss being fought (its parts, then its core) and waits for its death blasts. */
export function defeat(run: LevelRun): void {
  for (let i = 0; i < 3; i++) {
    run.breakBossPart();
    play(run, 0.1);
  }
  play(run, 1.2);
}
