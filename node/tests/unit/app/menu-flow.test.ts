import { describe, expect, it } from 'vitest';
import { MenuFlow, type MenuFlowOptions } from '../../../src/app/menu-flow';
import { buildLevelGrid } from '../../../src/core/content/level-catalog';
import type { MenuCommand } from '../../../src/input/menu-action';

const OPTIONS: MenuFlowOptions = {
  shipIds: ['balanced', 'heavy', 'light'],
  levels: buildLevelGrid(5, 5, ['1-1']),
  transitionSeconds: 0.25,
};

/** A flow on the title screen, with transitions finished. */
function atTitle(options: Partial<MenuFlowOptions> = {}): MenuFlow {
  const flow = new MenuFlow({ ...OPTIONS, ...options });
  flow.finishLoading();
  flow.update(1);
  return flow;
}

/** Sends commands, letting each screen transition finish. */
function send(flow: MenuFlow, ...commands: MenuCommand[]): void {
  for (const command of commands) {
    flow.dispatch(command);
    flow.update(1);
  }
}

/** The checkpoint of a 1-2 game over after its mini boss (P07-R08). */
const CHECKPOINT = {
  progress: 7800,
  bossesPassed: 1,
  score: 0,
  weapons: { weapon: 'bullet', levels: {} },
};

describe('MenuFlow', () => {
  it('P01-R01: starts on the loading screen and shows the title when loading completes', () => {
    const flow = new MenuFlow(OPTIONS);
    expect(flow.state.screen).toBe('loading');
    expect(flow.dispatch('confirm')).toBe('none');
    flow.finishLoading();
    expect(flow.state.screen).toBe('title');
    expect(flow.state.selectedId).toBe('start');
  });

  it('P01-R01: given the title screen, when Start is confirmed, then the screen is ship-select', () => {
    const flow = atTitle();
    expect(flow.dispatch('confirm')).toBe('screen');
    expect(flow.state.screen).toBe('ship-select');
  });

  it('P01-R01: given ship-select, when Back is pressed, then the screen is title', () => {
    const flow = atTitle();
    send(flow, 'confirm', 'back');
    expect(flow.state.screen).toBe('title');
  });

  it('P01-R01: Back from level-select returns to ship-select with the chosen ship still selected', () => {
    const flow = atTitle();
    send(flow, 'confirm', 'right', 'right', 'confirm');
    expect(flow.state.screen).toBe('level-select');
    send(flow, 'back');
    expect(flow.state.screen).toBe('ship-select');
    expect(flow.state.selectedId).toBe('light');
    expect(flow.state.chosenShipId).toBe('light');
  });

  it('P01-R01: invalid transitions are rejected and leave the state unchanged', () => {
    const flow = atTitle();
    const before = flow.state;
    const revision = flow.revision;
    expect(flow.goTo('game')).toBe(false);
    expect(flow.goTo('loading')).toBe(false);
    expect(flow.state).toEqual(before);
    expect(flow.revision).toBe(revision);
    expect(flow.goTo('ship-select')).toBe(true);
  });

  it('ignores Back on the title screen and moves on screens without a list', () => {
    const flow = atTitle();
    expect(flow.dispatch('back')).toBe('none');
    expect(flow.dispatch('left')).toBe('none');
    expect(flow.dispatch({ select: 0 })).toBe('none');
    expect(flow.state.screen).toBe('title');
  });

  it('P01-R06: the balanced (first) ship is highlighted the first time', () => {
    const flow = atTitle();
    send(flow, 'confirm');
    expect(flow.state.selectedId).toBe('balanced');
    expect(flow.state.highlightedShipId).toBe('balanced');
  });

  it('P01-R06: Right highlights the next ship and wraps around at the ends', () => {
    const flow = atTitle();
    send(flow, 'confirm');
    expect(flow.dispatch('right')).toBe('moved');
    expect(flow.state.selectedId).toBe('heavy');
    send(flow, 'right', 'right');
    expect(flow.state.selectedId).toBe('balanced');
    send(flow, 'left');
    expect(flow.state.selectedId).toBe('light');
  });

  it('P01-R06: Confirm stores the highlighted ship as the chosen ship and opens level-select', () => {
    const flow = atTitle();
    send(flow, 'confirm', 'right');
    expect(flow.state.chosenShipId).toBeNull();
    send(flow, 'confirm');
    expect(flow.state.chosenShipId).toBe('heavy');
    expect(flow.state.screen).toBe('level-select');
  });

  it('P01-R14: highlights the remembered ship, and ignores an unknown one', () => {
    const remembered = atTitle({ initialShipId: 'light' });
    send(remembered, 'confirm');
    expect(remembered.state.selectedId).toBe('light');
    const unknown = atTitle({ initialShipId: 'ufo' });
    send(unknown, 'confirm');
    expect(unknown.state.selectedId).toBe('balanced');
  });

  it('P01-R07: 1-1 is highlighted when level-select opens', () => {
    const flow = atTitle();
    send(flow, 'confirm', 'confirm', 'right', 'down', 'back', 'confirm');
    expect(flow.state.screen).toBe('level-select');
    expect(flow.state.selectedId).toBe('1-1');
  });

  it('P01-R07: the arrows move the selection in the 5 × 5 grid', () => {
    const flow = atTitle();
    send(flow, 'confirm', 'confirm', 'down', 'right', 'right');
    expect(flow.state.selectedId).toBe('2-3');
    send(flow, 'up', 'left', 'left', 'left');
    expect(flow.state.selectedId).toBe('1-1');
  });

  it('P01-R07: confirming a locked level only gives a "locked" feedback', () => {
    const flow = atTitle();
    send(flow, 'confirm', 'confirm', 'right');
    const before = flow.state;
    expect(flow.dispatch('confirm')).toBe('locked');
    expect(flow.state).toEqual(before);
  });

  it('P01-R07, P01-R08: confirming 1-1 opens the game screen with the chosen ship and level', () => {
    const flow = atTitle();
    send(flow, 'confirm', 'right', 'confirm', 'confirm');
    expect(flow.state).toMatchObject({
      screen: 'game',
      chosenShipId: 'heavy',
      chosenLevelId: '1-1',
      selectedId: null,
    });
  });

  describe('World 1 (P06)', () => {
    const WORLD_1 = ['1-1', '1-2', '1-3', '1-4', '1-5'];
    const world1 = () => atTitle({ levels: buildLevelGrid(5, 5, WORLD_1), resultDelaySeconds: 1 });
    const result = (levelId: string) => ({
      levelId,
      destroyed: 3,
      spawned: 5,
      outcome: 'complete' as const,
      score: 0,
    });

    it('P06-R01: any World 1 level can be started straight away, 1-5 included', () => {
      const flow = world1();
      send(flow, 'confirm', 'confirm', 'right', 'right', 'right', 'right');
      expect(flow.state.selectedId).toBe('1-5');
      send(flow, 'confirm');
      expect(flow.state).toMatchObject({ screen: 'game', chosenLevelId: '1-5' });
    });

    it('P06-R01: the levels of worlds 2 to 5 stay locked', () => {
      const flow = world1();
      send(flow, 'confirm', 'confirm', 'down');
      expect(flow.state.selectedId).toBe('2-1');
      expect(flow.dispatch('confirm')).toBe('locked');
    });

    it('P06-R03: at the end of 1-2, the overlay shows; Confirm goes to level-select on 1-3', () => {
      const flow = world1();
      send(flow, 'confirm', 'confirm', 'right', 'confirm');
      expect(flow.dispatch('confirm')).toBe('none');
      flow.completeLevel(result('1-2'));
      expect(flow.state).toMatchObject({ screen: 'game', levelResult: result('1-2') });
      // The overlay ignores input for a moment, so a held fire key does not skip it.
      expect(flow.state.transitioning).toBe(true);
      expect(flow.dispatch('confirm')).toBe('none');
      flow.update(1);
      expect(flow.dispatch('confirm')).toBe('screen');
      expect(flow.state).toMatchObject({
        screen: 'level-select',
        selectedId: '1-3',
        levelResult: null,
      });
    });

    it('GD-20: after "Game over" in 1-2, Confirm goes to level-select on 1-2 again', () => {
      const flow = world1();
      expect(flow.playDirect('heavy', '1-2')).toBe(true);
      flow.completeLevel({ ...result('1-2'), outcome: 'over' });
      flow.update(1);
      expect(flow.dispatch('confirm')).toBe('screen');
      expect(flow.state).toMatchObject({ screen: 'level-select', selectedId: '1-2' });
    });

    it('P07-R08: after the mini boss, a game over offers Continue (first) and level select', () => {
      const flow = world1();
      expect(flow.playDirect('heavy', '1-2')).toBe(true);
      const attempt = flow.state.attempt;
      const checkpoint = CHECKPOINT;
      flow.completeLevel({ ...result('1-2'), outcome: 'over', checkpoint });
      flow.update(1);
      expect(flow.state.choice).toBe(0);
      expect(flow.dispatch('right')).toBe('moved');
      expect(flow.state.choice).toBe(1);
      expect(flow.dispatch('right')).toBe('none');
      expect(flow.dispatch('up')).toBe('moved');
      expect(flow.dispatch({ select: 1 })).toBe('moved');
      expect(flow.dispatch({ select: 5 })).toBe('none');
      expect(flow.dispatch({ select: 0 })).toBe('moved');
      expect(flow.dispatch('confirm')).toBe('screen');
      expect(flow.state).toMatchObject({
        screen: 'game',
        levelResult: null,
        resume: checkpoint,
        attempt: attempt + 1,
      });
    });

    it('P07-R08: choosing level select after the mini boss goes there, on the level played', () => {
      const flow = world1();
      flow.playDirect('heavy', '1-2');
      const checkpoint = CHECKPOINT;
      flow.completeLevel({ ...result('1-2'), outcome: 'over', checkpoint });
      flow.update(1);
      send(flow, 'down', 'confirm');
      expect(flow.state).toMatchObject({ screen: 'level-select', selectedId: '1-2', resume: null });
      send(flow, 'confirm');
      expect(flow.state).toMatchObject({ screen: 'game', resume: null });
    });

    it('P06-R03: after 1-5, level-select highlights 1-5 again', () => {
      const flow = world1();
      expect(flow.playDirect('heavy', '1-5')).toBe(true);
      flow.completeLevel(result('1-5'));
      flow.completeLevel(result('1-1'));
      expect(flow.state.levelResult?.levelId).toBe('1-5');
      flow.update(1);
      send(flow, 'confirm');
      expect(flow.state.selectedId).toBe('1-5');
    });

    it('P06-R03, P12-R01: a result outside the game screen is ignored; the panel cannot be paused or left with Back', () => {
      const flow = world1();
      flow.completeLevel(result('1-1'));
      expect(flow.state.levelResult).toBeNull();
      send(flow, 'confirm', 'confirm', 'confirm');
      flow.completeLevel(result('1-1'));
      flow.update(1);
      send(flow, 'back', 'cancel', 'pause');
      expect(flow.pause()).toBe(false);
      expect(flow.state).toMatchObject({ screen: 'game', paused: false });
      expect(flow.state.levelResult).not.toBeNull();
    });

    it('P06-R09: a level can be started straight away with a ship; unknown or locked ones cannot', () => {
      const flow = world1();
      expect(flow.playDirect('light', '1-3')).toBe(true);
      expect(flow.state).toMatchObject({
        screen: 'game',
        chosenShipId: 'light',
        chosenLevelId: '1-3',
        highlightedShipId: 'light',
        transitioning: false,
      });
      const other = world1();
      expect(other.playDirect('light', '2-1')).toBe(false);
      expect(other.playDirect('wing', '1-1')).toBe(false);
      expect(other.playDirect('light', '9-9')).toBe(false);
      expect(other.state.screen).toBe('title');
    });
  });

  it('P01-R11: a pointer selection selects an entry; out-of-range ones are ignored', () => {
    const flow = atTitle();
    send(flow, 'confirm');
    expect(flow.dispatch({ select: 2 })).toBe('moved');
    expect(flow.state.selectedId).toBe('light');
    expect(flow.dispatch({ select: 2 })).toBe('none');
    expect(flow.dispatch({ select: 3 })).toBe('none');
    expect(flow.dispatch({ select: -1 })).toBe('none');
    expect(flow.dispatch({ select: 0.5 })).toBe('none');
    expect(flow.state.selectedId).toBe('light');
  });

  it('P01-R15: input is ignored during a screen transition', () => {
    const flow = atTitle();
    flow.dispatch('confirm');
    expect(flow.state.transitioning).toBe(true);
    expect(flow.dispatch('confirm')).toBe('none');
    flow.update(0.2);
    expect(flow.dispatch('back')).toBe('none');
    flow.update(0.05);
    expect(flow.state.transitioning).toBe(false);
    expect(flow.state.screen).toBe('ship-select');
    expect(flow.dispatch('back')).toBe('screen');
  });

  it('bumps the revision on every visible change', () => {
    const flow = atTitle();
    const start = flow.revision;
    flow.dispatch('confirm');
    expect(flow.revision).toBe(start + 1);
    flow.update(1);
    expect(flow.revision).toBe(start + 2);
    flow.update(1);
    expect(flow.revision).toBe(start + 2);
  });

  it('needs at least one ship and one level', () => {
    expect(() => new MenuFlow({ ...OPTIONS, shipIds: [] })).toThrow(/ship/);
    expect(() => new MenuFlow({ ...OPTIONS, levels: { columns: 1, levels: [] } })).toThrow(/level/);
  });
});
