import type { PropGroup } from '../render/game-view';

/** What the props page shows: a group, and the prop picked in it (index into its ids). */
export interface PropViewerSelection {
  readonly group: number;
  readonly prop: number;
}

export interface PropViewerPanelOptions {
  readonly doc: Pick<Document, 'createElement'>;
  readonly parent: HTMLElement;
  readonly groups: readonly PropGroup[];
  readonly initial: PropViewerSelection;
  readonly onChange: (selection: PropViewerSelection) => void;
}

const HELP = 'Drag to turn, wheel to zoom. Click a prop, or ←/→ to step through them.';

/**
 * Controls of the props page (reviewer, 2026-10-28): a button per group, a button per prop of
 * the shown group, and a readout of the picked prop. Uses the enemies page's styles.
 */
export class PropViewerPanel {
  readonly root: HTMLElement;
  #selection: PropViewerSelection;
  readonly #groupRow: HTMLElement;
  readonly #propRow: HTMLElement;
  readonly #readout: HTMLElement;

  constructor(private readonly options: PropViewerPanelOptions) {
    const { doc } = options;
    this.#selection = options.initial;
    this.root = this.#element('div', 'enemy-panel');
    this.root.append(this.#element('div', 'enemy-title', 'Props'));
    this.#groupRow = this.#element('div', 'enemy-row prop-groups');
    this.#propRow = this.#element('div', 'enemy-row prop-kinds');
    this.#readout = this.#element('div', 'enemy-readout prop-readout');
    this.root.append(this.#groupRow, this.#propRow, this.#readout);
    this.root.append(this.#element('div', 'enemy-help', HELP));
    options.groups.forEach((group, i) => {
      const button = doc.createElement('button');
      button.textContent = `${group.label} (${String(group.ids.length)})`;
      button.addEventListener('click', () => {
        this.#choose({ group: i, prop: 0 });
      });
      this.#groupRow.append(button);
    });
    options.parent.append(this.root);
    this.#render();
  }

  get selection(): PropViewerSelection {
    return this.#selection;
  }

  /** Sets the selection from code (keys, clicks on the scene), without calling `onChange`. */
  update(selection: PropViewerSelection): void {
    const regroup = selection.group !== this.#selection.group;
    this.#selection = selection;
    this.#render(regroup);
  }

  /** Shows `text` (the picked prop's id and size) under the buttons. */
  setReadout(text: string): void {
    this.#readout.textContent = text;
  }

  #choose(selection: PropViewerSelection): void {
    this.update(selection);
    this.options.onChange(selection);
  }

  #element(tag: string, className: string, text = ''): HTMLElement {
    const el = this.options.doc.createElement(tag);
    el.className = className;
    el.textContent = text;
    return el;
  }

  #render(regroup = true): void {
    const { group, prop } = this.#selection;
    [...this.#groupRow.children].forEach((b, i) => b.classList.toggle('selected', i === group));
    if (regroup) {
      this.#propRow.replaceChildren(
        ...(this.options.groups[group]?.ids ?? []).map((id, i) => {
          const button = this.options.doc.createElement('button');
          button.textContent = id;
          button.addEventListener('click', () => {
            this.#choose({ group, prop: i });
          });
          return button;
        }),
      );
    }
    [...this.#propRow.children].forEach((b, i) => b.classList.toggle('selected', i === prop));
  }
}
