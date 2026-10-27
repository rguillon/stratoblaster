import { HeightField } from '../../core/scenery/height-field';
import { PropPlacer, type PlacerSnapshot } from '../../core/scenery/prop-placement';
import { levelRoads, type RoadSnapshot } from '../../core/scenery/road-network';
import type { SceneryLevel } from '../../core/scenery/scenery-level';

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

/** Generates the ground of `level` from `seed` as plain data: what the worker runs. */
export function groundSnapshot(level: SceneryLevel, seed: number): GroundSnapshot {
  const { placer } = generate(level, seed);
  return { roads: placer.roads.snapshot(), placer: placer.snapshot() };
}

function generate(level: SceneryLevel, seed: number, made?: GroundSnapshot): LevelGround {
  const field = new HeightField(level, seed);
  const roads = levelRoads(field, level.roads, seed, made?.roads);
  const { props, sea } = level;
  const placer = new PropPlacer(field, props, seed, roads, sea?.level, made?.placer);
  return { level, seed, field, placer };
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

/** Where grounds are generated in the background: posts a level and seed, calls back with it. */
export type GroundGenerator = (
  level: SceneryLevel,
  seed: number,
  done: (made: GroundSnapshot | undefined) => void,
) => void;

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
 * generated there, if not already on its way (false until it comes back); without one, now.
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
  background(level, seed, (made) => {
    pending.splice(pending.indexOf(job), 1);
    // After a failed background generation, the ground is generated here when it is needed.
    if (made) keep(generate(level, seed, made));
    else failed = true;
  });
  return false;
}

/** The ground of `level` from `seed`: kept, or generated now. */
export function levelGround(level: SceneryLevel, seed: number): LevelGround {
  return find(level, seed) ?? keep(generate(level, seed));
}
