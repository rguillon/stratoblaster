import { randomIn, type Random } from '../math/rng';
import { isBoulevard, runWidth, streetWidth } from './lanes';
import type { District } from './districts';
import { removeCrossings, removeDeadEnds } from './street-dead-ends';
import { dedupe, linksByNode, Nodes, pair, type Link, type Node } from './street-links';
import { straightRuns } from './street-runs';
import type { RoadRules } from './scenery-level';
import { tileStreetRuns, type StreetRun } from './tile-streets';

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

/**
 * The straight streets of a district (phase 4 review), as maximal straight runs of built links,
 * each a list of points every `rules.step`:
 * - every section of the district has its own random columns, from past one screen edge to past
 *   the other, and rows; its first and last rows are full streets, so the columns of two sections
 *   meet them at T-junctions;
 * - each other link is built with the chance `links`, if its ground is buildable;
 * - then dead ends on screen are removed: a street that stops at a crossing goes on straight, or
 *   is cut back, until every street ends at a crossing, a junction, or off the screen;
 * - without crossings (`rules.noCrossings`, phase 6 review), every crossing then becomes a
 *   T-junction: one of its two stretches along the level goes, and the dead ends that leaves are
 *   removed again, without making new crossings;
 * - boulevards (`rules.boulevards`, reviewer 2026-10-28) are built along their whole line and run
 *   straight: at a crossing, the street across them is cut instead.
 */
export function streetRuns(
  district: District,
  rules: RoadRules,
  random: Random,
  buildable: (x: number, z: number) => boolean,
  outOfView: (node: Node) => boolean,
): { runs: StreetRun[]; blocks: Block[] } {
  // Phase 15: on a grid of tiles.
  if (rules.tiles)
    return tileStreetRuns(district, rules, rules.tiles, random, buildable, outOfView);
  const { links, layouts, nodes } = gridLinks(district, rules, random, buildable);
  const at = linksByNode(links, nodes.length);
  removeDeadEnds(at, nodes, outOfView, false);
  if (rules.noCrossings) removeCrossings(at, nodes, outOfView, random);
  const inset = (coord: number): number => streetWidth(rules, coord) / 2 + BLOCK_KERB;
  const blocks = gridBlocks(layouts, links, inset).filter((b) =>
    buildable((b.xMin + b.xMax) / 2, (b.zMin + b.zMax) / 2),
  );
  return {
    runs: straightRuns(
      links.filter((l) => l.built),
      rules.step,
    ).map((points) => ({ points, width: runWidth(rules, points) })),
    blocks,
  };
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

/** The nodes of one section of a district, by row and column. */
interface Layout {
  readonly grid: readonly (readonly Node[])[];
  /** Its first row was laid before it (by the section, or the district, before it). */
  readonly laidBefore: boolean;
}

/** The corners of cell (`c`, `r`) of `grid`: bottom left, bottom right, top left, top right. */
function corners(grid: Layout['grid'], c: number, r: number): [Node, Node, Node, Node] | undefined {
  const [n00, n10, n01, n11] = [
    grid[r]?.[c],
    grid[r]?.[c + 1],
    grid[r + 1]?.[c],
    grid[r + 1]?.[c + 1],
  ];
  return n00 && n10 && n01 && n11 ? [n00, n10, n01, n11] : undefined;
}

function gridBlocks(
  layouts: readonly Layout[],
  links: readonly Link[],
  inset: (coord: number) => number,
): Block[] {
  const built = new Set(links.filter((l) => l.built).map((l) => pair(l.a, l.b)));
  const has = (a: Node, b: Node): boolean => built.has(pair(a, b));
  const blocks: Block[] = [];
  for (const { grid, laidBefore } of layouts) {
    for (let r = 0; r + 1 < grid.length; r++) {
      for (let c = 0; c + 1 < (grid[r]?.length ?? 0); c++) {
        const cell = corners(grid, c, r);
        // The first row of a later section was laid on the merged columns (or, going on from
        // another district, with it): it is a full street.
        const block = cell && cellBlock(cell, has, r === 0 && laidBefore, inset);
        if (block) blocks.push(block);
      }
    }
  }
  return blocks;
}

/**
 * The block of a cell, up to the edge of the street along each side it has (avenues are wider);
 * `bottom` when its first row is known to be a street.
 */
function cellBlock(
  [n00, n10, n01, n11]: readonly [Node, Node, Node, Node],
  has: (a: Node, b: Node) => boolean,
  bottom: boolean,
  inset: (coord: number) => number,
): Block | undefined {
  const [x0, x1, z0, z1] = [n00.x, n11.x, n00.z, n11.z];
  const cut = (side: boolean, coord: number): number => (side ? inset(coord) : 0);
  const block = {
    xMin: x0 + cut(has(n00, n01), x0),
    xMax: x1 - cut(has(n10, n11), x1),
    zMin: z0 + cut(bottom || has(n00, n10), z0),
    zMax: z1 - cut(has(n01, n11), z1),
  };
  return block.xMax > block.xMin && block.zMax > block.zMin ? block : undefined;
}

function gridLinks(
  district: District,
  rules: RoadRules,
  random: Random,
  buildable: (x: number, z: number) => boolean,
): { links: Link[]; layouts: Layout[]; nodes: readonly Node[] } {
  const edge = rules.offscreenX + rules.step;
  const links: Link[] = [];
  const nodes = new Nodes(buildable);
  const add = (
    [ax, az]: readonly [number, number],
    [bx, bz]: readonly [number, number],
    across: boolean,
    required: boolean,
  ): void => {
    const [a, b] = [nodes.use(nodes.at(ax, az)), nodes.use(nodes.at(bx, bz))];
    const ground = nodes.ground(a) && buildable((ax + bx) / 2, (az + bz) / 2) && nodes.ground(b);
    const boulevard = isBoulevard(rules, streetWidth(rules, across ? az : ax));
    const built = ground && (required || boulevard || random() < chance);
    links.push({ a, b, across, required, boulevard, ground, built, cut: false });
  };
  let chance = 0;
  const columnsOf: number[][] = [];
  const layouts: Layout[] = [];
  district.parts.forEach((part, p) => {
    chance = part.grid.links;
    const xs = spaced(-edge, edge, part.grid.columns, random);
    columnsOf.push(xs);
    const zs = spaced(part.zMin, part.zMax, part.grid.rows, random);
    const goesOn = p === 0 && district.continues === true;
    const grid = zs.map((z) => xs.map((x) => nodes.at(x, z)));
    layouts.push({ grid, laidBefore: p > 0 || goesOn });
    zs.forEach((z, r) => {
      // Going on from another district: its first row was laid with it.
      if (r === 0 && goesOn) return;
      const boundary = r === 0 || r === zs.length - 1;
      // A boundary row shared with the previous section was already laid with its columns.
      const columns = r === 0 && p > 0 ? mergeColumns(columnsOf[p - 1] ?? [], xs) : xs;
      columns.slice(1).forEach((x, c) => {
        add([columns[c] ?? x, z], [x, z], true, boundary);
      });
    });
    for (const x of xs) {
      zs.slice(1).forEach((z, r) => {
        add([x, zs[r] ?? z], [x, z], false, false);
      });
    }
  });
  return { links: dedupe(links), layouts, nodes: nodes.used };
}

function mergeColumns(a: readonly number[], b: readonly number[]): number[] {
  return [...new Set([...a, ...b])].sort((x, y) => x - y);
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
