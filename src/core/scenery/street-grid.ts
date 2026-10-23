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
): { runs: { x: number; z: number }[][]; blocks: Block[] } {
  const { links, layouts } = gridLinks(district, rules, random, buildable);
  removeDeadEnds(links, outOfView);
  const blocks = gridBlocks(layouts, links, rules.mainWidth / 2 + BLOCK_KERB).filter((b) =>
    buildable((b.xMin + b.xMax) / 2, (b.zMin + b.zMax) / 2),
  );
  return { runs: straightRuns(links, rules.step), blocks };
}

/**
 * A city block: the ground between the streets around one cell of a district's grid, up to
 * `BLOCK_KERB` from the street edges. On a side without a street, it goes to the middle of the
 * missing street, so it meets the next block (phase 4 review).
 */
export interface Block {
  readonly xMin: number;
  readonly xMax: number;
  readonly zMin: number;
  readonly zMax: number;
}

/** Gap between a street's edge and the block beside it. */
const BLOCK_KERB = 0.5;

/** Columns and rows of one section of a district. */
interface Layout {
  readonly xs: readonly number[];
  readonly zs: readonly number[];
}

const linkKey = (a: Node, b: Node): string => `${key(a)}>${key(b)}`;

/** X and Z bounds of cell (`c`, `r`) of a layout. */
function cellBounds(
  xs: readonly number[],
  zs: readonly number[],
  c: number,
  r: number,
): [number, number, number, number] {
  return [xs[c] ?? 0, xs[c + 1] ?? 0, zs[r] ?? 0, zs[r + 1] ?? 0];
}

function gridBlocks(layouts: readonly Layout[], links: readonly Link[], inset: number): Block[] {
  const built = new Set(links.filter((l) => l.built).map((l) => linkKey(l.a, l.b)));
  const has = (a: Node, b: Node): boolean => built.has(linkKey(a, b));
  const blocks: Block[] = [];
  layouts.forEach(({ xs, zs }, p) => {
    for (let r = 0; r + 1 < zs.length; r++) {
      for (let c = 0; c + 1 < xs.length; c++) {
        const [x0, x1, z0, z1] = cellBounds(xs, zs, c, r);
        // The first row of a later section was laid on the merged columns: it is a full street.
        const bottom = (r === 0 && p > 0) || has({ x: x0, z: z0 }, { x: x1, z: z0 });
        const top = has({ x: x0, z: z1 }, { x: x1, z: z1 });
        const left = has({ x: x0, z: z0 }, { x: x0, z: z1 });
        const right = has({ x: x1, z: z0 }, { x: x1, z: z1 });
        const cut = (side: boolean): number => (side ? inset : 0);
        const block = {
          xMin: x0 + cut(left),
          xMax: x1 - cut(right),
          zMin: z0 + cut(bottom),
          zMax: z1 - cut(top),
        };
        if (block.xMax > block.xMin && block.zMax > block.zMin) blocks.push(block);
      }
    }
  });
  return blocks;
}

function gridLinks(
  district: District,
  rules: RoadRules,
  random: Random,
  buildable: (x: number, z: number) => boolean,
): { links: Link[]; layouts: Layout[] } {
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
  const layouts: Layout[] = [];
  district.parts.forEach((part, p) => {
    chance = part.grid.links;
    const xs = spaced(-edge, edge, part.grid.columns, random);
    columnsOf.push(xs);
    const zs = spaced(part.zMin, part.zMax, part.grid.rows, random);
    layouts.push({ xs, zs });
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
  return { links: dedupe(links), layouts };
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

/** `block` cut into `nx × nz` equal parts. */
export function blockParts(block: Block, nx: number, nz: number): Block[] {
  const w = (block.xMax - block.xMin) / nx;
  const d = (block.zMax - block.zMin) / nz;
  const parts: Block[] = [];
  for (let i = 0; i < nx; i++) {
    for (let j = 0; j < nz; j++) {
      const xMin = block.xMin + i * w;
      const zMin = block.zMin + j * d;
      parts.push({ xMin, xMax: xMin + w, zMin, zMax: zMin + d });
    }
  }
  return parts;
}
