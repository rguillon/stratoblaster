// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { MenuOverlay } from '../../../src/ui/menu-overlay';
import type { MenuCommand } from '../../../src/input/menu-action';
import type { MenuView } from '../../../src/ui/menu-view';

const TITLE: MenuView = {
  kind: 'title',
  title: 'Stratoblaster',
  highScoreLabel: 'High score',
  highScore: 12345,
  start: 'Start',
  hint: 'Press Space / Enter or tap to start',
  version: '0.0.0',
  commit: 'abc1234',
};

const SHIPS: MenuView = {
  kind: 'ship-select',
  heading: 'Choose your ship',
  hint: 'hint',
  back: 'Back',
  selected: 0,
  cardsWidthPercent: 95,
  ships: [
    { title: 'Balanced', lines: ['Speed ×1 (100 px/s)', 'HP 100'] },
    { title: 'Heavy', lines: ['Speed ×0.8 (80 px/s)', 'HP 140'] },
  ],
};

const LEVELS: MenuView = {
  kind: 'level-select',
  heading: 'Choose a level',
  hint: 'hint',
  back: 'Back',
  selected: 1,
  columns: 2,
  lockedText: 'Locked!',
  levels: [
    { label: '1-1', locked: false },
    { label: '1-2', locked: true },
    { label: '2-1', locked: true },
  ],
};

function setup() {
  const root = document.createElement('div');
  const commands: MenuCommand[] = [];
  const touch = { fire: [] as boolean[], drags: [] as [number, number][] };
  const overlay = new MenuOverlay(
    document,
    root,
    (c) => commands.push(c),
    { transitionSeconds: 0.25 },
    {
      fire: (held) => touch.fire.push(held),
      drag: (dx, dy) => touch.drags.push([dx, dy]),
    },
  );
  const $ = (selector: string) => root.querySelector<HTMLElement>(selector);
  const $$ = (selector: string) => [...root.querySelectorAll<HTMLElement>(selector)];
  return { root, overlay, commands, touch, $, $$ };
}

describe('MenuOverlay', () => {
  it('P01-R02: shows a progress bar on the loading screen', () => {
    const { overlay, $ } = setup();
    overlay.show({ kind: 'loading', text: 'Loading…', progress: 0.5 });
    expect($('.loading-bar')?.getAttribute('aria-valuenow')).toBe('50');
    expect($('.loading-fill')?.style.width).toBe('50%');
    expect($('.loading-percent')?.textContent).toBe('50 %');
    overlay.show({ kind: 'loading', text: 'Loading…', progress: 2 });
    expect($('.loading-bar')?.getAttribute('aria-valuenow')).toBe('100');
  });

  it('P01-R04: the title screen shows the title, the high score, Start (selected), hint and version', () => {
    const { overlay, $ } = setup();
    overlay.show(TITLE);
    expect($('.title-name')?.textContent).toBe('Stratoblaster');
    expect($('.title-high-score')?.textContent).toBe('12345');
    expect($('.title-start')?.textContent).toBe('Start');
    expect($('.title-start')?.classList.contains('selected')).toBe(true);
    expect($('.title-hint')?.textContent).toContain('Space / Enter');
    expect($('.version-number')?.textContent).toBe('v0.0.0');
    expect($('.version-commit')?.textContent).toBe('abc1234');
  });

  it('P01-R11: tapping the selected entry confirms it', () => {
    const { overlay, commands, $ } = setup();
    overlay.show(TITLE);
    $('.title-start')?.click();
    expect(commands).toEqual(['confirm']);
  });

  it('P01-R06: one card per ship with name and stats; the selected one is marked', () => {
    const { overlay, $, $$ } = setup();
    overlay.show(SHIPS);
    const cards = $$('.ship-card');
    expect(cards.map((c) => c.querySelector('.ship-card-name')?.textContent)).toEqual([
      'Balanced',
      'Heavy',
    ]);
    expect(cards[1]?.textContent).toContain('HP 140');
    expect(cards.map((c) => c.classList.contains('selected'))).toEqual([true, false]);
    expect(cards[0]?.getAttribute('aria-current')).toBe('true');
    expect($('.ship-cards')?.style.width).toBe('95%');
  });

  it('P01-R11: tapping another entry selects it; the Back button goes back', () => {
    const { overlay, commands, $, $$ } = setup();
    overlay.show(SHIPS);
    $$('.ship-card')[1]?.click();
    $('.menu-back')?.click();
    expect(commands).toEqual([{ select: 1 }, 'back']);
  });

  it('P01-R07: locked levels are greyed out with a padlock', () => {
    const { overlay, $$ } = setup();
    overlay.show(LEVELS);
    const cells = $$('.level-cell');
    expect(cells.map((c) => c.textContent)).toEqual(['1-1', '1-2', '2-1']);
    expect(cells.map((c) => c.classList.contains('locked'))).toEqual([false, true, true]);
    expect(cells[1]?.querySelector('.padlock')).not.toBeNull();
    expect(cells[0]?.querySelector('.padlock')).toBeNull();
    expect(cells[1]?.querySelector('.padlock')?.getAttribute('aria-label')).toBe('locked');
  });

  it('P01-R07: the locked feedback shakes the selected entry and shows a message', () => {
    const { overlay, $ } = setup();
    overlay.show(LEVELS);
    overlay.shakeSelected('Locked!');
    expect($('.level-cell.selected')?.classList.contains('shake')).toBe(true);
    expect($('.menu-status')?.textContent).toBe('Locked!');
    overlay.shakeSelected('Locked!');
    expect($('.level-cell.selected')?.classList.contains('shake')).toBe(true);
  });

  const GAME: MenuView = {
    kind: 'game',
    level: 'Level 1-1',
    fire: 'Fire',
    complete: null,
  };

  it('P06-R02: the game screen shows the level and the touch fire button, and no Back button', () => {
    const { overlay, touch, $ } = setup();
    overlay.show(GAME);
    expect($('.game-level')?.textContent).toBe('Level 1-1');
    // Phase 6 review: no Back button over the playfield (Esc / gamepad B still leave).
    expect($('.menu-back')).toBeNull();
    const fire = $('.game-fire');
    expect(fire?.textContent).toBe('Fire');
    fire?.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
    fire?.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
    expect(touch.fire).toEqual([true, false]);
    expect(touch.drags).toEqual([]);
  });

  it('P06-R02: dragging over the game screen flies the ship (logical pixels, Y up)', () => {
    const { overlay, touch, $ } = setup();
    overlay.show(GAME);
    const screen = $('.game-screen');
    screen?.dispatchEvent(new PointerEvent('pointermove', { clientX: 5, clientY: 5 }));
    screen?.dispatchEvent(new PointerEvent('pointerdown', { clientX: 10, clientY: 20 }));
    screen?.dispatchEvent(new PointerEvent('pointermove', { clientX: 14, clientY: 17 }));
    screen?.dispatchEvent(new PointerEvent('pointerup', {}));
    screen?.dispatchEvent(new PointerEvent('pointermove', { clientX: 30, clientY: 30 }));
    expect(touch.drags).toEqual([[4, 3]]);
  });

  it('P06-R03: the "Level complete" panel shows the level and the counts; a tap goes on', () => {
    const { overlay, commands, $ } = setup();
    overlay.show({
      ...GAME,
      complete: { heading: 'Level complete!', level: '1-2', enemies: '5 / 9', hint: 'Go on' },
    });
    expect($('.level-complete-heading')?.textContent).toBe('Level complete!');
    expect($('.level-complete-level')?.textContent).toBe('1-2');
    expect($('.level-complete-enemies')?.textContent).toBe('5 / 9');
    expect($('.game-fire')).toBeNull();
    $('.level-complete')?.click();
    expect(commands).toEqual(['confirm']);
  });

  it('P01-R15: a new screen fades in; a refresh of the same screen does not', () => {
    const { overlay, root, $ } = setup();
    overlay.show(TITLE);
    expect($('.menu-screen')?.classList.contains('menu-enter')).toBe(true);
    expect($('.menu-screen')?.style.animationDuration).toBe('0.25s');
    overlay.show({ ...SHIPS });
    overlay.show({ ...SHIPS, selected: 1 });
    expect($('.menu-screen')?.classList.contains('menu-enter')).toBe(false);
    expect(root.children).toHaveLength(1);
    expect(overlay.view).toMatchObject({ kind: 'ship-select', selected: 1 });
  });

  it('empties the root on dispose', () => {
    const { overlay, root } = setup();
    overlay.show(TITLE);
    overlay.dispose();
    expect(root.children).toHaveLength(0);
    expect(overlay.view).toBeUndefined();
    overlay.shakeSelected('x');
  });
});
