import { randomIn, type Random } from '../math/rng';
import type { PlacedSection, RoadRules, StreetGrid } from './scenery-level';

/** A run of consecutive sections with street grids (phase 4 review). */
export interface District {
  readonly zMin: number;
  zMax: number;
  readonly parts: { readonly grid: StreetGrid; readonly zMin: number; readonly zMax: number }[];
}

/** A point of the street network. */
interface Node {
  readonly x: number;
  readonly z: number;
}

/** A stretch of street between two neighbouring crossings. */
interface Link {
  readonly a: Node;
  readonly b: Node;
  readonly across: boolean;
  /** Links on a district or section boundary are always built (if their ground allows). */
  readonly required: boolean;
  /** Whether a street can be built on the ground there. */
  readonly ground: boolean;
  built: boolean;
}

/** Most passes of the dead-end removal (each pass can extend or cut every dead end by a link). */
const MAX_PASSES = 500;

/**
 * Runs of consecutive sections with a street grid. Districts at the ends of the level go on
 * past them (to `range`), out of view.
 */
export function findDistricts(
  sections: readonly PlacedSection[],
  range: { readonly zMin: number; readonly zMax: number },
): District[] {
  const districts: District[] = [];
  sections.forEach((placed, i) => {
    const grid = placed.section.streets;
    if (!grid) return;
    const zMin = i === 0 ? range.zMin : placed.start;
    const zMax = i === sections.length - 1 ? range.zMax : placed.end;
    const previous = districts.at(-1);
    if (previous && sections[i - 1]?.section.streets) {
      previous.parts.push({ grid, zMin, zMax });
      previous.zMax = zMax;
    } else {
      districts.push({ zMin, zMax, parts: [{ grid, zMin, zMax }] });
    }
  });
  return districts;
}

/** Positions from `from` to `to`, spaced by random gaps in `gap`, both ends included. */
function spaced(
  from: number,
  to: number,
  gap: readonly [number, number],
  random: Random,
): number[] {
  const out = [from];
  for (let v = from + randomIn(random, gap); v < to - gap[0] / 2; v += randomIn(random, gap)) {
    out.push(v);
  }
  out.push(to);
  return out;
}

const key = (n: Node): string => `${n.x.toFixed(3)},${n.z.toFixed(3)}`;

/**
 * The straight streets of a district (phase 4 review), as maximal straight runs of built links,
 * each a list of points every `rules.step`:
 * - every section of the district has its own random columns, from past one screen edge to past
 *   the other, and rows; its first and last rows are full streets, so the columns of two sections
 *   meet them at T-junctions;
 * - each other link is built with the chance `links`, if its ground is buildable;
 * - then dead ends on screen are removed: a street that stops at a crossing goes on straight, or
 *   is cut back, until every street ends at a crossing, a junction, or off the screen.
 */
export function streetRuns(
  district: District,
  rules: RoadRules,
  random: Random,
  buildable: (x: number, z: number) => boolean,
  outOfView: (node: Node) => boolean,
): { x: number; z: number }[][] {
  const links = gridLinks(district, rules, random, buildable);
  removeDeadEnds(links, outOfView);
  return straightRuns(links, rules.step);
}

function gridLinks(
  district: District,
  rules: RoadRules,
  random: Random,
  buildable: (x: number, z: number) => boolean,
): Link[] {
  const edge = rules.offscreenX + rules.step;
  const links: Link[] = [];
  const add = (a: Node, b: Node, across: boolean, required: boolean): void => {
    const mid = { x: (a.x + b.x) / 2, z: (a.z + b.z) / 2 };
    const ground = [a, mid, b].every((p) => buildable(p.x, p.z));
    const built = ground && (required || random() < chance);
    links.push({ a, b, across, required, ground, built });
  };
  let chance = 0;
  const columnsOf: number[][] = [];
  district.parts.forEach((part, p) => {
    chance = part.grid.links;
    const xs = spaced(-edge, edge, part.grid.columns, random);
    columnsOf.push(xs);
    const zs = spaced(part.zMin, part.zMax, part.grid.rows, random);
    zs.forEach((z, r) => {
      const boundary = r === 0 || r === zs.length - 1;
      // A boundary row shared with the previous section was already laid with its columns.
      const columns = r === 0 && p > 0 ? mergeColumns(columnsOf[p - 1] ?? [], xs) : xs;
      columns.slice(1).forEach((x, c) => {
        add({ x: columns[c] ?? x, z }, { x, z }, true, boundary);
      });
    });
    for (const x of xs) {
      zs.slice(1).forEach((z, r) => {
        add({ x, z: zs[r] ?? z }, { x, z }, false, false);
      });
    }
  });
  return dedupe(links);
}

function mergeColumns(a: readonly number[], b: readonly number[]): number[] {
  return [...new Set([...a, ...b])].sort((x, y) => x - y);
}

/** Drops links laid twice (the shared boundary rows), keeping the first. */
function dedupe(links: Link[]): Link[] {
  const seen = new Set<string>();
  return links.filter((l) => {
    const k = `${key(l.a)}>${key(l.b)}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

/** The links at each node. */
function linksByNode(links: readonly Link[]): Map<string, Link[]> {
  const at = new Map<string, Link[]>();
  for (const l of links) {
    for (const n of [l.a, l.b]) {
      const around = at.get(key(n));
      if (around) around.push(l);
      else at.set(key(n), [l]);
    }
  }
  return at;
}

/**
 * Fixes the node `k` if a single built street ends there on screen: the street goes on straight
 * when the next link's ground allows it, else it is cut back. Returns whether anything changed.
 */
function fixDeadEnd(
  k: string,
  around: readonly Link[],
  outOfView: (node: Node) => boolean,
): boolean {
  const built = around.filter((l) => l.built);
  const only = built[0];
  if (built.length !== 1 || !only || outOfView(key(only.a) === k ? only.a : only.b)) return false;
  const ahead = around.find((l) => l !== only && l.across === only.across);
  if (ahead?.ground) ahead.built = true;
  else only.built = false;
  return true;
}

function removeDeadEnds(links: Link[], outOfView: (node: Node) => boolean): void {
  const at = linksByNode(links);
  for (let pass = 0; pass < MAX_PASSES; pass++) {
    let changed = false;
    for (const [k, around] of at) changed = fixDeadEnd(k, around, outOfView) || changed;
    if (!changed) return;
  }
}

/** Maximal straight runs of built links, as points every `step`. */
function straightRuns(links: readonly Link[], step: number): { x: number; z: number }[][] {
  const runs: { x: number; z: number }[][] = [];
  const lines = new Map<string, Link[]>();
  for (const l of links.filter((link) => link.built)) {
    const line = l.across ? `z${l.a.z.toFixed(3)}` : `x${l.a.x.toFixed(3)}`;
    lines.set(line, [...(lines.get(line) ?? []), l]);
  }
  for (const line of lines.values()) {
    const along = (n: Node): number => (line[0]?.across ? n.x : n.z);
    line.sort((p, q) => along(p.a) - along(q.a));
    let run: Node[] = [];
    for (const l of line) {
      const last = run.at(-1);
      if (last && key(last) === key(l.a)) run.push(l.b);
      else {
        if (run.length > 1) runs.push(resample(run, step));
        run = [l.a, l.b];
      }
    }
    if (run.length > 1) runs.push(resample(run, step));
  }
  return runs;
}

/** Points every about `step` from the first to the last node of a straight run. */
function resample(run: readonly Node[], step: number): { x: number; z: number }[] {
  const first = run[0];
  const last = run.at(-1);
  if (!first || !last) return [];
  const length = Math.hypot(last.x - first.x, last.z - first.z);
  const count = Math.max(1, Math.round(length / step));
  return Array.from({ length: count + 1 }, (_, i) => ({
    x: first.x + ((last.x - first.x) * i) / count,
    z: first.z + ((last.z - first.z) * i) / count,
  }));
}
