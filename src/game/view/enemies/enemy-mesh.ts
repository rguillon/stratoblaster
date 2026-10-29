import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import type { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Enemy } from '../../../core/entities/enemy';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { EnemyModel } from '../../../render/game-view';
import { addModelAnimation, stepModelAnimations } from '../../../render/model-animation';
import { setOutline } from '../../../render/outline';
import { ENEMY_LOOK } from '../../config/enemy-look';
import {
  enemyColor,
  enemyMaterials,
  inEnemyFamily,
  meshOf,
  rimOf,
  tintedHull,
  unlit,
} from './enemy-materials';
import {
  breathScale,
  flutterAngle,
  glowLevel,
  isLivingMotion,
  newBreath,
  type Breath,
} from './living-motion';
import { addReactors, addRotors, type Reactor } from './enemy-engines';

export { BODY_MATERIALS, enemyColor, enemyMaterials, meshOf } from './enemy-materials';
export {
  breathScale,
  flutterAngle,
  glowLevel,
  isLivingMotion,
  newBreath,
  setLivingMotion,
  type Breath,
} from './living-motion';

type Rgb = readonly [number, number, number];

/** Builders for the three parts of an enemy model. */
export interface EnemyParts {
  /** Dark metal (use the `ENEMY_LOOK.hull` shades): the cyber parts grafted on (P16-R01). */
  readonly hull: SolidBuilder;
  /** Dark flesh (use the `ENEMY_LOOK.flesh` shades): the living body (P16-R01). */
  readonly flesh: SolidBuilder;
  /** Glowing veins, eyes and glands, pulsing slowly (P16-R07); in the enemies' colour family. */
  readonly vein: SolidBuilder;
  /**
   * Adds a wing hinged along Z at `pivot`, fluttering (P16-R07) on its own node: `draw` draws it
   * in model space, as at rest, with the same builders. `side` (-1 left, 1 right) sets which way
   * it flaps; `span` (its length out) picks the slower beat of big wings.
   */
  readonly flap: (pivot: Vec3, side: number, span: number, draw: (wing: WingParts) => void) => void;
  /** Neon lights, always lit. */
  readonly neon: SolidBuilder;
  /** Lights that brighten as the next attack charges (`Enemy.charge`); white, tinted by `charge`. */
  readonly charge: SolidBuilder;
  /**
   * Adds a reactor whose nozzle opens at `at`, thrusting towards -Z (phase 5 review): a dark
   * nozzle, a glowing core and an animated flame, light blue on every enemy.
   */
  readonly reactor: (at: Vec3, radius: number) => void;
  /**
   * Adds a rotor turning around +Y at `at` (phase 5 review: the Gnat's ducted fans): blades
   * `radius` long around a hub, on their own node so they spin.
   */
  readonly rotor: (at: Vec3, radius: number) => void;
  /**
   * Marks the tip of a gun's barrel at `at`, where its shots leave from (phase 7 review: the
   * game's muzzles must match): an empty node `<name>-muzzle-<kind>-<i>` (kinds as in a boss's
   * `Guns`: `gun`, `ring`, `missile`, `laser`).
   */
  readonly muzzle: (at: Vec3, kind?: string) => void;
}

type Vec3 = readonly [number, number, number];

/** The builders a fluttering wing is drawn with. */
export interface WingParts {
  readonly hull: SolidBuilder;
  readonly flesh: SolidBuilder;
  readonly neon: SolidBuilder;
  readonly vein: SolidBuilder;
}

interface Wing {
  readonly pivot: Vec3;
  readonly side: number;
  readonly span: number;
  readonly parts: WingParts;
}

/**
 * The hull (with a rim, P14-R04) and the neon lights (in the enemies' colour family, P14-R02)
 * of an enemy model whose neon is `neonColor`, under `root`.
 */
function addSurfaces(
  name: string,
  parts: WingParts,
  mats: SurfaceMaterials,
  neonColor: Rgb,
  root: TransformNode,
): void {
  const scene = root.getScene();
  for (const [geo, mat] of [
    [parts.hull.geometry, mats.hull],
    [parts.flesh.geometry, mats.flesh],
  ] as const) {
    if (geo.positions.length === 0) continue;
    const mesh = meshOf(`${name}-${mat.name}`, geo, mat, scene);
    mesh.parent = root;
    setOutline(mesh, rimOf(neonColor));
  }
  for (const [geo, mat] of [
    [parts.neon.geometry, mats.neon],
    [parts.vein.geometry, mats.vein],
  ] as const) {
    if (geo.positions.length === 0) continue;
    meshOf(`${name}-${mat.name}`, inEnemyFamily(geo), mat, scene).parent = root;
  }
}

interface SurfaceMaterials {
  readonly hull: Material;
  readonly flesh: Material;
  readonly neon: Material;
  readonly vein: StandardMaterial;
}

const wingParts = (): WingParts => ({
  hull: new SolidBuilder(),
  flesh: new SolidBuilder(),
  neon: new SolidBuilder(),
  vein: new SolidBuilder(),
});

/** The wings, each on a node at its pivot rolling as it flutters (P16-R07), under `body`. */
function addWings(
  name: string,
  wings: readonly Wing[],
  mats: SurfaceMaterials,
  neonColor: Rgb,
  body: TransformNode,
  clock: { time: number },
): void {
  wings.forEach(({ pivot, side, span, parts }, i) => {
    const node = new TransformNode(`${name}-wing-${String(i)}`, body.getScene());
    node.position.set(...pivot);
    node.parent = body;
    const inner = new TransformNode(`${node.name}-skin`, body.getScene());
    inner.position.set(-pivot[0], -pivot[1], -pivot[2]);
    inner.parent = node;
    addSurfaces(node.name, parts, mats, neonColor, inner);
    // Left and right wings of a pair beat together.
    addModelAnimation(node, () => {
      node.rotation.z = flutterAngle(side, span, clock.time);
    });
  });
}

/** The parts `build` draws, and the reactors, rotors, wings and muzzles it adds. */
function collectParts(build: (parts: EnemyParts) => void) {
  const reactors: Reactor[] = [];
  const rotors: Reactor[] = [];
  const wings: Wing[] = [];
  const muzzles: { at: Vec3; kind: string }[] = [];
  const parts: EnemyParts = {
    ...wingParts(),
    charge: new SolidBuilder(),
    reactor: (at, radius) => reactors.push({ at, radius }),
    rotor: (at, radius) => rotors.push({ at, radius }),
    muzzle: (at, kind = 'gun') => muzzles.push({ at, kind }),
    flap: (pivot, side, span, draw) => {
      const wing = { pivot, side, span, parts: wingParts() };
      draw(wing.parts);
      wings.push(wing);
    },
  };
  build(parts);
  return { parts, reactors, rotors, wings, muzzles };
}

/** Options of {@link buildEnemyModel}. */
export interface EnemyModelOptions {
  /** The breathing it shares with the rest of its creature (a new one by default). */
  readonly breath?: Breath;
}

/**
 * Builds an enemy model from the parts `build` draws (logical pixels, nose +Z, Y up). The
 * charge lights get their own material, brightened to `chargeColor` by the enemy's charge; the
 * hull is tinted towards `chargeColor`, the enemy's neon colour. Its body (hull, flesh, lights,
 * wings) is on a node of its own, `<name>-body`, that breathes (P16-R07); its reactors and
 * muzzles are not, so shots leave from the same points (P16-R08).
 */
export function buildEnemyModel(
  name: string,
  scene: Scene,
  neonColor: Rgb,
  build: (parts: EnemyParts) => void,
  { breath = newBreath() }: EnemyModelOptions = {},
): EnemyModel {
  // Phase 14 (P14-R02): every enemy's lights in the enemies' colour family.
  const chargeColor = enemyColor(neonColor);
  const { parts, reactors, rotors, wings, muzzles } = collectParts(build);
  const vein = unlit(`${name}-vein`, scene);
  const mats: SurfaceMaterials = {
    hull: tintedHull(scene, chargeColor),
    flesh: tintedHull(scene, chargeColor, true),
    neon: enemyMaterials(scene).neon,
    vein,
  };
  const root = new TransformNode(name, scene);
  const body = new TransformNode(`${name}-body`, scene);
  body.parent = root;
  const clock = { time: 0 };
  addReactors(name, reactors, parts, root);
  addRotors(name, rotors, mats.hull, body);
  muzzles.forEach(({ at, kind }, i) => {
    const node = new TransformNode(`${name}-muzzle-${kind}-${String(i)}`, scene);
    node.position.set(...at);
    node.parent = root;
  });
  addSurfaces(name, parts, mats, chargeColor, body);
  addWings(name, wings, mats, chargeColor, body, clock);
  const chargeMat = unlit(`${name}-charge`, scene);
  if (parts.charge.geometry.positions.length > 0) {
    meshOf(`${name}-charge`, parts.charge.geometry, chargeMat, scene).parent = body;
  }
  return {
    root,
    sync: (enemy: Enemy, dt: number) => {
      // P16-R07: driven by the frames' sim time, so a paused game holds still.
      if (isLivingMotion()) clock.time += dt;
      else clock.time = 0;
      body.scaling.setAll(isLivingMotion() ? breathScale(breath, clock.time) : 1);
      const glow = isLivingMotion() ? glowLevel(breath, clock.time) : 1;
      vein.emissiveColor.set(glow, glow, glow);
      stepModelAnimations(root, dt);
      const k = ENEMY_LOOK.chargeIdle + (1 - ENEMY_LOOK.chargeIdle) * enemy.charge;
      chargeMat.emissiveColor.set(chargeColor[0] * k, chargeColor[1] * k, chargeColor[2] * k);
    },
  };
}
