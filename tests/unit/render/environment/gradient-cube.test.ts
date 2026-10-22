import { describe, expect, it } from 'vitest';
import {
  buildGradientCubeFaces,
  sampleGradient,
} from '../../../../src/render/environment/gradient-cube';
import { at } from '../../../helpers/at';

const STOPS = [
  { at: -1, color: [0, 0, 0] },
  { at: 1, color: [1, 1, 1] },
] as const;

describe('gradient cube environment', () => {
  it('interpolates colour stops by height and clamps outside them', () => {
    expect(sampleGradient(STOPS, 0)).toEqual([0.5, 0.5, 0.5]);
    expect(sampleGradient(STOPS, 2)).toEqual([1, 1, 1]);
    expect(sampleGradient(STOPS, -2)).toEqual([0, 0, 0]);
  });

  it('builds 6 RGBA faces: +Y is the top colour, -Y the bottom one', () => {
    const faces = buildGradientCubeFaces(4, STOPS);
    expect(faces).toHaveLength(6);
    for (const face of faces) expect(face).toHaveLength(4 * 4 * 4);
    const [top, bottom, side] = [at(faces, 2), at(faces, 3), at(faces, 4)];
    expect(Array.from(top.slice(0, 4))).toEqual([255, 255, 255, 255]);
    expect(Array.from(bottom.slice(0, 4))).toEqual([0, 0, 0, 255]);
    // On a side face the first row is brighter than the last one.
    expect(at(side, 0)).toBeGreaterThan(at(side, side.length - 4));
  });

  it('rejects an empty stop list', () => {
    expect(() => sampleGradient([], 0)).toThrow(/stop/);
  });
});
