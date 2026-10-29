import { describe, expect, it } from 'vitest';
import { TILE } from '../../../../../src/game/config/tile-buildings';
import { PROP_GROUPS } from '../../../../../src/game/view/props/prop-groups';
import {
  ROAD_KIT,
  ROAD_KIT_MODELS,
  ROAD_SAMPLE_ID,
} from '../../../../../src/game/view/props/road-kit';
import { pieceRoadway } from '../../../../../src/render/scenery/tile-road-geometry';

// Phase 15: the road kit (P15-R03, R04) and how the `props/` page shows it (P15-R10).

describe('road kit (phase 15)', () => {
  it('P15-R03, R04: a straight, a turn, a T and an X of each size up to 3 × 3, and the 6 adapters', () => {
    const plain = ROAD_KIT.filter((p) => !p.piece.adapter);
    const adapters = ROAD_KIT.filter((p) => p.piece.adapter);
    expect(plain).toHaveLength(12);
    for (const size of [1, 2, 3]) {
      const kinds = plain.filter((p) => p.piece.size === size).map((p) => p.piece.kind);
      expect(kinds.sort()).toEqual(['cross', 'straight', 'tee', 'turn']);
    }
    expect(adapters).toHaveLength(6);
    expect(new Set(adapters.map((p) => p.piece.kind))).toEqual(new Set(['tee', 'cross']));
  });

  it('P15-R02, R03: every open side has the roadway of the straight of its size, between two sidewalks', () => {
    for (const { id, piece } of ROAD_KIT) {
      const { roadway } = pieceRoadway(piece, TILE);
      const size = piece.size * TILE.size;
      piece.sides.forEach((side, i) => {
        if (!side) return;
        // The roadway rectangles reaching this edge.
        const edge = i === 0 || i === 1 ? size : 0;
        const alongX = i % 2 === 1;
        const reaching = roadway.filter((r) =>
          alongX ? r[0] === edge || r[1] === edge : r[2] === edge || r[3] === edge,
        );
        const spans = reaching.map((r) => (alongX ? [r[2], r[3]] : [r[0], r[1]]));
        const from = side.offset * TILE.size + TILE.sidewalk;
        const to = (side.offset + side.size) * TILE.size - TILE.sidewalk;
        expect(spans, `${id} side ${String(i)}`).toContainEqual([from, to]);
      });
    }
  });

  it('P15-R10: the props page shows the road kit and its sample layout, and footprints in tiles', () => {
    const kit = PROP_GROUPS.find((g) => g.label === 'Road kit');
    expect(kit?.ids.length).toBe(19);
    expect(kit?.ids).toContain(ROAD_SAMPLE_ID);
    expect(ROAD_KIT_MODELS[ROAD_SAMPLE_ID]?.().structure.indices.length).toBeGreaterThan(0);
    const tiles = PROP_GROUPS.filter((g) => g.label.startsWith('Tiles:'));
    expect(tiles.length).toBeGreaterThan(10);
    for (const g of tiles)
      for (const id of g.ids) expect(g.notes?.[id], id).toMatch(/^\d×\d tiles$/);
  });
});
