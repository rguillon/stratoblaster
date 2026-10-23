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
import { renderGamePlaceholderScreen } from './screens/game-placeholder-screen';

/** Settings of a {@link MenuOverlay}. */
export interface MenuOverlayOptions {
  /** Fade-in time of a new screen, in seconds (P01-R15). */
  readonly transitionSeconds: number;
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
      return renderGamePlaceholderScreen(doc, view, handlers);
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
  ) {}

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
