import type { Scene } from '@babylonjs/core/scene';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { CreateCylinder } from '@babylonjs/core/Meshes/Builders/cylinderBuilder';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { SHOT_LOOK } from '../../config/shot-look';
import { PLAYER_SHIP_SCALE } from '../../config/ship-look';
import { buildReactorFlame } from '../reactor-flame';

const LOOK = SHOT_LOOK.missile;
const SIDES = 6;
const NOSE_FRACTION = 0.22;
const FIN_LENGTH_FRACTION = 0.25;
const FIN_THICKNESS = 0.03;

function materials(scene: Scene): { body: StandardMaterial; tip: StandardMaterial } {
  const body = new StandardMaterial('missile-body', scene);
  body.diffuseColor = new Color3(...LOOK.body);
  body.specularColor = new Color3(0.6, 0.6, 0.6);
  const tip = new StandardMaterial('missile-tip', scene);
  tip.diffuseColor = new Color3(...LOOK.tip);
  tip.emissiveColor = new Color3(...LOOK.tip).scale(0.5);
  return { body, tip };
}

/** Builds the missile body (along +Z, like the ship models): tube, red nose, four fins. */
function buildBody(name: string, scene: Scene, parent: TransformNode): void {
  const mats = materials(scene);
  const noseLength = LOOK.length * NOSE_FRACTION;
  const tubeLength = LOOK.length - noseLength;
  const tube = CreateCylinder(
    `${name}-tube`,
    { height: tubeLength, diameter: LOOK.radius * 2, tessellation: SIDES },
    scene,
  );
  tube.rotation.x = Math.PI / 2;
  tube.position.z = -noseLength / 2;
  const nose = CreateCylinder(
    `${name}-nose`,
    { height: noseLength, diameterTop: 0, diameterBottom: LOOK.radius * 2, tessellation: SIDES },
    scene,
  );
  nose.rotation.x = Math.PI / 2;
  nose.position.z = LOOK.length / 2 - noseLength / 2;
  tube.material = mats.body;
  nose.material = mats.tip;
  const finLength = LOOK.length * FIN_LENGTH_FRACTION;
  const fins = [0, Math.PI / 2].map((angle, i) => {
    const fin = CreateBox(
      `${name}-fin-${String(i)}`,
      { width: LOOK.finSpan * 2, height: FIN_THICKNESS, depth: finLength },
      scene,
    );
    fin.rotation.z = angle;
    fin.position.z = -LOOK.length / 2 + finLength / 2;
    fin.material = mats.body;
    return fin;
  });
  for (const mesh of [tube, nose, ...fins]) {
    mesh.parent = parent;
    mesh.isPickable = false;
  }
}

/**
 * P03-R03: a small missile with a reactor flame, seen from above on the playfield: the returned
 * pivot lies in the XY plane and points to +Y; turn it about Z to follow the heading.
 */
export function buildMissile(name: string, scene: Scene): TransformNode {
  const pivot = new TransformNode(name, scene);
  const model = new TransformNode(`${name}-model`, scene);
  model.parent = pivot;
  // Model +Z (nose) → playfield +Y; model +Y (top) → -Z, towards the camera.
  model.rotation.x = -Math.PI / 2;
  model.scaling.setAll(PLAYER_SHIP_SCALE);
  buildBody(name, scene, model);
  buildReactorFlame(`${name}-flame`, { nozzleZ: -LOOK.length / 2, ...LOOK.flame }, model);
  return pivot;
}
