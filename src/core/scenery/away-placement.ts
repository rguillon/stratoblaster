import { hash2D } from '../math/noise';
import { between, weighted } from './draws';
import type { PropPlacement } from './prop-placement';
import type {
  HamletRules,
  PropGroupRule,
  PropKindRule,
  PropRules,
  TerrainSection,
} from './scenery-level';

/** A building with the half-extents (X, Z) of the box of ground it takes. */
export interface Building {
  readonly placement: PropPlacement;
  readonly halfX: number;
  readonly halfZ: number;
}

/** What placing buildings away from the roads needs from the prop placer. */
export interface AwaySite {
  /** Length of the level along Z. */
  readonly length: number;
  /** Roads start and end beyond X = ±offscreenX. */
  readonly offscreenX: number;
  readonly seed: number;
  sectionAt(z: number): TerrainSection;
  /** The building group of the area around (`x`, `z`), among those `section` allows. */
  groupAt(x: number, z: number, section: TerrainSection): PropGroupRule | undefined;
  /** Distance to the nearest road edge (Infinity beyond about 60). */
  roadDistance(x: number, z: number): number;
  /** Height of the flat enough ground under a footprint of `radius`, or undefined. */
  ground(x: number, z: number, radius: number): number | undefined;
  /** Adds `building` if it keeps `gap` (default: the road setback) from the others. */
  add(building: Building, gap?: number): boolean;
}

/** Lone buildings and hamlets stand within this share of `offscreenX` of the level's middle… */
const AWAY_SPREAD = 0.5;
/** …and from this far before the level to this far after it (seen at its ends). */
const AWAY_MARGIN = 400;
/** Places a hamlet's centre is tried at. */
const HAMLET_TRIES = 6;
/** Tries per building of a hamlet, and draws per try (direction, distance, kind, scale). */
const BUILDING_TRIES = 4;
const BUILDING_DRAWS = 4;
/** Turns of the buildings of a hamlet around its common heading, in radians. */
const HAMLET_SKEW = 0.3;

/** A building to try: its kind, place, turn and scale. */
interface Candidate {
  readonly kind: PropKindRule;
  readonly x: number;
  readonly z: number;
  readonly rotation: number;
  readonly scale: number;
}

/**
 * `candidate` standing on its own, at least `clearance` from every road edge, or undefined when
 * the roads or the ground do not allow it.
 */
function standalone(site: AwaySite, c: Candidate, clearance: number): Building | undefined {
  const { kind, x, z, rotation, scale } = c;
  const reach = kind.frontage === undefined ? kind.footprint : kind.frontage * scale;
  if (site.roadDistance(x, z) < reach + clearance) return undefined;
  const y = site.ground(x, z, kind.footprint);
  if (y === undefined) return undefined;
  const turned = Math.abs(Math.cos(rotation)) + Math.abs(Math.sin(rotation));
  const half = kind.frontage === undefined ? kind.footprint : kind.frontage * scale * turned;
  return { placement: { kind: kind.id, x, y, z, rotation, scale }, halfX: half, halfZ: half };
}

/** Places `candidate` away from the roads if it fits; whether it did. */
function tryPlace(site: AwaySite, c: Candidate, clearance: number, gap?: number): boolean {
  const building = standalone(site, c, clearance);
  return building !== undefined && site.add(building, gap);
}

/** Hamlets every `spacing` along the level (phase 6 review, see `HamletRules`). */
export function placeHamlets(site: AwaySite, hamlets: HamletRules): void {
  const r = (n: number, draw: number): number => hash2D(n, draw, site.seed * 47 + 13);
  let z = -AWAY_MARGIN + between(hamlets.spacing, r(0, 0));
  for (let n = 1; z < site.length + AWAY_MARGIN; n++) {
    hamlet(site, hamlets, z, (draw) => r(n, draw));
    z += between(hamlets.spacing, r(n, 0));
  }
}

/** Where a hamlet about `z` can stand: away from the roads, on flat ground. */
function hamletCentre(
  site: AwaySite,
  { radius, clearance }: HamletRules,
  z: number,
  r: (draw: number) => number,
): { readonly x: number; readonly z: number } | undefined {
  const half = site.offscreenX * AWAY_SPREAD - radius;
  return Array.from({ length: HAMLET_TRIES }, (_, t) => ({
    x: (2 * r(1 + t) - 1) * half,
    z: z + (r(1 + HAMLET_TRIES + t) - 0.5) * radius,
  })).find(
    (c) =>
      site.roadDistance(c.x, c.z) >= radius + clearance &&
      site.ground(c.x, c.z, radius / 2) !== undefined,
  );
}

/** A hamlet about `z`, if its section has buildings and a place away from the roads. */
function hamlet(
  site: AwaySite,
  hamlets: HamletRules,
  z: number,
  r: (draw: number) => number,
): void {
  const section = site.sectionAt(z);
  if (section.streets || section.buildingDensity <= 0) return;
  const centre = hamletCentre(site, hamlets, z, r);
  const group = centre && site.groupAt(centre.x, centre.z, section);
  if (!centre || !group) return;
  const count = Math.round(between(hamlets.buildings, r(20)));
  // All turned about the same way, as in a village.
  const heading = Math.floor(r(21) * 4) * (Math.PI / 2);
  let placed = 0;
  for (let k = 0; placed < count && k < count * BUILDING_TRIES; k++) {
    const d = (draw: number): number => r(30 + k * BUILDING_DRAWS + draw);
    const kind = weighted(group.kinds, d(2));
    if (!kind) return;
    const [angle, distance] = [d(0) * 2 * Math.PI, Math.sqrt(d(1)) * hamlets.radius];
    const candidate = {
      kind,
      x: centre.x + Math.sin(angle) * distance,
      z: centre.z + Math.cos(angle) * distance,
      rotation: heading + (d(3) - 0.5) * HAMLET_SKEW,
      scale: between(kind.scale, d(3)),
    };
    if (tryPlace(site, candidate, hamlets.clearance, hamlets.gap)) placed++;
  }
}

/** A few lone buildings away from the roads (phase 6 review, see `PropRules.loners`). */
export function placeLoners(site: AwaySite, loners: NonNullable<PropRules['loners']>): void {
  const { cell } = loners;
  const half = site.offscreenX * AWAY_SPREAD;
  const [i0, i1] = [Math.floor(-half / cell), Math.ceil(half / cell)];
  const [j0, j1] = [Math.floor(-AWAY_MARGIN / cell), Math.ceil((site.length + AWAY_MARGIN) / cell)];
  for (let j = j0; j < j1; j++) {
    for (let i = i0; i < i1; i++) loner(site, loners, i, j);
  }
}

/** The lone building of cell (`i`, `j`), if it gets one. */
function loner(
  site: AwaySite,
  { cell, chance, clearance }: NonNullable<PropRules['loners']>,
  i: number,
  j: number,
): void {
  const r = (draw: number): number => hash2D(i, j, site.seed * 43 + 7 + draw);
  const [x, z] = [(i + r(0)) * cell, (j + r(1)) * cell];
  const section = site.sectionAt(z);
  if (section.streets || r(2) >= chance * section.buildingDensity) return;
  const kind = weighted(site.groupAt(x, z, section)?.kinds ?? [], r(3));
  if (!kind) return;
  const rotation = r(4) * 2 * Math.PI;
  tryPlace(site, { kind, x, z, rotation, scale: between(kind.scale, r(5)) }, clearance);
}
