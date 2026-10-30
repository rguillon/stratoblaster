import { describe, expect, it } from 'vitest';
import { applyStageFit, fitStage } from '../../../src/ui/stage-fit';

const LOGICAL = { width: 480, height: 640 };

describe('fitStage', () => {
  it.each([
    [800, 600],
    [1920, 1080],
    [390, 844],
  ])('P01-R13: at %i×%i the stage is fully visible and keeps the 3:4 ratio', (w, h) => {
    const fit = fitStage(w, h, LOGICAL);
    expect(fit.left).toBeGreaterThanOrEqual(0);
    expect(fit.top).toBeGreaterThanOrEqual(0);
    expect(fit.left + fit.width).toBeLessThanOrEqual(w);
    expect(fit.top + fit.height).toBeLessThanOrEqual(h);
    expect(fit.width / fit.height).toBeCloseTo(0.75, 2);
    // It fills the window in one direction.
    expect(Math.max(fit.width / w, fit.height / h)).toBeGreaterThan(0.99);
  });

  it('P01-R13: centres the stage', () => {
    expect(fitStage(800, 600, LOGICAL)).toEqual({
      left: 175,
      top: 0,
      width: 450,
      height: 600,
      scale: 0.9375,
    });
    expect(fitStage(390, 844, LOGICAL)).toMatchObject({
      left: 0,
      width: 390,
      top: 162,
      height: 520,
    });
  });

  it('handles an empty window', () => {
    expect(fitStage(0, 0, LOGICAL)).toMatchObject({ width: 0, height: 0, scale: 0 });
  });
});

describe('applyStageFit', () => {
  it('P01-R13: places the stage and scales the logical-size overlay', () => {
    const stage = { style: {} as CSSStyleDeclaration };
    const overlay = { style: {} as CSSStyleDeclaration };
    applyStageFit(stage, overlay, fitStage(800, 600, LOGICAL), LOGICAL);
    expect(stage.style).toMatchObject({
      left: '175px',
      top: '0px',
      width: '450px',
      height: '600px',
    });
    expect(overlay.style).toMatchObject({
      width: '480px',
      height: '640px',
      transform: 'scale(0.9375)',
    });
  });
});
