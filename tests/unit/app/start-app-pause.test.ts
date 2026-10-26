// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { startApp, type AppOptions, type RunningApp } from '../../../src/app/start-app';
import { MemoryStorage } from '../../../src/platform/key-value-storage';
import type { GamepadLike } from '../../../src/input/gamepad-menu-input';
import { SAMPLE_GAME } from '../../fixtures/sample-game';
import { FakeAudioContext } from '../../helpers/fake-audio';

function options(overrides: Partial<AppOptions> = {}): AppOptions {
  return {
    environment: false,
    doc: document,
    overlay: document.createElement('div'),
    storage: new MemoryStorage(),
    yieldToBrowser: () => Promise.resolve(),
    renderLoop: false,
    ...overrides,
  };
}

/** Runs frames until the current screen transition is over. */
function settle(app: RunningApp): void {
  for (let i = 0; i < 5; i++) app.tick(0.1);
}

/** Through the menus to the game screen on level `index` of the sample grid. */
async function toGame(app: RunningApp, index = 0): Promise<void> {
  await app.loaded;
  settle(app);
  app.command('confirm');
  settle(app);
  app.command('confirm');
  settle(app);
  app.command({ select: index });
  app.command('confirm');
}

describe('startApp: pause and audio (P12)', () => {
  let app: RunningApp | undefined;
  afterEach(() => {
    app?.dispose();
    app = undefined;
  });

  it('P12-R01, P12-R02: Back does nothing in a level; it is left from the pause menu (Main menu, Yes)', async () => {
    const overlay = document.createElement('div');
    app = startApp(new NullEngine(), SAMPLE_GAME, options({ overlay }));
    await toGame(app);
    const play = app.game();
    settle(app);
    app.command('back');
    expect(app.menu.flow.state.screen).toBe('game');
    overlay.querySelector<HTMLElement>('.game-pause')?.click();
    expect(app.menu.flow.state.screen).toBe('pause');
    expect(overlay.querySelector('.pause-panel')).not.toBeNull();
    for (const command of ['down', 'down', 'confirm', 'right', 'confirm'] as const) {
      settle(app);
      app.command(command);
    }
    expect(app.menu.flow.state.screen).toBe('title');
    expect(app.game()).toBeUndefined();
    expect(play?.view.scene.isDisposed).toBe(true);
    expect(overlay.querySelector('.game-hud')).toBeNull();
    settle(app);
  });

  it('P12-R01: a paused level stays exactly as it was for 10 s, then goes on from there', async () => {
    const keyboardTarget = new EventTarget();
    app = startApp(new NullEngine(), SAMPLE_GAME, options({ keyboardTarget }));
    await toGame(app, 1);
    settle(app);
    keyboardTarget.dispatchEvent(new KeyboardEvent('keydown', { code: 'Space' }));
    for (let i = 0; i < 20; i++) app.tick(0.05);
    const play = app.game();
    app.command('pause');
    const before = JSON.stringify(play?.state);
    for (let i = 0; i < 100; i++) app.tick(0.1);
    expect(JSON.stringify(play?.state)).toBe(before);
    // The debug keys do nothing while paused.
    keyboardTarget.dispatchEvent(new KeyboardEvent('keydown', { code: 'ArrowRight' }));
    expect(JSON.stringify(play?.state)).toBe(before);
    const time = play?.state.time ?? 0;
    app.command('resume');
    expect(app.game()).toBe(play);
    app.step(6);
    // No time skipped: six steps after the pause, not ten seconds.
    expect(play?.state.time).toBeCloseTo(time + 0.1, 5);
  });

  it('P12-R03, P12-R11: a hidden page pauses the level and silences the audio; it does not resume by itself', async () => {
    const target = new EventTarget();
    let hidden = false;
    const context = new FakeAudioContext();
    app = startApp(
      new NullEngine(),
      SAMPLE_GAME,
      options({
        visibility: { target, hidden: () => hidden },
        audio: { createContext: () => context.asContext() },
        gestureTarget: target,
      }),
    );
    await toGame(app);
    target.dispatchEvent(new Event('pointerdown'));
    expect(app.audio.state.context).toBe('running');
    hidden = true;
    target.dispatchEvent(new Event('visibilitychange'));
    expect(app.menu.flow.state).toMatchObject({ screen: 'pause', paused: true });
    expect(context.state).toBe('suspended');
    hidden = false;
    target.dispatchEvent(new Event('visibilitychange'));
    settle(app);
    expect(app.menu.flow.state).toMatchObject({ screen: 'pause', paused: true });
    expect(context.state).toBe('running');
  });

  it('P12-R03: the gamepad in use disconnected pauses the level', async () => {
    let pads: (GamepadLike | null)[] = [{ buttons: [{ pressed: false }], axes: [0.9, 0] }];
    app = startApp(new NullEngine(), SAMPLE_GAME, options({ gamepads: () => pads }));
    await toGame(app);
    settle(app);
    expect(app.menu.flow.state.screen).toBe('game');
    pads = [null];
    app.tick(0.05);
    expect(app.menu.flow.state).toMatchObject({ screen: 'pause', paused: true });
  });

  it('P12-R05: without AudioContext every screen works; the first gesture creates the context when it exists', async () => {
    const target = new EventTarget();
    const silent = startApp(new NullEngine(), SAMPLE_GAME, options({ gestureTarget: target }));
    await silent.loaded;
    target.dispatchEvent(new KeyboardEvent('keydown', { code: 'Enter' }));
    for (const command of ['confirm', 'confirm', 'confirm', 'pause', 'resume'] as const) {
      settle(silent);
      silent.command(command);
    }
    expect(silent.menu.flow.state.screen).toBe('game');
    expect(silent.audio.state.context).toBe('none');
    silent.dispose();
    const context = new FakeAudioContext();
    const ticks: (() => void)[] = [];
    app = startApp(
      new NullEngine(),
      SAMPLE_GAME,
      options({
        gestureTarget: target,
        audio: { createContext: () => context.asContext() },
        every: (tick) => {
          ticks.push(tick);
          return () => ticks.splice(0);
        },
      }),
    );
    await app.loaded;
    expect(app.audio.state.context).toBe('none');
    target.dispatchEvent(new KeyboardEvent('keydown', { code: 'Enter' }));
    expect(app.audio.state.context).toBe('running');
    expect(ticks).toHaveLength(1);
    ticks[0]?.();
  });

  it('P12-R05: a gamepad button is a gesture too', async () => {
    const context = new FakeAudioContext();
    app = startApp(
      new NullEngine(),
      SAMPLE_GAME,
      options({
        gamepads: () => [{ buttons: [{ pressed: true }], axes: [] }],
        audio: { createContext: () => context.asContext() },
      }),
    );
    await app.loaded;
    app.tick(0.016);
    expect(app.audio.state.context).toBe('running');
  });
});
