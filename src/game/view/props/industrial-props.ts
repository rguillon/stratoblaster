import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// P04-R04: industrial buildings. Sizes in world units (logical pixels), standing on Y = 0;
// the front faces -Z. Each model is a lit structure plus self-lit accents.

/** Factory hall with a sawtooth roof, two chimneys and a lit strip along the front. */
export function buildFactory(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.box([36, 12, 26], C.concrete, {}, C.roof);
  for (const z of [-8.5, 0, 8.5]) {
    s.box([36, 0.8, 9.5], C.metal, { at: [0, 13.6, z], pitch: -0.45 });
  }
  for (const x of [10, 15]) {
    s.cylinder(2.2, 28, 6, C.rust, { at: [x, 0, 9] }, 1.7);
    l.ring(1.85, 0.8, 6, L.red, { at: [x, 26.5, 9] });
  }
  l.box([30, 0.8, 0.4], L.cyan, { at: [0, 9, -13.2] });
  l.box([6, 4, 0.4], L.yellow, { at: [-12, 0, -13.2] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Three storage tanks with domed tops, joined by pipes, with warning lights on top. */
export function buildStorageTanks(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  const spots: readonly [number, number][] = [
    [-8, -5],
    [8, -5],
    [0, 8],
  ];
  for (const [x, z] of spots) {
    s.lathe(
      [
        [6, 0],
        [6, 14],
        [4.6, 16.4],
        [0, 17.6],
      ],
      8,
      C.white,
      { at: [x, 0, z] },
    );
    l.box([1.2, 1.2, 1.2], L.red, { at: [x, 17.2, z] });
  }
  s.box([18, 1.4, 1.4], C.metalDark, { at: [0, 4, -5] });
  s.box([1.4, 1.4, 12], C.metalDark, { at: [0, 6, 1.5] });
  l.ring(6.15, 0.7, 8, L.yellow, { at: [8, 10, -5] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Long warehouse with a pitched roof, loading doors and a pink sign. */
export function buildWarehouse(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.box([40, 10, 18], C.metal, {}, C.roof);
  s.box([42, 0.8, 10.5], C.rust, { at: [0, 11.3, 4.4], pitch: 0.4 });
  s.box([42, 0.8, 10.5], C.rust, { at: [0, 11.3, -4.4], pitch: -0.4 });
  for (const x of [-12, 0, 12]) {
    s.box([7, 6, 0.4], C.metalDark, { at: [x, 0, -9.1] });
    l.box([7, 0.5, 0.5], L.yellow, { at: [x, 6.3, -9.2] });
  }
  l.box([0.4, 3, 8], L.pink, { at: [20.3, 5, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Concrete cooling tower with a dark mouth and red lights on the rim. */
export function buildCoolingTower(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.lathe(
    [
      [14, 0],
      [11.5, 10],
      [9.2, 24],
      [10.4, 34],
    ],
    10,
    C.concrete,
  );
  s.cylinder(9.9, 0.4, 10, C.metalDark, { at: [0, 34, 0] });
  for (let i = 0; i < 4; i++) {
    const a = (i * Math.PI) / 2;
    l.box([1.2, 1, 1.2], L.red, { at: [10.6 * Math.cos(a), 34, 10.6 * Math.sin(a)] });
  }
  return { structure: s.geometry, lights: l.geometry };
}

/** Phase 4 review: stacks of shipping containers in rows, with a yellow gantry light. */
export function buildContainerYard(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  const colors = [C.containerBlue, C.containerRed, C.containerGreen, C.rust, C.white] as const;
  let n = 0;
  for (const z of [-5, -1.5, 2, 5.5]) {
    for (const x of [-6.5, 0, 6.5]) {
      const stack = 1 + (n % 3);
      for (let level = 0; level < stack; level++) {
        s.box([6, 2.6, 3], colors[(n + level) % colors.length] ?? C.rust, {
          at: [x, level * 2.6, z],
        });
      }
      n++;
    }
  }
  s.box([20, 0.8, 0.8], C.metalDark, { at: [0, 9, -7] });
  s.box([0.8, 9, 0.8], C.metalDark, { at: [-9.6, 0, -7] });
  s.box([0.8, 9, 0.8], C.metalDark, { at: [9.6, 0, -7] });
  l.box([2, 0.6, 1], L.yellow, { at: [0, 8.4, -7] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Phase 4 review: a refinery: three columns joined by pipes, and a flare stack. */
export function buildRefinery(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  const columns = [
    [-5, -2, 2.4, 26],
    [1, -3, 1.8, 20],
    [5, 3, 2, 30],
  ] as const;
  for (const [x, z, radius, height] of columns) {
    s.cylinder(radius, height, 6, C.metal, { at: [x, 0, z] });
    l.ring(radius + 0.1, 0.6, 6, L.yellow, { at: [x, height * 0.6, z] });
  }
  s.box([11, 1, 1], C.rust, { at: [0, 8, -2.5] });
  s.box([1, 1, 7], C.rust, { at: [3, 12, 0] });
  s.box([12, 3, 6], C.concreteDark, { at: [0, 0, 5] }, C.roof);
  s.cylinder(0.6, 34, 4, C.metalDark, { at: [-6, 0, 6] }, 0.4);
  l.box([1.2, 1.6, 1.2], L.red, { at: [-6, 34, 6] });
  return { structure: s.geometry, lights: l.geometry };
}
