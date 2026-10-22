import { describe, expect, it } from 'vitest';
import { ringAt } from '../../../../src/render/geometry/outline';

describe('ringAt', () => {
  it('wraps indices around the ring in both directions', () => {
    expect(ringAt(['a', 'b', 'c'], 3)).toBe('a');
    expect(ringAt(['a', 'b', 'c'], -1)).toBe('c');
  });

  it('throws on an empty ring', () => {
    expect(() => ringAt([], 0)).toThrow(RangeError);
  });
});
