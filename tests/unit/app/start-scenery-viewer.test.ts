// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import {
  startSceneryViewer,
  type RunningSceneryViewer,
} from '../../../src/app/start-scenery-viewer';
import { SAMPLE_GAME } from '../../fixtures/sample-game';
import { SCENERY_VIEWER_CONFIG } from '../../../src/config/scenery-viewer';

function start(keyboardTarget?: EventTarget): RunningSceneryViewer {
  return startSceneryViewer(new NullEngine(), SAMPLE_GAME, {
    environment: false,
    doc: document,
    panelParent: document.body,
    statsParent: document.body,
    renderLoop: false,
    ...(keyboardTarget ? { keyboardTarget } : {}),
  });
}

function text(selector: string): string {
  return document.querySelector(selector)?.textContent ?? '';
}

describe('startSceneryViewer', () => {
  let viewer: RunningSceneryViewer | undefined;
  afterEach(() => {
    viewer?.dispose();
    viewer = undefined;
    document.body.replaceChildren();
  });

  it('P04-R06: scrolls the first scenery level for its whole duration, then shows the end', () => {
    viewer = start();
    // The sample level: 2 sections of 10 s.
    expect(viewer.track.duration).toBe(20);
    expect(text('.scenery-title')).toBe('Sample ground');
    for (let i = 0; i < 60; i++) viewer.frame(1 / 30);
    expect(viewer.track.time).toBeCloseTo(2, 1);
    expect(text('.scenery-time')).toBe('Time: 0:01 / 0:20');
    viewer.frame(0.1);
    viewer.key('ArrowRight');
    viewer.key('ArrowRight');
    viewer.frame(0.1);
    expect(viewer.track.ended).toBe(true);
    expect(document.querySelector<HTMLElement>('.scenery-end')?.hidden).toBe(false);
    viewer.key('r');
    viewer.frame(0);
    expect(viewer.track.time).toBe(0);
    expect(document.querySelector<HTMLElement>('.scenery-end')?.hidden).toBe(true);
  });

  it('P04-R06: pauses, fast-forwards and seeks from the controls and keys', () => {
    const keys = new EventTarget();
    viewer = start(keys);
    const press = (key: string) => keys.dispatchEvent(new KeyboardEvent('keydown', { key }));
    const run = (seconds: number) => {
      for (let i = 0; i < seconds * 30; i++) viewer?.frame(1 / 30);
    };
    press('p');
    run(0.5);
    expect(viewer.track.time).toBe(0);
    press('p');
    press('f');
    run(0.5);
    expect(viewer.track.time).toBeCloseTo(0.5 * SCENERY_VIEWER_CONFIG.fastForward, 1);
    document.querySelector<HTMLButtonElement>('.scenery-fast')?.click();
    expect(viewer.track.timeScale).toBe(1);
    const slider = document.querySelector<HTMLInputElement>('.scenery-time-slider');
    if (!slider) throw new Error('no time slider');
    slider.value = '12';
    slider.dispatchEvent(new Event('input'));
    expect(viewer.track.time).toBe(12);
  });

  it('P04-R05: the camera looks down at the tilt of the game, over the playfield', () => {
    viewer = start();
    viewer.frame(0);
    const camera = viewer.stage.camera;
    const direction = camera.getDirection(new Vector3(0, 0, 1));
    const tilt = Math.acos(-direction.y) * (180 / Math.PI);
    expect(tilt).toBeCloseTo(SAMPLE_GAME.view.scenery.camera.tiltDeg, 3);
    expect(direction.z).toBeGreaterThan(0);
    expect(viewer.scene.getTransformNodeByName('scenery-ship')?.position.y).toBe(
      SAMPLE_GAME.view.scenery.camera.flightAltitude,
    );
  });

  it('P04-R02, P04-R03: switches the sea and the cloud layers, and their sliders', () => {
    const keys = new EventTarget();
    viewer = start(keys);
    const press = (key: string) => keys.dispatchEvent(new KeyboardEvent('keydown', { key }));
    expect(viewer.stage.seaEnabled).toBe(true);
    press('s');
    expect(viewer.stage.seaEnabled).toBe(false);
    press('1');
    expect(viewer.stage.clouds[0]?.enabled).toBe(false);
    press('1');
    const coverage = document.querySelector<HTMLInputElement>('.scenery-coverage');
    if (!coverage) throw new Error('no coverage slider');
    coverage.value = '80';
    coverage.dispatchEvent(new Event('input'));
    expect(viewer.stage.clouds[0]).toEqual({ enabled: true, coverage: 0.8, opacity: 0.6 });
  });

  it('P04-R01, P04-R04: a new seed rebuilds the ground and its props', () => {
    viewer = start();
    viewer.frame(0);
    expect(viewer.stage.stats.props).toBeGreaterThan(0);
    const before = viewer.stage.field.height(13, 57);
    document.querySelector<HTMLButtonElement>('.scenery-new-seed')?.click();
    viewer.frame(0);
    expect(viewer.stage.seed).toBe(8);
    expect(viewer.stage.field.height(13, 57)).not.toBe(before);
    expect(text('.scenery-seed') + text('.scenery-props')).toContain('Props:');
    expect(document.querySelector('.stats-tile')).not.toBeNull();
  });

  it('P04: the playfield outline toggles with O', () => {
    viewer = start();
    const frame = viewer.scene.getTransformNodeByName('playfield-frame');
    expect(frame?.isEnabled()).toBe(false);
    viewer.key('o');
    expect(frame?.isEnabled()).toBe(true);
  });
});
