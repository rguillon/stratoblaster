// The dead ends and crossings of a district's street grid, fixed (phase 4 review, phase 6
// review), split out of `street-grid.ts`.
import { MinHeap } from '../math/min-heap';
import type { Random } from '../math/rng';
import type { LinksAt, Link, Node } from './street-links';

/** Most passes of the dead-end removal (each pass can extend or cut every dead end by a link). */
const MAX_PASSES = 500;

const SIDES = ['left', 'right', 'down', 'up'] as const;

/** The side of `node` that `link` leaves it by, as an index of {@link SIDES}. */
function sideOf(node: Node, link: Link): number {
  const [self, other] = link.a === node ? [link.a, link.b] : [link.b, link.a];
  if (link.across) return other.x < self.x ? 0 : 1;
  return other.z < self.z ? 2 : 3;
}

/** Whether built streets (and `extra`, if given) leave `node` on all four sides. */
function isCrossing(node: Node, around: readonly Link[] | undefined, extra?: Link): boolean {
  let sides = 0;
  for (const l of around ?? []) if (l.built || l === extra) sides |= 1 << sideOf(node, l);
  return sides === 0b1111;
}

/** Whether building `link`, from `node`, would make a crossing at its far end. */
function makesCrossing(link: Link, node: Node, at: LinksAt): boolean {
  const far = link.a === node ? link.b : link.a;
  return isCrossing(far, at[far.id], link);
}

/**
 * Fixes `node` if a single built street ends there on screen: the street goes on straight when
 * the next link's ground allows it (and, with `tees`, its far end is no T-junction it would turn
 * into a crossing, nor was cut back before), else it is cut back. Returns the link it changed.
 */
function fixDeadEnd(
  node: Node,
  at: LinksAt,
  outOfView: (node: Node) => boolean,
  tees: boolean,
): Link | undefined {
  const around = at[node.id] ?? [];
  let only: Link | undefined;
  let built = 0;
  for (const l of around) {
    if (!l.built) continue;
    built++;
    only ??= l;
  }
  if (built !== 1 || !only || outOfView(node)) return undefined;
  const ahead = around.find((l) => l !== only && l.across === only.across);
  if (ahead && mayGoOn(ahead, node, at, tees)) {
    ahead.built = true;
    return ahead;
  }
  only.built = false;
  only.cut = true;
  return only;
}

/** Whether a dead end at `node` may go on through `ahead` (see {@link fixDeadEnd}). */
function mayGoOn(ahead: Link, node: Node, at: LinksAt, tees: boolean): boolean {
  return ahead.ground && !(tees && (ahead.cut || makesCrossing(ahead, node, at)));
}

/**
 * Fixes the dead ends, pass after pass over the nodes in order, until a pass changes nothing.
 * Reviewer, 2026-10-28: a pass only looks at the nodes whose links changed since they were last
 * looked at (those it would have fixed); the others would be left as they are. Same passes, same
 * fixes in the same order, without going through every node each time.
 */
export function removeDeadEnds(
  at: LinksAt,
  nodes: readonly Node[],
  outOfView: (node: Node) => boolean,
  tees: boolean,
): void {
  const passes = new Passes(nodes.length);
  for (let pass = 0; pass < MAX_PASSES; pass++) {
    let changed = false;
    for (let id = passes.take(); id !== undefined; id = passes.take()) {
      const node = nodes[id];
      const link = node && fixDeadEnd(node, at, outOfView, tees);
      if (!link) continue;
      changed = true;
      passes.again(link.a.id, id);
      passes.again(link.b.id, id);
    }
    if (!changed) return;
    passes.turn();
  }
}

/** The nodes a pass of the dead-end removal still looks at, in order, and those of the next. */
class Passes {
  #now: MinHeap;
  #next: number[] = [];
  readonly #inNow: Uint8Array;
  readonly #inNext: Uint8Array;

  /** The first pass looks at all `count` nodes. */
  constructor(count: number) {
    this.#now = new MinHeap(Array.from({ length: count }, (_, id) => id));
    this.#inNow = new Uint8Array(count).fill(1);
    this.#inNext = new Uint8Array(count);
  }

  /** The next node this pass looks at, if any. */
  take(): number | undefined {
    const id = this.#now.pop();
    if (id !== undefined) this.#inNow[id] = 0;
    return id;
  }

  /** Looks at node `id` again: later in this pass if it comes after `current`, else in the next. */
  again(id: number, current: number): void {
    if (id > current && !this.#inNow[id]) {
      this.#inNow[id] = 1;
      this.#now.push(id);
    } else if (id <= current && !this.#inNext[id]) {
      this.#inNext[id] = 1;
      this.#next.push(id);
    }
  }

  /** Starts the next pass. */
  turn(): void {
    const next = this.#next.sort((p, q) => p - q);
    for (const id of next) [this.#inNext[id], this.#inNow[id]] = [0, 1];
    this.#now = new MinHeap(next);
    this.#next = [];
  }
}

/**
 * The side of a crossing whose street goes: up or down the level, or left or right where a
 * boulevard runs along the level, so it keeps going straight. None where two boulevards cross.
 */
function sideToCut(around: readonly Link[], random: Random): (typeof SIDES)[number] | undefined {
  const along = around.some((l) => !l.across && l.boulevard);
  const across = around.some((l) => l.across && l.boulevard);
  if (along && across) return undefined;
  const coin = random() < 0.5;
  if (along) return coin ? 'left' : 'right';
  return coin ? 'down' : 'up';
}

/**
 * Turns every crossing into a T-junction (see `streetRuns`): the streets leaving it up or
 * down the level go. Cutting makes no crossing, nor does fixing the dead ends that leaves with
 * `tees`, so one pass is enough.
 */
export function removeCrossings(
  at: LinksAt,
  nodes: readonly Node[],
  outOfView: (node: Node) => boolean,
  random: Random,
): void {
  for (const node of nodes) {
    const around = at[node.id] ?? [];
    if (!isCrossing(node, around)) continue;
    const side = sideToCut(around, random);
    for (const l of around) {
      if (side && l.built && SIDES[sideOf(node, l)] === side) l.built = false;
    }
  }
  removeDeadEnds(at, nodes, outOfView, true);
}
