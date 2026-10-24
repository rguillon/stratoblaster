/** What the enemies page shows (P05-R11). Indices into the game's enemy kinds and weapons. */
export interface EnemyViewerSelection {
  readonly kind: number;
  /** `behaviour`: the enemy flies and attacks; `model`: its model alone, turning. */
  readonly view: 'behaviour' | 'model' | 'wireframe';
  readonly weapon: number;
  /** 1-based. */
  readonly level: number;
  readonly fire: boolean;
  readonly paused: boolean;
}

/** Live numbers shown under the controls. */
export interface EnemyViewerReadout {
  readonly enemies: number;
  readonly shots: number;
  readonly kills: number;
  readonly score: number;
}

export interface EnemyViewerPanelOptions {
  readonly doc: Pick<Document, 'createElement'>;
  readonly parent: HTMLElement;
  readonly kinds: readonly string[];
  readonly weapons: readonly string[];
  /** Number of levels of each weapon. */
  readonly levelCounts: readonly number[];
  readonly initial: EnemyViewerSelection;
  /** A line about the keys, under the readouts. */
  readonly help: string;
  readonly onChange: (selection: EnemyViewerSelection) => void;
}

const VIEWS = ['behaviour', 'model', 'wireframe'] as const;

/**
 * Controls of the enemies page: a button per enemy kind, the view (behaviour, model or
 * wireframe), the player's weapon and level, fire and pause toggles, and readouts. {@link update}
 * changes the selection from code (keyboard shortcuts).
 */
export class EnemyViewerPanel {
  readonly root: HTMLElement;
  #selection: EnemyViewerSelection;
  readonly #rows = new Map<string, HTMLElement>();
  readonly #readouts = new Map<string, HTMLElement>();

  constructor(private readonly options: EnemyViewerPanelOptions) {
    const { doc } = options;
    this.#selection = options.initial;
    this.root = doc.createElement('div');
    this.root.className = 'enemy-panel';
    const title = doc.createElement('div');
    title.className = 'enemy-title';
    title.textContent = 'Enemies';
    this.root.append(title);
    this.#addRow('kind', (kind) => ({ kind }));
    this.#addRow('view', (i) => ({ view: VIEWS[i] ?? 'behaviour' }));
    this.#addRow('weapon', (weapon) => ({ weapon }));
    this.#addRow('level', (i) => ({ level: i + 1 }));
    this.#addRow('toggles', (i) =>
      i === 0 ? { fire: !this.#selection.fire } : { paused: !this.#selection.paused },
    );
    for (const key of ['enemies', 'shots', 'kills', 'score']) {
      const el = doc.createElement('div');
      el.className = `enemy-readout enemy-${key}`;
      this.#readouts.set(key, el);
      this.root.append(el);
    }
    const help = doc.createElement('div');
    help.className = 'enemy-help';
    help.textContent = options.help;
    this.root.append(help);
    options.parent.append(this.root);
    this.#render();
  }

  get selection(): EnemyViewerSelection {
    return this.#selection;
  }

  /** Changes the selection, keeping the indices and the level in range. */
  update(change: Partial<EnemyViewerSelection>): void {
    const next = { ...this.#selection, ...change };
    const clamp = (v: number, n: number): number => Math.min(Math.max(0, v), Math.max(0, n - 1));
    const kind = clamp(next.kind, this.options.kinds.length);
    const weapon = clamp(next.weapon, this.options.weapons.length);
    const levels = this.options.levelCounts[weapon] ?? 1;
    const level = Math.min(Math.max(1, next.level), levels);
    this.#selection = { ...next, kind, weapon, level };
    this.#render();
    this.options.onChange(this.#selection);
  }

  /** Shows the live numbers. */
  showReadout(readout: EnemyViewerReadout): void {
    const set = (key: string, text: string): void => {
      const el = this.#readouts.get(key);
      if (el && el.textContent !== text) el.textContent = text;
    };
    set('enemies', `Enemies: ${String(readout.enemies)}`);
    set('shots', `Enemy shots: ${String(readout.shots)}`);
    set('kills', `Destroyed: ${String(readout.kills)}`);
    set('score', `Score: ${String(readout.score)}`);
  }

  #addRow(name: string, change: (i: number) => Partial<EnemyViewerSelection>): void {
    const row = this.options.doc.createElement('div');
    row.className = `enemy-row enemy-${name}`;
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
    const levels = Array.from(
      { length: this.options.levelCounts[s.weapon] ?? 1 },
      (_, i) => `L${String(i + 1)}`,
    );
    this.#fill('kind', this.options.kinds, (i) => i === s.kind);
    this.#fill('view', ['Behaviour', 'Model (M)', 'Wireframe (V)'], (i) => VIEWS[i] === s.view);
    this.#fill('weapon', this.options.weapons, (i) => i === s.weapon);
    this.#fill('level', levels, (i) => i + 1 === s.level);
    this.#fill('toggles', ['Fire (F)', 'Pause (P)'], (i) => (i === 0 ? s.fire : s.paused));
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
