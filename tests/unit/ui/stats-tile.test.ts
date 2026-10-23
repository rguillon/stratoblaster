// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { StatsTile } from '../../../src/ui/stats-tile';

describe('StatsTile', () => {
  it('P03 review: shows the frame rate and the polygons drawn', () => {
    const parent = document.createElement('div');
    const tile = new StatsTile(document, parent, 0.25);
    tile.update(0.016, { fps: 59.6, polygons: 12345.4 });
    expect(parent.contains(tile.root)).toBe(true);
    expect(tile.root.querySelector('.stats-fps')?.textContent).toBe('FPS: 60');
    expect(tile.root.querySelector('.stats-polygons')?.textContent).toBe('Polygons: 12,345');
  });

  it('changes the text at most every refresh period', () => {
    const tile = new StatsTile(document, document.createElement('div'), 0.25);
    const fps = () => tile.root.querySelector('.stats-fps')?.textContent;
    tile.update(0.1, { fps: 30, polygons: 1 });
    tile.update(0.1, { fps: 40, polygons: 1 });
    expect(fps()).toBe('FPS: 30');
    tile.update(0.2, { fps: 50, polygons: 1 });
    expect(fps()).toBe('FPS: 50');
  });
});
