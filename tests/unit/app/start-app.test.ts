// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { startApp, type AppOptions, type RunningApp } from '../../../src/app/start-app';
import { MemoryStorage } from '../../../src/platform/key-value-storage';
import type { GamepadLike } from '../../../src/input/gamepad-menu-input';
import { SAMPLE_BACKDROPS, SAMPLE_GAME } from '../../fixtures/sample-game';

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

const screenOf = (overlay: HTMLElement): string | undefined =>
  overlay.querySelector<HTMLElement>('.menu-screen')?.dataset.screen;

describe('startApp', () => {
  let app: RunningApp | undefined;
  afterEach(() => {
    app?.dispose();
    app = undefined;
  });

  it('ENG-145: starts the engine with a game other than src/game', async () => {
    app = startApp(new NullEngine(), SAMPLE_GAME, options());
    expect(app.clock.stepSeconds).toBeCloseTo(1 / 60);
    await app.loaded;
    expect(app.scenes()?.backdropScene.metadata).toEqual({ gameId: 'sample' });
  });

  it('P01-R02: shows a loading screen with real progress, then the title by itself', async () => {
    const overlay = document.createElement('div');
    app = startApp(new NullEngine(), SAMPLE_GAME, options({ overlay }));
    expect(screenOf(overlay)).toBe('loading');
    expect(app.scenes()).toBeUndefined();
    await app.loaded;
    expect(app.loadingProgress).toEqual([0, 0.25, 0.5, 0.75, 1]);
    expect(app.menu.flow.state.screen).toBe('title');
    expect(screenOf(overlay)).toBe('title');
  });

  it('P01-R05, P01-R06: animates the backdrop and shows the ship stage on ship-select', async () => {
    app = startApp(new NullEngine(), SAMPLE_GAME, options());
    await app.loaded;
    const backdrop = SAMPLE_BACKDROPS.at(-1);
    app.tick(0.05);
    expect(backdrop?.elapsed).toBeCloseTo(0.05);
    app.tick(10); // capped frame time
    expect(backdrop?.elapsed).toBeCloseTo(0.15);
    settle(app);
    app.command('confirm');
    settle(app);
    app.command('right');
    expect(backdrop?.screens).toContain('title');
    expect(backdrop?.screens.at(-1)).toBe('ship-select');
    expect(app.scenes()?.stage.selected).toBe(1);
  });

  it('P01-R11: taps on the overlay drive the menus', async () => {
    const overlay = document.createElement('div');
    app = startApp(new NullEngine(), SAMPLE_GAME, options({ overlay }));
    await app.loaded;
    settle(app);
    overlay.querySelector<HTMLElement>('.title-start')?.click();
    expect(app.menu.flow.state.screen).toBe('ship-select');
  });

  it('P01-R09: listens to the keyboard target', async () => {
    const keyboardTarget = new EventTarget();
    app = startApp(new NullEngine(), SAMPLE_GAME, options({ keyboardTarget }));
    await app.loaded;
    settle(app);
    keyboardTarget.dispatchEvent(new KeyboardEvent('keydown', { code: 'Enter' }));
    app.tick(0.016);
    expect(app.menu.flow.state.screen).toBe('ship-select');
  });

  it('P01-R10: polls the gamepads every frame', async () => {
    const pad: GamepadLike = { buttons: [{ pressed: true }], axes: [] };
    app = startApp(new NullEngine(), SAMPLE_GAME, options({ gamepads: () => [pad] }));
    await app.loaded;
    settle(app);
    expect(app.menu.flow.state.screen).toBe('title'); // A was pressed during the fade-in (ignored); holding it does not press again
  });

  it('runs in the render loop when asked', async () => {
    const engine = new NullEngine();
    app = startApp(engine, SAMPLE_GAME, options({ renderLoop: true }));
    await app.loaded;
    expect(engine.activeRenderLoops).toHaveLength(1);
    app.dispose();
    app = undefined;
    expect(engine.activeRenderLoops).toHaveLength(0);
  });

  it('disposes the scenes and the overlay', async () => {
    const overlay = document.createElement('div');
    app = startApp(new NullEngine(), SAMPLE_GAME, options({ overlay }));
    await app.loaded;
    const scenes = app.scenes();
    app.dispose();
    app = undefined;
    expect(scenes?.backdropScene.isDisposed).toBe(true);
    expect(scenes?.shipScene.isDisposed).toBe(true);
    expect(overlay.children).toHaveLength(0);
  });
});
