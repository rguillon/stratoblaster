// P15-R07, R08: the buildings of the districts laid on tiles (phase 15), split out of
// `prop-placement.ts`.
import { hash2D } from '../math/noise';
import type { Building } from './away-placement';
import { weighted } from './draws';
import type { HeightField } from './height-field';
import type { RoadNetwork } from './road-network';
import { roadPieces, roadTiles, tileKey } from './road-tiles';
import type {
  PropGroupRule,
  PropKindRule,
  PropRules,
  TerrainSection,
  TileRules,
} from './scenery-level';
import type { Block } from './street-grid';
import { packBlock, TileGround, type PackSite, type TileSpot } from './tile-packing';

/** What packing the districts needs from the prop placer. */
export interface DistrictSite {
  readonly field: HeightField;
  readonly rules: PropRules;
  readonly roads: RoadNetwork;
  readonly seed: number;
  /** The building group of the area around (`x`, `z`), among those `section` allows. */
  readonly groupAt: (x: number, z: number, section: TerrainSection) => PropGroupRule | undefined;
  readonly occupy: (building: Building) => void;
}

/** Tiles a kind of whole tiles stands on. */
const area = (kind: PropKindRule): number => (kind.tiles?.[0] ?? 0) * (kind.tiles?.[1] ?? 0);

/**
 * For each kind of whole tiles of a group, the order a tile tries the kinds in when it is drawn
 * first: it, then the others from the largest down, then the lots.
 */
type Tries = Map<PropKindRule | undefined, readonly PropKindRule[]> & {
  readonly kinds: readonly PropKindRule[];
};

function triesOf(group: PropGroupRule, lots: readonly PropKindRule[]): Tries {
  const kinds = group.kinds.filter((k) => k.tiles);
  const byArea = [...kinds].sort((a, b) => area(b) - area(a));
  return Object.assign(
    new Map(kinds.map((k) => [k, [k, ...byArea.filter((o) => o !== k), ...lots]])),
    { kinds },
  );
}

/** A block in whole tiles. */
const tileBlock = (block: Block, t: number) => ({
  x0: Math.round(block.xMin / t),
  x1: Math.round(block.xMax / t),
  z0: Math.round(block.zMin / t),
  z1: Math.round(block.zMax / t),
});

/**
 * Packs the blocks of the districts whose middle `within` accepts with buildings of whole tiles
 * (P15-R07, R08): at scale 1, turned by quarter turns to face a street, then lots where no
 * building of the area's group fits.
 */
export function packDistricts(
  site: DistrictSite,
  within: (z: number) => boolean,
  tiles: TileRules,
): void {
  const t = tiles.size;
  const road = roadTiles(roadPieces(site.roads.roads, tiles));
  const taken = new Set<number>();
  const grounds = new TileGround(site.field, tiles, site.rules);
  const lots = [...(site.rules.lots ?? [])].sort((a, b) => area(b) - area(a));
  const tries = new Map<PropGroupRule, Tries>();
  const take = (spot: TileSpot): void => {
    for (let a = 0; a < spot.w; a++) {
      for (let b = 0; b < spot.d; b++) taken.add(tileKey(spot.x + a, spot.z + b));
    }
    const [x, z] = [(spot.x + spot.w / 2) * t, (spot.z + spot.d / 2) * t];
    const placement = {
      kind: spot.kind.id,
      x,
      y: grounds.lowest(spot),
      z,
      rotation: spot.rotation,
      scale: 1,
    };
    site.occupy({ placement, halfX: (spot.w * t) / 2, halfZ: (spot.d * t) / 2 });
  };
  const free = (x: number, z: number): boolean => {
    const key = tileKey(x, z);
    return !road.has(key) && !taken.has(key) && grounds.fit(x, z, key);
  };
  site.roads.blocks.forEach((block, i) => {
    const cz = (block.zMin + block.zMax) / 2;
    if (!within(cz)) return;
    const { section } = site.field.sectionAt(cz);
    const random = (k: number): number => hash2D(i, k, site.seed * 41 + 7);
    const kindsAt = (x: number, z: number, n: number): readonly PropKindRule[] => {
      const group = site.groupAt((x + 0.5) * t, (z + 0.5) * t, section);
      if (!group) return lots;
      let order = tries.get(group);
      if (!order) tries.set(group, (order = triesOf(group, lots)));
      return order.get(weighted(order.kinds, random(n * 3 + 3)) ?? order.kinds[0]) ?? lots;
    };
    const pack: PackSite = { free, road: (x, z) => road.has(tileKey(x, z)), kindsAt, random };
    packBlock(pack, tileBlock(block, t), section.buildingDensity, take);
  });
}
