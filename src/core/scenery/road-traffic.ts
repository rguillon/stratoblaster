import type { Road } from './road-network';

// Phase 4 review: where streets cross each other (the centre line stops there, and a street
// meeting another goes on under it).

/** A straight street, from its first to its last point. */
export interface StreetLine {
  readonly road: number;
  readonly ax: number;
  readonly az: number;
  readonly bx: number;
  readonly bz: number;
  readonly width: number;
}

/** The streets of `roads` as straight lines (streets are straight, see `streetRuns`). */
export function streetLines(roads: readonly Road[]): StreetLine[] {
  return roads.flatMap((road) => {
    const [a, b] = [road.points[0], road.points.at(-1)];
    if (road.kind !== 'street' || !a || !b) return [];
    return [{ road: road.index, ax: a.x, az: a.z, bx: b.x, bz: b.z, width: road.width }];
  });
}

const linesOf = new WeakMap<readonly Road[], readonly StreetLine[]>();

/** {@link streetLines} of `roads`, made once per list of roads (P13-R04). */
export function cachedStreetLines(roads: readonly Road[]): readonly StreetLine[] {
  let lines = linesOf.get(roads);
  if (!lines) {
    lines = streetLines(roads);
    linesOf.set(roads, lines);
  }
  return lines;
}

const spans = new WeakMap<Road, readonly [number, number]>();

/** The lowest and highest Z of the points of `road`, worked out once (P13-R04). */
export function roadZSpan(road: Road): readonly [number, number] {
  let span = spans.get(road);
  if (!span) {
    let [min, max] = [Infinity, -Infinity];
    for (const p of road.points) [min, max] = [Math.min(min, p.z), Math.max(max, p.z)];
    span = [min, max];
    spans.set(road, span);
  }
  return span;
}

function distance(line: StreetLine, x: number, z: number): number {
  const [dx, dz] = [line.bx - line.ax, line.bz - line.az];
  const t = Math.max(
    0,
    Math.min(1, ((x - line.ax) * dx + (z - line.az) * dz) / (dx * dx + dz * dz || 1)),
  );
  return Math.hypot(line.ax + t * dx - x, line.az + t * dz - z);
}

/** Z length of the buckets of a {@link StreetIndex}. */
const BUCKET = 32;
/** Margin the buckets are widened by around each street: queries reaching further scan them all. */
const BUCKET_REACH = 1;

/**
 * The streets of a list of lines by bands of Z (P13-R04): each band holds the streets within
 * `width / 2 + BUCKET_REACH` of it, so a point only checks the streets near it.
 */
class StreetIndex {
  readonly #bands = new Map<number, StreetLine[]>();
  static readonly #none: readonly StreetLine[] = [];

  constructor(lines: readonly StreetLine[]) {
    for (const line of lines) {
      const reach = line.width / 2 + BUCKET_REACH;
      const first = Math.floor((Math.min(line.az, line.bz) - reach) / BUCKET);
      const last = Math.floor((Math.max(line.az, line.bz) + reach) / BUCKET);
      for (let band = first; band <= last; band++) {
        const list = this.#bands.get(band);
        if (list) list.push(line);
        else this.#bands.set(band, [line]);
      }
    }
  }

  near(z: number): readonly StreetLine[] {
    return this.#bands.get(Math.floor(z / BUCKET)) ?? StreetIndex.#none;
  }
}

const indexes = new WeakMap<readonly StreetLine[], StreetIndex>();

/**
 * The lines that may be within `margin` of the edge of a street at (_, z): those of its band
 * when `margin` is within the bands' reach (the same answers as all of them, faster), all of
 * them otherwise. The index of `lines` is built on the first query and kept with them.
 */
function linesNear(lines: readonly StreetLine[], z: number, margin: number): readonly StreetLine[] {
  if (margin > BUCKET_REACH) return lines;
  let index = indexes.get(lines);
  if (!index) {
    index = new StreetIndex(lines);
    indexes.set(lines, index);
  }
  return index.near(z);
}

/** Whether (x, z) of street `road` is within `margin` of the edge of another street. */
export function inCrossing(
  lines: readonly StreetLine[],
  road: number,
  x: number,
  z: number,
  margin: number,
): boolean {
  return linesNear(lines, z, margin).some(
    (l) => l.road !== road && distance(l, x, z) < l.width / 2 + margin,
  );
}

/** Width of the widest other street that (x, z) of street `road` lies on, if any. */
export function meetingWidth(
  lines: readonly StreetLine[],
  road: number,
  x: number,
  z: number,
): number | undefined {
  let widest: number | undefined;
  for (const l of linesNear(lines, z, 0.5)) {
    if (l.road !== road && distance(l, x, z) < 0.5) widest = Math.max(widest ?? 0, l.width);
  }
  return widest;
}
