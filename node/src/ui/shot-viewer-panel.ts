/** What the shots viewer shows (P03-R10). Indices into the game's ships and weapons. */
export interface ShotViewerSelection {
  readonly ship: number;
  readonly weapon: number;
  /** 1-based. */
  readonly level: number;
  readonly guides: boolean;
  readonly targets: boolean;
}

/** Live numbers shown under the controls. */
export interface ShotViewerReadout {
  readonly summary: string;
  readonly shots: number;
  readonly damagePerSecond: number;
  readonly kills: number;
}

export interface ShotViewerPanelOptions {
  readonly doc: Pick<Document, 'createElement'>;
  readonly parent: HTMLElement;
  readonly ships: readonly string[];
  readonly weapons: readonly string[];
  /** Number of levels of each weapon. */
  readonly levelCounts: readonly number[];
  readonly initial: ShotViewerSelection;
  readonly onChange: (selection: ShotViewerSelection) => void;
}

type Toggle = 'guides' | 'targets';

/**
 * Controls of the shots viewer: a row of buttons per choice (ship, weapon, level) and two
 * toggles, plus readouts. {@link update} changes the selection from code (keyboard shortcuts).
 */
export class ShotViewerPanel {
  readonly root: HTMLElement;
  #selection: ShotViewerSelection;
  readonly #rows = new Map<string, HTMLElement>();
  readonly #readouts = new Map<string, HTMLElement>();

  constructor(private readonly options: ShotViewerPanelOptions) {
    const { doc } = options;
    this.#selection = options.initial;
    this.root = doc.createElement('div');
    this.root.className = 'shot-panel';
    this.#addRow('ship', (ship) => ({ ship }));
    this.#addRow('weapon', (weapon) => ({ weapon }));
    this.#addRow('level', (i) => ({ level: i + 1 }));
    this.#addRow('toggles', (i) => this.#flip(i === 0 ? 'guides' : 'targets'));
    for (const key of ['summary', 'shots', 'damage', 'kills']) {
      const el = doc.createElement('div');
      el.className = `shot-readout shot-${key}`;
      this.#readouts.set(key, el);
      this.root.append(el);
    }
    options.parent.append(this.root);
    this.#render();
  }

  get selection(): ShotViewerSelection {
    return this.#selection;
  }

  /** Changes the selection, keeping the level within the selected weapon's levels. */
  update(change: Partial<ShotViewerSelection>): void {
    const next = { ...this.#selection, ...change };
    const levels = this.options.levelCounts[next.weapon] ?? 1;
    this.#selection = { ...next, level: Math.min(Math.max(1, next.level), levels) };
    this.#render();
    this.options.onChange(this.#selection);
  }

  /** Shows the live numbers. */
  showReadout(readout: ShotViewerReadout): void {
    const set = (key: string, text: string): void => {
      const el = this.#readouts.get(key);
      if (el && el.textContent !== text) el.textContent = text;
    };
    set('summary', readout.summary);
    set('shots', `Shots in flight: ${String(readout.shots)}`);
    set('damage', `Damage/s: ${readout.damagePerSecond.toFixed(1)}`);
    set('kills', `Targets destroyed: ${String(readout.kills)}`);
  }

  #flip(toggle: Toggle): Partial<ShotViewerSelection> {
    return { [toggle]: !this.#selection[toggle] };
  }

  #addRow(name: string, change: (i: number) => Partial<ShotViewerSelection>): void {
    const row = this.options.doc.createElement('div');
    row.className = `shot-row shot-${name}`;
    row.addEventListener('click', (event) => {
      const button = (event.target as HTMLElement).closest('button');
      const index = Number(button?.dataset.index);
      if (button && Number.isInteger(index)) this.update(change(index));
    });
    this.#rows.set(name, row);
    this.root.append(row);
  }

  /** Rebuilds the buttons (the level row depends on the weapon) and marks the selected ones. */
  #render(): void {
    const s = this.#selection;
    const levelLabels = Array.from(
      { length: this.options.levelCounts[s.weapon] ?? 1 },
      (_, i) => `L${String(i + 1)}`,
    );
    this.#fill('ship', this.options.ships, (i) => i === s.ship);
    this.#fill('weapon', this.options.weapons, (i) => i === s.weapon);
    this.#fill('level', levelLabels, (i) => i + 1 === s.level);
    this.#fill('toggles', ['Guides (G)', 'Targets (T)'], (i) => (i === 0 ? s.guides : s.targets));
  }

  #fill(name: string, labels: readonly string[], selected: (i: number) => boolean): void {
    const row = this.#rows.get(name);
    if (!row) return;
    if (row.children.length !== labels.length) {
      row.replaceChildren(
        ...labels.map((label, i) => {
          const button = this.options.doc.createElement('button');
          button.type = 'button';
          button.dataset.index = String(i);
          button.textContent = label;
          return button;
        }),
      );
    }
    [...row.children].forEach((button, i) => {
      button.classList.toggle('selected', selected(i));
      button.setAttribute('aria-pressed', String(selected(i)));
    });
  }
}
