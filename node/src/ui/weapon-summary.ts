import type { WeaponDefinition } from '../core/entities/weapon';

function signedAngle(deg: number): string {
  if (deg === 0) return '0°';
  return `${deg > 0 ? '+' : '−'}${String(Math.abs(deg))}°`;
}

function plural(n: number, word: string): string {
  return `${String(n)} ${word}${n === 1 ? '' : 's'}`;
}

/**
 * One-line description of a weapon at a level, for the shots viewer (P03-R10), e.g.
 * "Bullet L3 · 3 streams (0°, −10°, +10°) · 8 shots/s per stream · 10 damage".
 */
export function weaponSummary(weapon: WeaponDefinition, level: number): string {
  const head = `${weapon.name} L${String(level)}`;
  if (weapon.kind === 'beam') {
    const beam = weapon.levels[level - 1];
    if (!beam) return head;
    const pierce =
      level > 1 ? `goes through ${plural(level - 1, 'ship')}` : 'stops at the first ship';
    return `${head} · ${String(beam.damagePerSecond)} damage/s · ${String(beam.width)} px wide · ${pierce}`;
  }
  const streams = weapon.levels[level - 1] ?? [];
  const angles = streams.map((s) => signedAngle(s.angleDeg)).join(', ');
  const area = weapon.blastRadius > 0 ? ` within ${String(weapon.blastRadius)} px` : '';
  return [
    head,
    `${plural(streams.length, 'stream')} (${angles})`,
    `${String(weapon.shotsPerSecond)} shots/s per stream`,
    `${String(weapon.damage)} damage${area}`,
  ].join(' · ');
}
