import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { Camera } from '@babylonjs/core/Cameras/camera';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import { ShipSelectStage } from '../../../src/render/ship-select-stage';
import { MENU_CONFIG } from '../../../src/config/menu';
import { at } from '../../helpers/at';

const box = (s: Scene) => CreateBox('ship', { size: 1 }, s);

const ids = (meshes: readonly { uniqueId: number }[]) => meshes.map((m) => m.uniqueId);

describe('ShipSelectStage', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
    scene = undefined;
  });

  function setup(): ShipSelectStage {
    scene = new Scene(new NullEngine());
    return new ShipSelectStage(scene, [box, box, box], MENU_CONFIG.shipSelect);
  }

  it('P01-R06: shows the ships side by side, framed by a fixed horizontal field of view', () => {
    const stage = setup();
    expect(stage.showcase.pivots).toHaveLength(3);
    expect(stage.camera.fovMode).toBe(Camera.FOVMODE_HORIZONTAL_FIXED);
    const visibleHalfWidth = stage.camera.radius * Math.tan(stage.camera.fov / 2);
    expect(visibleHalfWidth).toBeGreaterThan(stage.showcase.width / 2);
  });

  it('P01-R06: the highlighted ship is bigger, lit by the spot and sits on the ring', () => {
    const stage = setup();
    const [first, second] = [at(stage.showcase.pivots, 0), at(stage.showcase.pivots, 1)];
    expect(first.scaling.x).toBeCloseTo(MENU_CONFIG.shipSelect.highlightScale);
    expect(second.scaling.x).toBeCloseTo(MENU_CONFIG.shipSelect.dimScale);
    expect(ids(stage.spot.includedOnlyMeshes)).toEqual(ids(first.getChildMeshes(false)));
    expect(stage.ring.position.x).toBe(first.position.x);

    stage.select(1);
    expect(stage.selected).toBe(1);
    expect(stage.ring.position.x).toBe(second.position.x);
    expect(ids(stage.spot.includedOnlyMeshes)).toEqual(ids(second.getChildMeshes(false)));
    // P13-R02: each ship keeps its own key light; only the highlighted one is on.
    const spots = stage.scene.lights.filter((l) => l.name.startsWith('ship-select-spot'));
    expect(spots.map((l) => l.intensity > 0)).toEqual(spots.map((l) => l === stage.spot));
    expect(spots).toHaveLength(stage.showcase.pivots.length);
    stage.update(0.05);
    expect(second.scaling.x).toBeGreaterThan(MENU_CONFIG.shipSelect.dimScale);
    expect(first.scaling.x).toBeLessThan(MENU_CONFIG.shipSelect.highlightScale);
    for (let i = 0; i < 100; i++) stage.update(0.05);
    expect(second.scaling.x).toBeCloseTo(MENU_CONFIG.shipSelect.highlightScale);
    expect(first.scaling.x).toBeCloseTo(MENU_CONFIG.shipSelect.dimScale);
  });

  it('P01-R06: rotates the ships at ship_select_rotation_speed', () => {
    const stage = setup();
    stage.update(1);
    expect(at(stage.showcase.pivots, 2).rotation.y).toBeCloseTo(0.5);
  });

  it('clamps the selection to the available ships', () => {
    const stage = setup();
    stage.select(9);
    expect(stage.selected).toBe(2);
    stage.select(-1);
    expect(stage.selected).toBe(0);
  });
});
