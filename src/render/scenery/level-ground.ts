import { HeightField } from '../../core/scenery/height-field';
import { PropPlacer } from '../../core/scenery/prop-placement';
import { levelRoads, type RoadNetwork } from '../../core/scenery/road-network';
import type { SceneryLevel } from '../../core/scenery/scenery-level';

/** A level's generated ground: its height field and its props' placer (with the roads). */
interface LevelGround {
  readonly level: SceneryLevel;
  readonly seed: number;
  readonly field: HeightField;
  readonly placer: PropPlacer;
}

/**
 * The ground generated last (P13-R03): starting the same level again (Retry, Continue, the next
 * attempt) reuses it instead of generating it again. Generation is deterministic, so the ground
 * is the same either way.
 */
let lastGround: LevelGround | undefined;

/**
 * Generates the ground of `level` (or finds it generated last), so a {@link SceneryStage} built
 * next for it starts straight away: a level's loading can do it as a step of its own (P13-R03).
 */
export function prepareLevelGround(level: SceneryLevel, seed = level.seed): void {
  levelGround(level, seed);
}

/** The roads made last, by {@link prepareLevelRoads}, for the ground made next. */
let lastRoads:
  { level: SceneryLevel; seed: number; field: HeightField; roads: RoadNetwork } | undefined;

/** The first half of {@link prepareLevelGround}: the level's roads (P13-R03). */
export function prepareLevelRoads(level: SceneryLevel, seed = level.seed): void {
  if (lastGround?.level === level && lastGround.seed === seed) return;
  if (lastRoads?.level === level && lastRoads.seed === seed) return;
  const field = new HeightField(level, seed);
  lastRoads = { level, seed, field, roads: levelRoads(field, level.roads, seed) };
}

/** The roads made by {@link prepareLevelRoads} for `level` and `seed`, now taken. */
function takeRoads(level: SceneryLevel, seed: number): { field: HeightField; roads: RoadNetwork } {
  prepareLevelRoads(level, seed);
  const made = lastRoads;
  lastRoads = undefined;
  if (made?.level === level && made.seed === seed) return made;
  const field = new HeightField(level, seed);
  return { field, roads: levelRoads(field, level.roads, seed) };
}

/** The ground of `level` from `seed`: the one generated last when it is the same. */
export function levelGround(level: SceneryLevel, seed: number): LevelGround {
  if (lastGround?.level === level && lastGround.seed === seed) return lastGround;
  const { field, roads } = takeRoads(level, seed);
  const placer = new PropPlacer(field, level.props, seed, roads, level.sea?.level);
  lastGround = { level, seed, field, placer };
  return lastGround;
}
