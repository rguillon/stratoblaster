import type { MenuDocument } from './screens/elements';
import { renderLoadingScreen } from './screens/loading-screen';

/**
 * The loading screen of a level (P13-R03): the menus' loading screen over the game screen, with
 * the level's real progress. It fades in only after a short delay (CSS), so a quick load does
 * not flash it.
 */
export class LevelLoadingScreen {
  #root: HTMLElement | undefined;

  constructor(
    private readonly doc: MenuDocument,
    private readonly parent: HTMLElement,
    private readonly text: string,
  ) {}

  /** Shows `progress` (0..1). */
  show(progress: number): void {
    const root = renderLoadingScreen(this.doc, { kind: 'loading', text: this.text, progress });
    root.classList.add('level-loading');
    if (this.#root) this.#root.replaceWith(root);
    else this.parent.append(root);
    this.#root = root;
  }

  dispose(): void {
    this.#root?.remove();
    this.#root = undefined;
  }
}
