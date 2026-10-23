import type { ShipSelectView } from '../menu-view';
import { backButton, element, entry, type MenuDocument } from './elements';
import type { ScreenHandlers } from './screen-handlers';

/** Ship select screen (P01-R06): a card with name and stats under each rotating ship. */
export function renderShipSelectScreen(
  doc: MenuDocument,
  view: ShipSelectView,
  handlers: ScreenHandlers,
): HTMLElement {
  const root = element(doc, 'div', 'menu-screen ship-select-screen');
  const cards = element(doc, 'div', 'ship-cards');
  cards.style.width = `${String(view.cardsWidthPercent)}%`;
  view.ships.forEach((ship, i) => {
    const card = entry(doc, 'ship-card', i, i === view.selected, handlers.onTap);
    card.append(element(doc, 'div', 'ship-card-name', ship.title));
    for (const line of ship.lines) card.append(element(doc, 'div', 'ship-card-stat', line));
    cards.append(card);
  });
  root.append(
    backButton(doc, view.back, handlers.onBack),
    element(doc, 'h2', 'menu-heading', view.heading),
    cards,
    element(doc, 'div', 'menu-hint', view.hint),
  );
  return root;
}
