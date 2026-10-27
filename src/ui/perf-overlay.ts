/** What a the perf monitor has measured (P13-R01). Times in milliseconds. */
export interface PerfNumbers {
  /** Frames longer than the long-frame limit since the counts were last reset. */
  readonly longFrames: number;
  /** Longest frame since the counts were last reset. */
  readonly longestFrame: number;
  /** Frames measured since the counts were last reset. */
  readonly frames: number;
  /** How long the last level took from its confirmation to its first drawn frame, if any. */
  readonly lastLoad: number | null;
  /** Longest frame of the last level loading (P13-R03: the longest frozen step), if any. */
  readonly longestLoadStep: number | null;
}

/** Formats milliseconds for the overlay. */
function ms(value: number | null): string {
  return value === null ? '–' : `${value.toFixed(0)} ms`;
}

/**
 * The debug perf overlay (P13-R01, ENG-111; dev and e2e builds only): long frames, the longest
 * frame and the last level loading time. Hidden until toggled (F3); the text changes at most every
 * `refreshSeconds`, so the numbers stay readable.
 */
export class PerfOverlay {
  readonly root: HTMLElement;
  #sinceRefresh = Infinity;

  constructor(
    doc: Pick<Document, 'createElement'>,
    parent: HTMLElement,
    private readonly refreshSeconds: number,
  ) {
    this.root = doc.createElement('div');
    this.root.className = 'perf-overlay';
    this.root.hidden = true;
    parent.append(this.root);
  }

  get shown(): boolean {
    return !this.root.hidden;
  }

  toggle(): void {
    this.root.hidden = !this.root.hidden;
    this.#sinceRefresh = Infinity;
  }

  /** Shows `numbers` if shown and `refreshSeconds` have passed since the last change. */
  update(dt: number, numbers: PerfNumbers): void {
    this.#sinceRefresh += dt;
    if (!this.shown || this.#sinceRefresh < this.refreshSeconds) return;
    this.#sinceRefresh = 0;
    this.root.textContent = [
      `Long frames: ${String(numbers.longFrames)}`,
      `Longest frame: ${ms(numbers.longestFrame)}`,
      `Level load: ${ms(numbers.lastLoad)}`,
    ].join('\n');
  }

  dispose(): void {
    this.root.remove();
  }
}
