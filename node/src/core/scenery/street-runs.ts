// The straight runs of the street grids' built links (phase 4 review), split out of
// `street-grid.ts`.

/** A point of the street network. */
interface GridNode {
  readonly x: number;
  readonly z: number;
}

/** A built stretch of street between two neighbouring crossings. */
interface GridLink {
  readonly a: GridNode;
  readonly b: GridNode;
  readonly across: boolean;
}

const key = (n: GridNode): string => `${n.x.toFixed(3)},${n.z.toFixed(3)}`;

/** Whether `a` and `b` are the same node: mostly the same object (`street-links.ts`). */
const same = (a: GridNode, b: GridNode): boolean => a === b || key(a) === key(b);

/** Maximal straight runs of the built links `links`, as points every `step`. */
export function straightRuns(
  links: readonly GridLink[],
  step: number,
): { x: number; z: number }[][] {
  const runs: { x: number; z: number }[][] = [];
  const lines = new Map<string, GridLink[]>();
  for (const l of links) {
    const line = l.across ? `z${l.a.z.toFixed(3)}` : `x${l.a.x.toFixed(3)}`;
    // Reviewer, 2026-10-28: added to the line's list, not copied into a new one each time.
    const list = lines.get(line);
    if (list) list.push(l);
    else lines.set(line, [l]);
  }
  for (const line of lines.values()) {
    const along = (n: GridNode): number => (line[0]?.across ? n.x : n.z);
    line.sort((p, q) => along(p.a) - along(q.a));
    let run: GridNode[] = [];
    for (const l of line) {
      const last = run.at(-1);
      if (last && same(last, l.a)) run.push(l.b);
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
function resample(run: readonly GridNode[], step: number): { x: number; z: number }[] {
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
