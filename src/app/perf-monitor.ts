import { ENGINE_CONFIG } from '../config/engine';
import { PerfOverlay, type PerfNumbers } from '../ui/perf-overlay';
import type { MenuDocument } from '../ui/screens/elements';

type ListenTarget = Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;

/** What {@link perfOverlay} needs from the app's options. */
export interface PerfOverlayOptions {
  readonly doc: MenuDocument;
  /** Where the overlay goes; none when omitted (production builds). */
  readonly perfParent?: HTMLElement;
  readonly keyboardTarget?: ListenTarget;
}

/** A frame's simulation, as the app's ticker runs it. */
interface Ticker {
  readonly simulate: (dt: number) => void;
}

export type { PerfNumbers } from '../ui/perf-overlay';

/**
 * Times the work of each frame and of each level start (P13-R01): how many frames are longer
 * than `longFrameMs`, the longest one, and the last loading time. `now` is the clock, in
 * milliseconds (`performance.now` in the browser).
 */
export class PerfMonitor {
  #longFrames = 0;
  #longestFrame = 0;
  #frames = 0;
  #lastLoad: number | null = null;
  #longestLoadStep: number | null = null;
  #loadingStep = 0;
  #frameStart: number | null = null;
  #loadStart: number | null = null;
  /** Frames left to skip before counting again (a level's first second, P13-R04). */
  #skip = 0;

  constructor(
    private readonly longFrameMs: number,
    private readonly now: () => number,
  ) {}

  get numbers(): PerfNumbers {
    return {
      longFrames: this.#longFrames,
      longestFrame: this.#longestFrame,
      frames: this.#frames,
      lastLoad: this.#lastLoad,
      longestLoadStep: this.#longestLoadStep,
    };
  }

  /** Whether a level is loading (between {@link loadStarted} and {@link loadFinished}). */
  get loading(): boolean {
    return this.#loadStart !== null;
  }

  /** Starts timing a frame. */
  frameStarted(): void {
    this.#frameStart = this.now();
  }

  /** Ends the frame started last; it counts unless skipped or part of a level loading. */
  frameEnded(): void {
    if (this.#frameStart === null) return;
    const time = this.now() - this.#frameStart;
    this.#frameStart = null;
    if (this.loading) {
      this.#loadingStep = Math.max(this.#loadingStep, time);
      return;
    }
    if (this.#skip > 0) {
      this.#skip--;
      return;
    }
    this.#frames++;
    this.#longestFrame = Math.max(this.#longestFrame, time);
    if (time > this.longFrameMs) this.#longFrames++;
  }

  /** A level was confirmed: its loading starts now. */
  loadStarted(): void {
    // The frame the level was confirmed in is part of its loading.
    this.#loadStart = this.#frameStart ?? this.now();
    this.#loadingStep = 0;
  }

  /**
   * The level's first frame was drawn: records the loading time and resets the frame counts,
   * which then skip the next `skipFrames` frames.
   */
  loadFinished(skipFrames = 0): void {
    if (this.#loadStart === null) return;
    this.#lastLoad = this.now() - this.#loadStart;
    this.#loadStart = null;
    // The frame drawing the level ends after this: it counts as a loading step if longer.
    this.#longestLoadStep = this.#loadingStep;
    this.reset(skipFrames);
  }

  /** Clears the frame counts (not the last loading time), skipping the next `skipFrames`. */
  reset(skipFrames = 0): void {
    this.#longFrames = 0;
    this.#longestFrame = 0;
    this.#frames = 0;
    this.#skip = skipFrames;
  }
}

/** The perf overlay (P13-R01), toggled by its key, refreshed after each frame's simulation. */
export function perfOverlay(
  options: PerfOverlayOptions,
  perf: PerfMonitor,
): { wrap: <T extends Ticker>(ticker: T) => T; dispose: () => void } {
  const { perfParent, keyboardTarget } = options;
  if (!perfParent) return { wrap: (ticker) => ticker, dispose: () => undefined };
  const overlay = new PerfOverlay(options.doc, perfParent, ENGINE_CONFIG.perfOverlay.refresh);
  const onKey = (event: Event): void => {
    const key = event as KeyboardEvent;
    if (key.code !== ENGINE_CONFIG.perfOverlay.key) return;
    key.preventDefault();
    overlay.toggle();
  };
  keyboardTarget?.addEventListener('keydown', onKey);
  return {
    wrap: (ticker) => ({
      ...ticker,
      simulate: (dt: number) => {
        ticker.simulate(dt);
        overlay.update(dt, perf.numbers);
      },
    }),
    dispose: () => {
      keyboardTarget?.removeEventListener('keydown', onKey);
      overlay.dispose();
    },
  };
}
