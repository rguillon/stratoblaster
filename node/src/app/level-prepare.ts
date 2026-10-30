import type { GameDefinition } from '../core/content/game-definition';
import { findGameLevel, type GameLevel } from '../core/content/game-level';
import { withRunout, type SceneryLevel } from '../core/scenery/scenery-level';
import type { GameView } from '../render/game-view';
import type { BackgroundLoader } from '../render/scenery/background-loader';
import { requestLevelGround } from '../render/scenery/level-ground';
import { sceneryTextureJobs } from '../render/scenery/procedural-textures';

/** Each level's scenery with its runout, made once, so its generated ground is reused (P13-R03). */
const runouts = new WeakMap<GameLevel, SceneryLevel>();

export function sceneryWithRunout(level: GameLevel): SceneryLevel {
  let scenery = runouts.get(level);
  if (!scenery) {
    scenery = withRunout(level.scenery, level.runout ?? 0);
    runouts.set(level, scenery);
  }
  return scenery;
}

export function levelOf(game: GameDefinition, id: string): GameLevel {
  const level = findGameLevel(game.gameLevels, id);
  if (!level) throw new Error(`Level "${id}" cannot be played`);
  return level;
}

/**
 * Asks for the ground of level `levelId` ahead of its {@link GamePlay} (P13-R03): true once it is
 * ready (generated in the background when a worker does it, false until then).
 */
export function prepareLevel(game: GameDefinition, levelId: string): boolean {
  return requestLevelGround(sceneryWithRunout(levelOf(game, levelId)));
}

/**
 * Starts preparing level `levelId` in the background, if it is one (P13-R03): its ground and its
 * scenery textures, while the player is still choosing it. Nothing without a background loader.
 */
export function prefetchLevel(
  game: GameDefinition<GameView>,
  levelId: string | null,
  loader: BackgroundLoader | undefined,
): void {
  const level = levelId === null ? undefined : findGameLevel(game.gameLevels, levelId);
  if (!loader || !level) return;
  requestLevelGround(sceneryWithRunout(level));
  const look = game.view.scenery.looks[level.scenery.id];
  if (look) loader.prefetchTextures(sceneryTextureJobs(look, level.scenery.seed));
}

/** Seconds the level select highlight rests on a level before it is prefetched. */
const PREFETCH_AFTER = 0.25;

/**
 * Prefetches the level highlighted on the level select screen once the highlight rests on it
 * (P13-R03), so that moving across the grid does not queue every level passed over.
 */
export class LevelPrefetcher {
  #highlighted: string | null = null;
  #rest = 0;
  #done = new Set<string>();

  constructor(
    private readonly game: GameDefinition<GameView>,
    private readonly loader: BackgroundLoader | undefined,
  ) {}

  /** `dt` seconds later, with `levelId` highlighted (null: no level select shown). */
  update(dt: number, levelId: string | null): void {
    if (levelId !== this.#highlighted) {
      this.#highlighted = levelId;
      this.#rest = 0;
    }
    this.#rest += dt;
    if (levelId === null || this.#rest < PREFETCH_AFTER || this.#done.has(levelId)) return;
    this.#done.add(levelId);
    prefetchLevel(this.game, levelId, this.loader);
  }

  /** The level the highlight has rested on for `seconds` (at least until prefetched), if any. */
  restedOn(seconds: number): string | null {
    return this.#rest >= Math.max(seconds, PREFETCH_AFTER) ? this.#highlighted : null;
  }

  /** The level being started now is prefetched at once, if it is not yet. */
  start(levelId: string): void {
    if (this.#done.has(levelId)) return;
    this.#done.add(levelId);
    prefetchLevel(this.game, levelId, this.loader);
  }
}
