import type { GameLevel } from '../../src/core/content/game-level';
import type { ShotTarget } from '../../src/core/entities/shot-target';
import type { BossRank } from '../../src/core/systems/boss-fights';
import { LevelRun } from '../../src/core/systems/level-run';
import { BOSS_FIGHT_RULES } from '../../src/game/config/boss-fights';
import { BONUS_RULES } from '../../src/game/config/bonuses';
import { PLAYER_WEAPONS } from '../../src/game/config/player-weapons';
import { BOSS_KINDS } from '../../src/game/sim/boss-kinds';
import { ENEMY_KINDS } from '../../src/game/sim/enemy-kinds';

const STEP = 1 / 60;
/** The balanced ship's speed and acceleration (phase 6 review, D-045, D-047). */
const SHIP = {
  start: { x: 240, y: 90 },
  maxSpeed: 225,
  accelerationSeconds: 0.18,
  muzzleOffset: 20,
};

/** A run of `level` with the game's content, guns at `weaponLevel`, nothing hurting the player. */
export function bossRun(level: GameLevel, weaponLevel = 3, bonuses = false): LevelRun {
  return new LevelRun({
    screen: { width: 480, height: 640 },
    level,
    kinds: ENEMY_KINDS,
    weapon: PLAYER_WEAPONS[0],
    weaponLevel,
    weapons: PLAYER_WEAPONS,
    ship: SHIP,
    // The ship's reach at the bottom of the screen, as in the game (x 107–373).
    bounds: { minY: 30, maxY: 440, centerX: 240, halfWidthAt: () => 133 },
    cullMargin: 80,
    maxEnemyAge: 40,
    endWait: 10,
    seed: 606,
    bossKinds: BOSS_KINDS,
    bossRules: BOSS_FIGHT_RULES,
    ...(bonuses ? { bonuses: BONUS_RULES } : {}),
  });
}

/** What the bot shoots at: a part that shields the core, then the other parts, then the core. */
function targetOf(run: LevelRun): ShotTarget | undefined {
  const boss = run.fights.boss;
  if (!boss) return undefined;
  const intact = boss.parts.filter((p) => !p.destroyed);
  return intact.find((p) => p.shieldsCore) ?? intact[0] ?? boss.core;
}

/**
 * Where to fly to hit the target: under it, ahead by its speed over the last step times the
 * bullets' flight time up to it.
 */
function leadingAim(run: LevelRun): () => number {
  let last: { x: number; target: ShotTarget } | undefined;
  return () => {
    const target = targetOf(run);
    if (!target) return run.ship.x;
    const vx = last?.target === target ? (target.x - last.x) / STEP : 0;
    last = { x: target.x, target };
    const flight = Math.max(0, target.y - run.ship.y) / PLAYER_WEAPONS[0].launchSpeed;
    return target.x + vx * flight;
  };
}

/**
 * Plays `run` from the arrival of its `rank` boss with a bot always firing at it (P07-R10): it
 * flies under its target, leading it by the bullets' flight time. Returns the seconds from the
 * boss's arrival to the end of its death blasts, or Infinity after `maxSeconds`.
 */
export function fightBoss(run: LevelRun, rank: BossRank, maxSeconds = 400): number {
  const boss = run.fights.bosses.find((b) => b.rank === rank);
  if (!boss) throw new Error(`No ${rank} boss`);
  run.seek(boss.at / run.track.speed);
  let time = 0;
  let arrived = false;
  const aim = leadingAim(run);
  while (time < maxSeconds) {
    const x = aim();
    run.step(STEP, {
      move: { x: Math.max(-1, Math.min(1, (x - run.ship.x) / 8)), y: 0 },
      fire: true,
    });
    arrived ||= run.fights.active;
    if (arrived) time += STEP;
    if (arrived && !run.fights.active) return time;
  }
  return Infinity;
}
