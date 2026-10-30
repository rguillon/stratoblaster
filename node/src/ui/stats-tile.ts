/** Rendering numbers shown by a {@link StatsTile}. */
export interface RenderStats {
  readonly fps: number;
  /** Triangles drawn in the last frame. */
  readonly polygons: number;
}

/**
 * A small debug tile with the frame rate and the number of polygons drawn. The text changes at
 * most every `refreshSeconds`, so the numbers stay readable.
 */
export class StatsTile {
  readonly root: HTMLElement;
  readonly #fps: HTMLElement;
  readonly #polygons: HTMLElement;
  #sinceRefresh = Infinity;

  constructor(
    doc: Pick<Document, 'createElement'>,
    parent: HTMLElement,
    private readonly refreshSeconds: number,
  ) {
    this.root = doc.createElement('div');
    this.root.className = 'stats-tile';
    this.#fps = doc.createElement('div');
    this.#fps.className = 'stats-fps';
    this.#polygons = doc.createElement('div');
    this.#polygons.className = 'stats-polygons';
    this.root.append(this.#fps, this.#polygons);
    parent.append(this.root);
  }

  /** Shows `stats` if `refreshSeconds` have passed since the last change (and the first time). */
  update(dt: number, stats: RenderStats): void {
    this.#sinceRefresh += dt;
    if (this.#sinceRefresh < this.refreshSeconds) return;
    this.#sinceRefresh = 0;
    this.#fps.textContent = `FPS: ${String(Math.round(stats.fps))}`;
    this.#polygons.textContent = `Polygons: ${Math.round(stats.polygons).toLocaleString('en-US')}`;
  }
}
