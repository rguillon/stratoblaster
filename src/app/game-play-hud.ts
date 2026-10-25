import type { MenuTexts } from '../core/content/menu-texts';
import type { LevelRun } from '../core/systems/level-run';
import type { BossBarFrame } from '../ui/boss-bar';
import type { HudFrame } from '../ui/game-hud';

/** The boss health bar of `run`'s fight (P07-R02), if a boss is being fought. */
export function bossBarFrame(run: LevelRun, texts: MenuTexts): BossBarFrame | undefined {
  const bar = run.fights.bar;
  if (!bar) return undefined;
  const { name, share, notches } = bar;
  return { name, share, notches, rank: bar.rank === 'mini' ? texts.hudMiniBoss : texts.hudBoss };
}

/** What the HUD shows of `run` (phase 6 review, P07-R02); `maxHealth` stands for no hull. */
export function hudFrame(run: LevelRun, maxHealth: number, texts: MenuTexts): HudFrame {
  const { shots, track, hull, enemies } = run;
  return {
    health: hull?.health ?? maxHealth,
    maxHealth,
    lives: hull?.lives ?? 0,
    weapon: shots.weapon.name,
    weaponLevel: shots.level,
    weaponLevels: shots.weapon.levels.length,
    progress: track.length > 0 ? track.progress / track.length : 1,
    destroyed: enemies.kills,
    boss: bossBarFrame(run, texts),
  };
}
