import type { KeyValueStorage } from '../platform/key-value-storage';

/** What the menus read from storage at start-up. */
export interface SavedChoices {
  /** Best score so far, 0 when none or unreadable (P01-R04). */
  readonly highScore: number;
  /** Ship chosen last time (P01-R14), or null. */
  readonly lastShipId: string | null;
}

/** Storage keys of a game, prefixed with its id so several games can share a domain. */
export function savedChoiceKeys(gameId: string): { highScore: string; lastShip: string } {
  return { highScore: `${gameId}_high_score`, lastShip: `${gameId}_last_ship` };
}

const SCORE = /^\d{1,15}$/;

/** Parses a stored high score. Anything but a plain non-negative integer reads as 0. */
export function parseHighScore(raw: string | null): number {
  return raw !== null && SCORE.test(raw.trim()) ? Number(raw.trim()) : 0;
}

export function loadSavedChoices(storage: KeyValueStorage, gameId: string): SavedChoices {
  const keys = savedChoiceKeys(gameId);
  return {
    highScore: parseHighScore(storage.get(keys.highScore)),
    lastShipId: storage.get(keys.lastShip),
  };
}

export function saveLastShip(storage: KeyValueStorage, gameId: string, shipId: string): void {
  storage.set(savedChoiceKeys(gameId).lastShip, shipId);
}

/** Saves `score` as the new high score (GD-51, P11-R03). */
export function saveHighScore(storage: KeyValueStorage, gameId: string, score: number): void {
  storage.set(savedChoiceKeys(gameId).highScore, String(Math.max(0, Math.floor(score))));
}
