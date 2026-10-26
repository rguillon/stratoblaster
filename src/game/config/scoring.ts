/**
 * Scoring (P11-R01, R07): each enemy kind's points are in its data (GD-50); a boss scores its
 * points for its core, and `bossPartShare` of them (rounded to `roundTo`) for each part the
 * player destroys. Life and bomb bonuses picked up at the most score `overflow` instead.
 */
export const SCORING = {
  bossPartShare: 0.1,
  roundTo: 10,
  overflow: { life: 5000, bomb: 2000 },
} as const;

/** The points of one destroyed part of a boss worth `bossPoints` (P11-R01). */
export function bossPartPoints(bossPoints: number): number {
  const { bossPartShare, roundTo } = SCORING;
  return Math.round((bossPoints * bossPartShare) / roundTo) * roundTo;
}
