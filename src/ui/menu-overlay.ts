import { pointerCommand } from '../input/pointer-menu-input';
import type { MenuCommand } from '../input/menu-action';
import type { MenuView } from './menu-view';
import type { MenuDocument } from './screens/elements';
import type { ScreenHandlers } from './screens/screen-handlers';
import { shrinkToFit } from './shrink-to-fit';
import { renderLoadingScreen } from './screens/loading-screen';
import { renderTitleScreen } from './screens/title-screen';
import { renderShipSelectScreen } from './screens/ship-select-screen';
import { renderLevelSelectScreen } from './screens/level-select-screen';
import { renderGameScreen } from './screens/game-screen';
import { renderSettingsScreen } from './screens/settings-screen';

/** Settings of a {@link MenuOverlay}. */
export interface MenuOverlayOptions {
  /** Fade-in time of a new screen, in seconds (P01-R15). */
  readonly transitionSeconds: number;
}

/** Touch controls of the game screen (P06-R02), in logical pixels with Y up. */
export interface GameTouchHandlers {
  fire(held: boolean): void;
  drag(dx: number, dy: number): void;
}

function renderScreen(doc: MenuDocument, view: MenuView, handlers: ScreenHandlers): HTMLElement {
  switch (view.kind) {
    case 'loading':
      return renderLoadingScreen(doc, view);
    case 'title':
      return renderTitleScreen(doc, view, handlers);
    case 'ship-select':
      return renderShipSelectScreen(doc, view, handlers);
    case 'level-select':
      return renderLevelSelectScreen(doc, view, handlers);
    case 'game':
      return renderGameScreen(doc, view, handlers);
    case 'settings':
      return renderSettingsScreen(doc, view, handlers);
  }
}

function selectedIndex(view: MenuView): number {
  return 'selected' in view ? view.selected : 0;
}

/**
 * The HTML/CSS menu overlay (P01-R13), laid out at the logical resolution. It renders a
 * {@link MenuView} and turns taps and clicks into menu commands (P01-R11); it never reads
 * raw keys or gamepad buttons.
 */
export class MenuOverlay {
  #current: HTMLElement | undefined;
  #view: MenuView | undefined;

  constructor(
    private readonly doc: MenuDocument,
    private readonly root: HTMLElement,
    private readonly onCommand: (command: MenuCommand) => void,
    private readonly options: MenuOverlayOptions,
    private readonly touch?: GameTouchHandlers,
  ) {}

  /** Screen pixels per logical pixel: the overlay is laid out at the logical size and scaled. */
  #scale(): number {
    const shown = this.root.getBoundingClientRect().width;
    const laidOut = this.root.offsetWidth;
    return shown > 0 && laidOut > 0 ? shown / laidOut : 1;
  }

  /** The view shown last. */
  get view(): MenuView | undefined {
    return this.#view;
  }

  /** Replaces the overlay content with `view`. A new screen fades in. */
  show(view: MenuView): void {
    const isNewScreen = this.#view?.kind !== view.kind;
    this.#view = view;
    const screen = renderScreen(this.doc, view, {
      onTap: (index) => {
        this.onCommand(pointerCommand(index, selectedIndex(view)));
      },
      onBack: () => {
        this.onCommand('back');
      },
      onFire: (held) => {
        this.touch?.fire(held);
      },
      onDrag: (dx, dy) => {
        const scale = this.#scale();
        this.touch?.drag(dx / scale, -dy / scale);
      },
      onPause: () => {
        this.onCommand('pause');
      },
      onSet: (index, value) => {
        this.onCommand({ set: index, value });
      },
    });
    screen.dataset.screen = view.kind;
    if (isNewScreen && view.kind !== 'loading') {
      screen.classList.add('menu-enter');
      screen.style.animationDuration = `${String(this.options.transitionSeconds)}s`;
    }
    this.#current?.remove();
    this.root.append(screen);
    this.#current = screen;
    const logo = screen.querySelector<HTMLElement>('.title-name');
    if (logo) shrinkToFit(logo);
  }

  /** "Locked" feedback (P01-R07): shakes the selected entry and shows `text`. */
  shakeSelected(text: string): void {
    const selected = this.#current?.querySelector<HTMLElement>('.menu-entry.selected');
    if (selected) {
      selected.classList.remove('shake');
      selected.getBoundingClientRect(); // forces a reflow, so the CSS animation restarts
      selected.classList.add('shake');
    }
    const status = this.#current?.querySelector('.menu-status');
    if (status) status.textContent = text;
  }

  dispose(): void {
    this.#current?.remove();
    this.#current = undefined;
    this.#view = undefined;
  }
}
