// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { GamePlay } from '../../../src/app/game-play';
import { GameControls } from '../../../src/input/game-controls';
import { GAME_CONTROLS_CONFIG } from '../../../src/config/game-controls';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

let play: GamePlay | undefined;
afterEach(() => {
  play?.dispose();
  play = undefined;
});

describe('GamePlay.attach (P13-R03)', () => {
  it('P13-R03: a level built ahead shows no HUD until it is attached', () => {
    const hudParent = document.createElement('div');
    const game = new GamePlay(
      new NullEngine(),
      SAMPLE_GAME,
      { shipId: 'cube', levelId: 'a' },
      new GameControls(GAME_CONTROLS_CONFIG),
      {
        environment: false,
        debug: false,
        startTime: 0,
        doc: document,
        hudParent,
        onComplete: () => undefined,
      },
    );
    play = game;
    expect(hudParent.querySelector('.hud-ship')).toBeNull();
    game.attach();
    game.attach();
    expect(hudParent.querySelectorAll('.hud-ship')).toHaveLength(1);
  });
});
