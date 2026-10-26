import type { KeyValueStorage } from '../platform/key-value-storage';
import type { Volumes } from './settings-menu';

/** Storage keys of the volume settings (P12-R04, D-010), prefixed with the game's id. */
export function savedSettingKeys(gameId: string): { music: string; sfx: string } {
  return { music: `${gameId}_music_volume`, sfx: `${gameId}_sfx_volume` };
}

const STEP = /^\d{1,2}$/;

/** A stored volume step: anything but a whole number from 0 to `maxStep` reads as `fallback`. */
export function parseVolume(raw: string | null, maxStep: number, fallback: number): number {
  const text = raw?.trim() ?? '';
  if (!STEP.test(text)) return fallback;
  const step = Number(text);
  return step <= maxStep ? step : fallback;
}

/** The saved volumes, or the defaults where nothing valid is saved (P12-R04). */
export function loadVolumes(
  storage: KeyValueStorage,
  gameId: string,
  maxStep: number,
  defaults: Volumes,
): Volumes {
  const keys = savedSettingKeys(gameId);
  return {
    music: parseVolume(storage.get(keys.music), maxStep, defaults.music),
    sfx: parseVolume(storage.get(keys.sfx), maxStep, defaults.sfx),
  };
}

/** Saves both volumes (on every change, P12-R04). */
export function saveVolumes(storage: KeyValueStorage, gameId: string, volumes: Volumes): void {
  const keys = savedSettingKeys(gameId);
  storage.set(keys.music, String(volumes.music));
  storage.set(keys.sfx, String(volumes.sfx));
}
