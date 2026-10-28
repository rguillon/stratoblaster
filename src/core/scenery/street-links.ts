// The nodes and links of a district's street grid (phase 4 review), split out of
// `street-grid.ts`.

/**
 * A point of the street network: one object per place (to within 0.001), numbered in the order
 * it is first used (reviewer, 2026-10-28: numbers, not text keys, in the dead-end removal).
 */
export interface Node {
  readonly x: number;
  readonly z: number;
  /** Order of first use, the order dead ends are fixed in; -1 until used. */
  id: number;
}

/** Nodes of a district are numbered below this, so a pair of them makes one number. */
const NODE_LIMIT = 2 ** 21;

const key = (x: number, z: number): string => `${x.toFixed(3)},${z.toFixed(3)}`;

/** One number for the link from `a` to `b`. */
export const pair = (a: Node, b: Node): number => a.id * NODE_LIMIT + b.id;

/** The nodes of a district, each place made once. */
export class Nodes {
  readonly #byPlace = new Map<string, Node>();
  /** Whether each node's ground is buildable, asked once per node (reviewer, 2026-10-28). */
  readonly #grounds = new Map<Node, boolean>();
  /** The nodes used, by number. */
  readonly used: Node[] = [];

  constructor(private readonly buildable: (x: number, z: number) => boolean) {}

  /** The node at (`x`, `z`). */
  at(x: number, z: number): Node {
    const k = key(x, z);
    let node = this.#byPlace.get(k);
    if (!node) {
      node = { x, z, id: -1 };
      this.#byPlace.set(k, node);
    }
    return node;
  }

  /** `node`, numbered if it was not used yet. */
  use(node: Node): Node {
    if (node.id < 0) {
      node.id = this.used.length;
      this.used.push(node);
    }
    return node;
  }

  /** Whether a street can be built on the ground at `node`. */
  ground(node: Node): boolean {
    let ground = this.#grounds.get(node);
    if (ground === undefined) {
      ground = this.buildable(node.x, node.z);
      this.#grounds.set(node, ground);
    }
    return ground;
  }
}

/** A stretch of street between two neighbouring crossings. */
export interface Link {
  readonly a: Node;
  readonly b: Node;
  readonly across: boolean;
  /** Links on a district or section boundary are always built (if their ground allows). */
  readonly required: boolean;
  /** On a boulevard's line: always built, and never cut to undo a crossing. */
  readonly boulevard: boolean;
  /** Whether a street can be built on the ground there. */
  readonly ground: boolean;
  built: boolean;
  /**
   * Cut back while removing dead ends: with `tees`, never built again, so a street cannot keep
   * going on and being cut back.
   */
  cut: boolean;
}

/** Drops links laid twice (the shared boundary rows), keeping the first. */
export function dedupe(links: Link[]): Link[] {
  const seen = new Set<number>();
  return links.filter((l) => {
    const k = pair(l.a, l.b);
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

/** The links at each of the `count` nodes, by node number. */
export type LinksAt = readonly (readonly Link[])[];

export function linksByNode(links: readonly Link[], count: number): LinksAt {
  const at = Array.from({ length: count }, (): Link[] => []);
  for (const l of links) for (const n of [l.a, l.b]) at[n.id]?.push(l);
  return at;
}
