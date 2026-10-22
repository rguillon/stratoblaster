import type { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { CreateDisc } from '@babylonjs/core/Meshes/Builders/discBuilder';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { createFacetedLatheAlongZ } from '../../render/geometry/lathe-z';
import type { OutlinePoint } from '../../render/geometry/outline';
import { getShipMaterials } from './ship-materials';
import {
  BODY_SECTION,
  PART_FACETS,
  buildReactor,
  mirrorX,
  navLight,
  panel,
  plate,
  tagPart,
} from './ship-parts';

// P02-R02: inspired by modern flying-wing stealth bombers (B-2 / B-21): no fuselage and no
// tail, swept leading edges with accent bands, sawtooth trailing edge with elevons, a raised
// cockpit with a dark visor, dorsal intakes feeding 2 reactors, bomb bay doors underneath.
// Wingspan 6 units. Low-poly and polygonal like the other ships: faceted hump and visor.

/** Right half of the planform (X ≥ 0), nose to wing tip to centre line. */
const HALF_WING: readonly OutlinePoint[] = [
  [0, 1.7],
  [3.0, -0.55],
  [2.85, -0.8],
  [1.85, -0.2],
  [1.15, -0.9],
  [0.55, -0.45],
  [0, -0.95],
];
/** Full planform, clockwise from the nose. */
export const HEAVY_PLANFORM: readonly OutlinePoint[] = [
  ...HALF_WING,
  ...mirrorX(HALF_WING.slice(1, -1)).reverse(),
];
/** Accent band just behind the right leading edge. */
const LEADING_BAND: readonly OutlinePoint[] = [
  [0.12, 1.55],
  [2.9, -0.53],
  [2.8, -0.6],
  [0.12, 1.4],
];
/** Elevons along the right sawtooth trailing edge. */
const ELEVONS: readonly (readonly OutlinePoint[])[] = [
  [
    [1.9, -0.12],
    [2.7, -0.6],
    [2.72, -0.69],
    [1.92, -0.21],
  ],
  [
    [0.62, -0.38],
    [1.1, -0.74],
    [1.12, -0.83],
    [0.6, -0.46],
  ],
];
/** Right bomb bay door, under the centre body. */
const BAY_DOOR: readonly OutlinePoint[] = [
  [0.03, 0.55],
  [0.38, 0.5],
  [0.38, -0.3],
  [0.03, -0.35],
];
const WING_THICKNESS = 0.12;
const REACTOR_OFFSET_X = 0.7;
const REACTOR = { radius: 0.2, length: 1.1 };

const SIDES = [
  ['right', 1],
  ['left', -1],
] as const;

function forSide(sign: number, outline: readonly OutlinePoint[]): readonly OutlinePoint[] {
  return sign > 0 ? outline : mirrorX(outline);
}

function buildWing(root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const wing = tagPart(new TransformNode('heavy-wing', scene), 'wing');
  wing.parent = root;
  panel('heavy-wing-panel', HEAVY_PLANFORM, WING_THICKNESS, mats.hull, wing);
  const top = WING_THICKNESS / 2;
  for (const [side, sign] of SIDES) {
    plate(`heavy-band-${side}`, forSide(sign, LEADING_BAND), top, mats.accent, wing);
    ELEVONS.forEach((elevon, i) => {
      plate(`heavy-elevon-${side}-${String(i)}`, forSide(sign, elevon), top, mats.trim, wing);
    });
    plate(`heavy-bay-door-${side}`, forSide(sign, BAY_DOOR), -top, mats.trim, wing);
    navLight(`heavy-wing-${side}-light`, new Vector3(sign * 2.95, 0, -0.6), wing);
  }
}

function buildCockpit(root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const frame = createFacetedLatheAlongZ(
    'heavy-cockpit',
    [
      [1.25, 0],
      [1.15, 0.2],
      [0.95, 0.28],
      [0.7, 0],
    ],
    BODY_SECTION,
    scene,
  );
  frame.scaling.set(1.05, 0.3, 1);
  frame.position.y = 0.13;
  frame.material = mats.trim;
  frame.parent = root;

  // Dark visor set into the front of the cockpit hump.
  const visor = tagPart(
    createFacetedLatheAlongZ(
      'heavy-visor',
      [
        [1.29, 0],
        [1.22, 0.15],
        [1.08, 0.21],
        [0.92, 0],
      ],
      BODY_SECTION,
      scene,
    ),
    'canopy',
  );
  visor.scaling.y = 0.32;
  visor.position.y = 0.15;
  visor.material = mats.canopy;
  visor.parent = root;
  navLight('heavy-dorsal-light', new Vector3(0, 0.22, 0.1), root);
}

function buildCentreBody(root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const body = createFacetedLatheAlongZ(
    'heavy-body',
    [
      [1.65, 0],
      [1.1, 0.3],
      [0.2, 0.5],
      [-0.6, 0.38],
      [-0.85, 0],
    ],
    BODY_SECTION,
    scene,
  );
  body.scaling.set(1.7, 0.42, 1);
  body.material = mats.hull;
  body.parent = tagPart(new TransformNode('heavy-body-root', scene), 'body');
  body.parent.parent = root;
}

function buildIntake(side: string, sign: number, root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const hump = createFacetedLatheAlongZ(
    `heavy-intake-${side}`,
    [
      [0.55, 0],
      [0.55, 0.2],
      [0.2, 0.25],
      [-0.5, 0.24],
      [-0.5, 0],
    ],
    PART_FACETS,
    scene,
  );
  hump.scaling.y = 0.6;
  hump.position.set(sign * REACTOR_OFFSET_X, 0.06, -0.1);
  hump.material = mats.accent;
  hump.parent = root;
  // Dark intake mouth, facing forward.
  const mouth = CreateDisc(
    `heavy-intake-${side}-mouth`,
    { radius: 0.17, tessellation: PART_FACETS },
    scene,
  );
  mouth.convertToFlatShadedMesh();
  mouth.rotation.y = Math.PI;
  mouth.scaling.y = 0.6;
  mouth.position.set(sign * REACTOR_OFFSET_X, 0.06, 0.46);
  mouth.material = mats.canopy;
  mouth.parent = root;
}

/** Builds the heavy player ship (P02-R02). */
export function buildHeavyShip(scene: Scene): TransformNode {
  const root = new TransformNode('ship-heavy', scene);
  buildWing(root, scene);
  buildCentreBody(root, scene);
  buildCockpit(root, scene);
  for (const [side, sign] of SIDES) {
    buildIntake(side, sign, root, scene);
    const reactor = buildReactor(`heavy-reactor-${side}`, REACTOR, scene);
    reactor.position.set(sign * REACTOR_OFFSET_X, 0.05, -0.55);
    reactor.parent = root;
  }
  return root;
}
