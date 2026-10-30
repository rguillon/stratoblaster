// The towers of the city blocks (phase 4 review), split out of `prop-placement.ts`.
import type { Building } from './away-placement';
import type { PropGroupRule } from './scenery-level';
import type { Block } from './street-grid';

/** Gap between a tower and the edge of its part of the podium roof. */
const TOWER_MARGIN = 1;
/** Towers are drawn among the kinds at least this share of the largest one that fits. */
const LARGEST_SHARE = 0.75;

/** The largest kind of `groups` that fits `part`, standing at `y`, with the ground it takes. */
export function towerIn(
  part: Block,
  groups: readonly PropGroupRule[],
  y: number,
  r: number,
): Building | undefined {
  const half = Math.min(part.xMax - part.xMin, part.zMax - part.zMin) / 2 - TOWER_MARGIN;
  const fitting = groups
    .flatMap((g) => g.kinds)
    .map((kind) => ({
      kind,
      scale: Math.min(kind.scale[1], half / (kind.frontage ?? kind.footprint / kind.scale[1])),
    }))
    .filter(({ kind, scale }) => scale >= kind.scale[0]);
  const largest = Math.max(
    ...fitting.map(({ kind, scale }) => (kind.frontage ?? kind.footprint) * scale),
  );
  const choices = fitting.filter(
    ({ kind, scale }) => (kind.frontage ?? kind.footprint) * scale >= largest * LARGEST_SHARE,
  );
  const choice = choices[Math.floor(r * choices.length)];
  if (!choice) return undefined;
  // Shifted within the room its part leaves around it, so towers do not line up (review).
  const size = (choice.kind.frontage ?? choice.kind.footprint) * choice.scale;
  const shift = (min: number, max: number, t: number): number =>
    (min + max) / 2 + (t - 0.5) * Math.max(0, max - min - 2 * (size + TOWER_MARGIN));
  const placement = {
    kind: choice.kind.id,
    x: shift(part.xMin, part.xMax, (r * 31) % 1),
    y,
    z: shift(part.zMin, part.zMax, (r * 57) % 1),
    rotation: (Math.floor(r * 4 * 7919) % 4) * (Math.PI / 2),
    scale: choice.scale,
  };
  return { placement, halfX: size, halfZ: size };
}
