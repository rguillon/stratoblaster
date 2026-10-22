import type { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
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

// P02-R03: a faceted tandem-wing interceptor, like a dragonfly. A small front wing pair sits
// low (anhedral) and a larger swept rear pair sits high (dihedral); each of the 4 wings carries
// a hexagonal reactor at its tip, so the front flames stream under the rear wings. Everything
// is polygonal: fuselage with a smooth top and a faceted belly, hexagonal canopy and nacelles, diamond-section cannons.

/** Right front wing (X > 0): short, swept back. */
const FRONT_WING: readonly OutlinePoint[] = [
  [0.18, 1.0],
  [0.85, 0.62],
  [0.85, 0.3],
  [0.18, 0.25],
];
const FRONT_STRIPE: readonly OutlinePoint[] = [
  [0.4, 0.82],
  [0.78, 0.6],
  [0.78, 0.52],
  [0.4, 0.72],
];
/** Right rear wing (X > 0): larger, swept back, with a cranked trailing edge. */
const REAR_WING: readonly OutlinePoint[] = [
  [0.18, -0.1],
  [1.68, -0.66],
  [1.68, -1.0],
  [0.9, -0.95],
  [0.18, -1.2],
];
const REAR_STRIPE: readonly OutlinePoint[] = [
  [0.5, -0.3],
  [1.6, -0.72],
  [1.6, -0.82],
  [0.5, -0.42],
];
/** Darker panel where the rear wing meets the fuselage. */
const REAR_ROOT: readonly OutlinePoint[] = [
  [0.18, -0.1],
  [0.5, -0.22],
  [0.5, -1.08],
  [0.18, -1.2],
];
/** Dorsal blade, standing up (X becomes height). */
const FIN: readonly OutlinePoint[] = [
  [0, -0.35],
  [0.36, -1.0],
  [0.36, -1.18],
  [0, -1.3],
];
/** Canopy profile, `[z, radius]`. */
const CANOPY: readonly ProfilePoint[] = [
  [1.35, 0],
  [1.2, 0.07],
  [0.9, 0.1],
  [0.65, 0],
];
const WING_THICKNESS = 0.05;
const CANNON = { length: 0.9, radius: 0.035 };

/** The 4 wings: front or rear pair, side, tilt around the nose axis and tip reactor. */
export const LIGHT_WINGS = [
  ...(['right', 'left'] as const).map((side) => ({
    name: `front-${side}`,
    pair: 'front' as const,
    side: side === 'right' ? 1 : -1,
    outline: FRONT_WING,
    stripe: FRONT_STRIPE,
    tilt: -0.22, // anhedral: tips down
    reactor: { radius: 0.1, length: 0.7, x: 0.92, z: 0.42 },
  })),
  ...(['right', 'left'] as const).map((side) => ({
    name: `rear-${side}`,
    pair: 'rear' as const,
    side: side === 'right' ? 1 : -1,
    outline: REAR_WING,
    stripe: REAR_STRIPE,
    tilt: 0.16, // dihedral: tips up
    reactor: { radius: 0.13, length: 1.0, x: 1.76, z: -0.78 },
  })),
];

function buildBody(root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const bodyRoot = tagPart(new TransformNode('light-body-root', scene), 'body');
  bodyRoot.parent = root;
  const body = createFacetedLatheAlongZ(
    'light-body',
    [
      [2.15, 0],
      [1.85, 0.08],
      [1.5, 0.15],
      [1.0, 0.21],
      [0.5, 0.25],
      [-0.3, 0.25],
      [-0.9, 0.21],
      [-1.25, 0.15],
      [-1.4, 0],
    ],
    BODY_SECTION,
    scene,
  );
  body.scaling.y = 0.75;
  body.material = mats.hull;
  body.parent = bodyRoot;
  // Accent collar between the cockpit and the wings.
  const collar = createFacetedLatheAlongZ(
    'light-collar',
    [
      [0.2, 0],
      [0.2, 0.27],
      [0.05, 0.27],
      [0.05, 0],
    ],
    BODY_SECTION,
    scene,
  );
  collar.scaling.y = 0.78;
  collar.material = mats.accent;
  collar.parent = bodyRoot;
}

/** Dorsal blade and the twin cannons under the front wing roots. */
function buildFinAndCannons(root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const fin = new TransformNode('light-fin', scene);
  fin.position.y = 0.14;
  fin.rotation.z = Math.PI / 2;
  fin.parent = root;
  panel('light-fin-panel', FIN, 0.04, mats.accent, fin);
  navLight('light-fin-light', new Vector3(0.36, 0, -1.09), fin);

  // Diamond section.
  for (const sign of [1, -1]) {
    const x = sign * 0.3;
    const side = sign > 0 ? 'right' : 'left';
    facetedRod(`light-cannon-${side}`, CANNON, new Vector3(x, -0.1, 1.0), mats.trim, root);
    navLight(`light-cannon-${side}-muzzle`, new Vector3(x, -0.1, 1.0 + CANNON.length / 2), root);
  }
}

function buildCockpit(root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const profile = (scale: number): ProfilePoint[] => CANOPY.map(([z, r]) => [z, r * scale]);
  const frame = createFacetedLatheAlongZ('light-canopy-frame', profile(1.2), PART_FACETS, scene);
  frame.scaling.y = 0.8;
  frame.position.y = 0.1;
  frame.material = mats.trim;
  frame.parent = root;

  const canopy = tagPart(
    createFacetedLatheAlongZ('light-canopy', profile(1), PART_FACETS, scene),
    'canopy',
  );
  canopy.scaling.y = 0.9;
  canopy.position.y = 0.13;
  canopy.material = mats.canopy;
  canopy.parent = root;
}

function buildWing(wingDef: (typeof LIGHT_WINGS)[number], root: TransformNode, scene: Scene): void {
  const mats = getShipMaterials(scene);
  const { name, side, tilt, reactor: pod } = wingDef;
  const forSide = (o: readonly OutlinePoint[]): readonly OutlinePoint[] =>
    side > 0 ? o : mirrorX(o);
  const wing = tagPart(new TransformNode(`light-wing-${name}`, scene), 'wing');
  // Tilt around the nose axis: a positive tilt raises the tip of a right wing.
  wing.rotation.z = side * tilt;
  wing.parent = root;
  panel(`light-wing-${name}-panel`, forSide(wingDef.outline), WING_THICKNESS, mats.hull, wing);
  plate(
    `light-wing-${name}-stripe`,
    forSide(wingDef.stripe),
    WING_THICKNESS / 2,
    mats.accent,
    wing,
  );
  if (wingDef.pair === 'rear') {
    plate(`light-wing-${name}-root`, forSide(REAR_ROOT), WING_THICKNESS / 2, mats.trim, wing);
  }

  const reactor = buildReactor(`light-reactor-${name}`, pod, scene);
  reactor.position.set(side * pod.x, 0, pod.z);
  reactor.parent = wing;
  navLight(
    `light-wing-${name}-light`,
    new Vector3(side * (pod.x + pod.radius), 0, pod.z + pod.length * 0.3),
    wing,
  );
}

/** Builds the light player ship (P02-R03). */
export function buildLightShip(scene: Scene): TransformNode {
  const root = new TransformNode('ship-light', scene);
  buildBody(root, scene);
  buildFinAndCannons(root, scene);
  buildCockpit(root, scene);
  for (const wing of LIGHT_WINGS) buildWing(wing, root, scene);
  return root;
}
