import type { LoadingView } from '../menu-view';
import { element, type MenuDocument } from './elements';

/** Loading screen with a progress bar (P01-R02). */
export function renderLoadingScreen(doc: MenuDocument, view: LoadingView): HTMLElement {
  const root = element(doc, 'div', 'menu-screen loading-screen');
  const percent = Math.round(Math.min(1, Math.max(0, view.progress)) * 100);
  const bar = element(doc, 'div', 'loading-bar');
  bar.setAttribute('role', 'progressbar');
  bar.setAttribute('aria-valuemin', '0');
  bar.setAttribute('aria-valuemax', '100');
  bar.setAttribute('aria-valuenow', String(percent));
  const fill = element(doc, 'div', 'loading-fill');
  fill.style.width = `${String(percent)}%`;
  bar.append(fill);
  root.append(
    element(doc, 'div', 'loading-text', view.text),
    bar,
    element(doc, 'div', 'loading-percent', `${String(percent)} %`),
  );
  return root;
}
