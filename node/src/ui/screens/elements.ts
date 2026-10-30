/** The DOM API the menu screens use. */
export type MenuDocument = Pick<Document, 'createElement' | 'createElementNS'>;

/** Creates `<tag class="className">text</tag>`. */
export function element(
  doc: MenuDocument,
  tag: keyof HTMLElementTagNameMap,
  className: string,
  text?: string,
): HTMLElement {
  const el = doc.createElement(tag);
  el.className = className;
  if (text !== undefined) el.textContent = text;
  return el;
}

/**
 * A tappable menu entry (P01-R11). Uses `role="button"` on a `div` rather than `<button>`,
 * so the browser never turns Space / Enter into a second click: the keyboard goes through
 * the menu input only.
 */
export function entry(
  doc: MenuDocument,
  className: string,
  index: number,
  selected: boolean,
  onTap: (index: number) => void,
): HTMLElement {
  const el = element(doc, 'div', `menu-entry ${className}`);
  el.setAttribute('role', 'button');
  el.dataset.index = String(index);
  if (selected) {
    el.classList.add('selected');
    el.setAttribute('aria-current', 'true');
  }
  el.addEventListener('click', () => {
    onTap(index);
  });
  return el;
}

/** The on-screen Back button of a menu screen (P01-R11). */
export function backButton(doc: MenuDocument, label: string, onBack: () => void): HTMLElement {
  const el = element(doc, 'div', 'menu-back', `◀ ${label}`);
  el.setAttribute('role', 'button');
  el.addEventListener('click', onBack);
  return el;
}

const SVG = 'http://www.w3.org/2000/svg';

/** A small padlock icon for locked levels. */
export function padlock(doc: MenuDocument): SVGSVGElement {
  const svg = doc.createElementNS(SVG, 'svg');
  svg.setAttribute('viewBox', '0 0 16 16');
  svg.setAttribute('class', 'padlock');
  svg.setAttribute('aria-label', 'locked');
  const shackle = doc.createElementNS(SVG, 'path');
  shackle.setAttribute('d', 'M4.5 7V5a3.5 3.5 0 0 1 7 0v2');
  shackle.setAttribute('fill', 'none');
  shackle.setAttribute('stroke', 'currentColor');
  shackle.setAttribute('stroke-width', '1.6');
  const body = doc.createElementNS(SVG, 'rect');
  for (const [k, v] of Object.entries({ x: '3', y: '7', width: '10', height: '8', rx: '1.5' })) {
    body.setAttribute(k, v);
  }
  body.setAttribute('fill', 'currentColor');
  svg.append(shackle, body);
  return svg;
}
