import type { PauseView } from '../menu-view';
import { element, entry, type MenuDocument } from './elements';
import type { ScreenHandlers } from './screen-handlers';

/** The `Leave the level?` question (P12-R02): No and Yes, a tap selects, a second tap confirms. */
function question(
  doc: MenuDocument,
  asked: NonNullable<PauseView['question']>,
  handlers: ScreenHandlers,
): HTMLElement {
  const box = element(doc, 'div', 'pause-question');
  const row = element(doc, 'div', 'pause-choices');
  asked.choices.forEach((label, i) => {
    const choice = entry(doc, 'pause-choice', i, i === asked.selected, handlers.onTap);
    choice.textContent = label;
    row.append(choice);
  });
  box.append(element(doc, 'div', 'pause-question-text', asked.text), row);
  return box;
}

/**
 * The pause menu (P12-R02) over the playfield, dimmed by a layer behind it: Resume, Settings and
 * Main menu, or the question before leaving the level.
 */
export function pausePanel(
  doc: MenuDocument,
  view: PauseView,
  selected: number,
  handlers: ScreenHandlers,
): HTMLElement {
  const dim = element(doc, 'div', 'pause-dim');
  const panel = element(doc, 'div', 'pause-panel');
  panel.append(element(doc, 'div', 'pause-heading', view.heading));
  if (view.question) {
    panel.append(question(doc, view.question, handlers));
  } else {
    view.entries.forEach((label, i) => {
      const item = entry(doc, 'pause-entry', i, i === selected, handlers.onTap);
      item.textContent = label;
      panel.append(item);
    });
    panel.append(element(doc, 'div', 'menu-hint pause-hint', view.hint));
  }
  dim.append(panel);
  return dim;
}
