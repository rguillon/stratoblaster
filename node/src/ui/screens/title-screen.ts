import type { TitleView } from '../menu-view';
import { element, entry, type MenuDocument } from './elements';
import type { ScreenHandlers } from './screen-handlers';

/** Title screen (P01-R04): high score, game title, Start, Settings (P12-R04), controls hint, version. */
export function renderTitleScreen(
  doc: MenuDocument,
  view: TitleView,
  handlers: ScreenHandlers,
): HTMLElement {
  const root = element(doc, 'div', 'menu-screen title-screen');
  const score = element(doc, 'div', 'title-score');
  score.append(
    element(doc, 'div', 'title-score-label', view.highScoreLabel),
    element(doc, 'div', 'title-high-score', String(view.highScore)),
  );
  const start = entry(doc, 'title-start', 0, view.selected === 0, handlers.onTap);
  start.textContent = view.start;
  const settings = entry(doc, 'title-settings', 1, view.selected === 1, handlers.onTap);
  settings.textContent = view.settings;
  const version = element(doc, 'div', 'title-version');
  version.append(
    element(doc, 'div', 'version-number', `v${view.version}`),
    element(doc, 'div', 'version-commit', view.commit),
  );
  root.append(
    score,
    element(doc, 'h1', 'title-name', view.title),
    start,
    settings,
    element(doc, 'div', 'menu-hint title-hint', view.hint),
    version,
  );
  return root;
}
