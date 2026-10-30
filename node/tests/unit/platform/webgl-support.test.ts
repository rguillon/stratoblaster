import { describe, expect, it } from 'vitest';
import { hasWebGL2 } from '../../../src/platform/webgl-support';

describe('hasWebGL2', () => {
  it('ENG-06: true when a WebGL2 context can be created', () => {
    expect(hasWebGL2(() => ({ getContext: () => ({}) }))).toBe(true);
  });

  it('ENG-06: false when the context is unavailable', () => {
    expect(hasWebGL2(() => ({ getContext: () => null }))).toBe(false);
  });

  it('ENG-06: false when probing throws', () => {
    expect(
      hasWebGL2(() => {
        throw new Error('no canvas');
      }),
    ).toBe(false);
  });
});
