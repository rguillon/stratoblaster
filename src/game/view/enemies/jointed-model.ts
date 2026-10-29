import type { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Enemy } from '../../../core/entities/enemy';
import { JointedEnemy, type JointedDesign } from '../../../core/entities/jointed-enemy';
import type { EnemyModel } from '../../../render/game-view';
import { bossPoint } from '../bosses/boss-limbs';
import { buildEnemyModel, newBreath, type EnemyParts } from './enemy-mesh';

type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];
type Draw = (parts: EnemyParts) => void;

/**
 * How an enemy with moving parts is drawn (P05-R13), everything in model space as at rest
 * (logical pixels, nose +Z, Y up; a point `(x, y)` of the design is at {@link bossPoint}).
 */
export interface JointedDrawing {
  /** The hull, which does not move. */
  readonly body: Draw;
  /** What turns with each joint but cannot be destroyed (necks, shoulders), by joint id. */
  readonly limbs?: Readonly<Record<string, Draw>>;
  /** Each part, by part id: it moves with its joint or the spin, and goes when destroyed. */
  readonly parts: Readonly<Record<string, Draw>>;
  /** What turns with the spin around the centre and cannot be destroyed (a launch ring). */
  readonly ring?: Draw;
}

interface Frame {
  readonly node: TransformNode;
  /** Its pivot in model space. */
  readonly origin: Vec3;
}

const ORIGIN: Vec3 = [0, 0, 0];
const sub = (a: Vec3, b: Vec3): Vec3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];

/** A node per joint, hung on the joint it hangs on, its pivot where the design puts it. */
function jointFrames(name: string, design: JointedDesign, root: TransformNode): Map<string, Frame> {
  const specs = design.joints ?? {};
  const frames = new Map<string, Frame>();
  const make = (id: string): Frame => {
    const made = frames.get(id);
    if (made) return made;
    const spec = specs[id];
    if (!spec) throw new Error(`Enemy "${name}" has no joint "${id}"`);
    const parent = spec.parent === undefined ? { node: root, origin: ORIGIN } : make(spec.parent);
    const origin = bossPoint(spec.x, spec.y);
    const node = new TransformNode(`${name}-${id}-joint`, root.getScene());
    node.parent = parent.node;
    node.position.set(...sub(origin, parent.origin));
    const frame = { node, origin };
    frames.set(id, frame);
    return frame;
  };
  for (const id of Object.keys(specs)) make(id);
  return frames;
}

/**
 * Builds the model of an enemy with moving parts (P05-R13): its hull on the root, its limbs and
 * parts on their joints' nodes (or on a ring turning with the enemy's spin), each drawn by
 * {@link buildEnemyModel} with the enemy's neon `color`. The joints turn as the enemy's do, and a
 * destroyed part disappears.
 */
export function buildJointedModel(
  name: string,
  scene: Scene,
  color: Rgb,
  design: JointedDesign,
  drawing: JointedDrawing,
): EnemyModel {
  // P16-R07: its hull, limbs and parts breathe as one creature.
  const look = { breath: newBreath() };
  const body = buildEnemyModel(name, scene, color, drawing.body, look);
  const { root } = body;
  const frames = jointFrames(name, design, root);
  const ring = new TransformNode(`${name}-ring`, scene);
  ring.parent = root;
  const pieces: EnemyModel[] = [];
  const hang = (piece: string, draw: Draw, frame: Frame): EnemyModel => {
    const model = buildEnemyModel(`${name}-${piece}`, scene, color, draw, look);
    model.root.parent = frame.node;
    model.root.position.set(...sub(ORIGIN, frame.origin));
    pieces.push(model);
    return model;
  };
  const frameOf = (joint: string | undefined): Frame =>
    (joint === undefined ? undefined : frames.get(joint)) ?? { node: root, origin: ORIGIN };
  if (drawing.ring) hang('ring', drawing.ring, { node: ring, origin: ORIGIN });
  for (const [joint, draw] of Object.entries(drawing.limbs ?? {})) {
    hang(joint, draw, frameOf(joint));
  }
  const parts = design.parts.map((spec) => {
    const draw = drawing.parts[spec.id];
    if (!draw) throw new Error(`Enemy "${name}" does not draw its part "${spec.id}"`);
    return hang(spec.id, draw, spec.orbits ? { node: ring, origin: ORIGIN } : frameOf(spec.joint));
  });
  return {
    root,
    sync: (enemy: Enemy, dt: number) => {
      body.sync(enemy, dt);
      for (const piece of pieces) piece.sync(enemy, dt);
      if (!(enemy instanceof JointedEnemy)) return;
      for (const [id, { node }] of frames) node.rotation.y = enemy.joints.angle(id);
      ring.rotation.y = enemy.spin;
      parts.forEach((model, i) => {
        model.root.setEnabled(enemy.parts[i]?.destroyed !== true);
      });
    },
  };
}
