// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { GamePlay, type GamePlayOptions } from '../../../src/app/game-play';
import type { LevelResult } from '../../../src/core/systems/level-run';
import { GameControls } from '../../../src/input/game-controls';
import { GAME_CONTROLS_CONFIG } from '../../../src/config/game-controls';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

let play: GamePlay | undefined;
afterEach(() => {
  play?.dispose();
  play = undefined;
});

function start(overrides: Partial<GamePlayOptions> = {}, levelId = 'a') {
  const controls = new GameControls(GAME_CONTROLS_CONFIG);
  const results: LevelResult[] = [];
  const game = new GamePlay(new NullEngine(), SAMPLE_GAME, { shipId: 'cube', levelId }, controls, {
    environment: false,
    debug: false,
    startTime: 0,
    doc: document,
    onComplete: (result) => results.push(result),
    ...overrides,
  });
  play = game;
  return { game, controls, results };
}

/** Runs `seconds` of frames of 0.1 s. */
const frames = (game: GamePlay, seconds: number) => {
  for (let i = 0; i < Math.round(seconds * 10); i++) game.frame(0.1);
};

describe('GamePlay', () => {
  it('P06-R02: the chosen ship flies over the scrolling level, moved by the controls', () => {
    const { game, controls } = start();
    expect(game.state).toMatchObject({ levelId: 'a', phase: 'playing', time: 0, duration: 20 });
    expect(game.state.player).toEqual({ x: 150, y: 90 });
    controls.key('ArrowRight', true);
    controls.key('Space', true);
    frames(game, 1);
    expect(game.state.time).toBeCloseTo(1, 1);
    expect(game.state.player.x).toBeGreaterThan(170);
    expect(game.state.firing).toBe(true);
    expect(game.state.shots).toBeGreaterThan(0);
    expect(game.view.stage.camera.position.z).toBeGreaterThan(game.view.stage.framing.back);
  });

  it('phase 6 review: the ship banks into sideways moves and levels out when let go', () => {
    const { game, controls } = start();
    expect(game.roll).toBe(0);
    controls.key('ArrowRight', true);
    frames(game, 1);
    // Right wing down, away from the camera: up to 35° at full sideways speed.
    expect(game.roll).toBeLessThan(-0.4);
    expect(game.roll).toBeGreaterThanOrEqual(-(35 * Math.PI) / 180 - 1e-9);
    controls.key('ArrowRight', false);
    controls.key('ArrowLeft', true);
    frames(game, 1);
    expect(game.roll).toBeGreaterThan(0.4);
    controls.key('ArrowLeft', false);
    frames(game, 2);
    expect(Math.abs(game.roll)).toBeLessThan(0.01);
  });

  it('P06-R02: starts every level with the first weapon at level 1', () => {
    const { game } = start();
    expect(game.run.shots.weapon.id).toBe(SAMPLE_GAME.playerWeapons[0]?.id);
    expect(game.run.shots.level).toBe(1);
  });

  it('P06-R07: the level brings its waves in, and counts what spawned', () => {
    const { game } = start();
    frames(game, 0.5);
    expect(game.state.spawned).toBe(1);
    expect(game.state.wavesTriggered).toBe(1);
  });

  it('P06-R03: tells once that the level is complete, with its counts', () => {
    const { game, results } = start();
    frames(game, 35);
    expect(game.state.phase).toBe('complete');
    expect(results).toEqual([{ levelId: 'a', destroyed: 0, spawned: 5 }]);
    frames(game, 1);
    expect(results).toHaveLength(1);
  });

  it('P06-R09: without debug mode, F, ← and → do nothing to the time', () => {
    const { game } = start();
    expect(game.debugKey('KeyF', true)).toBe(false);
    expect(game.debugKey('ArrowRight', true)).toBe(false);
    frames(game, 0.5);
    expect(game.timeScale).toBe(1);
    expect(game.state.time).toBeCloseTo(0.5, 1);
  });

  it('P06-R09: in debug mode, F fast-forwards ×4 and ← / → jump 10 s', () => {
    const { game } = start({ debug: true });
    expect(game.debugKey('KeyF', true)).toBe(true);
    expect(game.debugKey('KeyF', false)).toBe(true);
    expect(game.timeScale).toBe(4);
    frames(game, 0.5);
    expect(game.state.time).toBeCloseTo(2, 1);
    game.debugKey('KeyF', true);
    expect(game.timeScale).toBe(1);
    game.debugKey('ArrowRight', true);
    expect(game.state.time).toBeCloseTo(12, 1);
    game.debugKey('ArrowLeft', true);
    expect(game.state.time).toBeCloseTo(2, 1);
    expect(game.debugKey('KeyQ', true)).toBe(false);
  });

  it('P06-R09: starts at the given time, with the waves before it skipped; shows the debug tile', () => {
    const statsParent = document.createElement('div');
    const { game } = start({ debug: true, startTime: 6, statsParent });
    expect(game.state.time).toBeCloseTo(6);
    frames(game, 0.5);
    expect(game.state.spawned).toBe(0);
    expect(statsParent.querySelector('.stats-fps')?.textContent).toMatch(/^FPS: /);
    expect(statsParent.querySelector('.stats-polygons')?.textContent).toMatch(/^Polygons: /);
  });

  it('phase 6 review: shows a HUD with the health, the weapon level, the progress and the kills', () => {
    const hudParent = document.createElement('div');
    const { game, controls } = start({ hudParent });
    frames(game, 5);
    expect(hudParent.querySelector('.hud-ship')?.textContent).toBe('Cube');
    expect(hudParent.querySelector('.hud-health-text')?.textContent).toBe('Life 3 / 3');
    expect(hudParent.querySelector('.hud-weapon')?.textContent).toBe('Pea 1/2');
    expect(hudParent.querySelector<HTMLElement>('.hud-progress-fill')?.style.width).toMatch(
      /^(24\.\d|25)%$/,
    );
    expect(hudParent.querySelector('.hud-destroyed')?.textContent).toBe('x0');
    // Phase 6 review: E switches to the next weapon, and the HUD follows.
    controls.key('KeyE', true);
    frames(game, 0.1);
    expect(game.run.shots.weapon.id).toBe('ray');
    expect(hudParent.querySelector('.hud-weapon')?.textContent).toBe('Ray 1/2');
    game.dispose();
    play = undefined;
    expect(hudParent.querySelector('.game-hud')).toBeNull();
  });

  it('refuses a level that cannot be played', () => {
    expect(() => start({}, 'b')).toThrow(/cannot be played/);
  });
});
