// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Camera } from '@babylonjs/core/Cameras/camera';
import { startShotViewer, type RunningShotViewer } from '../../../src/app/start-shot-viewer';
import { SAMPLE_GAME, SAMPLE_SHOT_RENDERERS } from '../../fixtures/sample-game';
import { SHOT_VIEWER_CONFIG } from '../../../src/config/shot-viewer';

function start(keyboardTarget?: EventTarget): RunningShotViewer {
  return startShotViewer(new NullEngine(), SAMPLE_GAME, {
    environment: false,
    doc: document,
    panelParent: document.body,
    renderLoop: false,
    ...(keyboardTarget ? { keyboardTarget } : {}),
  });
}

describe('startShotViewer', () => {
  let viewer: RunningShotViewer | undefined;
  afterEach(() => {
    viewer?.dispose();
    viewer = undefined;
  });

  it('P03-R10: looks straight down on the playfield with an orthographic camera', () => {
    viewer = start();
    const camera = viewer.scene.activeCamera;
    expect(camera?.mode).toBe(Camera.ORTHOGRAPHIC_CAMERA);
    expect(camera?.orthoTop).toBe(SAMPLE_GAME.screen.height / 2);
    expect(viewer.scene.getTransformNodeByName('playfield-ship')).not.toBeNull();
  });

  it('P03 review: shots leave just below the tip of the ship nose, measured on the model', () => {
    viewer = start();
    // The sample ship is a unit cube scaled by playerShipScale (10): its nose tip is 5 px above
    // the ship centre.
    const noseY = SHOT_VIEWER_CONFIG.shipY + SAMPLE_GAME.view.playerShipScale / 2;
    expect(viewer.world.muzzleY).toBeCloseTo(noseY - SHOT_VIEWER_CONFIG.muzzleInset);
    expect(viewer.world.centerY).toBe(SHOT_VIEWER_CONFIG.shipY);
  });

  it('P03-R10: fires the first weapon at level 1 and hands each renderer its own shots', () => {
    viewer = start();
    const renderers = SAMPLE_SHOT_RENDERERS.slice(-2);
    viewer.frame(1 / 30);
    expect(viewer.world.weapon.id).toBe('pea');
    expect(viewer.world.activeCount).toBe(1);
    const [pea, ray] = renderers;
    expect(pea?.frames.at(-1)?.projectiles).toHaveLength(1);
    expect(ray?.frames.at(-1)?.projectiles).toHaveLength(0);
    expect(document.body.textContent).toContain('Pea L1');
  });

  it('P03-R10: keyboard shortcuts switch level, weapon, guides and targets', () => {
    const keys = new EventTarget();
    viewer = start(keys);
    const press = (key: string) => keys.dispatchEvent(new KeyboardEvent('keydown', { key }));
    press('2');
    expect(viewer.world.level).toBe(2);
    press('w');
    expect(viewer.world.weapon.id).toBe('ray');
    expect(viewer.world.level).toBe(1);
    press('g');
    expect(viewer.scene.getMeshByName('stream-guides')).not.toBeNull();
    press('t');
    expect(viewer.targets.enabled).toBe(false);
    press('s');
    expect(viewer.panel.selection.ship).toBe(1);
    press('x');
    expect(viewer.panel.selection.ship).toBe(1);
  });

  it('P03-R02: the beam renderer gets the beam while the beam weapon is selected', () => {
    viewer = start();
    viewer.panel.update({ weapon: 1 });
    viewer.frame(1 / 30);
    const ray = SAMPLE_SHOT_RENDERERS.at(-1);
    expect(ray?.weaponId).toBe('ray');
    expect(ray?.frames.at(-1)?.beam.length).toBeGreaterThan(0);
  });

  it('P03 review: shows an FPS and polygon tile when given a place for it', () => {
    const statsParent = document.createElement('div');
    viewer = startShotViewer(new NullEngine(), SAMPLE_GAME, {
      environment: false,
      doc: document,
      panelParent: document.body,
      statsParent,
      renderLoop: false,
      frameSeconds: () => 0.02,
    });
    viewer.frame(0.02);
    viewer.scene.render();
    viewer.frame(0.02);
    expect(statsParent.querySelector('.stats-fps')?.textContent).toMatch(/^FPS: \d+$/);
    expect(statsParent.querySelector('.stats-polygons')?.textContent).toMatch(/^Polygons: [\d,]+$/);
    viewer.dispose();
    viewer = undefined;
    expect(statsParent.querySelector('.stats-tile')).toBeNull();
  });

  it('disposes the renderers and removes the panel', () => {
    viewer = start();
    const renderers = SAMPLE_SHOT_RENDERERS.slice(-2);
    viewer.dispose();
    viewer = undefined;
    expect(renderers.every((r) => r.disposed)).toBe(true);
    expect(document.querySelector('.shot-panel')).toBeNull();
  });
});
