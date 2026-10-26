import type { SettingsView, SliderView } from '../menu-view';
import { backButton, element, entry, type MenuDocument } from './elements';
import type { ScreenHandlers } from './screen-handlers';

/** The slider value under a pointer at `clientX` over `track`: its nearest step. */
function valueAt(track: HTMLElement, clientX: number, max: number): number {
  const box = track.getBoundingClientRect();
  if (box.width <= 0) return 0;
  const share = Math.min(1, Math.max(0, (clientX - box.left) / box.width));
  return Math.round(share * max);
}

/** A bar of `max` cells, the first `value` of them lit, like the settings sketch. */
function sliderBar(doc: MenuDocument, slider: SliderView): HTMLElement {
  const bar = element(doc, 'div', 'slider-bar');
  for (let i = 0; i < slider.max; i++) {
    bar.append(element(doc, 'span', i < slider.value ? 'slider-cell on' : 'slider-cell'));
  }
  return bar;
}

/** Tapping or dragging on the bar sets the slider (P12-R04). */
function dragToSet(bar: HTMLElement, index: number, max: number, handlers: ScreenHandlers): void {
  let dragging = false;
  const set = (event: PointerEvent): void => {
    handlers.onSet?.(index, valueAt(bar, event.clientX, max));
  };
  bar.addEventListener('pointerdown', (event) => {
    dragging = true;
    event.stopPropagation();
    set(event);
  });
  bar.addEventListener('pointermove', (event) => {
    if (dragging) set(event);
  });
  for (const type of ['pointerup', 'pointercancel', 'pointerleave']) {
    bar.addEventListener(type, () => {
      dragging = false;
    });
  }
  // The row's own click would select it again: the bar already did.
  bar.addEventListener('click', (event) => {
    event.stopPropagation();
  });
}

function sliderRow(
  doc: MenuDocument,
  slider: SliderView,
  index: number,
  selected: boolean,
  handlers: ScreenHandlers,
): HTMLElement {
  const row = entry(doc, 'settings-slider', index, selected, handlers.onTap);
  row.setAttribute('role', 'slider');
  row.setAttribute('aria-label', slider.label);
  row.setAttribute('aria-valuemin', '0');
  row.setAttribute('aria-valuemax', String(slider.max));
  row.setAttribute('aria-valuenow', String(slider.value));
  const bar = sliderBar(doc, slider);
  dragToSet(bar, index, slider.max, handlers);
  row.append(
    element(doc, 'span', 'slider-label', slider.label),
    bar,
    element(doc, 'span', 'slider-value', String(slider.value)),
  );
  return row;
}

/**
 * Settings screen (P12-R04): the Music and Sound effects sliders. Over a paused level, the
 * playfield shows dimmed behind it.
 */
export function renderSettingsScreen(
  doc: MenuDocument,
  view: SettingsView,
  handlers: ScreenHandlers,
): HTMLElement {
  const over = view.overLevel ? ' over-level' : '';
  const root = element(doc, 'div', `menu-screen settings-screen${over}`);
  const list = element(doc, 'div', 'settings-list');
  view.sliders.forEach((slider, i) => {
    list.append(sliderRow(doc, slider, i, i === view.selected, handlers));
  });
  root.append(
    backButton(doc, view.back, handlers.onBack),
    element(doc, 'h2', 'menu-heading', view.heading),
    list,
    element(doc, 'div', 'menu-hint', view.hint),
  );
  return root;
}
