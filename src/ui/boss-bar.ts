import { element, type MenuDocument } from './screens/elements';

/** What the boss health bar shows on one frame (P07-R02). */
export interface BossBarFrame {
  readonly name: string;
  /** Its kind, e.g. `MINI BOSS` or `BOSS`. */
  readonly rank: string;
  /** Share of the bar filled, 0..1. */
  readonly share: number;
  /** Where each destroyable part's share ends along the bar, 0..1. */
  readonly notches: readonly number[];
}

const percent = (share: number): string =>
  `${String(Math.round(Math.min(1, Math.max(0, share)) * 1000) / 10)}%`;

/**
 * The boss health bar (P07-R02), a slim gauge up the left edge of the playfield under the
 * player's HUD, clear of the boss (reviewer, 2026-10-26): the boss's kind and name written along
 * it, and the health of its core and parts together filling it from the bottom, with a notch at
 * the end of each part's share. Hidden while no boss is fought; the page is touched only on
 * changes.
 */
export class BossBar {
  readonly root: HTMLElement;
  readonly #name: HTMLElement;
  readonly #rank: HTMLElement;
  readonly #fill: HTMLElement;
  readonly #notches: HTMLElement;
  #shown = '';
  #notchKey = '';

  constructor(
    private readonly doc: MenuDocument,
    parent: HTMLElement,
  ) {
    this.root = element(doc, 'div', 'boss-bar');
    this.root.hidden = true;
    const label = element(doc, 'div', 'boss-label');
    this.#rank = element(doc, 'span', 'boss-rank');
    this.#name = element(doc, 'span', 'boss-name');
    label.append(this.#rank, this.#name);
    const bar = element(doc, 'div', 'boss-track');
    this.#fill = element(doc, 'div', 'boss-fill');
    this.#notches = element(doc, 'div', 'boss-notches');
    bar.append(this.#fill, this.#notches);
    this.root.append(label, bar);
    parent.append(this.root);
  }

  /** Shows `frame`, or hides the bar when there is no boss. */
  update(frame: BossBarFrame | undefined): void {
    const key = frame ? [frame.rank, frame.name, percent(frame.share)].join('|') : '';
    if (key === this.#shown) return;
    this.#shown = key;
    this.root.hidden = frame === undefined;
    if (!frame) return;
    this.#rank.textContent = frame.rank;
    this.#name.textContent = frame.name;
    this.#fill.style.height = percent(frame.share);
    this.#setNotches(frame.notches);
  }

  #setNotches(notches: readonly number[]): void {
    const key = notches.map(percent).join(',');
    if (key === this.#notchKey) return;
    this.#notchKey = key;
    this.#notches.replaceChildren(
      ...notches.map((at) => {
        const notch = element(this.doc, 'div', 'boss-notch');
        notch.style.bottom = percent(at);
        return notch;
      }),
    );
  }
}
