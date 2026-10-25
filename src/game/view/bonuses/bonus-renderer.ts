import type { Scene } from '@babylonjs/core/scene';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import type { ColoredGeometry } from '../../../render/geometry/gradient-shapes';
import type { BonusRenderer } from '../../../render/game-view';
import { NodePool } from '../../../render/node-pool';
import { BONUS_LOOK as LOOK } from '../../config/bonus-look';
import { buildGlowDisc } from '../shot-geometry';
import { additiveTemplate } from '../shots/shot-meshes';
import { buildBonusBadge } from './bonus-geometry';

type Rgb = readonly [number, number, number];

/** A disabled template showing its vertex colours, unlit and opaque (so it glows, GD-61). */
function opaqueTemplate(name: string, geo: ColoredGeometry, scene: Scene): Mesh {
  const mesh = new Mesh(name, scene);
  const data = new VertexData();
  data.positions = geo.positions;
  data.indices = geo.indices;
  data.colors = geo.colors;
  data.applyToMesh(mesh);
  const material = new StandardMaterial(name, scene);
  material.emissiveColor = Color3.White();
  material.diffuseColor = Color3.Black();
  material.specularColor = Color3.Black();
  material.disableLighting = true;
  // Both sides show as it spins.
  material.backFaceCulling = false;
  mesh.material = material;
  mesh.isPickable = false;
  mesh.setEnabled(false);
  return mesh;
}

/** A thin ring at the rim of a disc, black (nothing, added on) inside and out. */
function ring(segments: number, color: Rgb): ColoredGeometry {
  const inside: Rgb[] = Array.from({ length: 6 }, (): Rgb => [0, 0, 0]);
  return buildGlowDisc(segments, [...inside, [0.4, 0.4, 0.4], color, [0, 0, 0]]);
}

/** A pool of clones of `template`, each enabled. */
function pool(template: Mesh): NodePool<Mesh> {
  return new NodePool((i) => {
    const mesh = template.clone(`${template.name}-${String(i)}`);
    mesh.setEnabled(true);
    return mesh;
  });
}

/** A pickup flash in progress. */
interface Flash {
  readonly x: number;
  readonly y: number;
  age: number;
}

/** Ages the `flashes` by `dt`, starts one where each of `picked` was, and draws them as rings. */
function syncFlashes(
  rings: NodePool<Mesh>,
  flashes: Flash[],
  picked: readonly { readonly x: number; readonly y: number }[],
  dt: number,
): void {
  const { size, depth, flash } = LOOK;
  for (const f of flashes) f.age += dt;
  for (const p of picked) flashes.push({ x: p.x, y: p.y, age: 0 });
  const live = flashes.filter((f) => f.age < flash.life);
  flashes.splice(0, flashes.length, ...live);
  rings.show(flashes.length).forEach((mesh, i) => {
    const f = flashes[i];
    if (!f) return;
    const t = f.age / flash.life;
    const radius = size * flash.size * Math.sqrt(Math.max(t, 0.05));
    mesh.position.set(f.x, f.y, depth - 0.5);
    mesh.scaling.set(radius, radius, 1);
    mesh.visibility = 1 - t;
  });
}

/**
 * The weapon bonuses (phase 6 review), in playfield space: each one a badge swinging from side
 * to side over a pulsing halo, and a ring flashing out where the ship picks one up.
 */
export function createBonusRenderer(scene: Scene): BonusRenderer {
  const { size, depth, halo, flash } = LOOK;
  const colors = { frame: LOOK.frame, face: LOOK.face, chevrons: LOOK.chevrons };
  const templates = [
    opaqueTemplate('bonus-badge', buildBonusBadge({ ...colors, inset: LOOK.frameInset }), scene),
    additiveTemplate('bonus-halo', buildGlowDisc(halo.segments, halo.colors), scene),
    additiveTemplate('bonus-flash', ring(flash.segments, flash.color), scene),
  ] as const;
  const [badges, halos, rings] = templates.map(pool) as [
    NodePool<Mesh>,
    NodePool<Mesh>,
    NodePool<Mesh>,
  ];
  const flashes: Flash[] = [];
  return {
    sync: ({ bonuses, picked, dtSeconds }) => {
      badges.show(bonuses.length).forEach((mesh, i) => {
        const bonus = bonuses[i];
        if (!bonus) return;
        mesh.position.set(bonus.x, bonus.y, depth);
        mesh.scaling.setAll(size);
        const { amplitude, hz } = LOOK.swing;
        mesh.rotation.y = amplitude * Math.sin(2 * Math.PI * hz * bonus.age);
      });
      halos.show(bonuses.length).forEach((mesh, i) => {
        const bonus = bonuses[i];
        if (!bonus) return;
        const pulse = 1 + halo.pulse * Math.sin(2 * Math.PI * halo.pulseHz * bonus.age);
        mesh.position.set(bonus.x, bonus.y, depth + 0.5);
        mesh.scaling.set(size * halo.size * pulse, size * halo.size * pulse, 1);
      });
      syncFlashes(rings, flashes, picked, dtSeconds);
    },
    dispose: () => {
      for (const p of [badges, halos, rings]) p.dispose();
      for (const t of templates) t.dispose();
    },
  };
}
