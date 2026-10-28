import type { PieceSide, PieceSides, RoadPiece } from '../../../core/scenery/road-tiles';
import type { ColoredGeometry } from '../../../render/geometry/gradient-shapes';
import type { PropGeometry, PropModelFactory } from '../../../render/scenery/scenery-look';
import { addPiece, type TileRoadLook } from '../../../render/scenery/tile-road-geometry';
import { BASE_SCENERY_LOOK } from '../../config/scenery-look';
import { TILE } from '../../config/tile-buildings';

// Phase 15 (P15-R03, R04, R10): the road kit, for the `props/` page: a straight, a 90° turn, a T
// and an X for each size, the T and X adapters for each pair of sizes, and a sample layout where
// each piece is joined to the straights of its open sides.

const LOOK: TileRoadLook = BASE_SCENERY_LOOK.roads.tiles;
const SIZES = [1, 2, 3, 4] as const;

/** A named piece of the kit, at tile (0, 0). */
interface KitPiece {
  readonly id: string;
  readonly piece: RoadPiece;
}

const side = (size: number, offset = 0): PieceSide => ({ size, offset });

function kitPiece(id: string, size: number, sides: PieceSides, kind: RoadPiece['kind']): KitPiece {
  const adapter = sides.some((s) => s !== undefined && s.size !== size);
  return { id, piece: { x: 0, z: 0, size, kind, adapter, sides } };
}

/** The 16 pieces of one size each: straight (along Z), turn, T and X. */
const PIECES: readonly KitPiece[] = SIZES.flatMap((n) => {
  const s = side(n);
  return [
    kitPiece(`road-straight-${String(n)}`, n, [s, undefined, s, undefined], 'straight'),
    kitPiece(`road-turn-${String(n)}`, n, [s, s, undefined, undefined], 'turn'),
    kitPiece(`road-tee-${String(n)}`, n, [undefined, s, s, s], 'tee'),
    kitPiece(`road-cross-${String(n)}`, n, [s, s, s, s], 'cross'),
  ];
});

/**
 * The 12 adapters: for each pair N > M, the size-M road ending on (T) or crossing (X) the size-N
 * road, which runs along X; the narrow road as close to the middle as the grid allows.
 */
const ADAPTERS: readonly KitPiece[] = SIZES.flatMap((n) =>
  SIZES.filter((m) => m < n).flatMap((m) => {
    const wide = side(n);
    const narrow = side(m, Math.floor((n - m) / 2));
    const name = `${String(n)}-${String(m)}`;
    return [
      kitPiece(`road-tee-${name}`, n, [undefined, wide, narrow, wide], 'tee'),
      kitPiece(`road-cross-${name}`, n, [narrow, wide, narrow, wide], 'cross'),
    ];
  }),
);

export const ROAD_KIT: readonly KitPiece[] = [...PIECES, ...ADAPTERS];

/** Id of the sample layout. */
export const ROAD_SAMPLE_ID = 'road-sample';

const flat = (): number => 0;

/** `pieces` drawn on flat ground, centred on the origin. */
function geometryOf(pieces: readonly RoadPiece[]): PropGeometry {
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  for (const p of pieces) addPiece(geo, p, TILE, LOOK, flat);
  const xs = pieces.flatMap((p) => [p.x, p.x + p.size]);
  const zs = pieces.flatMap((p) => [p.z, p.z + p.size]);
  const [cx, cz] = [
    ((Math.min(...xs) + Math.max(...xs)) / 2) * TILE.size,
    ((Math.min(...zs) + Math.max(...zs)) / 2) * TILE.size,
  ];
  for (let i = 0; i < geo.positions.length; i += 3) {
    geo.positions[i] = (geo.positions[i] ?? 0) - cx;
    geo.positions[i + 2] = (geo.positions[i + 2] ?? 0) - cz;
  }
  return { structure: geo };
}

/** Steps to the next piece beyond side `i` (+Z, +X, -Z, -X). */
const STEPS = [
  [0, 1],
  [1, 0],
  [0, -1],
  [-1, 0],
] as const;

/** The straight pieces joined to each open side of `piece`, at (x, z). */
function withStubs(piece: RoadPiece, x: number, z: number): RoadPiece[] {
  const placed = { ...piece, x, z };
  const stubs = piece.sides.flatMap((s, i): RoadPiece[] => {
    if (!s) return [];
    const [dx, dz] = STEPS[i] ?? [0, 0];
    const alongZ = dz !== 0;
    const sides: PieceSides = alongZ
      ? [side(s.size), undefined, side(s.size), undefined]
      : [undefined, side(s.size), undefined, side(s.size)];
    const sx = alongZ ? x + s.offset : dx > 0 ? x + piece.size : x - s.size;
    const sz = alongZ ? (dz > 0 ? z + piece.size : z - s.size) : z + s.offset;
    return [{ x: sx, z: sz, size: s.size, kind: 'straight', adapter: false, sides }];
  });
  return [placed, ...stubs];
}

/** The sample layout (P15-R10): every piece of the kit with straights on its open sides. */
function buildSample(): PropGeometry {
  const cell = 4 + 2 * Math.max(...SIZES);
  const columns = 7;
  const pieces = ROAD_KIT.flatMap(({ piece }, i) =>
    withStubs(piece, (i % columns) * cell, Math.floor(i / columns) * cell),
  );
  return geometryOf(pieces);
}

/** The road kit and its sample layout, as models for the `props/` page. */
export const ROAD_KIT_MODELS: Readonly<Record<string, PropModelFactory>> = {
  ...Object.fromEntries(ROAD_KIT.map(({ id, piece }) => [id, () => geometryOf([piece])])),
  [ROAD_SAMPLE_ID]: buildSample,
};

/** What each piece is, shown after its name. */
export const ROAD_KIT_NOTES: Readonly<Record<string, string>> = Object.fromEntries(
  ROAD_KIT.map(({ id, piece }) => [
    id,
    `${String(piece.size)}×${String(piece.size)}${piece.adapter ? ' adapter' : ''}`,
  ]),
);
