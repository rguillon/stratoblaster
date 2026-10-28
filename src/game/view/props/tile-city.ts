import { PROP_COLORS as C } from '../../config/prop-look';
import { crown, plinth, volume, type LotKit } from './city-lots';
import { any, lamp, NEON, NEON_DIM, plot, r, tree, type Rgb, type TileKit } from './tile-kit';

// Phase 15 (P15-R09): the city made for the grid of tiles: mid-rise blocks, offices, towers and
// skyscrapers, and the lots (car parks, yards, plazas, parks). See `tile-kit.ts`.

const FACADES: readonly Rgb[] = [C.glassBlue, C.glassDark, C.glassGreen, C.concrete, C.white];
const ROOFS: readonly Rgb[] = [C.roof, C.metal, C.metalDark];

function lotKit(k: TileKit, facades: readonly Rgb[], lights: readonly Rgb[]): LotKit {
  return {
    s: k.s,
    l: k.l,
    facade: any(k, facades),
    windows: any(k, lights),
    roof: any(k, ROOFS),
    random: k.random,
  };
}

/**
 * Tiers stepping back from the plot up to `height`, rows of lit windows, neon up two corners
 * on some, and something on top: the city buildings, from mid-rise blocks to skyscrapers.
 */
function stepped(
  k: TileKit,
  height: readonly [number, number],
  tiers: number,
  facades: readonly Rgb[],
) {
  const kit = lotKit(k, facades, NEON_DIM);
  let y = plinth(kit, [0, 0, k.w, k.d]);
  const top = r(k, height);
  let [w, d] = [k.w * r(k, [0.7, 0.85]), k.d * r(k, [0.7, 0.85])];
  for (let t = 0; t < tiers; t++) {
    const h = (top - y) / (tiers - t);
    volume(kit, [0, 0, w, d], y, h);
    if (t === 0 && k.random() < 0.5) {
      const neon = any(k, NEON);
      for (const c of [-1, 1])
        k.l.box([0.4, h - 2, 0.4], neon, { at: [(c * w) / 2, y + 1, -d / 2] });
    }
    y += h;
    [w, d] = [w * r(k, [0.72, 0.88]), d * r(k, [0.72, 0.88])];
  }
  crown(kit, [0, y, 0], Math.min(w, d) * 0.8);
}

export function buildMidrise(k: TileKit): void {
  stepped(k, [16, 28], 1, [C.brick, C.concrete, C.white, C.farmWall]);
}

export function buildOffice(k: TileKit): void {
  stepped(k, [26, 42], 2, FACADES);
}

export function buildTower(k: TileKit): void {
  stepped(k, [44, 66], 2 + Math.floor(k.random() * 2), FACADES);
}

export function buildSkyscraper(k: TileKit): void {
  stepped(k, [70, 110], 2 + Math.floor(k.random() * 2), [C.glassBlue, C.glassDark, C.glassGreen]);
}

export function buildCarPark(k: TileKit): void {
  plot(k, C.metalDark);
  const rows = Math.max(1, Math.round(k.d / 6));
  for (let j = 0; j < rows; j++) {
    const z = -k.d / 2 + (k.d / rows) * (j + 0.5);
    for (let x = -k.w / 2 + 1; x < k.w / 2 - 3; x += 3) {
      k.s.box([0.15, 0.05, 4], C.white, { at: [x, 0.2, z] });
      if (k.random() < 0.5)
        k.s.box([1.6, 1.2, 3.6], any(k, [C.containerRed, C.containerBlue, C.white]), {
          at: [x + 1.5, 0.2, z],
        });
    }
  }
  lamp(k, -k.w / 2 + 0.5, -k.d / 2 + 0.5);
}

export function buildYard(k: TileKit): void {
  plot(k, C.concrete);
  for (let i = 0; i < 4; i++) {
    k.s.box([1.6, 1.2 + k.random(), 1.6], any(k, [C.wood, C.rust, C.containerGreen]), {
      at: [r(k, [-k.w / 2 + 1, k.w / 2 - 1]), 0.2, r(k, [-k.d / 2 + 1, k.d / 2 - 1])],
    });
  }
  lamp(k, k.w / 2 - 0.5, -k.d / 2 + 0.5);
}

export function buildPlaza(k: TileKit): void {
  plot(k, C.paving);
  k.s.cylinder(3, 0.8, 10, C.concreteDark, { at: [0, 0.2, 0] });
  k.l.ring(2.6, 0.3, 10, any(k, NEON), { at: [0, 1, 0] });
  for (const [x, z] of [
    [-1, -1],
    [1, -1],
    [-1, 1],
    [1, 1],
  ] as const) {
    tree(k, (x * k.w) / 3, (z * k.d) / 3, 3);
  }
}

export function buildPark(k: TileKit): void {
  plot(k, C.leaf);
  k.s.box([1.2, 0.05, k.d - 1], C.paving, { at: [0, 0.2, 0], yaw: 0.4 });
  lamp(k, k.w / 2 - 0.5, -k.d / 2 + 0.5);
  const n = Math.max(2, Math.round((k.w * k.d) / 40));
  for (let i = 0; i < n; i++) {
    tree(
      k,
      r(k, [-k.w / 2 + 2.5, k.w / 2 - 2.5]),
      r(k, [-k.d / 2 + 2.5, k.d / 2 - 2.5]),
      r(k, [3, 4]),
    );
  }
}
