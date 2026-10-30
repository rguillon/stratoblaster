import type { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { CreateDisc } from '@babylonjs/core/Meshes/Builders/discBuilder';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { createFacetedLatheAlongZ, type ProfilePoint } from '../../render/geometry/lathe-z';
import type { OutlinePoint } from '../../render/geometry/outline';
import { getShipMaterials } from './ship-materials';
import {
  BODY_SECTION,
  PART_FACETS,
  buildReactor,
  facetedRod,
  mirrorX,
  navLight,
  panel,
  plate,
  tagPart,
} from './ship-parts';

// P02-R01: inspired by the Macross Delta VF-31J: long pointed nose, framed bubble canopy,
// canards, dual reactors fed by side intakes, forward-swept wings, canted twin tails and
// ventral fins, a gun pod under the belly. Model units: nose towards +Z, about 4.8 units long.
// Low-poly and polygonal like the other ships: fuselage with a smooth top and a faceted belly, canopy, intakes and pods.

/** Right main wing (X > 0). The tip's leading edge is ahead of the root's: forward-swept. */
export const BALANCED_WING: readonly OutlinePoint[] = [
  [0.35, 0.15],
  [2.0, 0.7],
  [2.05, 0.4],
  [0.35, -0.95],
];
const WING_THICKNESS = 0.07;
/** Accent band near the wing tip, following the forward sweep. */
const WING_BAND: readonly OutlinePoint[] = [
  [1.45, 0.48],
  [1.75, 0.58],
  [1.78, 0.3],
  [1.48, 0.12],
];
/** Trailing-edge flap line. */
const WING_FLAP: readonly OutlinePoint[] = [
  [0.45, -0.72],
  [1.3, -0.1],
  [1.36, -0.2],
  [0.45, -0.86],
];
const STRAKE: readonly OutlinePoint[] = [
  [0.2, 1.3],
  [0.62, 0.35],
  [0.2, 0.2],
];
const CANARD: readonly OutlinePoint[] = [
  [0.22, 1.12],
  [0.68, 0.86],
  [0.7, 0.74],
  [0.22, 0.8],
];
const TAIL: readonly OutlinePoint[] = [
  [0, -0.75],
  [0.85, -1.35],
  [0.85, -1.6],
  [0, -1.55],
];
const TAIL_STRIPE: readonly OutlinePoint[] = [
  [0.5, -1.15],
  [0.75, -1.3],
  [0.75, -1.4],
  [0.5, -1.27],
];
const VENTRAL_FIN: readonly OutlinePoint[] = [
  [0, -0.95],
  [0.38, -1.25],
  [0.38, -1.4],
  [0, -1.35],
];
const TAIL_CANT = 0.4; // rad from vertical, outwards
const VENTRAL_CANT = 0.55; // rad from vertical, outwards
const REACTOR_OFFSET_X = 0.42;
const REACTOR = { radius: 0.22, length: 1.7 };

function buildBody(root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const bodyRoot = tagPart(new TransformNode('balanced-body-root', scene), 'body');
  bodyRoot.parent = root;
  const body = createFacetedLatheAlongZ(
    'balanced-body',
    [
      [2.4, 0],
      [2.2, 0.07],
      [1.8, 0.14],
      [0.9, 0.3],
      [-0.2, 0.36],
      [-1.4, 0.3],
      [-1.6, 0],
    ],
    BODY_SECTION,
    scene,
  );
  body.scaling.y = 0.7;
  body.material = mats.hull;
  body.parent = bodyRoot;

  // Dorsal spine running from the canopy to the tails.
  const spine = createFacetedLatheAlongZ(
    'balanced-spine',
    [
      [0.7, 0],
      [0.3, 0.12],
      [-1.2, 0.11],
      [-1.55, 0],
    ],
    PART_FACETS,
    scene,
  );
  spine.position.y = 0.17;
  spine.scaling.x = 0.8;
  spine.material = mats.hull;
  spine.parent = bodyRoot;

  facetedRod(
    'balanced-gun-pod',
    { length: 1.7, radius: 0.065 },
    new Vector3(0, -0.28, 0.2),
    mats.trim,
    root,
    PART_FACETS,
  );
  navLight('balanced-gun-muzzle', new Vector3(0, -0.28, 1.06), root);
}

/** Canopy profile, `[z, radius]`. */
const CANOPY: readonly ProfilePoint[] = [
  [1.4, 0],
  [1.25, 0.08],
  [1.1, 0.11],
  [0.9, 0.08],
  [0.8, 0],
];
/** Middle of the canopy along Z, for scaling the frame around it. */
const CANOPY_MID_Z = 1.1;

function buildCockpit(root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  // The frame is the canopy profile, a bit larger and longer.
  const frameProfile: ProfilePoint[] = CANOPY.map(([z, r]) => [
    CANOPY_MID_Z + (z - CANOPY_MID_Z) * 1.2,
    r * 1.2,
  ]);
  const frame = createFacetedLatheAlongZ('balanced-canopy-frame', frameProfile, PART_FACETS, scene);
  frame.scaling.y = 0.8;
  frame.position.y = 0.15;
  frame.material = mats.trim;
  frame.parent = root;

  const canopy = tagPart(
    createFacetedLatheAlongZ('balanced-canopy', CANOPY, PART_FACETS, scene),
    'canopy',
  );
  canopy.position.y = 0.17;
  canopy.material = mats.canopy;
  canopy.parent = root;
}

function buildIntake(side: string, sign: number, root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const intake = createFacetedLatheAlongZ(
    `balanced-intake-${side}`,
    [
      [0.35, 0],
      [0.35, 0.15],
      [-0.2, 0.2],
      [-0.2, 0],
    ],
    PART_FACETS,
    scene,
  );
  intake.scaling.x = 0.8;
  intake.position.set(sign * REACTOR_OFFSET_X, -0.06, 0.05);
  intake.material = mats.trim;
  intake.parent = root;
  // Dark intake mouth, facing forward.
  const mouth = CreateDisc(
    `balanced-intake-${side}-mouth`,
    { radius: 0.12, tessellation: PART_FACETS },
    scene,
  );
  mouth.convertToFlatShadedMesh();
  mouth.rotation.y = Math.PI;
  mouth.scaling.x = 0.8;
  mouth.position.set(sign * REACTOR_OFFSET_X, -0.06, 0.41);
  mouth.material = mats.canopy;
  mouth.parent = root;
}

function buildWing(side: string, sign: number, root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const mirror = (o: readonly OutlinePoint[]): readonly OutlinePoint[] =>
    sign > 0 ? o : mirrorX(o);
  const wing = tagPart(new TransformNode(`balanced-wing-${side}`, scene), 'wing');
  wing.parent = root;
  panel(`balanced-wing-${side}-panel`, mirror(BALANCED_WING), WING_THICKNESS, mats.hull, wing);
  plate(`balanced-wing-${side}-band`, mirror(WING_BAND), WING_THICKNESS / 2, mats.accent, wing);
  plate(`balanced-wing-${side}-flap`, mirror(WING_FLAP), WING_THICKNESS / 2, mats.trim, wing);
  panel(`balanced-strake-${side}`, mirror(STRAKE), 0.05, mats.accent, wing);
  const canard = panel(`balanced-canard-${side}`, mirror(CANARD), 0.04, mats.hull, wing);
  canard.position.y = 0.08;
  navLight(`balanced-wing-${side}-light`, new Vector3(sign * 2.03, 0, 0.55), wing);
}

function buildTails(side: string, sign: number, root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const tail = tagPart(new TransformNode(`balanced-tail-${side}`, scene), 'tail');
  tail.position.set(sign * 0.38, 0.12, 0);
  // Stand the panel up (X becomes height), then cant it outwards.
  tail.rotation.z = Math.PI / 2 - sign * TAIL_CANT;
  tail.parent = root;
  panel(`balanced-tail-${side}-panel`, TAIL, 0.05, mats.hull, tail);
  plate(`balanced-tail-${side}-stripe`, TAIL_STRIPE, sign * 0.03, mats.accent, tail);
  navLight(`balanced-tail-${side}-light`, new Vector3(0.85, 0, -1.47), tail);

  // Ventral fin: same trick, pointing down and outwards.
  const fin = new TransformNode(`balanced-ventral-${side}`, scene);
  fin.position.set(sign * 0.3, -0.16, 0);
  fin.rotation.z = -Math.PI / 2 + sign * VENTRAL_CANT;
  fin.parent = root;
  panel(`balanced-ventral-${side}-panel`, VENTRAL_FIN, 0.04, mats.accent, fin);
}

/** Builds the balanced player ship (P02-R01). */
export function buildBalancedShip(scene: Scene): TransformNode {
  const root = new TransformNode('ship-balanced', scene);
  buildBody(root, scene);
  buildCockpit(root, scene);
  for (const [side, sign] of [
    ['right', 1],
    ['left', -1],
  ] as const) {
    buildIntake(side, sign, root, scene);
    buildWing(side, sign, root, scene);
    buildTails(side, sign, root, scene);
    const reactor = buildReactor(`balanced-reactor-${side}`, REACTOR, scene);
    reactor.position.set(sign * REACTOR_OFFSET_X, -0.05, -0.95);
    reactor.parent = root;
  }
  return root;
}
