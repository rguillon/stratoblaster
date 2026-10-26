import type { GameLevel } from '../../src/core/content/game-level';
import { HeightField } from '../../src/core/scenery/height-field';
import { PropPlacer } from '../../src/core/scenery/prop-placement';
import { levelRoads } from '../../src/core/scenery/road-network';
import type { TerrainSection } from '../../src/core/scenery/scenery-level';
import { LevelRun } from '../../src/core/systems/level-run';
import { PLAYER_WEAPONS } from '../../src/game/config/player-weapons';
import { ENEMY_KINDS } from '../../src/game/sim/enemy-kinds';

/** What a level throws at the player, per minute of scroll (see `world-1.test.ts`, D-038). */
export interface LevelMetrics {
  readonly spawned: number;
  readonly health: number;
  readonly peak: number;
  readonly firstHalf: number;
  readonly secondHalf: number;
  /** Enemies and their total health per minute of scroll. */
  readonly perMinute: number;
  readonly healthPerMinute: number;
}

/**
 * Plays `game` through without shooting, its bosses left out (as in `world-1.test.ts`): enemies
 * spawned, their health, the most on screen at once, and the health spawned in each half.
 */
export function levelMetrics(game: GameLevel): LevelMetrics {
  const run = new LevelRun({
    screen: { width: 480, height: 640 },
    level: { ...game, bosses: [] },
    kinds: ENEMY_KINDS,
    weapon: PLAYER_WEAPONS[0],
    weaponLevel: 1,
    ship: { start: { x: 240, y: 90 }, maxSpeed: 100, accelerationSeconds: 0.08, muzzleOffset: 20 },
    bounds: { minY: 30, maxY: 440, centerX: 240, halfWidthAt: () => 140 },
    cullMargin: 80,
    maxEnemyAge: 40,
    endWait: 10,
    seed: 606,
  });
  let [peak, firstHalf] = [0, -1];
  const still = { move: { x: 0, y: 0 }, fire: false };
  while (run.phase !== 'complete') {
    run.step(1 / 60, still);
    peak = Math.max(peak, run.enemies.onScreen);
    if (firstHalf < 0 && run.track.time >= run.track.duration / 2) {
      firstHalf = run.enemies.spawnedHealth;
    }
  }
  const { spawned, spawnedHealth } = run.enemies;
  const minutes = run.track.duration / 60;
  return {
    spawned,
    health: spawnedHealth,
    peak,
    firstHalf,
    secondHalf: spawnedHealth - firstHalf,
    perMinute: spawned / minutes,
    healthPerMinute: spawnedHealth / minutes,
  };
}

/** Share of the ground under the playfield that is under the sea. */
export function seaShare(game: GameLevel): number {
  const { scenery } = game;
  if (!scenery.sea) return 0;
  const field = new HeightField(scenery);
  let [wet, all] = [0, 0];
  for (let z = 0; z < field.length; z += 20) {
    for (let x = -240; x <= 240; x += 20) {
      all++;
      if (field.height(x, z) < scenery.sea.level) wet++;
    }
  }
  return wet / all;
}

/** Buildings placed over the whole level with its own seed: props that are not `plants`. */
export function buildingCount(game: GameLevel, plants: ReadonlySet<string>): number {
  const { scenery } = game;
  const field = new HeightField(scenery);
  const placer = new PropPlacer(
    field,
    scenery.props,
    scenery.seed,
    levelRoads(field, scenery.roads, scenery.seed),
    scenery.sea?.level,
  );
  const area = { xMin: -400, xMax: 400, zMin: 0, zMax: field.length };
  return placer.place(area).filter((p) => !plants.has(p.kind)).length;
}

/**
 * Shares of the ground under the playfield that are under the water level (phase 9): in the
 * sections `isSea` says are sea, and in the others (rivers, swamps, lakes, pools).
 */
export function waterShares(
  game: GameLevel,
  isSea: (section: TerrainSection) => boolean,
): { readonly sea: number; readonly inland: number } {
  const { scenery } = game;
  if (!scenery.sea) return { sea: 0, inland: 0 };
  const field = new HeightField(scenery);
  let [sea, inland, all] = [0, 0, 0];
  for (let z = 0; z < field.length; z += 20) {
    const open = isSea(field.sectionAt(z).section);
    for (let x = -240; x <= 240; x += 20) {
      all++;
      if (field.height(x, z) >= scenery.sea.level) continue;
      if (open) sea++;
      else inland++;
    }
  }
  return { sea: sea / all, inland: inland / all };
}
