import { describe, expect, it } from 'vitest';
import { groundGlowLook } from '../../../src/app/level-scene';

describe('ground glow (reviewer, 2026-10-28)', () => {
  it('is drawn at full resolution and antialiased, its blur as wide on screen as before', () => {
    expect(groundGlowLook({ intensity: 0.3, blurKernelSize: 16 })).toEqual({
      intensity: 0.3,
      blurKernelSize: 32,
      ratio: 1,
      samples: 4,
    });
  });
});
