/** Live settings of one cloud layer, as percentages. */
export interface CloudControls {
  readonly enabled: boolean;
  /** Intensity: share of the sky covered, 0..100. */
  readonly coverage: number;
  readonly opacity: number;
}

/** What the generated level viewer shows (P04). */
export interface SceneryViewerSettings {
  readonly paused: boolean;
  readonly fastForward: boolean;
  readonly sea: boolean;
  /** Outline of the playfield on the flight plane. */
  readonly frame: boolean;
  readonly clouds: readonly CloudControls[];
}

/** Live numbers shown under the controls. */
export interface SceneryViewerReadout {
  readonly time: number;
  readonly section: string;
  readonly props: number;
  readonly seed: number;
  readonly ended: boolean;
}

export interface SceneryViewerPanelOptions {
  readonly doc: Pick<Document, 'createElement'>;
  readonly parent: HTMLElement;
  readonly levelName: string;
  /** Level duration, in seconds. */
  readonly duration: number;
  /** Whether the level has a sea that can be shown or hidden. */
  readonly hasSea: boolean;
  readonly initial: SceneryViewerSettings;
  readonly onChange: (settings: SceneryViewerSettings) => void;
  readonly onSeek: (time: number) => void;
  readonly onRestart: () => void;
  readonly onNewSeed: () => void;
}

/** `m:ss`. */
export function formatTime(seconds: number): string {
  // A hair of slack, so that 2 s summed from frame steps (1.999…) shows as 0:02.
  const s = Math.max(0, Math.floor(seconds + 1e-6));
  return `${String(Math.floor(s / 60))}:${String(s % 60).padStart(2, '0')}`;
}

type Doc = SceneryViewerPanelOptions['doc'];

function element<K extends keyof HTMLElementTagNameMap>(
  doc: Doc,
  tag: K,
  className: string,
  text = '',
): HTMLElementTagNameMap[K] {
  const el = doc.createElement(tag);
  el.className = className;
  el.textContent = text;
  return el;
}

function slider(
  doc: Doc,
  className: string,
  max: number,
  onInput: (value: number) => void,
): HTMLInputElement {
  const input = element(doc, 'input', className);
  input.type = 'range';
  input.min = '0';
  input.max = String(max);
  input.step = '1';
  input.addEventListener('input', () => {
    onInput(Number(input.value));
  });
  return input;
}

/**
 * Controls of the generated level viewer: play / pause, fast-forward, restart, new seed, sea and
 * playfield outline toggles, a time slider, and an on/off switch plus intensity and opacity
 * sliders per cloud layer; then live readouts and a "level end" banner.
 */
export class SceneryViewerPanel {
  readonly root: HTMLElement;
  #settings: SceneryViewerSettings;
  readonly #buttons = new Map<string, HTMLButtonElement>();
  readonly #cloudSliders: { coverage: HTMLInputElement; opacity: HTMLInputElement }[] = [];
  readonly #time: HTMLInputElement;
  readonly #readouts = new Map<string, HTMLElement>();
  readonly #end: HTMLElement;

  constructor(private readonly options: SceneryViewerPanelOptions) {
    const { doc } = options;
    this.#settings = options.initial;
    this.root = element(doc, 'div', 'scenery-panel');
    this.root.append(element(doc, 'div', 'scenery-title', options.levelName));
    this.#row([
      ['pause', 'Pause (P)', () => ({ paused: !this.#settings.paused })],
      ['fast', `×4 (F)`, () => ({ fastForward: !this.#settings.fastForward })],
      ['restart', 'Restart (R)', undefined],
      ['new-seed', 'New seed (N)', undefined],
    ]);
    this.#row([
      ['sea', 'Sea (S)', () => ({ sea: !this.#settings.sea })],
      ['frame', 'Playfield (O)', () => ({ frame: !this.#settings.frame })],
    ]);
    this.#button('restart')?.addEventListener('click', options.onRestart);
    this.#button('new-seed')?.addEventListener('click', options.onNewSeed);
    const sea = this.#button('sea');
    if (sea) sea.disabled = !options.hasSea;
    this.#time = slider(doc, 'scenery-time-slider', Math.ceil(options.duration), options.onSeek);
    this.root.append(this.#readout('time'), this.#time);
    options.initial.clouds.forEach((_, i) => {
      this.#cloudRow(i);
    });
    for (const key of ['section', 'props', 'seed']) this.root.append(this.#readout(key));
    this.#end = element(doc, 'div', 'scenery-end', 'Level end — press R to restart');
    this.#end.hidden = true;
    this.root.append(this.#end);
    options.parent.append(this.root);
    this.#render();
  }

  get settings(): SceneryViewerSettings {
    return this.#settings;
  }

  /** Changes the settings (from a control or a keyboard shortcut). */
  update(change: Partial<SceneryViewerSettings>): void {
    this.#settings = {
      ...this.#settings,
      ...change,
      sea: (change.sea ?? this.#settings.sea) && this.options.hasSea,
    };
    this.#render();
    this.options.onChange(this.#settings);
  }

  /** Changes one cloud layer's settings. */
  updateCloud(index: number, change: Partial<CloudControls>): void {
    const clouds = this.#settings.clouds.map((c, i) => (i === index ? { ...c, ...change } : c));
    this.update({ clouds });
  }

  showReadout(readout: SceneryViewerReadout): void {
    const set = (key: string, text: string): void => {
      const el = this.#readouts.get(key);
      if (el && el.textContent !== text) el.textContent = text;
    };
    set('time', `Time: ${formatTime(readout.time)} / ${formatTime(this.options.duration)}`);
    set('section', `Section: ${readout.section}`);
    set('props', `Props: ${String(readout.props)}`);
    set('seed', `Seed: ${String(readout.seed)}`);
    const value = String(Math.round(readout.time));
    if (this.#time.value !== value) this.#time.value = value;
    this.#end.hidden = !readout.ended;
  }

  #button(key: string): HTMLButtonElement | undefined {
    return this.#buttons.get(key);
  }

  #readout(key: string): HTMLElement {
    const el = element(this.options.doc, 'div', `scenery-readout scenery-${key}`);
    this.#readouts.set(key, el);
    return el;
  }

  #row(
    buttons: readonly (readonly [
      string,
      string,
      (() => Partial<SceneryViewerSettings>) | undefined,
    ])[],
  ): void {
    const row = element(this.options.doc, 'div', 'scenery-row');
    for (const [key, label, change] of buttons) {
      const button = element(this.options.doc, 'button', `scenery-${key}`, label);
      button.type = 'button';
      if (change) {
        button.addEventListener('click', () => {
          this.update(change());
        });
      }
      this.#buttons.set(key, button);
      row.append(button);
    }
    this.root.append(row);
  }

  #cloudRow(index: number): void {
    const { doc } = this.options;
    const row = element(doc, 'div', `scenery-row scenery-cloud scenery-cloud-${String(index + 1)}`);
    const toggle = element(
      doc,
      'button',
      'scenery-cloud-toggle',
      `Clouds ${String(index + 1)} (${String(index + 1)})`,
    );
    toggle.type = 'button';
    toggle.addEventListener('click', () => {
      this.updateCloud(index, { enabled: !(this.#settings.clouds[index]?.enabled ?? false) });
    });
    this.#buttons.set(`cloud-${String(index)}`, toggle);
    const coverage = slider(doc, 'scenery-coverage', 100, (coverage) => {
      this.updateCloud(index, { coverage });
    });
    const opacity = slider(doc, 'scenery-opacity', 100, (opacity) => {
      this.updateCloud(index, { opacity });
    });
    coverage.title = 'Intensity (coverage)';
    opacity.title = 'Opacity';
    this.#cloudSliders.push({ coverage, opacity });
    row.append(
      toggle,
      element(doc, 'span', 'scenery-label', 'Intensity'),
      coverage,
      element(doc, 'span', 'scenery-label', 'Opacity'),
      opacity,
    );
    this.root.append(row);
  }

  #render(): void {
    const s = this.#settings;
    const pressed = (key: string, on: boolean): void => {
      const button = this.#button(key);
      button?.classList.toggle('selected', on);
      button?.setAttribute('aria-pressed', String(on));
    };
    pressed('pause', s.paused);
    pressed('fast', s.fastForward);
    pressed('sea', s.sea);
    pressed('frame', s.frame);
    s.clouds.forEach((cloud, i) => {
      pressed(`cloud-${String(i)}`, cloud.enabled);
      const sliders = this.#cloudSliders[i];
      if (!sliders) return;
      sliders.coverage.value = String(cloud.coverage);
      sliders.opacity.value = String(cloud.opacity);
    });
  }
}
