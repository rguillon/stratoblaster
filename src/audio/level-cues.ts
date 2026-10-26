import type { LevelRun } from '../core/systems/level-run';
import type { EnemyBullet, EnemyLaser } from '../core/systems/enemy-shots';
import type { Projectile } from '../core/systems/projectile-motion';

/**
 * The engine's sound cues (P12-R09): what happened in a level step that a game may give a sound.
 * `fire:<weaponId>` (a volley of a projectile weapon), `beam-start:<weaponId>` (a beam starts;
 * `beam:<weaponId>` names its looping hum), `weapon-switch`, `weapon-up`, `enemy-bullet`,
 * `enemy-missile`, `laser-warning`, `laser-fire`, `hit`, `hit-blocked`, `player-hit`,
 * `blast-small`, `blast-large`, `part-destroyed`, `boss-destroyed`, `life-lost`, `extra-life`,
 * `bomb`, `bonus:<kind>`; and on the menus `menu-move`, `menu-confirm`, `menu-back`, `pause`,
 * `resume`, `slider`.
 */
export interface SoundCue {
  readonly cue: string;
  /** Where it happened on the playfield, for sounds panned with their position. */
  readonly x?: number;
}

/** What the player's weapons, hull and bombs were at the last step. */
interface PlayerSnapshot {
  readonly weapon: string;
  readonly level: number;
  readonly lives: number;
  readonly bombs: number;
  readonly bosses: number;
}

/**
 * Turns the state of a {@link LevelRun} after each step into sound cues (P12-R09), by comparing
 * it with the step before: new shots, impacts, blasts, hits, bonuses picked up. Audio only reads
 * the core's state, it never changes it (ENG-11). One cue of a kind per step: a volley of shots
 * is one sound.
 */
export class LevelCues {
  #started = false;
  #shots = new Set<Projectile>();
  #bullets = new Set<EnemyBullet>();
  #lasers = new Map<EnemyLaser, EnemyLaser['phase']>();
  #missileId = 0;
  #snapshot: PlayerSnapshot = { weapon: '', level: 0, lives: 0, bombs: 0, bosses: 0 };
  /** The beam weapon firing at the last step, if any. */
  beam: string | undefined;

  constructor(private readonly largeBlastRadius: number) {}

  /** The cues of the step just run. The first call only takes the starting state. */
  observe(run: LevelRun): SoundCue[] {
    const cues: SoundCue[] = [];
    const add = (cue: string, x?: number): void => {
      if (!cues.some((c) => c.cue === cue)) cues.push(x === undefined ? { cue } : { cue, x });
    };
    this.#playerShots(run, add);
    this.#enemyShots(run, add);
    this.#laserCues(run, add);
    this.#impacts(run, add);
    this.#hits(run, add);
    this.#player(run, add);
    if (!this.#started) {
      this.#started = true;
      return [];
    }
    return cues;
  }

  #playerShots(run: LevelRun, add: (cue: string, x?: number) => void): void {
    const alive = new Set<Projectile>();
    for (const shot of run.shots.projectiles) {
      if (!shot.alive) continue;
      alive.add(shot);
      if (!this.#shots.has(shot)) add(`fire:${shot.weapon.id}`, shot.x);
    }
    this.#shots = alive;
    const beam = run.shots.beam.length > 0 ? run.shots.weapon.id : undefined;
    if (beam !== undefined && beam !== this.beam) add(`beam-start:${beam}`, run.ship.x);
    this.beam = beam;
  }

  #enemyShots(run: LevelRun, add: (cue: string, x?: number) => void): void {
    const { shots } = run.enemies;
    const alive = new Set<EnemyBullet>();
    for (const bullet of shots.bullets) {
      if (!bullet.alive) continue;
      alive.add(bullet);
      if (!this.#bullets.has(bullet)) add('enemy-bullet', bullet.x);
    }
    this.#bullets = alive;
    for (const missile of shots.missiles) {
      if (missile.alive && missile.id > this.#missileId) add('enemy-missile', missile.x);
      this.#missileId = Math.max(this.#missileId, missile.id);
    }
  }

  /** A laser's warning line, then its beam. */
  #laserCues(run: LevelRun, add: (cue: string, x?: number) => void): void {
    const lasers = new Map<EnemyLaser, EnemyLaser['phase']>();
    for (const laser of run.enemies.shots.lasers) {
      const before = this.#lasers.get(laser);
      if (before === undefined) add('laser-warning', laser.x);
      if (laser.phase === 'firing' && before !== 'firing') add('laser-fire', laser.x);
      lasers.set(laser, laser.phase);
    }
    this.#lasers = lasers;
  }

  #impacts(run: LevelRun, add: (cue: string, x?: number) => void): void {
    for (const impact of run.impacts) add(impact.blocked ? 'hit-blocked' : 'hit', impact.x);
    for (const blast of run.blasts) {
      const large = blast.kind === 'enemy' && blast.radius >= this.largeBlastRadius;
      add(large ? 'blast-large' : 'blast-small', blast.x);
    }
    for (const part of run.enemies.brokenParts) add('part-destroyed', part.x);
  }

  /** Hits on the player, and bonuses picked up. */
  #hits(run: LevelRun, add: (cue: string, x?: number) => void): void {
    for (const hit of run.hits) {
      if (hit.event === 'hit') add('player-hit', hit.x);
      else if (hit.event !== 'ignored') add('life-lost', hit.x);
    }
    for (const bonus of run.bonuses?.picked ?? []) add(`bonus:${bonus.kind}`, bonus.x);
  }

  #player(run: LevelRun, add: (cue: string, x?: number) => void): void {
    const now: PlayerSnapshot = {
      weapon: run.shots.weapon.id,
      level: run.shots.level,
      lives: run.hull?.lives ?? 0,
      bombs: run.bombs?.fired ?? 0,
      bosses: run.fights.defeated.length,
    };
    const before = this.#snapshot;
    if (now.weapon !== before.weapon) add('weapon-switch');
    else if (now.level > before.level) add('weapon-up');
    if (now.lives > before.lives) add('extra-life');
    if (now.bombs > before.bombs) add('bomb', run.ship.x);
    if (now.bosses > before.bosses) add('boss-destroyed');
    this.#snapshot = now;
  }
}
