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
    expect(app.loadingProgress).toEqual([0, 0.2, 0.4, 0.6, 0.8, 1]);
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

  describe('game screen (P06)', () => {
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

    it('ENG-52: step runs the level being played, one step a frame', async () => {
      app = startApp(new NullEngine(), SAMPLE_GAME, options());
      await toGame(app);
      const start = app.game()?.state.time ?? 0;
      app.step(120);
      expect(app.game()?.state.time).toBeCloseTo(start + 2, 5);
    });

    it('P06-R02: confirming a level starts it; the keys fly and fire the ship', async () => {
      const keyboardTarget = new EventTarget();
      const overlay = document.createElement('div');
      app = startApp(new NullEngine(), SAMPLE_GAME, options({ keyboardTarget, overlay }));
      await toGame(app);
      const play = app.game();
      expect(play?.state.levelId).toBe('a');
      expect(screenOf(overlay)).toBe('game');
      // Phase 6 review: a HUD over the level, no Back button.
      expect(overlay.querySelector('.game-hud')).not.toBeNull();
      expect(overlay.querySelector('.menu-back')).toBeNull();
      const x = play?.state.player.x ?? 0;
      keyboardTarget.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyD' }));
      keyboardTarget.dispatchEvent(new KeyboardEvent('keydown', { code: 'Space' }));
      for (let i = 0; i < 10; i++) app.tick(0.05);
      expect(play?.state.player.x).toBeGreaterThan(x);
      expect(play?.state.firing).toBe(true);
      keyboardTarget.dispatchEvent(new KeyboardEvent('keyup', { code: 'Space' }));
      app.tick(0.05);
      expect(play?.state.firing).toBe(false);
      keyboardTarget.dispatchEvent(new Event('blur'));
      app.tick(0.05);
      expect(app.controls.read(1, 1).move).toEqual({ x: 0, y: 0 });
    });

    it('P06-R02: the touch fire button and drags reach the controls', async () => {
      const overlay = document.createElement('div');
      app = startApp(new NullEngine(), SAMPLE_GAME, options({ overlay }));
      await toGame(app);
      settle(app);
      const fire = overlay.querySelector('.game-fire');
      fire?.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
      expect(app.controls.read(1 / 60, 50).fire).toBe(true);
      const screen = overlay.querySelector('.game-screen');
      screen?.dispatchEvent(new PointerEvent('pointerdown', { clientX: 0, clientY: 0 }));
      screen?.dispatchEvent(new PointerEvent('pointermove', { clientX: 10, clientY: 0 }));
      expect(app.controls.read(1, 50).move.x).toBeCloseTo(0.2);
    });

    it('P06-R03: at the end of the level the overlay shows; Confirm goes to level-select', async () => {
      const overlay = document.createElement('div');
      app = startApp(new NullEngine(), SAMPLE_GAME, options({ overlay }));
      await toGame(app, 2);
      for (let i = 0; i < 25 * 10 && !app.menu.flow.state.levelResult; i++) app.tick(0.1);
      expect(app.menu.flow.state.levelResult).toEqual({
        levelId: 'c',
        destroyed: 0,
        spawned: 0,
        outcome: 'complete',
        score: 0,
      });
      expect(overlay.querySelector('.level-complete-level')?.textContent).toBe('C');
      // Past the overlay's input delay (1 s): ten ticks of 0.1 s fall just short of it.
      settle(app);
      settle(app);
      settle(app);
      app.command('confirm');
      expect(app.menu.flow.state).toMatchObject({ screen: 'level-select', selectedId: 'c' });
      expect(app.game()).toBeUndefined();
    });

    it('P06-R09: debug options start their level straight away, with the first ship', async () => {
      const keyboardTarget = new EventTarget();
      const statsParent = document.createElement('div');
      app = startApp(
        new NullEngine(),
        SAMPLE_GAME,
        options({
          keyboardTarget,
          statsParent,
          debug: { levelId: 'c', time: 5, shipId: null, boss: null },
        }),
      );
      await app.loaded;
      expect(app.menu.flow.state).toMatchObject({
        screen: 'game',
        chosenShipId: 'cube',
        chosenLevelId: 'c',
      });
      expect(app.game()?.state.time).toBeCloseTo(5);
      keyboardTarget.dispatchEvent(new KeyboardEvent('keydown', { code: 'ArrowRight' }));
      expect(app.game()?.state.time).toBeCloseTo(15);
      const x = app.game()?.state.player.x;
      app.tick(0.1);
      expect(app.game()?.state.player.x).toBe(x);
      expect(statsParent.querySelector('.stats-tile')).not.toBeNull();
    });
  });

  it('ENG-52: step runs whole simulation frames, then renders once', async () => {
    const engine = new NullEngine();
    app = startApp(engine, SAMPLE_GAME, options());
    await app.loaded;
    const backdrop = SAMPLE_BACKDROPS.at(-1);
    const renders = { count: 0 };
    app.scenes()?.backdropScene.onAfterRenderObservable.add(() => renders.count++);
    app.step(3);
    expect(backdrop?.elapsed).toBeCloseTo(3 / 60);
    expect(renders.count).toBe(1);
    app.step(3, false);
    expect(backdrop?.elapsed).toBeCloseTo(6 / 60);
    expect(renders.count).toBe(1);
    // The fade-in is over after enough frames: the title takes input.
    app.step(30);
    app.command('confirm');
    expect(app.menu.flow.state.screen).toBe('ship-select');
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
