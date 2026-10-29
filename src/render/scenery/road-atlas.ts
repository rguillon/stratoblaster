import type { RoadPiece } from '../../core/scenery/road-tiles';
import type { TileRules } from '../../core/scenery/scenery-level';
import { paintPiece } from './road-paint';
import type { TileRoadLook } from './tile-road-geometry';

// Phase 15 (experiment, reviewer 2026-10-28): the road pieces painted once into one texture, an
// atlas, so each piece is drawn as one surface (no stacked layers to fight in depth). Pure: the
// atlas is an RGBA pixel array; the scenery stage uploads it.

/** Pixels per tile in the atlas. */
export const ATLAS_PX = 64;
/** Pieces up to this many tiles fit in a slot. */
const SLOT_TILES = 3;
/** Pixels repeated round each slot, so mipmaps do not bleed from a neighbour. */
const PAD = 4;
const SLOT = SLOT_TILES * ATLAS_PX + 2 * PAD;
/** Slots per row and per column. */
const SLOTS = 8;
export const ATLAS_SIZE = SLOT * SLOTS;

/** Where a piece is in the atlas: its texture coordinates (u0, v0) to (u1, v1). */
export type AtlasRect = readonly [number, number, number, number];

type Rgb = readonly [number, number, number];

/** Key of a piece's look: its size and its open sides (where it is does not matter). */
const keyOf = (p: RoadPiece): string =>
  `${String(p.size)}:${p.sides.map((s) => (s ? `${String(s.size)}/${String(s.offset)}` : '-')).join(',')}`;

/** The road pieces of one look, painted into the slots of an atlas as they are first asked for. */
export class RoadAtlas {
  readonly data = new Uint8Array(ATLAS_SIZE * ATLAS_SIZE * 4);
  /** Whether pixels changed since the last upload. */
  dirty = false;
  readonly #slots = new Map<string, AtlasRect>();

  constructor(
    private readonly tile: TileRules,
    private readonly look: TileRoadLook,
  ) {}

  /** Where `piece` is in the atlas; undefined when it is larger than a slot or the atlas is full. */
  rectOf(piece: RoadPiece): AtlasRect | undefined {
    const key = keyOf(piece);
    const known = this.#slots.get(key);
    if (known) return known;
    const slot = this.#slots.size;
    if (piece.size > SLOT_TILES || slot >= SLOTS * SLOTS) return undefined;
    const n = piece.size * ATLAS_PX;
    const [sx, sy] = [(slot % SLOTS) * SLOT, Math.floor(slot / SLOTS) * SLOT];
    this.#blit(paintPiece(piece, this.tile, this.look, n), n, sx, sy);
    const rect: AtlasRect = [
      (sx + PAD) / ATLAS_SIZE,
      (sy + PAD) / ATLAS_SIZE,
      (sx + PAD + n) / ATLAS_SIZE,
      (sy + PAD + n) / ATLAS_SIZE,
    ];
    this.#slots.set(key, rect);
    this.dirty = true;
    return rect;
  }

  /** Writes `pixels` (`n` × `n`) at (sx + PAD, sy + PAD), its edge pixels repeated into the pad. */
  #blit(pixels: readonly Rgb[], n: number, sx: number, sy: number): void {
    const clamp = (v: number): number => Math.min(n - 1, Math.max(0, v));
    for (let y = -PAD; y < n + PAD; y++) {
      for (let x = -PAD; x < n + PAD; x++) {
        const c = pixels[clamp(y) * n + clamp(x)] ?? this.look.sidewalk;
        const o = ((sy + PAD + y) * ATLAS_SIZE + sx + PAD + x) * 4;
        this.data[o] = Math.round(c[0] * 255);
        this.data[o + 1] = Math.round(c[1] * 255);
        this.data[o + 2] = Math.round(c[2] * 255);
        this.data[o + 3] = 255;
      }
    }
  }
}
