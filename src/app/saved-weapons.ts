import type { WeaponLevels } from '../core/systems/run-arsenal';
import type { KeyValueStorage } from '../platform/key-value-storage';

/** Storage key of the weapons kept between levels, prefixed with the game's id. */
export function savedWeaponsKey(gameId: string): string {
  return `${gameId}_weapons`;
}

function isLevel(value: unknown): value is number {
  return typeof value === 'number' && Number.isInteger(value) && value >= 1;
}

/**
 * Parses stored weapons (`{"weapon":"guns","levels":{"guns":3}}`). Anything else, or an
 * unreadable value, reads as null: the player starts with the weapons at their first level.
 */
export function parseWeaponLevels(raw: string | null): WeaponLevels | null {
  if (raw === null) return null;
  let value: unknown;
  try {
    value = JSON.parse(raw);
  } catch {
    return null;
  }
  if (typeof value !== 'object' || value === null) return null;
  const { weapon, levels } = value as { weapon?: unknown; levels?: unknown };
  if (typeof weapon !== 'string' || typeof levels !== 'object' || levels === null) return null;
  const entries = Object.entries(levels);
  if (!entries.every(([, level]) => isLevel(level))) return null;
  return { weapon, levels: Object.fromEntries(entries) };
}

/** The weapons the player kept from the last level completed, or null. */
export function loadSavedWeapons(storage: KeyValueStorage, gameId: string): WeaponLevels | null {
  return parseWeaponLevels(storage.get(savedWeaponsKey(gameId)));
}

/** Keeps the player's weapons when a level is completed, for the next levels. */
export function saveWeapons(storage: KeyValueStorage, gameId: string, weapons: WeaponLevels): void {
  storage.set(savedWeaponsKey(gameId), JSON.stringify(weapons));
}
