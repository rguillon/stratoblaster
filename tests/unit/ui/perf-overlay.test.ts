// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { PerfOverlay } from '../../../src/ui/perf-overlay';

const NUMBERS = {
  longFrames: 3,
  longestFrame: 72.4,
  frames: 600,
  lastLoad: 1234,
  longestLoadStep: 180,
};

describe('PerfOverlay', () => {
  it('P13-R01: hidden until toggled, then shows long frames, longest frame and loading time', () => {
    const parent = document.createElement('div');
    const overlay = new PerfOverlay(document, parent, 0.25);
    overlay.update(1, NUMBERS);
    expect(overlay.root.hidden).toBe(true);
    expect(overlay.root.textContent).toBe('');
    overlay.toggle();
    overlay.update(0, NUMBERS);
    expect(overlay.root.textContent).toBe(
      'Long frames: 3\nLongest frame: 72 ms\nLevel load: 1234 ms',
    );
    // Refreshed at most every 0.25 s.
    overlay.update(0.1, { ...NUMBERS, longFrames: 4 });
    expect(overlay.root.textContent).toContain('Long frames: 3');
    overlay.update(0.2, { ...NUMBERS, longFrames: 4, lastLoad: null });
    expect(overlay.root.textContent).toContain('Long frames: 4');
    expect(overlay.root.textContent).toContain('Level load: –');
    overlay.toggle();
    expect(overlay.shown).toBe(false);
    overlay.dispose();
    expect(parent.children).toHaveLength(0);
  });
});
