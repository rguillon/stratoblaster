import type { LevelSelectView } from '../menu-view';
import { backButton, element, entry, padlock, type MenuDocument } from './elements';
import type { ScreenHandlers } from './screen-handlers';

/** Level select screen (P01-R07): a grid of levels, locked ones greyed out with a padlock. */
export function renderLevelSelectScreen(
  doc: MenuDocument,
  view: LevelSelectView,
  handlers: ScreenHandlers,
): HTMLElement {
  const root = element(doc, 'div', 'menu-screen level-select-screen');
  const grid = element(doc, 'div', 'level-grid');
  grid.style.gridTemplateColumns = `repeat(${String(view.columns)}, 1fr)`;
  view.levels.forEach((level, i) => {
    const cell = entry(doc, 'level-cell', i, i === view.selected, handlers.onTap);
    cell.append(element(doc, 'span', 'level-label', level.label));
    if (level.locked) {
      // Still selectable (not aria-disabled): confirming it gives the "locked" feedback.
      cell.classList.add('locked');
      cell.append(padlock(doc));
    }
    grid.append(cell);
  });
  root.append(
    backButton(doc, view.back, handlers.onBack),
    element(doc, 'h2', 'menu-heading', view.heading),
    grid,
    element(doc, 'div', 'menu-status'),
    element(doc, 'div', 'menu-hint', view.hint),
  );
  return root;
}
