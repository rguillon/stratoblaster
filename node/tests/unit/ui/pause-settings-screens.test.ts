// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { MenuOverlay } from '../../../src/ui/menu-overlay';
import type { MenuCommand } from '../../../src/input/menu-action';
import type { MenuView } from '../../../src/ui/menu-view';

const TITLE: MenuView = {
  kind: 'title',
  title: 'Stratoblaster',
  highScoreLabel: 'High score',
  highScore: 0,
  start: 'Start',
  settings: 'Settings',
  selected: 1,
  hint: 'hint',
  version: '0.0.0',
  commit: 'abc1234',
};

const GAME: MenuView = {
  kind: 'game',
  level: 'Level 1-1',
  fire: 'Fire',
  pause: '❚❚',
  complete: null,
  paused: null,
  selected: 0,
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
  return { overlay, commands, touch, $, $$ };
}

describe('MenuOverlay: pause and settings (P12)', () => {
  it('P12-R04: the title screen lists Settings under Start; a tap on it selects it', () => {
    const { overlay, commands, $ } = setup();
    overlay.show(TITLE);
    expect($('.title-settings')?.textContent).toBe('Settings');
    expect($('.title-settings')?.classList.contains('selected')).toBe(true);
    expect($('.title-start')?.classList.contains('selected')).toBe(false);
    $('.title-start')?.click();
    expect(commands).toEqual([{ select: 0 }]);
  });

  it('P12-R01: the pause button pauses; its press does not start a drag', () => {
    const { overlay, commands, touch, $ } = setup();
    overlay.show(GAME);
    const button = $('.game-pause');
    expect(button?.textContent).toBe('❚❚');
    button?.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, clientX: 0 }));
    $('.game-screen')?.dispatchEvent(new PointerEvent('pointermove', { clientX: 9, clientY: 0 }));
    button?.click();
    expect(commands).toEqual(['pause']);
    expect(touch.drags).toEqual([]);
  });

  it('P12-R02: the pause menu shows over a dim layer, without the fire and pause buttons; taps select then confirm', () => {
    const { overlay, commands, $, $$ } = setup();
    overlay.show({
      ...GAME,
      selected: 0,
      paused: {
        heading: 'Paused',
        entries: ['Resume', 'Settings', 'Main menu'],
        hint: 'Esc',
        question: null,
      },
    });
    expect($('.pause-dim .pause-heading')?.textContent).toBe('Paused');
    expect($('.game-fire')).toBeNull();
    expect($('.game-pause')).toBeNull();
    const entries = $$('.pause-entry');
    expect(entries.map((e) => e.textContent)).toEqual(['Resume', 'Settings', 'Main menu']);
    expect(entries[0]?.classList.contains('selected')).toBe(true);
    entries[2]?.click();
    entries[0]?.click();
    expect(commands).toEqual([{ select: 2 }, 'confirm']);
  });

  it('P12-R02: the question before leaving shows No and Yes', () => {
    const { overlay, commands, $, $$ } = setup();
    overlay.show({
      ...GAME,
      selected: 0,
      paused: {
        heading: 'Paused',
        entries: ['Resume', 'Settings', 'Main menu'],
        hint: 'Esc',
        question: { text: 'Leave the level?', choices: ['No', 'Yes'], selected: 0 },
      },
    });
    expect($('.pause-question-text')?.textContent).toBe('Leave the level?');
    expect($$('.pause-entry')).toEqual([]);
    const choices = $$('.pause-choice');
    expect(choices.map((c) => c.textContent)).toEqual(['No', 'Yes']);
    choices[1]?.click();
    expect(commands).toEqual([{ select: 1 }]);
  });

  it('P12-R04: the settings screen shows a bar per slider; taps on a bar set it, the Back button goes back', () => {
    const { overlay, commands, $, $$ } = setup();
    overlay.show({
      kind: 'settings',
      heading: 'Settings',
      hint: 'hint',
      back: 'Back',
      selected: 0,
      overLevel: true,
      sliders: [
        { label: 'Music', value: 6, max: 10 },
        { label: 'Sound effects', value: 8, max: 10 },
      ],
    });
    expect($('.settings-screen')?.classList.contains('over-level')).toBe(true);
    const rows = $$('.settings-slider');
    expect(rows.map((r) => r.querySelector('.slider-label')?.textContent)).toEqual([
      'Music',
      'Sound effects',
    ]);
    expect(rows[1]?.getAttribute('aria-valuenow')).toBe('8');
    expect($$('.slider-value').map((v) => v.textContent)).toEqual(['6', '8']);
    expect(rows[0]?.querySelectorAll('.slider-cell.on')).toHaveLength(6);
    const bar = rows[1]?.querySelector<HTMLElement>('.slider-bar');
    if (!bar) throw new Error('no bar');
    bar.getBoundingClientRect = () => ({ left: 100, width: 200 }) as DOMRect;
    bar.dispatchEvent(new PointerEvent('pointerdown', { clientX: 150 }));
    bar.dispatchEvent(new PointerEvent('pointermove', { clientX: 300 }));
    bar.dispatchEvent(new PointerEvent('pointerup', {}));
    bar.dispatchEvent(new PointerEvent('pointermove', { clientX: 100 }));
    bar.click();
    rows[1]?.click();
    $('.menu-back')?.click();
    expect(commands).toEqual([{ set: 1, value: 3 }, { set: 1, value: 10 }, { select: 1 }, 'back']);
  });
});
