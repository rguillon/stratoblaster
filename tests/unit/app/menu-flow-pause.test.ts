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

describe('MenuFlow: pause and settings (P12)', () => {
  it('P12-R01: given game, Backspace / B (back) do nothing; Escape (cancel) and P (pause) pause', () => {
    const flow = atTitle();
    send(flow, 'confirm', 'confirm', 'confirm');
    expect(flow.state.screen).toBe('game');
    send(flow, 'confirm', 'up', 'back', 'resume');
    expect(flow.state).toMatchObject({ screen: 'game', paused: false });
    expect(flow.dispatch('cancel')).toBe('paused');
    expect(flow.state).toMatchObject({ screen: 'pause', paused: true, selectedId: 'resume' });
    flow.update(1);
    expect(flow.dispatch('cancel')).toBe('resumed');
    flow.update(1);
    expect(flow.dispatch('pause')).toBe('paused');
    flow.update(1);
    expect(flow.dispatch('pause')).toBe('resumed');
    expect(flow.state.screen).toBe('game');
  });

  describe('pause (P12)', () => {
    /** A flow playing level 1-1, transitions finished. */
    function playing(): MenuFlow {
      const flow = atTitle();
      send(flow, 'confirm', 'confirm', 'confirm');
      return flow;
    }

    it('P12-R01, P12-R02: pausing keeps the attempt; Resume goes back to it, not to a new one', () => {
      const flow = playing();
      const { attempt } = flow.state;
      expect(flow.pause()).toBe(true);
      expect(flow.pause()).toBe(false);
      flow.update(1);
      expect(flow.dispatch('confirm')).toBe('resumed');
      expect(flow.state).toMatchObject({ screen: 'game', paused: false, attempt });
    });

    it('P12-R02: back and pause resume; resume (test API) too; directions move the selection', () => {
      for (const action of ['back', 'pause', 'resume'] as const) {
        const flow = playing();
        flow.pause();
        flow.update(1);
        expect(flow.dispatch('down')).toBe('moved');
        expect(flow.state.selectedId).toBe('settings');
        expect(flow.dispatch({ select: 2 })).toBe('moved');
        expect(flow.dispatch(action)).toBe('resumed');
      }
    });

    it('P12-R02: Main menu, then Yes, goes to the title with Start selected', () => {
      const flow = playing();
      flow.pause();
      // The pause menu takes input once its screen transition has finished.
      flow.update(1);
      send(flow, 'down', 'down', 'confirm');
      expect(flow.state).toMatchObject({ screen: 'pause', leaving: true, choice: 0 });
      send(flow, 'right');
      expect(flow.state.choice).toBe(1);
      send(flow, 'confirm');
      expect(flow.state).toMatchObject({ screen: 'title', paused: false, selectedId: 'start' });
    });

    it('P12-R02: No, or Back, on the question goes back to the pause menu, still paused', () => {
      const flow = playing();
      flow.pause();
      // The pause menu takes input once its screen transition has finished.
      flow.update(1);
      send(flow, 'down', 'down', 'confirm', 'confirm');
      expect(flow.state).toMatchObject({ screen: 'pause', paused: true, leaving: false });
      send(flow, 'confirm', { select: 1 }, { select: 0 }, 'cancel');
      expect(flow.state).toMatchObject({ screen: 'pause', paused: true, leaving: false });
    });

    it('P12-R02, P12-R04: Settings from the pause menu keeps the level paused; Back returns to the pause menu', () => {
      const flow = playing();
      flow.pause();
      // The pause menu takes input once its screen transition has finished.
      flow.update(1);
      send(flow, 'down', 'confirm');
      expect(flow.state).toMatchObject({ screen: 'settings', paused: true, selectedId: 'music' });
      send(flow, 'pause', 'confirm');
      expect(flow.state.screen).toBe('settings');
      send(flow, 'back');
      expect(flow.state).toMatchObject({ screen: 'pause', paused: true });
    });
  });

  describe('settings (P12-R04)', () => {
    it('P12-R04: the title has Start (selected) and Settings; Settings opens the settings screen', () => {
      const flow = atTitle({ volumes: { music: 6, sfx: 8 }, volumeSteps: 10 });
      expect(flow.state.selectedId).toBe('start');
      expect(flow.dispatch('down')).toBe('moved');
      expect(flow.state.selectedId).toBe('settings');
      send(flow, 'confirm');
      expect(flow.state).toMatchObject({
        screen: 'settings',
        paused: false,
        selectedId: 'music',
        volumes: { music: 6, sfx: 8 },
      });
    });

    it('P12-R04: left / right and taps change the volumes; Escape goes back to the title, on Settings', () => {
      const flow = atTitle({ volumes: { music: 6, sfx: 8 }, volumeSteps: 10 });
      send(flow, 'down', 'confirm');
      expect(flow.dispatch('left')).toBe('adjusted');
      expect(flow.dispatch('down')).toBe('moved');
      expect(flow.dispatch({ set: 1, value: 0 })).toBe('adjusted');
      expect(flow.dispatch({ select: 0 })).toBe('moved');
      expect(flow.state.volumes).toEqual({ music: 5, sfx: 0 });
      send(flow, 'cancel');
      expect(flow.state).toMatchObject({ screen: 'title', selectedId: 'settings' });
    });

    it('P12-R04: volumes default to full when the options give none', () => {
      expect(atTitle().state.volumes).toEqual({ music: 10, sfx: 10 });
    });
  });
});
