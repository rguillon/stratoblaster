// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { GamePlay, type GamePlayOptions } from '../../../src/app/game-play';
import type { SkyScript } from '../../../src/core/scenery/sky-look';
import { GameControls } from '../../../src/input/game-controls';
import { GAME_CONTROLS_CONFIG } from '../../../src/config/game-controls';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

let play: GamePlay | undefined;
afterEach(() => {
  play?.dispose();
  play = undefined;
});

function start(
  overrides: Partial<GamePlayOptions>,
  levelId: string,
  definition: typeof SAMPLE_GAME,
) {
  const controls = new GameControls(GAME_CONTROLS_CONFIG);
  const game = new GamePlay(new NullEngine(), definition, { shipId: 'cube', levelId }, controls, {
    environment: false,
    debug: false,
    startTime: 0,
    doc: document,
    onComplete: () => undefined,
    ...overrides,
  });
  play = game;
  return { game, controls };
}

/** Runs `seconds` of frames of 0.1 s. */
const frames = (game: GamePlay, seconds: number) => {
  for (let i = 0; i < Math.round(seconds * 10); i++) game.frame(0.1);
};

describe('GamePlay weather', () => {
  const level = SAMPLE_GAME.gameLevels.find((l) => l.id === 'a');
  const sceneryId = level?.scenery.id ?? '';
  const look = SAMPLE_GAME.view.scenery.looks[sceneryId];
  const BLIZZARD: SkyScript = {
    start: { timeOfDay: 'afternoon', clouds: [0.9, 0.8], weather: { kind: 'snow', strength: 1 } },
  };
  /** The sample game, its level a in a blizzard. */
  const SNOWY = {
    ...SAMPLE_GAME,
    view: {
      ...SAMPLE_GAME.view,
      scenery: {
        ...SAMPLE_GAME.view.scenery,
        looks: {
          ...SAMPLE_GAME.view.scenery.looks,
          ...(look
            ? {
                [sceneryId]: {
                  ...look,
                  atmosphere: BLIZZARD,
                },
              }
            : {}),
        },
      },
    },
  };

  /** Plays level a for 6 s, firing and moving the same way, and returns what happened. */
  const playThrough = (overrides: Partial<GamePlayOptions>) => {
    const { game, controls } = start(overrides, 'a', SNOWY);
    controls.key('Space', true);
    controls.key('ArrowLeft', true);
    frames(game, 3);
    controls.key('ArrowLeft', false);
    controls.key('ArrowRight', true);
    frames(game, 3);
    const { run } = game;
    const outcome = {
      state: { ...game.state, sky: undefined },
      enemies: run.enemies.enemies.map((e) => [e.x, e.y, e.health]),
      bullets: run.enemies.shots.bullets.filter((b) => b.alive).map((b) => [b.x, b.y]),
      weather: game.view.stage.weatherParticles,
    };
    game.dispose();
    play = undefined;
    return outcome;
  };

  it('P08-R05: weather is only a look: the same level plays the same without it (weather=0)', () => {
    const snowing = playThrough({});
    const clear = playThrough({ atmosphere: { weather: false } });
    expect(snowing.weather).toBeGreaterThan(0);
    expect(clear.weather).toBe(0);
    expect(clear.state).toEqual(snowing.state);
    expect(clear.enemies).toEqual(snowing.enemies);
    expect(clear.bullets).toEqual(snowing.bullets);
  });
});
