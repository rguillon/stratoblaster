import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import {
  any,
  frontLights,
  gable,
  lamp,
  plot,
  r,
  windows,
  type Rgb,
  type TileKit,
} from './tile-kit';

// Phase 15 (P15-R09): the works made for the grid of tiles: outposts, mines, oil, refineries,
// factories, warehouses, docks and the foundries of heavy industry. See `tile-kit.ts`.

const SHEDS = [C.corrugated, C.metal, C.concrete, C.rust] as const;
const CONTAINERS = [C.containerBlue, C.containerGreen, C.containerRed, C.rust] as const;

/** Rows of cylinders (tanks, silos) over the plot, `per` tiles apart. */
function cylinders(k: TileKit, radius: number, height: [number, number], color: Rgb) {
  const nx = Math.max(1, Math.floor(k.w / (2 * radius + 1.5)));
  const nz = Math.max(1, Math.floor(k.d / (2 * radius + 1.5)));
  for (let i = 0; i < nx; i++) {
    for (let j = 0; j < nz; j++) {
      const [x, z] = [-k.w / 2 + (k.w / nx) * (i + 0.5), -k.d / 2 + (k.d / nz) * (j + 0.5)];
      const h = r(k, height);
      k.s.cylinder(radius, h, 10, color, { at: [x, 0, z] });
      k.s.cylinder(radius, 0.8, 10, C.metalDark, { at: [x, h, z] }, radius * 0.6);
      k.l.ring(radius + 0.05, 0.25, 10, L.red, { at: [x, h * 0.7, z] });
    }
  }
}

/** A chimney `h` high at (x, z), a glowing ring near its top. */
function chimney(k: TileKit, x: number, z: number, h: number, radius = 0.9): void {
  k.s.cylinder(radius, h, 8, C.concreteDark, { at: [x, 0, z] }, radius * 0.75);
  k.l.ring(radius * 0.8, 0.5, 8, L.red, { at: [x, h - 1.2, z] });
}

export function buildWaterTower(k: TileKit): void {
  plot(k, C.sand);
  for (const [x, z] of [
    [-2, -2],
    [2, -2],
    [-2, 2],
    [2, 2],
  ] as const) {
    k.s.box([0.4, 8, 0.4], C.metalDark, { at: [x, 0, z] });
  }
  k.s.cylinder(3, 3.5, 10, C.silver, { at: [0, 8, 0] }, 2.6);
  k.l.ring(3.05, 0.3, 10, L.cyan, { at: [0, 9.5, 0] });
}

export function buildSolar(k: TileKit): void {
  plot(k, C.sand);
  const rows = Math.max(2, Math.round(k.d / 3));
  for (let i = 0; i < rows; i++) {
    k.s.box([k.w - 1, 0.3, 1.6], C.solar, {
      at: [0, 0.8, -k.d / 2 + (k.d / rows) * (i + 0.5)],
      pitch: 0.3,
    });
  }
  lamp(k, k.w / 2 - 0.5, -k.d / 2 + 0.5);
}

export function buildRadio(k: TileKit): void {
  plot(k, C.sand);
  k.s.box([4, 3, 3], C.concrete, { at: [-1.5, 0, -2] }, C.roof);
  k.s.cylinder(0.4, 14, 4, C.metal, { at: [2, 0, 1.5] }, 0.1);
  k.l.box([0.5, 0.5, 0.5], L.red, { at: [2, 14, 1.5] });
  k.l.box([2.5, 0.4, 0.2], L.window, { at: [-1.5, 1.2, -3.6] });
}

export function buildDepot(k: TileKit): void {
  plot(k, C.sand);
  k.s.box([k.w * 0.6, 5, k.d * 0.5], any(k, SHEDS), { at: [-k.w * 0.15, 0, -k.d * 0.15] });
  gable(k, [k.w * 0.6, k.d * 0.5], 5, 1.5, C.roof, [-k.w * 0.15, -k.d * 0.15]);
  cylindersAt(k, [k.w * 0.3, k.d * 0.25], 1.6, 4);
  frontLights(k, k.w * 0.6, -k.d * 0.4, 4.5, L.yellowDim);
}

function cylindersAt(
  k: TileKit,
  [x, z]: readonly [number, number],
  radius: number,
  h: number,
): void {
  k.s.cylinder(radius, h, 8, C.silver, { at: [x, 0, z] });
}

export function buildHeadframe(k: TileKit): void {
  plot(k, C.ore);
  const h = r(k, [14, 20]);
  for (const [x, z] of [
    [-2, -2],
    [2, -2],
    [-2, 2],
    [2, 2],
  ] as const) {
    k.s.box([0.6, h, 0.6], C.mineYellow, { at: [x * 0.8, 0, z * 0.8 - k.d * 0.15] });
  }
  k.s.cylinder(2, 0.8, 10, C.metalDark, { at: [0, h, -k.d * 0.15], pitch: Math.PI / 2 });
  k.s.box([k.w * 0.5, 6, k.d * 0.3], any(k, SHEDS), { at: [0, 0, k.d * 0.3] }, C.roof);
  k.l.box([0.5, 0.5, 0.5], L.red, { at: [0, h + 1.5, -k.d * 0.15] });
  windows(k, [k.w * 0.5, k.d * 0.3], [1, 5], L.windowDim, [0, k.d * 0.3]);
}

export function buildOreSilos(k: TileKit): void {
  plot(k, C.ore);
  cylinders(k, Math.min(k.w, k.d) / 2 - 1, [8, 12], C.metal);
}

export function buildMineWorks(k: TileKit): void {
  plot(k, C.ore);
  k.s.box([k.w * 0.55, 9, k.d * 0.5], C.corrugated, { at: [-k.w * 0.2, 0, -k.d * 0.2] }, C.roof);
  k.s.box([1.4, 1.4, k.d * 0.7], C.mineYellow, { at: [k.w * 0.15, 5, k.d * 0.05], pitch: -0.3 });
  k.s.lathe(
    [
      [k.w * 0.18, 0],
      [0, k.w * 0.2],
    ],
    7,
    C.ore,
    { at: [k.w * 0.3, 0, k.d * 0.28] },
  );
  chimney(k, -k.w * 0.35, k.d * 0.3, 14);
  windows(k, [k.w * 0.55, k.d * 0.5], [1, 8], L.windowDim, [-k.w * 0.2, -k.d * 0.2]);
}

export function buildPumpjack(k: TileKit): void {
  plot(k, C.sand);
  const n = Math.max(1, Math.round(k.d / 10));
  for (let i = 0; i < n; i++) {
    const z = -k.d / 2 + (k.d / n) * (i + 0.5);
    k.s.box([2.5, 1, 5], C.concreteDark, { at: [0, 0, z] });
    k.s.box([0.6, 4, 0.6], C.metalDark, { at: [0, 1, z] });
    k.s.box([0.7, 0.7, 6.5], C.mineYellow, { at: [0, 4.5, z], pitch: 0.2 });
    k.s.box([1.4, 2, 0.8], C.metalDark, { at: [0, 4.3, z - 3.2], pitch: 0.2 });
    k.l.box([0.3, 0.3, 0.3], L.red, { at: [0, 5.6, z + 2.6] });
  }
}

export function buildOilTanks(k: TileKit): void {
  plot(k, C.sand);
  cylinders(k, Math.min(4, Math.min(k.w, k.d) / 2 - 0.8), [4, 6], C.white);
}

export function buildFlare(k: TileKit): void {
  plot(k, C.concreteDark);
  k.s.cylinder(0.7, 16, 6, C.metal, { at: [0, 0, 0] }, 0.5);
  k.l.lathe(
    [
      [0.6, 16],
      [1, 17.5],
      [0, 19.5],
    ],
    6,
    L.molten,
  );
  k.s.box([3, 2, 2], C.metalDark, { at: [-2.5, 0, -2.5] });
}

export function buildTanks(k: TileKit): void {
  plot(k, C.concreteDark);
  cylinders(
    k,
    Math.min(5, Math.min(k.w, k.d) / 2 - 0.8),
    [5, 8],
    any(k, [C.white, C.silver, C.metal]),
  );
}

export function buildRefinery(k: TileKit): void {
  plot(k, C.concreteDark);
  const n = Math.max(2, Math.round((k.w * k.d) / 120));
  for (let i = 0; i < n; i++) {
    const [x, z] = [r(k, [-k.w / 2 + 2, k.w / 2 - 2]), r(k, [-k.d / 2 + 2, k.d / 2 - 2])];
    const h = r(k, [12, 22]);
    k.s.cylinder(1.4, h, 8, C.silver, { at: [x, 0, z] });
    k.l.ring(1.45, 0.3, 8, L.yellow, { at: [x, h * 0.6, z] });
  }
  k.s.box([k.w - 2, 1, 1], C.metal, { at: [0, 6, 0] });
  k.s.box([1, 1, k.d - 2], C.metal, { at: [0, 6, 0] });
  k.s.box([k.w * 0.4, 4, k.d * 0.25], C.concrete, { at: [-k.w * 0.25, 0, -k.d * 0.33] }, C.roof);
}

export function buildFactory(k: TileKit): void {
  plot(k, C.concreteDark);
  const [w, d] = [k.w - 1, k.d * 0.75];
  const z = (k.d - d) / 2 - 0.5;
  const h = r(k, [8, 12]);
  k.s.box([w, h, d], any(k, SHEDS), { at: [0, 0, z] });
  const teeth = Math.max(2, Math.round(d / 6));
  for (let i = 0; i < teeth; i++) {
    gable(k, [w, d / teeth], h, 2.2, C.roof, [0, z - d / 2 + (d / teeth) * (i + 0.5)]);
  }
  for (let i = 0; i < Math.max(1, Math.round(k.w / 12)); i++) {
    chimney(k, -w / 2 + 2 + i * 6, z + d / 2 - 2, h + r(k, [10, 16]));
  }
  windows(k, [w, d], [1.5, h - 1], L.windowDim, [0, z], 3.5);
  frontLights(k, w, z - d / 2, h - 1.5, any(k, [L.pink, L.cyan]));
}

export function buildWarehouse(k: TileKit): void {
  plot(k, C.concreteDark);
  const [w, d] = [k.w - 1, k.d - 3];
  const h = r(k, [6, 9]);
  k.s.box([w, h, d], any(k, SHEDS), { at: [0, 0, 1] });
  gable(k, [w, d], h, 1.5, C.roof, [0, 1], d > w);
  const doors = Math.max(1, Math.round(w / 5));
  for (let i = 0; i < doors; i++) {
    k.l.box([2.5, 3, 0.2], L.yellowDim, {
      at: [-w / 2 + (w / doors) * (i + 0.5), 0, 1 - d / 2 - 0.1],
    });
  }
}

export function buildContainers(k: TileKit): void {
  plot(k, C.concreteDark);
  const cols = Math.max(1, Math.floor(k.w / 3.5));
  const rows = Math.max(1, Math.floor(k.d / 7));
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      const stack = 1 + Math.floor(k.random() * 2);
      for (let n = 0; n < stack; n++) {
        k.s.box([2.4, 2.5, 6], any(k, CONTAINERS), {
          at: [-k.w / 2 + (k.w / cols) * (i + 0.5), n * 2.5, -k.d / 2 + (k.d / rows) * (j + 0.5)],
        });
      }
    }
  }
  lamp(k, -k.w / 2 + 0.3, -k.d / 2 + 0.3, 8);
}

export function buildCoolingTower(k: TileKit): void {
  plot(k, C.concreteDark);
  const rad = Math.min(k.w, k.d) * 0.36;
  k.s.lathe(
    [
      [rad, 0],
      [rad * 0.72, rad * 1.6],
      [rad * 0.78, rad * 2.2],
    ],
    14,
    C.concrete,
  );
  k.l.ring(rad * 0.74, 0.5, 14, L.red, { at: [0, rad * 2.1, 0] });
  k.s.box([k.w * 0.25, 4, k.d * 0.2], C.metal, { at: [k.w * 0.33, 0, -k.d * 0.36] });
}

export function buildFoundry(k: TileKit): void {
  plot(k, C.rustDark);
  const [w, d] = [k.w - 2, k.d * 0.6];
  const h = r(k, [14, 20]);
  k.s.box([w, h, d], any(k, [C.rust, C.metalDark, C.corrugated]), { at: [0, 0, -k.d * 0.15] });
  gable(k, [w, d], h, 4, C.metalDark, [0, -k.d * 0.15]);
  const mouths = Math.max(2, Math.round(w / 8));
  for (let i = 0; i < mouths; i++) {
    const x = -w / 2 + (w / mouths) * (i + 0.5);
    k.l.box([3, 4, 0.3], L.molten, { at: [x, 0.5, -k.d * 0.15 - d / 2 - 0.15] });
    chimney(k, x, k.d * 0.3, h + r(k, [14, 22]), 1.2);
  }
  k.s.box([w, 1.2, 1.2], C.metal, { at: [0, h * 0.7, k.d * 0.3] });
}

export function buildPlant(k: TileKit): void {
  plot(k, C.concreteDark);
  k.s.box([k.w * 0.5, 16, k.d * 0.45], C.metalDark, { at: [-k.w * 0.22, 0, -k.d * 0.25] }, C.roof);
  windows(k, [k.w * 0.5, k.d * 0.45], [2, 15], L.windowDim, [-k.w * 0.22, -k.d * 0.25], 4);
  const rad = Math.min(k.w, k.d) * 0.16;
  k.s.lathe(
    [
      [rad, 0],
      [rad * 0.72, rad * 1.6],
      [rad * 0.8, rad * 2.2],
    ],
    12,
    C.concrete,
    {
      at: [k.w * 0.25, 0, -k.d * 0.25],
    },
  );
  for (let i = 0; i < 3; i++) {
    k.s.cylinder(2.2, 9, 10, C.silver, { at: [-k.w / 2 + 3 + i * 5.5, 0, k.d * 0.28] });
  }
  chimney(k, k.w * 0.3, k.d * 0.3, 34, 1.4);
  k.s.box([k.w - 2, 1, 1], C.rust, { at: [0, 7, k.d * 0.05] });
}

export function buildDockCrane(k: TileKit): void {
  plot(k, C.concreteDark);
  const long = Math.max(k.w, k.d);
  const alongZ = k.d > k.w;
  for (const a of [-long / 3, long / 3]) {
    const [x, z] = alongZ ? [0, a] : [a, 0];
    k.s.box([1, 14, 1], C.signalOrange, { at: [x - 2, 0, z] });
    k.s.box([1, 14, 1], C.signalOrange, { at: [x + 2, 0, z] });
  }
  k.s.box(alongZ ? [5, 1.5, long - 1] : [long - 1, 1.5, 5], C.signalOrange, { at: [0, 14, 0] });
  k.s.box([2, 2, 3], C.metalDark, { at: [0, 15.5, 0] });
  k.l.box([0.4, 0.4, 0.4], L.red, { at: [0, 17.6, 0] });
}
