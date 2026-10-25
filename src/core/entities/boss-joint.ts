/**
 * Moving limbs of a boss (phase 7 review): a joint turns what hangs on it (parts, their hit
 * circles and muzzles, other joints) around its pivot, swinging to and fro. Joints hang on other
 * joints, so an arm can bend at the shoulder, the elbow and the wrist.
 */

/** A joint: its pivot, the joint it hangs on, and how it swings. */
export interface BossJointSpec {
  /** Its pivot, from the boss's centre (X right, Y up), as the boss is drawn at rest. */
  readonly x: number;
  readonly y: number;
  /** The joint it hangs on, if any: it moves with that one. */
  readonly parent?: string;
  /**
   * It swings up to `amplitudeDeg` either way (clockwise on screen first) and back every
   * `period` seconds, starting `phase` (0..1) of a period in.
   */
  readonly swing: {
    readonly amplitudeDeg: number;
    readonly period: number;
    readonly phase?: number;
  };
}

/** What a part says about the joint it hangs on (see `BossPartSpec`). */
interface JointedPart {
  readonly id: string;
  readonly joint?: string;
  readonly orbits?: boolean;
}

/** Throws when a joint or a part hangs on no joint or a joint on itself, or a part also orbits. */
function checkJoints(
  specs: ReadonlyMap<string, BossJointSpec>,
  parts: readonly JointedPart[],
): void {
  for (const { id, joint, orbits } of parts) {
    if (joint === undefined) continue;
    if (!specs.has(joint)) throw new Error(`Part "${id}" hangs on no joint "${joint}"`);
    if (orbits) throw new Error(`Part "${id}" both orbits and hangs on a joint`);
  }
  for (const id of specs.keys()) {
    const seen = new Set<string>();
    for (let j: string | undefined = id; j !== undefined; j = specs.get(j)?.parent) {
      if (!specs.has(j)) throw new Error(`Boss joint "${id}" hangs on no joint "${j}"`);
      if (seen.has(j)) throw new Error(`Boss joint "${id}" hangs on itself`);
      seen.add(j);
    }
  }
}

/** The joints of a boss, by id, and how far each is turned now. */
export class BossJoints {
  readonly #specs: ReadonlyMap<string, BossJointSpec>;
  readonly #angles = new Map<string, number>();
  #time = 0;

  /** Throws when a joint or one of `parts` hangs on no joint, or a part also orbits. */
  constructor(
    specs: Readonly<Record<string, BossJointSpec>> = {},
    parts: readonly JointedPart[] = [],
  ) {
    this.#specs = new Map(Object.entries(specs));
    checkJoints(this.#specs, parts);
    this.step(0);
  }

  /** Swings them on by `dt` seconds. */
  step(dt: number): void {
    this.#time += dt;
    for (const [id, { swing }] of this.#specs) {
      const turns = this.#time / swing.period + (swing.phase ?? 0);
      this.#angles.set(id, ((swing.amplitudeDeg * Math.PI) / 180) * Math.sin(2 * Math.PI * turns));
    }
  }

  /** How far joint `id` is turned on the one it hangs on: radians, clockwise on screen. */
  angle(id: string): number {
    return this.#angles.get(id) ?? 0;
  }

  /**
   * Where the point `(x, y)` (from the boss's centre, as drawn at rest) of something hanging on
   * joint `id` is now, turned by that joint and those it hangs on. Unmoved without a joint.
   */
  move(id: string | undefined, x: number, y: number): [x: number, y: number] {
    let [px, py] = [x, y];
    for (let j = id; j !== undefined;) {
      const spec = this.#specs.get(j);
      if (!spec) break;
      const a = this.angle(j);
      const [c, s] = [Math.cos(a), Math.sin(a)];
      const [dx, dy] = [px - spec.x, py - spec.y];
      [px, py] = [spec.x + dx * c + dy * s, spec.y - dx * s + dy * c];
      j = spec.parent;
    }
    return [px, py];
  }
}
