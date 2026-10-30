import { ringAt, type OutlinePoint } from './outline';

type Triangle = [number, number, number];

function cross(o: OutlinePoint, a: OutlinePoint, b: OutlinePoint): number {
  return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
}

function inTriangle(p: OutlinePoint, a: OutlinePoint, b: OutlinePoint, c: OutlinePoint): boolean {
  return cross(a, b, p) >= 0 && cross(b, c, p) >= 0 && cross(c, a, p) >= 0;
}

function cornerAt(ring: readonly number[], i: number): Triangle {
  return [ringAt(ring, i - 1), ringAt(ring, i), ringAt(ring, i + 1)];
}

function isEar(
  points: readonly OutlinePoint[],
  corner: Triangle,
  ring: readonly number[],
): boolean {
  const [a, b, c] = corner.map((j) => ringAt(points, j)) as [
    OutlinePoint,
    OutlinePoint,
    OutlinePoint,
  ];
  if (cross(a, b, c) <= 0) return false;
  return ring.every((j) => corner.includes(j) || !inTriangle(ringAt(points, j), a, b, c));
}

/**
 * Triangulates a simple polygon given counter-clockwise (ear clipping, O(n²)).
 * Returns triangles as index triples into `points`, each counter-clockwise.
 */
export function triangulatePolygon(points: readonly OutlinePoint[]): Triangle[] {
  const ring = points.map((_, i) => i);
  const triangles: Triangle[] = [];
  while (ring.length >= 3) {
    const ear = ring.findIndex((_, i) => isEar(points, cornerAt(ring, i), ring));
    if (ear < 0) throw new Error('The outline is not a simple polygon');
    triangles.push(cornerAt(ring, ear));
    ring.splice(ear, 1);
  }
  return triangles;
}
