import type { GameScreenView } from '../menu-view';
import { element, type MenuDocument } from './elements';
import type { ScreenHandlers } from './screen-handlers';

/** The "Level complete" (or "Game over") panel (P06-R03); tapping it goes on, like Confirm. */
function levelComplete(
  doc: MenuDocument,
  complete: NonNullable<GameScreenView['complete']>,
  handlers: ScreenHandlers,
): HTMLElement {
  const over = complete.over ? ' game-over' : '';
  const panel = element(doc, 'div', `menu-entry selected level-complete${over}`);
  panel.setAttribute('role', 'button');
  panel.dataset.index = '0';
  panel.append(
    element(doc, 'div', 'level-complete-heading', complete.heading),
    element(doc, 'div', 'level-complete-level', complete.level),
    element(doc, 'div', 'level-complete-enemies', complete.enemies),
    element(doc, 'div', 'menu-hint', complete.hint),
  );
  panel.addEventListener('click', () => {
    handlers.onTap(0);
  });
  return panel;
}

/** The touch fire button: shoots while pressed (P06-R02). */
function fireButton(doc: MenuDocument, label: string, handlers: ScreenHandlers): HTMLElement {
  const button = element(doc, 'div', 'game-fire', label);
  button.setAttribute('role', 'button');
  const press = (held: boolean) => (event: Event) => {
    event.stopPropagation();
    handlers.onFire?.(held);
  };
  button.addEventListener('pointerdown', press(true));
  for (const type of ['pointerup', 'pointercancel', 'pointerleave']) {
    button.addEventListener(type, press(false));
  }
  return button;
}

/**
 * Drag anywhere to fly (P06-R02, GD §2 touch): pointer moves while a finger or button is down
 * are passed on as screen pixel offsets.
 */
function dragArea(root: HTMLElement, handlers: ScreenHandlers): void {
  let last: { x: number; y: number } | undefined;
  root.addEventListener('pointerdown', (e) => {
    last = { x: e.clientX, y: e.clientY };
  });
  root.addEventListener('pointermove', (e) => {
    if (!last) return;
    handlers.onDrag?.(e.clientX - last.x, e.clientY - last.y);
    last = { x: e.clientX, y: e.clientY };
  });
  for (const type of ['pointerup', 'pointercancel']) {
    root.addEventListener(type, () => {
      last = undefined;
    });
  }
}

/**
 * The overlay of the game screen (P06-R02, R03): the level played, the touch fire button and the
 * drag area over the playfield, and the "Level complete" panel at the end. The HUD is drawn by
 * `GameHud`, which updates every frame.
 */
export function renderGameScreen(
  doc: MenuDocument,
  view: GameScreenView,
  handlers: ScreenHandlers,
): HTMLElement {
  const root = element(doc, 'div', 'menu-screen game-screen');
  // No Back button over the playfield (phase 6 review): Esc or the gamepad's B leave the level.
  root.append(element(doc, 'div', 'game-level', view.level));
  if (view.complete) {
    root.append(levelComplete(doc, view.complete, handlers));
  } else {
    root.append(fireButton(doc, view.fire, handlers));
    dragArea(root, handlers);
  }
  return root;
}
