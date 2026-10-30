import type { Scene } from '@babylonjs/core/scene';
import { PBRMaterial } from '@babylonjs/core/Materials/PBR/pbrMaterial';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { SHIP_LOOK } from '../config/ship-look';
import { READABILITY } from '../config/readability';

/** Materials shared by all the player ships of a scene. */
export interface ShipMaterials {
  readonly hull: PBRMaterial;
  readonly accent: PBRMaterial;
  readonly canopy: PBRMaterial;
  /** Darker metal for panel lines, frames, intakes and barrels. */
  readonly trim: PBRMaterial;
  /** Small blue lights (wing tips, tails, cannon muzzles). */
  readonly navLight: StandardMaterial;
  readonly nozzle: PBRMaterial;
  readonly reactorCore: StandardMaterial;
  readonly reactorExhaust: StandardMaterial;
  readonly reactorFlame: StandardMaterial;
  readonly reactorPlasma: StandardMaterial;
}

type Rgb = readonly [number, number, number];
interface MetalLook {
  readonly albedo: Rgb;
  readonly metallic: number;
  readonly roughness: number;
}

const CACHE = new WeakMap<Scene, ShipMaterials>();

function metal(name: string, look: MetalLook, scene: Scene): PBRMaterial {
  const mat = new PBRMaterial(name, scene);
  mat.albedoColor = new Color3(...look.albedo);
  mat.metallic = look.metallic;
  mat.roughness = look.roughness;
  mat.directIntensity = READABILITY.hullLight.direct;
  mat.environmentIntensity = READABILITY.hullLight.environment;
  return mat;
}

function light(name: string, emissive: Rgb, scene: Scene): StandardMaterial {
  const mat = new StandardMaterial(name, scene);
  mat.emissiveColor = new Color3(...emissive);
  mat.diffuseColor = Color3.Black();
  mat.specularColor = Color3.Black();
  mat.disableLighting = true;
  return mat;
}

function glow(
  name: string,
  look: { emissive: Rgb; alpha: number },
  scene: Scene,
): StandardMaterial {
  const mat = light(name, look.emissive, scene);
  mat.alpha = look.alpha;
  mat.backFaceCulling = false;
  return mat;
}

function createShipMaterials(scene: Scene): ShipMaterials {
  const canopy = metal('ship-canopy', SHIP_LOOK.canopy, scene);
  canopy.emissiveColor = new Color3(...SHIP_LOOK.canopy.emissive);
  const reactorCore = light('ship-reactor-core', SHIP_LOOK.reactorCore.emissive, scene);
  reactorCore.backFaceCulling = false;
  return {
    hull: metal('ship-hull', SHIP_LOOK.hull, scene),
    accent: metal('ship-accent', SHIP_LOOK.accent, scene),
    canopy,
    trim: metal('ship-trim', SHIP_LOOK.trim, scene),
    navLight: light('ship-nav-light', SHIP_LOOK.navLight.emissive, scene),
    nozzle: metal('ship-nozzle', SHIP_LOOK.nozzle, scene),
    reactorCore,
    reactorExhaust: glow('ship-reactor-exhaust', SHIP_LOOK.reactorExhaust, scene),
    reactorFlame: glow('ship-reactor-flame', SHIP_LOOK.reactorFlame, scene),
    reactorPlasma: glow('ship-reactor-plasma', SHIP_LOOK.reactorPlasma, scene),
  };
}

/** Returns the scene's ship materials, creating them on first use. */
export function getShipMaterials(scene: Scene): ShipMaterials {
  let materials = CACHE.get(scene);
  if (!materials) {
    materials = createShipMaterials(scene);
    CACHE.set(scene, materials);
  }
  return materials;
}
