import type { MenuTexts } from '../core/content/menu-texts';
import type { LevelRun } from '../core/systems/level-run';
import type { BossBarFrame } from '../ui/boss-bar';
import { GameHud, type HudFrame } from '../ui/game-hud';
import type { MenuDocument } from '../ui/screens/elements';
import { StatsTile } from '../ui/stats-tile';
import { GAME_PLAY_CONFIG as CFG } from '../config/game-play';

/** The boss health bar of `run`'s fight (P07-R02), if a boss is being fought. */
export function bossBarFrame(run: LevelRun, texts: MenuTexts): BossBarFrame | undefined {
  const bar = run.fights.bar;
  if (!bar) return undefined;
  const { name, share, notches } = bar;
  return { name, share, notches, rank: bar.rank === 'mini' ? texts.hudMiniBoss : texts.hudBoss };
}

/**
 * What the HUD shows of `run` (phase 6 review, P07-R02, P11-R02); `maxHealth` stands for no
 * hull, `highScore` is the saved one.
 */
export function hudFrame(
  run: LevelRun,
  maxHealth: number,
  texts: MenuTexts,
  highScore = 0,
): HudFrame {
  const { shots, track, hull } = run;
  return {
    health: hull?.health ?? maxHealth,
    maxHealth,
    lives: hull?.lives ?? 0,
    weapon: shots.weapon.name,
    weaponLevel: shots.level,
    weaponLevels: shots.weapon.levels.length,
    progress: track.length > 0 ? track.progress / track.length : 1,
    score: run.score,
    highScore: Math.max(highScore, run.score),
    bombs: run.bombs?.count,
    boss: bossBarFrame(run, texts),
  };
}

/**
 * The in-game HUD of a level (phase 6 review, P11-R02, R06) in `parent`, for the ship named
 * `ship`, with the game's `texts`; `onBomb` is the touch bomb button's.
 */
export function createHud(
  doc: MenuDocument,
  parent: HTMLElement,
  ship: string,
  texts: MenuTexts,
  onBomb: () => void,
): GameHud {
  return new GameHud(doc, parent, {
    ship,
    texts: {
      health: texts.hudHealth,
      weapon: texts.hudWeapon,
      lives: texts.hudLives,
      bombs: texts.hudBombs,
      score: texts.hudScore,
      highScore: texts.hudHighScore,
      bomb: texts.hudBomb,
    },
    onBomb,
  });
}

/** Where a level's HUD and debug tile go, and what they show. */
export interface LevelOverlaysOptions {
  readonly doc: MenuDocument;
  readonly debug: boolean;
  readonly statsParent?: HTMLElement;
  readonly hudParent?: HTMLElement;
}

/** The level's HUD (with a parent) and debug tile (in debug mode, with a parent). */
export function createLevelOverlays(
  options: LevelOverlaysOptions,
  ship: string,
  texts: MenuTexts,
  onBomb: () => void,
): { hud: GameHud | undefined; stats: StatsTile | undefined } {
  const { doc, debug, statsParent, hudParent } = options;
  return {
    stats: debug && statsParent ? new StatsTile(doc, statsParent, CFG.stats.refresh) : undefined,
    hud: hudParent && createHud(doc, hudParent, ship, texts, onBomb),
  };
}
