import { describe, expect, it } from 'vitest';
import type { Road } from '../../../../src/core/scenery/road-network';
import type { RoadRules, SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';
import { checkStreet, FLAT, network, offscreen, RULES } from '../../../helpers/road-network';

/** Where the centre lines of two different roads meet: the point, and the two roads. */
function meetings(roads: readonly Road[]): { x: number; z: number; a: Road; b: Road }[] {
  const out: { x: number; z: number; a: Road; b: Road }[] = [];
  const box = (r: Road) => {
    const xs = r.points.map((p) => p.x);
    const zs = r.points.map((p) => p.z);
    return [Math.min(...xs), Math.max(...xs), Math.min(...zs), Math.max(...zs)] as const;
  };
  roads.forEach((a, i) => {
    const [ax0, ax1, az0, az1] = box(a);
    for (const b of roads.slice(i + 1)) {
      const [bx0, bx1, bz0, bz1] = box(b);
      if (ax1 < bx0 || bx1 < ax0 || az1 < bz0 || bz1 < az0) continue;
      a.points.slice(1).forEach((p2, j) => {
        const p1 = a.points[j];
        if (!p1) return;
        b.points.slice(1).forEach((q2, k) => {
          const q1 = b.points[k];
          if (!q1) return;
          const d = (q2.z - q1.z) * (p2.x - p1.x) - (q2.x - q1.x) * (p2.z - p1.z);
          if (d === 0) return;
          const u = ((q2.x - q1.x) * (p1.z - q1.z) - (q2.z - q1.z) * (p1.x - q1.x)) / d;
          const v = ((p2.x - p1.x) * (p1.z - q1.z) - (p2.z - p1.z) * (p1.x - q1.x)) / d;
          if (u < 0 || u > 1 || v < 0 || v > 1) return;
          out.push({ x: p1.x + u * (p2.x - p1.x), z: p1.z + u * (p2.z - p1.z), a, b });
        });
      });
    }
  });
  return out;
}

/** Whether (x, z) is within `reach` of one end of `road`. */
function atEnd(road: Road, x: number, z: number, reach: number): boolean {
  return [road.points[0], road.points.at(-1)].some(
    (p) => p !== undefined && Math.hypot(p.x - x, p.z - z) <= reach,
  );
}

describe('RoadNetwork without crossings (phase 6 review)', () => {
  const SEPARATE: RoadRules = { ...RULES, noCrossings: { gap: 10 } };
  const [flat] = SAMPLE_SCENERY_LEVEL.sections;
  if (!flat) throw new Error('no section');
  const TOWN: SceneryLevel = {
    ...FLAT,
    sections: [
      { ...flat, name: 'open', seconds: 20 },
      {
        ...flat,
        name: 'town',
        seconds: 15,
        streets: { rows: [30, 40], columns: [25, 35], links: 0.8 },
      },
      { ...flat, name: 'open again', seconds: 15 },
    ],
  };

  it('roads only meet where a path or a street ends on another road, never cross', () => {
    for (const seed of [3, 4, 5, 6]) {
      const n = network(TOWN, SEPARATE, seed);
      expect(n.roads.filter((r) => r.kind === 'cross').length).toBeGreaterThan(0);
      for (const { x, z, a, b } of meetings(n.roads)) {
        const reach = RULES.step * 1.5;
        // One of them ends there (a path or a street), on the other, which is no path.
        const [end, through] = atEnd(a, x, z, reach) ? [a, b] : [b, a];
        const where = `${a.kind}/${b.kind} at ${x.toFixed(0)}, ${z.toFixed(0)}`;
        expect(atEnd(end, x, z, reach), where).toBe(true);
        expect(end.kind, where).not.toBe('main');
        expect(through.kind, where).not.toBe('cross');
        // Both end there only at a street corner.
        if (atEnd(through, x, z, reach))
          expect([end.kind, through.kind]).toEqual(['street', 'street']);
      }
    }
  });

  it('main roads keep at least gap apart', () => {
    for (const seed of [3, 4, 5]) {
      // No paths, which start on the main roads.
      const n = network(FLAT, { ...SEPARATE, crossSpacing: [1e6, 1e6] }, seed);
      const mains = n.roads.filter((r) => r.kind === 'main');
      expect(mains.length).toBeGreaterThanOrEqual(2);
      for (const road of mains) {
        for (const p of road.points) {
          expect(n.edgeDistance(p.x, p.z, road)).toBeGreaterThanOrEqual(10 + p.width / 2 - 1e-6);
        }
      }
    }
  });

  it('a path ends off the screen or on another main road or street', () => {
    for (const seed of [3, 4, 5]) {
      const n = network(TOWN, SEPARATE, seed);
      for (const path of n.roads.filter((r) => r.kind === 'cross')) {
        const end = path.points.at(-1);
        if (!end || offscreen(RULES, end)) continue;
        expect(n.edgeDistance(end.x, end.z, path)).toBeLessThanOrEqual(0);
      }
    }
  });

  it('street grids have T-junctions only: no street runs on through another', () => {
    const n = network(TOWN, SEPARATE);
    const streets = n.roads.filter((r) => r.kind === 'street');
    expect(streets.length).toBeGreaterThan(5);
    for (const street of streets) checkStreet(n, street, [400, 700]);
    const reach = RULES.step / 2;
    expect(meetings(streets).length).toBeGreaterThan(0);
    for (const { x, z, a, b } of meetings(streets)) {
      expect(atEnd(a, x, z, reach) || atEnd(b, x, z, reach)).toBe(true);
    }
  });
});
