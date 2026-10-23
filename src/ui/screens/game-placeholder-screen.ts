import type { GamePlaceholderView } from '../menu-view';
import { backButton, element, type MenuDocument } from './elements';
import type { ScreenHandlers } from './screen-handlers';

/** Placeholder game screen (P01-R08): the chosen ship and level, and how to go back. */
export function renderGamePlaceholderScreen(
  doc: MenuDocument,
  view: GamePlaceholderView,
  handlers: ScreenHandlers,
): HTMLElement {
  const root = element(doc, 'div', 'menu-screen game-screen');
  root.append(
    backButton(doc, view.back, handlers.onBack),
    element(doc, 'div', 'game-message', view.message),
    element(doc, 'div', 'menu-hint', view.hint),
  );
  return root;
}
