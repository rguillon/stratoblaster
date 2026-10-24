import { describe, expect, it } from 'vitest';
import { MenuController, type MenuDisplay } from '../../../src/app/menu-controller';
import type { MenuState } from '../../../src/app/menu-flow';
import type { MenuAction } from '../../../src/input/menu-action';
import { MemoryStorage } from '../../../src/platform/key-value-storage';
import type { MenuView } from '../../../src/ui/menu-view';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

class RecordingDisplay implements MenuDisplay {
  readonly views: MenuView[] = [];
  readonly shakes: string[] = [];
  show(view: MenuView): void {
    this.views.push(view);
  }
  shakeSelected(text: string): void {
    this.shakes.push(text);
  }
  get last(): MenuView | undefined {
    return this.views.at(-1);
  }
}

function setup(storage = new MemoryStorage()) {
  const display = new RecordingDisplay();
  const pending: MenuAction[] = [];
  const changes: MenuState[] = [];
  const controller = new MenuController(SAMPLE_GAME, {
    display,
    input: { update: () => pending.splice(0) },
    storage,
    transitionSeconds: 0.25,
    cardsWidthPercent: 95,
    version: '0.1.0',
    commit: 'abc1234',
    onChange: (state) => changes.push(state),
  });
  const press = (...actions: MenuAction[]): void => {
    for (const action of actions) {
      pending.push(action);
      controller.tick(0.016);
      controller.tick(1);
    }
  };
  return { controller, display, storage, changes, press };
}

describe('MenuController', () => {
  it('P01-R02: shows the loading progress, then the title screen when loading completes', () => {
    const { controller, display } = setup();
    expect(display.last).toMatchObject({ kind: 'loading', progress: 0 });
    controller.setProgress(0.5);
    expect(display.last).toMatchObject({ kind: 'loading', progress: 0.5 });
    controller.finishLoading();
    expect(display.last).toMatchObject({ kind: 'title', highScore: 0 });
  });

  it('P01-R04: shows the stored high score', () => {
    const storage = new MemoryStorage();
    storage.set('sample_high_score', '12345');
    const { controller, display } = setup(storage);
    controller.finishLoading();
    expect(display.last).toMatchObject({ kind: 'title', highScore: 12345 });
  });

  it('P01-R12: runs the flow from the input actions of each frame', () => {
    const { controller, display, press } = setup();
    controller.finishLoading();
    controller.tick(1);
    press('confirm', 'right');
    expect(display.last).toMatchObject({ kind: 'ship-select', selected: 1 });
    press('confirm', 'confirm');
    expect(display.last).toMatchObject({ kind: 'game', level: 'LA' });
  });

  it('P01-R07: gives the "locked" feedback on a locked level', () => {
    const { controller, display, press } = setup();
    controller.finishLoading();
    controller.tick(1);
    press('confirm', 'confirm', 'right', 'confirm');
    expect(display.shakes).toEqual(['Nope']);
    expect(display.last).toMatchObject({ kind: 'level-select', selected: 1 });
  });

  it('P01-R14: saves the chosen ship, and highlights it next time', () => {
    const storage = new MemoryStorage();
    const first = setup(storage);
    first.controller.finishLoading();
    first.controller.tick(1);
    first.controller.command('confirm');
    first.controller.tick(1);
    first.controller.command({ select: 1 });
    first.controller.command('confirm');
    expect(storage.get('sample_last_ship')).toBe('brick');
    const second = setup(storage);
    second.controller.finishLoading();
    second.controller.tick(1);
    second.press('confirm');
    expect(second.display.last).toMatchObject({ kind: 'ship-select', selected: 1 });
  });

  it('P06-R03, P06-R09: starts a level straight away and shows its result', () => {
    const { controller, display, changes } = setup();
    controller.finishLoading();
    expect(controller.playDirect('brick', 'c')).toBe(true);
    expect(display.last).toMatchObject({ kind: 'game', level: 'LC', complete: null });
    controller.completeLevel({ levelId: 'c', destroyed: 1, spawned: 2, outcome: 'complete' });
    expect(display.last).toMatchObject({ kind: 'game', complete: { enemies: '1/2' } });
    expect(changes.at(-1)?.levelResult).toEqual({
      levelId: 'c',
      destroyed: 1,
      spawned: 2,
      outcome: 'complete',
    });
  });

  it('only redraws and notifies when something changed', () => {
    const { controller, display, changes } = setup();
    controller.finishLoading();
    const shown = display.views.length;
    const notified = changes.length;
    controller.refresh();
    controller.tick(0);
    expect(display.views).toHaveLength(shown);
    expect(changes).toHaveLength(notified);
  });
});
