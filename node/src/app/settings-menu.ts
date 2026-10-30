import type { MenuDirection } from '../input/menu-action';

/** The two volume settings (P12-R04), each a step from 0 (silent) to the slider's maximum. */
export interface Volumes {
  readonly music: number;
  readonly sfx: number;
}

/** The sliders of the settings screen, in display order. */
export const SETTINGS_SLIDERS: readonly (keyof Volumes)[] = ['music', 'sfx'];

/** What a command did on the settings screen. */
export type SettingsFeedback = 'none' | 'moved' | 'adjusted';

/**
 * The settings screen (P12-R04): up / down pick a slider, left / right change it by one step, a
 * tap or a drag sets it. Pure: the app saves and applies the volumes.
 */
export class SettingsMenu {
  #selection = 0;
  #volumes: Volumes;

  constructor(
    volumes: Volumes,
    private readonly maxStep: number,
  ) {
    this.#volumes = { music: this.#clamp(volumes.music), sfx: this.#clamp(volumes.sfx) };
  }

  get selection(): number {
    return this.#selection;
  }

  get selectedId(): keyof Volumes {
    return SETTINGS_SLIDERS[this.#selection] ?? 'music';
  }

  get volumes(): Volumes {
    return this.#volumes;
  }

  /** The screen opens with the first slider selected. */
  open(): void {
    this.#selection = 0;
  }

  move(direction: MenuDirection): SettingsFeedback {
    if (direction === 'left' || direction === 'right') {
      const current = this.#volumes[this.selectedId];
      return this.set(this.#selection, current + (direction === 'left' ? -1 : 1));
    }
    return this.select(this.#selection + (direction === 'up' ? -1 : 1));
  }

  select(index: number): SettingsFeedback {
    if (!Number.isInteger(index) || index < 0 || index >= SETTINGS_SLIDERS.length) return 'none';
    if (index === this.#selection) return 'none';
    this.#selection = index;
    return 'moved';
  }

  /** Sets slider `index` to `value` (rounded and clamped to the slider) and selects it. */
  set(index: number, value: number): SettingsFeedback {
    const id = SETTINGS_SLIDERS[index];
    if (id === undefined || !Number.isFinite(value)) return 'none';
    const moved = index !== this.#selection;
    this.#selection = index;
    const step = this.#clamp(value);
    if (step === this.#volumes[id]) return moved ? 'moved' : 'none';
    this.#volumes = { ...this.#volumes, [id]: step };
    return 'adjusted';
  }

  #clamp(value: number): number {
    return Math.min(this.maxStep, Math.max(0, Math.round(value)));
  }
}
