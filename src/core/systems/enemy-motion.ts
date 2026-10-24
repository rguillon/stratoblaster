/**
 * Movement helpers for enemies (GD-45). Playfield logical pixels, Y up; headings in radians from
 * +Y, positive to the right.
 */

export type PathPoint = readonly [x: number, y: number];

/** A point along a {@link Path}, with the direction of travel there. */
export interface PathPose {
  readonly x: number;
  readonly y: number;
  readonly heading: number;
}

function catmullRom(p0: number, p1: number, p2: number, p3: number, t: number): number {
  const t2 = t * t;
  return (
    0.5 *
    (2 * p1 +
      (p2 - p0) * t +
      (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
      (3 * p1 - p0 - 3 * p2 + p3) * t2 * t)
  );
}

/**
 * A smooth predefined path through control points (a Catmull-Rom curve), followed by distance
 * travelled, so an enemy moving along it at a constant speed keeps that speed on the curves.
 */
export class Path {
  readonly #points: PathPoint[] = [];
  /** Distance travelled from the start at each sampled point. */
  readonly #lengths: number[] = [];

  constructor(controls: readonly PathPoint[], samplesPerSpan = 16) {
    if (controls.length < 2) throw new Error('A path needs at least 2 points');
    const at = (i: number): PathPoint =>
      controls[Math.min(Math.max(i, 0), controls.length - 1)] ?? [0, 0];
    for (let span = 0; span < controls.length - 1; span++) {
      const [p0, p1, p2, p3] = [at(span - 1), at(span), at(span + 1), at(span + 2)];
      const first = span === 0 ? 0 : 1;
      for (let s = first; s <= samplesPerSpan; s++) {
        const t = s / samplesPerSpan;
        this.#add([
          catmullRom(p0[0], p1[0], p2[0], p3[0], t),
          catmullRom(p0[1], p1[1], p2[1], p3[1], t),
        ]);
      }
    }
  }

  #add(point: PathPoint): void {
    const last = this.#points.at(-1);
    const step = last ? Math.hypot(point[0] - last[0], point[1] - last[1]) : 0;
    this.#lengths.push((this.#lengths.at(-1) ?? 0) + step);
    this.#points.push(point);
  }

  /** Total length. */
  get length(): number {
    return this.#lengths.at(-1) ?? 0;
  }

  /** The pose `distance` along the path, clamped to its ends. */
  at(distance: number): PathPose {
    const d = Math.min(Math.max(distance, 0), this.length);
    let i = 1;
    while (i < this.#lengths.length - 1 && (this.#lengths[i] ?? 0) < d) i++;
    const [a, b] = [this.#points[i - 1] ?? [0, 0], this.#points[i] ?? [0, 0]];
    const [la, lb] = [this.#lengths[i - 1] ?? 0, this.#lengths[i] ?? 0];
    const t = lb > la ? (d - la) / (lb - la) : 0;
    return {
      x: a[0] + (b[0] - a[0]) * t,
      y: a[1] + (b[1] - a[1]) * t,
      heading: Math.atan2(b[0] - a[0], b[1] - a[1]),
    };
  }
}

/**
 * `count` headings spread `spacing` radians apart, centred on `center` (e.g. a fan of 3 bullets
 * at -15°, 0° and +15° from straight down).
 */
export function fanHeadings(center: number, count: number, spacing: number): number[] {
  return Array.from({ length: count }, (_, i) => center + (i - (count - 1) / 2) * spacing);
}

/** Moves `value` towards `target` by at most `maxStep`. */
export function approach(value: number, target: number, maxStep: number): number {
  if (Math.abs(target - value) <= maxStep) return target;
  return value + Math.sign(target - value) * maxStep;
}
