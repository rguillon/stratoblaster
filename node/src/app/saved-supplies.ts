import type { Supplies } from '../core/systems/level-run-types';
import type { KeyValueStorage } from '../platform/key-value-storage';

/** Storage key of the lives and bombs kept between levels, prefixed with the game's id. */
export function savedSuppliesKey(gameId: string): string {
  return `${gameId}_supplies`;
}

const isCount = (value: unknown, least: number): value is number =>
  typeof value === 'number' && Number.isInteger(value) && value >= least;

/**
 * Parses stored lives and bombs (`{"lives":4,"bombs":6}`). Anything else, or an unreadable
 * value, reads as null: the player starts with the game's starting lives and bombs.
 */
export function parseSupplies(raw: string | null): Supplies | null {
  if (raw === null) return null;
  let value: unknown;
  try {
    value = JSON.parse(raw);
  } catch {
    return null;
  }
  if (typeof value !== 'object' || value === null) return null;
  const { lives, bombs } = value as { lives?: unknown; bombs?: unknown };
  return isCount(lives, 1) && isCount(bombs, 0) ? { lives, bombs } : null;
}

/** The lives and bombs the player kept from the last level completed, or null. */
export function loadSavedSupplies(storage: KeyValueStorage, gameId: string): Supplies | null {
  return parseSupplies(storage.get(savedSuppliesKey(gameId)));
}

/**
 * Keeps the player's lives and bombs when a level is completed, for the next levels (reviewer,
 * 2026-10-28).
 */
export function saveSupplies(storage: KeyValueStorage, gameId: string, supplies: Supplies): void {
  storage.set(savedSuppliesKey(gameId), JSON.stringify(supplies));
}
