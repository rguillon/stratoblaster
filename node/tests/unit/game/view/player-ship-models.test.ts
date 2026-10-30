import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import { PBRMaterial } from '@babylonjs/core/Materials/PBR/pbrMaterial';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { PLAYER_SHIPS } from '../../../../src/game/config/player-ships';
import { PLAYER_SHIP_MODELS } from '../../../../src/game/view/player-ship-models';
import { BALANCED_WING } from '../../../../src/game/view/balanced-ship';
import { HEAVY_PLANFORM } from '../../../../src/game/view/heavy-ship';
import { getShipMaterials } from '../../../../src/game/view/ship-materials';
import { partOf, type ShipPart } from '../../../../src/game/view/ship-parts';
import { SHIP_VIEWER_CONFIG } from '../../../../src/config/ship-viewer';
import { countTriangles } from '../../../../src/render/mesh-stats';
import { at } from '../../../helpers/at';

let scene: Scene;
beforeEach(() => {
  scene = new Scene(new NullEngine());
});
afterEach(() => {
  scene.dispose();
});

function build(id: string): TransformNode {
  const factory = PLAYER_SHIP_MODELS[id];
  if (!factory) throw new Error(`no model for ${id}`);
  const root = factory(scene);
  root.computeWorldMatrix(true);
  for (const node of root.getDescendants(false)) (node as TransformNode).computeWorldMatrix(true);
  return root;
}

function parts(root: TransformNode, part: ShipPart): TransformNode[] {
  return root.getDescendants(false, (n) => partOf(n as TransformNode) === part) as TransformNode[];
}

function isBlue(r: number, g: number, b: number): boolean {
  return b > r && b > g;
}

describe('player ship models', () => {
  it('provides one model per ship of the roster', () => {
    expect(Object.keys(PLAYER_SHIP_MODELS).sort()).toEqual(
      PLAYER_SHIPS.ships.map((s) => s.id).sort(),
    );
  });

  it.each(PLAYER_SHIPS.ships.map((s) => s.id))(
    'P02-R01..R03 / GD-61: %s ship is shiny grey/blue with a blue light behind each reactor',
    (id) => {
      const root = build(id);
      const reactors = parts(root, 'reactor');
      expect(reactors.length).toBeGreaterThan(0);
      const inReactor = new Set(reactors.flatMap((r) => r.getChildMeshes(false)));
      const glass = getShipMaterials(scene).canopy;
      for (const mesh of root.getChildMeshes(false).filter((m) => !inReactor.has(m))) {
        const mat = mesh.material;
        if (mat instanceof StandardMaterial) {
          // Only small blue lights may be unlit.
          expect(partOf(mesh), mesh.name).toBe('light');
          const { r, g, b } = mat.emissiveColor;
          expect(isBlue(r, g, b), mesh.name).toBe(true);
          continue;
        }
        expect(mat, mesh.name).toBeInstanceOf(PBRMaterial);
        if (mat === glass) continue;
        const pbr = mat as PBRMaterial;
        expect(pbr.metallic ?? 0, mesh.name).toBeGreaterThanOrEqual(0.7);
        expect(pbr.roughness ?? 1, mesh.name).toBeLessThanOrEqual(0.35);
        expect(pbr.albedoColor.b, mesh.name).toBeGreaterThan(pbr.albedoColor.r);
      }
      for (const reactor of reactors) {
        const lights = reactor
          .getChildMeshes(false)
          .filter(
            (m): m is AbstractMesh =>
              m.material instanceof StandardMaterial &&
              isBlue(
                m.material.emissiveColor.r,
                m.material.emissiveColor.g,
                m.material.emissiveColor.b,
              ),
          );
        expect(lights.length, reactor.name).toBeGreaterThan(0);
        // Behind the reactor: the ship flies towards +Z.
        for (const light of lights) expect(light.position.z, light.name).toBeLessThan(0);
      }
    },
  );

  it.each(PLAYER_SHIPS.ships.map((s) => s.id))(
    '%s ship fits its slot in the viewer while rotating',
    (id) => {
      const { min, max } = build(id).getHierarchyBoundingVectors(true);
      const reach = Math.max(
        Math.hypot(min.x, min.z),
        Math.hypot(max.x, max.z),
        Math.hypot(min.x, max.z),
        Math.hypot(max.x, min.z),
      );
      expect(reach).toBeLessThan(SHIP_VIEWER_CONFIG.spacing / 2);
    },
  );

  it('P02-R01: balanced ship has dual reactors, forward-swept wings and canted twin tails', () => {
    const root = build('balanced');
    expect(parts(root, 'reactor')).toHaveLength(2);
    expect(parts(root, 'wing')).toHaveLength(2);
    const [rootX, rootZ] = at(BALANCED_WING, 0);
    const [tipX, tipZ] = at(BALANCED_WING, 1);
    expect(tipX).toBeGreaterThan(rootX);
    expect(tipZ, 'wing tip ahead of the wing root').toBeGreaterThan(rootZ);
    const tails = parts(root, 'tail');
    expect(tails).toHaveLength(2);
    for (const tail of tails) {
      const { min, max } = tail.getHierarchyBoundingVectors(true);
      const sign = Math.sign(tail.position.x);
      expect(max.y, `${tail.name} stands up`).toBeGreaterThan(0.6);
      expect(sign * ((min.x + max.x) / 2), `${tail.name} cants outwards`).toBeGreaterThan(
        Math.abs(tail.position.x),
      );
    }
  });

  it('P02-R02: heavy ship is a tailless flying wing with 2 reactors', () => {
    const root = build('heavy');
    expect(parts(root, 'reactor')).toHaveLength(2);
    expect(parts(root, 'tail')).toHaveLength(0);
    const xs = HEAVY_PLANFORM.map(([x]) => x);
    const zs = HEAVY_PLANFORM.map(([, z]) => z);
    const span = Math.max(...xs) - Math.min(...xs);
    const length = Math.max(...zs) - Math.min(...zs);
    expect(span).toBeGreaterThan(2 * length);
  });

  it('P02-R03: light ship has 4 tandem wings, each with its own reactor', () => {
    const root = build('light');
    const wings = parts(root, 'wing');
    expect(wings).toHaveLength(4);
    expect(parts(root, 'reactor')).toHaveLength(4);
    const reactorOf = new Map(
      wings.map((wing) => {
        const reactors = parts(wing, 'reactor');
        expect(reactors, wing.name).toHaveLength(1);
        const p = at(reactors, 0).getAbsolutePosition();
        expect(Math.sign(p.x), `${wing.name} reactor side`).toBe(
          wing.name.includes('right') ? 1 : -1,
        );
        return [wing.name.replace('light-wing-', ''), p] as const;
      }),
    );
    for (const side of ['right', 'left']) {
      const front = reactorOf.get(`front-${side}`);
      const rear = reactorOf.get(`rear-${side}`);
      if (!front || !rear) throw new Error(`missing ${side} wing`);
      // Tandem layout: the front pair is ahead of and lower than the rear pair.
      expect(front.z).toBeGreaterThan(rear.z);
      expect(front.y).toBeLessThan(rear.y);
    }
  });

  it.each(PLAYER_SHIPS.ships.map((s) => s.id))(
    'P02-R01..R03: %s ship stays low-poly (under 2,000 triangles)',
    (id) => {
      expect(countTriangles(build(id))).toBeLessThan(2000);
    },
  );

  it.each(PLAYER_SHIPS.ships.map((s) => s.id))(
    'P02-R01..R03: %s ship is polygonal: only its flames are round',
    (id) => {
      const root = build(id);
      const roundExceptions = /-(exhaust|flame)$/;
      for (const mesh of root.getChildMeshes(false)) {
        if (roundExceptions.test(mesh.name)) continue;
        // Flat shading duplicates vertices per face: a mesh has 3 vertices per triangle.
        expect(mesh.getTotalVertices(), mesh.name).toBe(mesh.getTotalIndices());
      }
    },
  );

  it.each([
    ['balanced', 30],
    ['heavy', 25],
    ['light', 30],
  ] as const)('%s ship is detailed: at least %i parts and blue nav lights', (id, minMeshes) => {
    const root = build(id);
    expect(root.getChildMeshes(false).length).toBeGreaterThanOrEqual(minMeshes);
    expect(parts(root, 'light').length).toBeGreaterThanOrEqual(2);
  });

  it('shares materials between ships of the same scene', () => {
    const a = build('balanced').getChildMeshes(false)[0]?.material;
    const b = build('light').getChildMeshes(false)[0]?.material;
    expect(a).toBeDefined();
    expect(a).toBe(b);
  });
});
