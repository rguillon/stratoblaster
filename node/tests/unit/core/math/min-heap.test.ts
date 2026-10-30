import { describe, expect, it } from 'vitest';
import { MinHeap } from '../../../../src/core/math/min-heap';
import { createRng } from '../../../../src/core/math/rng';

describe('MinHeap (reviewer, 2026-10-28)', () => {
  it('gives its numbers back smallest first, pushed before or while taking them out', () => {
    const random = createRng(7);
    const heap = new MinHeap([1, 4, 9]);
    const all = [1, 4, 9];
    for (let i = 0; i < 200; i++) {
      const value = Math.floor(random() * 1000);
      heap.push(value);
      all.push(value);
    }
    const out: number[] = [];
    for (let v = heap.pop(); v !== undefined; v = heap.pop()) {
      out.push(v);
      // Pushed while taking out, larger than the last one out: still in order.
      if (out.length === 50) {
        heap.push(v + 0.5);
        all.push(v + 0.5);
      }
    }
    expect(out).toEqual(all.sort((a, b) => a - b));
    expect(heap.size).toBe(0);
    expect(heap.pop()).toBeUndefined();
  });
});
