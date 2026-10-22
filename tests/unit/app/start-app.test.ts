import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { startApp, type RunningApp } from '../../../src/app/start-app';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

describe('startApp', () => {
  let app: RunningApp | undefined;
  afterEach(() => {
    app?.dispose();
    app = undefined;
  });

  it('ENG-145: starts the engine with a game other than src/game', () => {
    const engine = new NullEngine();
    app = startApp(engine, SAMPLE_GAME);
    expect(app.scene.metadata).toEqual({ gameId: 'sample' });
    expect(app.clock.stepSeconds).toBeCloseTo(1 / 60);
  });

  it('disposes the scene', () => {
    const engine = new NullEngine();
    app = startApp(engine, SAMPLE_GAME);
    const { scene } = app;
    app.dispose();
    app = undefined;
    expect(scene.isDisposed).toBe(true);
  });
});
