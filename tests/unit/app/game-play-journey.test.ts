// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { GamePlay, type GamePlayOptions } from '../../../src/app/game-play';
import type { LevelResult } from '../../../src/core/systems/level-run';
import { GameControls } from '../../../src/input/game-controls';
import { GAME_CONTROLS_CONFIG } from '../../../src/config/game-controls';
import { SAMPLE_GAME } from '../../fixtures/sample-game';
import { BOSSY } from './game-play-games';

let play: GamePlay | undefined;
afterEach(() => {
  play?.dispose();
  play = undefined;
});

function start(overrides: Partial<GamePlayOptions> = {}, levelId = 'a', definition = SAMPLE_GAME) {
  const controls = new GameControls(GAME_CONTROLS_CONFIG);
  const results: LevelResult[] = [];
  const game = new GamePlay(new NullEngine(), definition, { shipId: 'cube', levelId }, controls, {
    environment: false,
    debug: false,
    startTime: 0,
    // The arrival and departure have their own test below.
    journey: false,
    doc: document,
    onComplete: (result) => results.push(result),
    ...overrides,
  });
  game.attach();
  play = game;
  return { game, controls, results };
}

const frames = (game: GamePlay, seconds: number) => {
  for (let i = 0; i < Math.round(seconds * 10); i++) game.frame(0.1);
};

describe("GamePlay: the ship's arrival and departure", () => {
  it('reviewer 2026-10-28: the ship rises in from below, and flies off the top after the final boss', () => {
    const { game, controls, results } = start({ journey: true, debug: true }, 'a', BOSSY);
    expect(game.state.player.y).toBeLessThan(0);
    // Arriving, the controls do nothing.
    controls.key('ArrowRight', true);
    frames(game, 0.5);
    expect(game.state.player.x).toBe(150);
    controls.key('ArrowRight', false);
    frames(game, 1.5);
    expect(game.state.player.y).toBeCloseTo(90, 0);
    game.debugKey('KeyK', true); // no-op outside a fight
    const { game: final, results: done } = start(
      { journey: true, debug: true, startBoss: 'final' },
      'a',
      BOSSY,
    );
    frames(final, 3);
    for (let i = 0; i < 3; i++) {
      final.debugKey('KeyK', true);
      frames(final, 0.2);
    }
    frames(final, 2);
    // Cleared: the player still flies it, then it leaves by the top and the level completes.
    expect([final.state.phase, done]).toEqual(['clearing', []]);
    frames(final, 5);
    expect(final.state.player.y).toBeGreaterThan(SAMPLE_GAME.screen.height);
    expect(final.state.phase).toBe('complete');
    expect(done).toHaveLength(1);
    expect(results).toEqual([]);
  });
});
