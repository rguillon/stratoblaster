import type { Building } from '../../core/scenery/away-placement';
import { HeightField } from '../../core/scenery/height-field';
import { PropPlacer, type PlacerSnapshot } from '../../core/scenery/prop-placement';
import { levelRoads, type Road, type RoadSnapshot } from '../../core/scenery/road-network';
import { runoutStart, type SceneryLevel } from '../../core/scenery/scenery-level';

/** A level's generated ground: its height field and its props' placer (with the roads). */
export interface LevelGround {
  readonly level: SceneryLevel;
  readonly seed: number;
  readonly field: HeightField;
  readonly placer: PropPlacer;
}

/** What generating a level's ground made, as plain data (sent back by a worker, P13-R03). */
export interface GroundSnapshot {
  readonly roads: RoadSnapshot;
  readonly placer: PlacerSnapshot;
}

/**
 * What generating the runout of a level's ground added, as plain data (reviewer, 2026-10-28: the
 * worker sends it after the rest of the ground).
 */
export interface RunoutSnapshot {
  readonly roads: readonly Road[];
  readonly buildings: readonly Building[];
}

/**
 * Generates the ground of `level` from `seed` as plain data, its runout apart: what the worker
 * runs. The ground first, then `runout()` for the rest.
 */
export function generateInTwo(
  level: SceneryLevel,
  seed: number,
): { readonly ground: GroundSnapshot; runout(): RunoutSnapshot } {
  const made = withoutRunout(level, seed);
  const { placer } = made;
  return {
    ground: { roads: placer.roads.snapshot(), placer: placer.snapshot() },
    runout: () => addRunout(made),
  };
}

/** The ground of `level` up to its runout: generated, or from what was made before. */
function withoutRunout(level: SceneryLevel, seed: number, made?: GroundSnapshot): LevelGround {
  const field = new HeightField(level, seed);
  const options = { runoutFrom: runoutStart(level), made: made?.roads };
  const roads = levelRoads(field, level.roads, seed, options);
  const { props, sea } = level;
  const placer = new PropPlacer(field, props, seed, roads, sea?.level, made?.placer);
  return { level, seed, field, placer };
}

/** Adds the runout to `ground`: generated, or what was made before. What it added. */
function addRunout(ground: LevelGround, made?: RunoutSnapshot): RunoutSnapshot {
  const { placer } = ground;
  const roads = placer.roads.addRunout(made?.roads);
  return { roads, buildings: placer.placeRunout(made?.buildings) };
}

/** The whole ground of `level`, generated here. */
function generate(level: SceneryLevel, seed: number): LevelGround {
  const ground = withoutRunout(level, seed);
  addRunout(ground);
  return ground;
}

/** Grounds kept for reuse (P13-R03): the level being played, Retry, and those prefetched. */
const KEPT = 3;
const kept: LevelGround[] = [];

function keep(ground: LevelGround): LevelGround {
  kept.unshift(ground);
  kept.length = Math.min(kept.length, KEPT);
  return ground;
}

function find(level: SceneryLevel, seed: number): LevelGround | undefined {
  const i = kept.findIndex((g) => g.level === level && g.seed === seed);
  const [ground] = i >= 0 ? kept.splice(i, 1) : [];
  return ground && keep(ground);
}

/** What a background generation sends back for a level: its ground, then its runout. */
export interface GroundReplies {
  /** The ground up to the runout, or undefined when the generation failed. */
  ground(made: GroundSnapshot | undefined): void;
  /** Then its runout, or undefined when the generation failed after the ground. */
  runout(made: RunoutSnapshot | undefined): void;
}

/** Where grounds are generated in the background: posts a level and seed, answers `replies`. */
export type GroundGenerator = (level: SceneryLevel, seed: number, replies: GroundReplies) => void;

let background: GroundGenerator | undefined;
/** Set once a background generation failed: the grounds are generated here from then on. */
let failed = false;
/** The grounds being generated in the background. */
const pending: { level: SceneryLevel; seed: number }[] = [];

/** Generates the grounds in the background from now on, with `generator` (P13-R03). */
export function generateGroundsWith(generator: GroundGenerator | undefined): void {
  background = generator;
  failed = false;
}

/**
 * Asks for the ground of `level`: true when it is ready. With a background generator it is
 * generated there, if not already on its way (false until it comes back, its runout after it);
 * without one, now.
 */
export function requestLevelGround(level: SceneryLevel, seed = level.seed): boolean {
  if (find(level, seed)) return true;
  if (!background || failed) {
    keep(generate(level, seed));
    return true;
  }
  if (pending.some((p) => p.level === level && p.seed === seed)) return false;
  const job = { level, seed };
  pending.push(job);
  let ground: LevelGround | undefined;
  background(level, seed, {
    ground: (made) => {
      pending.splice(pending.indexOf(job), 1);
      // After a failed background generation, the ground is generated here when it is needed.
      if (!made) failed = true;
      else if (!find(level, seed)) ground = keep(withoutRunout(level, seed, made));
    },
    // Adds nothing to a ground that has its runout already (one generated here meanwhile); if it
    // failed, the runout is generated here.
    runout: (made) => {
      if (!made) failed = true;
      if (ground) addRunout(ground, made ?? addRunout(withoutRunout(level, seed)));
    },
  });
  return false;
}

/** The ground of `level` from `seed`: kept, or generated now. */
export function levelGround(level: SceneryLevel, seed: number): LevelGround {
  return find(level, seed) ?? keep(generate(level, seed));
}
