import type { MenuDirection } from '../input/menu-action';

/** The entries of the pause menu, in display order (P12-R02). */
export const PAUSE_ENTRIES = ['resume', 'settings', 'main-menu'] as const;

export type PauseEntry = (typeof PAUSE_ENTRIES)[number];

/** What a command did on the pause menu: the flow carries out `resume`, `settings`, `leave`. */
export type PauseOutcome = 'none' | 'moved' | 'ask' | 'resume' | 'settings' | 'leave';

/**
 * The pause menu (P12-R02): Resume, Settings, Main menu. Main menu asks `Leave the level?` with
 * No (selected first) and Yes. Pure: the flow changes screens.
 */
export class PauseMenu {
  #selection = 0;
  #leaving = false;
  /** On the question: 0 No, 1 Yes. */
  #choice = 0;

  get selection(): number {
    return this.#selection;
  }

  get selectedId(): PauseEntry {
    return PAUSE_ENTRIES[this.#selection] ?? 'resume';
  }

  /** Whether the `Leave the level?` question shows. */
  get leaving(): boolean {
    return this.#leaving;
  }

  get choice(): number {
    return this.#choice;
  }

  /** The menu opens on Resume, without the question. */
  open(): void {
    this.#selection = 0;
    this.#leaving = false;
    this.#choice = 0;
  }

  move(direction: MenuDirection): PauseOutcome {
    if (this.#leaving) return this.#choose(direction === 'left' || direction === 'up' ? 0 : 1);
    if (direction === 'left' || direction === 'right') return 'none';
    return this.select(this.#selection + (direction === 'up' ? -1 : 1));
  }

  select(index: number): PauseOutcome {
    if (this.#leaving) return index === 0 || index === 1 ? this.#choose(index) : 'none';
    if (!Number.isInteger(index) || index < 0 || index >= PAUSE_ENTRIES.length) return 'none';
    if (index === this.#selection) return 'none';
    this.#selection = index;
    return 'moved';
  }

  confirm(): PauseOutcome {
    if (this.#leaving) {
      if (this.#choice === 1) return 'leave';
      this.#leaving = false;
      return 'ask';
    }
    switch (this.selectedId) {
      case 'resume':
        return 'resume';
      case 'settings':
        return 'settings';
      case 'main-menu':
        this.#leaving = true;
        this.#choice = 0;
        return 'ask';
    }
  }

  /** Back: closes the question, or resumes the level. */
  back(): PauseOutcome {
    if (!this.#leaving) return 'resume';
    this.#leaving = false;
    return 'ask';
  }

  #choose(choice: number): PauseOutcome {
    if (choice === this.#choice) return 'none';
    this.#choice = choice;
    return 'moved';
  }
}
