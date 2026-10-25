import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Boss, type BossPart, type BossPartSpec } from '../../../core/entities/boss';
import type { BossTurret } from '../../../core/entities/boss-turret';
import type { Enemy } from '../../../core/entities/enemy';
import { createRng } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { EnemyModel } from '../../../render/game-view';
import type { BossDesign } from '../../config/bosses/boss-kit';
import { BOSS_LOOK } from '../../config/boss-look';
import { buildEnemyModel, meshOf, type EnemyParts } from '../enemies/enemy-mesh';
import {
  BossLimbs,
  bossPoint,
  hang,
  JointFrames,
  ORIGIN,
  type JointFrame,
  type LimbDrawing,
} from './boss-limbs';

export { bossPoint, type LimbDrawing } from './boss-limbs';

type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** Draws a part around its centre `at` (model space), with the builders of an enemy model. */
export type PartDrawing = (parts: EnemyParts, at: Vec3) => void;

/** What a boss model is drawn from (P07-R01, R05). */
export interface BossDrawing {
  /** The core body: hull, neon, charge lights, reactors. Always shown. */
  readonly core: (parts: EnemyParts) => void;
  /** Every destroyable part, by part id. Hidden and replaced by a stump once destroyed. */
  readonly parts: Readonly<Record<string, PartDrawing>>;
  /** A body turning with the boss's spin (`BossPartSpec.orbits` parts are drawn on it). */
  readonly ring?: (parts: EnemyParts) => void;
  /**
   * The turrets of its core (`core`) and parts, by piece, drawn around their pivot (`Guns.turret`)
   * as they are at rest: they turn with the turret's aim (phase 7 review), on their piece.
   */
  readonly turrets?: Readonly<Record<string, PartDrawing>>;
  /**
   * What is drawn on its joints (`BossStats.joints`), by joint (phase 7 review): drawn as at
   * rest, they move with the joint. One that belongs to a part goes and flashes with it; the
   * others flash with the core.
   */
  readonly limbs?: Readonly<Record<string, LimbDrawing>>;
}

/** A piece's turret: its model, on a node turning around its pivot. */
interface TurretView {
  readonly pivot: TransformNode;
  readonly model: EnemyModel;
}

/** The turret of `piece` on `holder` (its piece's model), if the boss's drawing has one. */
function buildTurret(
  design: BossDesign,
  piece: string,
  drawing: BossDrawing,
  holder: TransformNode,
  neon: Rgb,
): TurretView | undefined {
  const draw = drawing.turrets?.[piece];
  const turret = design.guns[piece]?.turret;
  if (!draw && !turret) return undefined;
  if (!draw || !turret)
    throw new Error(`Boss "${design.id}": "${piece}" needs a turret and its drawing`);
  const scene = holder.getScene();
  const at = bossPoint(...turret);
  const pivot = new TransformNode(`${design.id}-${piece}-pivot`, scene);
  pivot.position.set(...at);
  pivot.parent = holder;
  const model = buildEnemyModel(`${design.id}-${piece}-turret`, scene, neon, (p) => {
    draw(p, at);
  });
  model.root.position.set(-at[0], -at[1], -at[2]);
  model.root.parent = pivot;
  return { pivot, model };
}

/** Shows a turret turned by its aim (+Y turns the nose, down the screen, clockwise on screen). */
function showTurret(
  view: TurretView | undefined,
  turret: BossTurret | undefined,
  lit: Enemy,
  dt: number,
): void {
  if (!view) return;
  view.pivot.rotation.y = turret?.aim ?? 0;
  view.model.sync(lit, dt);
}

const FLASH_CACHE = new WeakMap<Scene, { flash: StandardMaterial; smoke: StandardMaterial }>();

/** The flash and smoke materials of the scene, created on first use. */
function effectMaterials(scene: Scene): { flash: StandardMaterial; smoke: StandardMaterial } {
  let mats = FLASH_CACHE.get(scene);
  if (!mats) {
    const flash = new StandardMaterial('boss-flash', scene);
    flash.emissiveColor = new Color3(...BOSS_LOOK.flash.color);
    flash.disableLighting = true;
    const smoke = new StandardMaterial('boss-smoke', scene);
    smoke.emissiveColor = new Color3(...BOSS_LOOK.smoke.color);
    smoke.disableLighting = true;
    smoke.alpha = BOSS_LOOK.smoke.alpha;
    smoke.backFaceCulling = false;
    mats = { flash, smoke };
    FLASH_CACHE.set(scene, mats);
  }
  return mats;
}

/** A piece of the model shown for a part, or the core, with its hit flash. */
class FlashGroup {
  readonly #hulls: { mesh: Mesh; material: Material | null }[];

  constructor(
    readonly model: EnemyModel,
    private readonly flash: Material,
  ) {
    this.#hulls = model.root
      .getChildMeshes<Mesh>()
      .filter((m) => m.material?.name === 'enemy-hull')
      .map((mesh) => ({ mesh, material: mesh.material }));
  }

  /** Flashes white for a moment after a hit (P07-R01). */
  show(sinceHit: number): void {
    const on = sinceHit < BOSS_LOOK.flash.seconds;
    for (const hull of this.#hulls) {
      hull.mesh.material = on ? this.flash : hull.material;
      hull.mesh.useVertexColors = !on;
    }
  }
}

/** The smoke rising from a damaged part (P07-R01): a few puffs drifting back and fading. */
function buildSmoke(name: string, radius: number, scene: Scene, parent: TransformNode) {
  const look = BOSS_LOOK.smoke;
  const node = new TransformNode(`${name}-smoke`, scene);
  node.parent = parent;
  const disc = new SolidBuilder();
  const outline = Array.from({ length: 6 }, (_, k) => {
    const a = (2 * Math.PI * k) / 6;
    return [Math.cos(a) * radius * look.size, Math.sin(a) * radius * look.size] as const;
  });
  disc.slab(outline, [0, 0.1], [1, 1, 1]);
  const puffs = Array.from({ length: look.puffs }, (_, i) => {
    const mesh = meshOf(
      `${name}-puff-${String(i)}`,
      disc.geometry,
      effectMaterials(scene).smoke,
      scene,
    );
    mesh.parent = node;
    return mesh;
  });
  let time = 0;
  return {
    node,
    step(dt: number): void {
      time += dt;
      puffs.forEach((puff, i) => {
        const t = (time / look.seconds + i / puffs.length) % 1;
        puff.position.set(0, look.rise * t + radius, -look.drift * t);
        puff.scaling.setAll(0.6 + t);
        puff.visibility = 1 - t;
      });
    },
  };
}

/** A burnt, sparking stump where a destroyed part was (P07-R01). */
function buildStump(name: string, radius: number, scene: Scene, parent: TransformNode) {
  const look = BOSS_LOOK.stump;
  const node = new TransformNode(`${name}-stump`, scene);
  node.parent = parent;
  const model = buildEnemyModel(name + '-stump', scene, look.spark, ({ hull, charge }) => {
    hull.cylinder(radius * 0.55, radius * 0.25, 6, look.char, {});
    for (let k = 0; k < 3; k++) {
      const a = (2 * Math.PI * k) / 3 + 0.4;
      const shard = [
        [-radius * 0.12, 0],
        [radius * 0.12, 0],
        [0, radius * 0.5],
      ] as const;
      hull.slab(shard, [0, radius * 0.18], look.char, { yaw: a, at: [0, radius * 0.2, 0] });
    }
    charge.cylinder(radius * 0.2, radius * 0.32, 4, [1, 1, 1], {});
  });
  model.root.parent = node;
  const random = createRng(name.length * 7919);
  return {
    node,
    sync(enemy: Enemy, dt: number): void {
      // Sparks flicker at random.
      enemy.charge = random() < look.sparkChance ? 1 : 0;
      model.sync(enemy, dt);
    },
  };
}

/** The pieces of one part: its model (and turret), its smoke, its stump. */
interface PartView {
  readonly group: FlashGroup;
  readonly turret: TurretView | undefined;
  readonly smoke: ReturnType<typeof buildSmoke>;
  readonly stump: ReturnType<typeof buildStump>;
}

/** The charge lights of the stumps spark on their own: a stand-in enemy for their sync. */
const STUMP_STATE = { charge: 0 } as unknown as Enemy;

/**
 * Builds the model of a boss (P07-R05) from `drawing`, in the colour `neon`: its core body, its
 * parts on their own nodes (each flashing white when hit, smoking under half health, replaced by
 * a burnt stump once destroyed), and an optional ring turning with the boss's spin.
 */
export function buildBossModel(
  design: BossDesign,
  scene: Scene,
  neon: Rgb,
  drawing: BossDrawing,
): EnemyModel {
  const name = design.id;
  const { flash } = effectMaterials(scene);
  const root = new TransformNode(name, scene);
  const { core, coreTurret, ringNode, ring } = buildBody(design, drawing, root, { flash, neon });
  const joints = new JointFrames(design, root);
  const holder = (spec: BossPartSpec) => joints.frame(spec.joint, spec.orbits ? ringNode : root);
  const look = { flash, neon };
  const parts = design.stats.parts.map((spec) =>
    buildPart(design, spec, drawing, holder(spec), look),
  );
  const limbs = new BossLimbs(design, drawing.limbs, joints, (limb, draw) => {
    return new FlashGroup(buildEnemyModel(`${name}-${limb}-limb`, scene, neon, draw), flash);
  });
  const lit = { charge: 0 };
  return {
    root,
    sync: (boss: Enemy, dt: number) => {
      // After a part is destroyed, its lights strobe while it holds its fire (P07-R04).
      lit.charge = strobe(boss);
      const enemy = lit as unknown as Enemy;
      core.model.sync(enemy, dt);
      ring?.model.sync(enemy, dt);
      limbs.show(boss instanceof Boss ? boss : undefined, enemy, dt);
      if (!(boss instanceof Boss)) {
        showTurret(coreTurret, undefined, enemy, dt);
        return;
      }
      showTurret(coreTurret, boss.core.turret, enemy, dt);
      // It rolls into its sideways moves (phase 7 review). Screen right is the model's -X (its
      // nose points down the screen): +Z rolls -X down.
      root.rotation.z = boss.roll;
      ringNode.rotation.y = boss.spin;
      core.show(boss.core.sinceHit);
      ring?.show(boss.core.sinceHit);
      boss.parts.forEach((part, i) => {
        const view = parts[i];
        if (view) showPart(view, part, enemy, dt);
      });
    },
  };
}

/** The core body (and its turret) on `root`, and the ring turning with the boss's spin. */
function buildBody(
  design: BossDesign,
  drawing: BossDrawing,
  root: TransformNode,
  { flash, neon }: { readonly flash: Material; readonly neon: Rgb },
) {
  const [name, scene] = [design.id, root.getScene()];
  const coreModel = buildEnemyModel(`${name}-core`, scene, neon, drawing.core);
  coreModel.root.parent = root;
  const coreTurret = buildTurret(design, 'core', drawing, coreModel.root, neon);
  const core = new FlashGroup(coreModel, flash);
  const ringNode = new TransformNode(`${name}-ring`, scene);
  ringNode.parent = root;
  const ring =
    drawing.ring &&
    new FlashGroup(buildEnemyModel(`${name}-ringbody`, scene, neon, drawing.ring), flash);
  if (ring) ring.model.root.parent = ringNode;
  return { core, coreTurret, ringNode, ring };
}

/** The model, smoke and stump of one part, on `frame` (the boss, its turning ring or a joint). */
function buildPart(
  design: BossDesign,
  spec: BossPartSpec,
  drawing: BossDrawing,
  frame: JointFrame,
  { flash, neon }: { readonly flash: Material; readonly neon: Rgb },
): PartView {
  const name = design.id;
  const scene = frame.node.getScene();
  const draw = drawing.parts[spec.id];
  if (!draw) throw new Error(`Boss "${name}" has no drawing for its part "${spec.id}"`);
  const at = bossPoint(spec.x, spec.y);
  const model = buildEnemyModel(`${name}-${spec.id}`, scene, neon, (p) => {
    draw(p, at);
  });
  hang(model.root, ORIGIN, frame);
  const turret = buildTurret(design, spec.id, drawing, model.root, neon);
  const spot = new TransformNode(`${name}-${spec.id}-spot`, scene);
  hang(spot, at, frame);
  const smoke = buildSmoke(`${name}-${spec.id}`, spec.radius, scene, spot);
  const stump = buildStump(`${name}-${spec.id}`, spec.radius, scene, spot);
  return { group: new FlashGroup(model, flash), turret, smoke, stump };
}

/**
 * The brightness of a boss's charge lights: its own, a strobe during a stage change, and a fast
 * flicker while it is angry (phase 7 review).
 */
function strobe(enemy: Enemy): number {
  if (!(enemy instanceof Boss)) return enemy.charge;
  if (enemy.pause > 0) {
    return Math.floor(enemy.pause * BOSS_LOOK.stageStrobeHz * 2) % 2 === 0 ? 1 : 0;
  }
  if (enemy.rage <= 0) return enemy.charge;
  const { hz, dim } = BOSS_LOOK.rageFlicker;
  return Math.floor(enemy.rage * hz * 2) % 2 === 0 ? 1 : dim;
}

/** A part: its model while it stands (flashing, smoking), its stump once destroyed. */
function showPart(view: PartView, part: BossPart, lit: Enemy, dt: number): void {
  const destroyed = part.destroyed;
  view.group.model.root.setEnabled(!destroyed);
  view.stump.node.setEnabled(destroyed);
  const smoking = !destroyed && part.health < part.maxHealth * BOSS_LOOK.smoke.below;
  view.smoke.node.setEnabled(smoking);
  if (destroyed) {
    view.stump.sync(STUMP_STATE, dt);
    return;
  }
  view.group.model.sync(lit, dt);
  showTurret(view.turret, part.turret, lit, dt);
  view.group.show(part.sinceHit);
  if (smoking) view.smoke.step(dt);
}
