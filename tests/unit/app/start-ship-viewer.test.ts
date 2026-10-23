import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Camera } from '@babylonjs/core/Cameras/camera';
import { startShipViewer, type RunningShipViewer } from '../../../src/app/start-ship-viewer';
import { SHIP_VIEWER_CONFIG } from '../../../src/config/ship-viewer';
import { SAMPLE_GAME } from '../../fixtures/sample-game';
import { FAKE_DOCUMENT, FakeElement } from '../../helpers/fake-dom';
import { at } from '../../helpers/at';

describe('startShipViewer', () => {
  let viewer: RunningShipViewer | undefined;
  afterEach(() => {
    viewer?.dispose();
    viewer = undefined;
  });

  it('shows every player ship of the game side by side, in roster order', () => {
    viewer = startShipViewer(new NullEngine(), SAMPLE_GAME, { environment: false });
    expect(viewer.showcase.pivots).toHaveLength(2);
    const { pivots } = viewer.showcase;
    expect(at(pivots, 0).position.x).toBeLessThan(at(pivots, 1).position.x);
    expect(viewer.scene.lights.length).toBeGreaterThan(0);
  });

  it('frames the whole row with a fixed horizontal field of view', () => {
    viewer = startShipViewer(new NullEngine(), SAMPLE_GAME, { environment: false });
    const { camera } = viewer;
    expect(camera.fovMode).toBe(Camera.FOVMODE_HORIZONTAL_FIXED);
    const visibleHalfWidth = camera.radius * Math.tan(camera.fov / 2);
    expect(visibleHalfWidth).toBeGreaterThan(viewer.showcase.width / 2);
  });

  it('rotates the ships every rendered frame', () => {
    viewer = startShipViewer(new NullEngine(), SAMPLE_GAME, {
      environment: false,
      frameSeconds: () => 0.5,
    });
    viewer.scene.render();
    viewer.scene.render();
    for (const pivot of viewer.showcase.pivots) {
      expect(pivot.rotation.y).toBeCloseTo(SHIP_VIEWER_CONFIG.rotationSpeedRadPerSec);
    }
  });

  it('uses the engine frame time by default', () => {
    viewer = startShipViewer(new NullEngine(), SAMPLE_GAME, { environment: false });
    viewer.scene.render();
    // NullEngine reports no elapsed time outside its render loop.
    expect(at(viewer.showcase.pivots, 0).rotation.y).toBe(0);
  });

  it('shows a caption with the name, stats and polygon count under each ship', () => {
    const parent = new FakeElement('body');
    viewer = startShipViewer(new NullEngine(), SAMPLE_GAME, {
      environment: false,
      captions: {
        doc: FAKE_DOCUMENT as unknown as Document,
        parent: parent as unknown as HTMLElement,
      },
    });
    const row = at(parent.children, 0);
    expect(row.children.map((c) => c.children[0]?.textContent)).toEqual(['Cube', 'Brick']);
    // Sample ships are boxes: 12 triangles each.
    expect(row.children.map((c) => c.children[3]?.textContent)).toEqual([
      '12 polygons',
      '12 polygons',
    ]);
    viewer.dispose();
    viewer = undefined;
    expect(row.removed).toBe(true);
  });

  it('fails clearly when a ship has no model', () => {
    const game = { ...SAMPLE_GAME, view: { ...SAMPLE_GAME.view, playerShipModels: {} } };
    expect(() => startShipViewer(new NullEngine(), game, { environment: false })).toThrow(
      /no model for player ship "cube"/i,
    );
  });

  it('disposes the scene', () => {
    viewer = startShipViewer(new NullEngine(), SAMPLE_GAME, { environment: false });
    const { scene } = viewer;
    viewer.dispose();
    viewer = undefined;
    expect(scene.isDisposed).toBe(true);
  });
});
