import { isAlive, type ShotTarget } from '../entities/shot-target';
import type { BeamLevel } from '../entities/weapon';

/** A straight piece of beam, from `y0` up to `y1`, at a given level (1-based). */
export interface BeamSegment {
  readonly x: number;
  readonly y0: number;
  readonly y1: number;
  readonly level: number;
  readonly width: number;
  /** Whether the segment ends on a target (otherwise it runs to the top). */
  readonly hit: boolean;
}

/** A target the beam touches, with the level of the segment that touches it. */
export interface BeamHit {
  readonly target: ShotTarget;
  readonly level: number;
  readonly y: number;
}

export interface BeamTrace {
  readonly segments: readonly BeamSegment[];
  readonly hits: readonly BeamHit[];
}

/** The lowest living target above `fromY`, not yet hit, that a beam of `width` at `x` touches. */
function firstTargetAbove(
  targets: readonly ShotTarget[],
  x: number,
  fromY: number,
  width: number,
  done: ReadonlySet<ShotTarget>,
): ShotTarget | undefined {
  let best: ShotTarget | undefined;
  for (const target of targets) {
    if (!isAlive(target) || done.has(target) || target.y <= fromY) continue;
    if (Math.abs(target.x - x) > target.radius + width / 2) continue;
    if (!best || target.y < best.y) best = target;
  }
  return best;
}

/**
 * Traces a beam fired straight up from (x, y) at `level` (P03-R02). At level 1 the beam stops
 * at the first target it touches. Above, it goes through the target and continues from it one
 * level lower, so a level-N beam touches at most N targets.
 */
export function traceBeam(
  levels: readonly BeamLevel[],
  level: number,
  x: number,
  y: number,
  top: number,
  targets: readonly ShotTarget[],
): BeamTrace {
  const segments: BeamSegment[] = [];
  const hits: BeamHit[] = [];
  const done = new Set<ShotTarget>();
  let from = y;
  for (let current = level; current >= 1; current--) {
    const width = levels[current - 1]?.width ?? 0;
    const target = firstTargetAbove(targets, x, from, width, done);
    if (!target) {
      segments.push({ x, y0: from, y1: top, level: current, width, hit: false });
      break;
    }
    const contact = Math.max(from, target.y - target.radius);
    segments.push({ x, y0: from, y1: contact, level: current, width, hit: true });
    hits.push({ target, level: current, y: contact });
    done.add(target);
    from = contact;
  }
  return { segments, hits };
}
