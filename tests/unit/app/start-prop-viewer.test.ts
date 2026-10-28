// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { startPropViewer, type RunningPropViewer } from '../../../src/app/start-prop-viewer';
import { GAME } from '../../../src/game';
import { SAMPLE_GAME } from '../../fixtures/sample-game';
import { at } from '../../helpers/at';

describe('startPropViewer (reviewer, 2026-10-28)', () => {
  let viewer: RunningPropViewer | undefined;
  afterEach(() => {
    viewer?.dispose();
    viewer = undefined;
  });

  const start = (game = SAMPLE_GAME) =>
    startPropViewer(new NullEngine(), game, {
      environment: false,
      doc: document,
      panelParent: document.body,
      keyboardTarget: window,
      renderLoop: false,
    });

  it('without groups, shows every prop model in one group, centred on the first', () => {
    viewer = start();
    expect(viewer.groups).toEqual([
      { label: 'Props', ids: Object.keys(SAMPLE_GAME.view.scenery.propModels) },
    ]);
    expect(viewer.props.map((p) => p.id)).toEqual(at(viewer.groups, 0).ids);
    const first = at(viewer.props, 0);
    expect(first.triangles).toBeGreaterThan(0);
    expect(first.root.getChildMeshes().length).toBeGreaterThan(0);
    expect(viewer.camera.target.x).toBeCloseTo(first.root.position.x);
    expect(viewer.panel.root.textContent).toContain(`${first.id} — `);
    viewer.scene.render();
  });

  it('lays out the game’s groups on a grid, props apart, and steps with the arrow keys', () => {
    viewer = start(GAME);
    const labels = viewer.groups.map((g) => g.label);
    expect(labels).toEqual(expect.arrayContaining(['Shared', 'World 1', 'Road kit', 'Cars']));
    const all = viewer.groups.flatMap((g) => g.ids);
    expect(new Set(all).size).toBe(all.length);
    expect(new Set(all)).toEqual(new Set(Object.keys(GAME.view.scenery.propModels)));
    const cars = labels.indexOf('Cars');
    viewer.select({ group: cars, prop: 0 });
    const positions = viewer.props.map(
      (p) => `${String(p.root.position.x)},${String(p.root.position.z)}`,
    );
    expect(new Set(positions).size).toBe(viewer.props.length);
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
    expect(viewer.panel.selection).toEqual({ group: cars, prop: 1 });
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }));
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }));
    expect(viewer.panel.selection.prop).toBe(viewer.props.length - 1);
  });
});
