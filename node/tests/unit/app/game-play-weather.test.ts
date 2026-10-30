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

describe('GamePlay weather', () => {
  const level = SAMPLE_GAME.gameLevels.find((l) => l.id === 'a');
  const sceneryId = level?.scenery.id ?? '';
  const look = SAMPLE_GAME.view.scenery.looks[sceneryId];
  const BLIZZARD: SkyScript = {
    start: { timeOfDay: 'afternoon', clouds: [0.9, 0.8], weather: { kind: 'snow', strength: 1 } },
  };
  /** P09-R05: heavy rain and lightning. */
  const THUNDERSTORM: SkyScript = {
    start: {
      timeOfDay: 'afternoon',
      clouds: [0.9, 0.9],
      storm: 1,
      weather: { kind: 'rain', strength: 0.8 },
      lightning: 1,
    },
  };
  /** P10-R06: a forge night, falling ash and embers together. */
  const FORGE_NIGHT: SkyScript = {
    start: {
      timeOfDay: 'night',
      clouds: [0.6, 0.5],
      weather: { kind: 'ash', strength: 0.3 },
      secondWeather: { kind: 'embers', strength: 0.6 },
    },
  };
  /** P10-R05: the level's liquid as lava. */
  const LAVA = {
    crust: [0.08, 0.03, 0.02],
    plate: [0.2, 0.07, 0.04],
    glow: [1, 0.35, 0.05],
    hot: [1, 0.85, 0.45],
    cell: 26,
    crack: 0.12,
    churn: 0.05,
    intensity: 1.3,
    edge: { color: [1, 0.4, 0.08], width: 1.6, cracks: 6 },
  } as const;

  /** The sample game, its level a under `sky` (and with lava for its sea, if `lava`). */
  const under = (sky: SkyScript, lava = false) => ({
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
                  atmosphere: sky,
                  ...(lava ? { sea: { ...look.sea, lava: LAVA } } : {}),
                },
              }
            : {}),
        },
      },
    },
  });

  /**
   * Plays level a under `sky` for `seconds` (half moving left, half right), firing all along,
   * and returns what happened, with the most weather and the brightest flash drawn.
   */
  const playThrough = (
    sky: SkyScript,
    overrides: Partial<GamePlayOptions>,
    seconds = 6,
    lava = false,
  ) => {
    const { game, controls } = start(overrides, 'a', under(sky, lava));
    let flash = 0;
    const half = (key: string) => {
      controls.key(key, true);
      for (let i = 0; i < Math.round(seconds * 5); i++) {
        game.frame(0.1);
        flash = Math.max(flash, game.view.stage.lightningFlash);
      }
      controls.key(key, false);
    };
    controls.key('Space', true);
    half('ArrowLeft');
    half('ArrowRight');
    const { run } = game;
    const outcome = {
      state: { ...game.state, sky: undefined },
      enemies: run.enemies.enemies.map((e) => [e.x, e.y, e.health]),
      bullets: run.enemies.shots.bullets.filter((b) => b.alive).map((b) => [b.x, b.y]),
      weather: game.view.stage.weatherParticles,
      flash,
      lava: game.view.stage.lava !== undefined,
    };
    game.dispose();
    play = undefined;
    return outcome;
  };

  it('P08-R05: weather is only a look: the same level plays the same without it (weather=0)', () => {
    const snowing = playThrough(BLIZZARD, {});
    const clear = playThrough(BLIZZARD, { atmosphere: { weather: false } });
    expect(snowing.weather).toBeGreaterThan(0);
    expect(clear.weather).toBe(0);
    expect(clear.state).toEqual(snowing.state);
    expect(clear.enemies).toEqual(snowing.enemies);
    expect(clear.bullets).toEqual(snowing.bullets);
  });

  it('P09-R05: rain and lightning are only a look: the level plays the same without them', () => {
    // 20 s: the first strikes come within 4 to 10 s.
    const storm = playThrough(THUNDERSTORM, {}, 20);
    const clear = playThrough(THUNDERSTORM, { atmosphere: { weather: false } }, 20);
    expect(storm.weather).toBeGreaterThan(0);
    expect(storm.flash).toBeGreaterThan(0);
    expect(clear.weather).toBe(0);
    expect(clear.flash).toBe(0);
    expect(clear.state).toEqual(storm.state);
    expect(clear.enemies).toEqual(storm.enemies);
    expect(clear.bullets).toEqual(storm.bullets);
  });

  it('P10-R06: falling ash and embers are only a look: the level plays the same without them', () => {
    const forge = playThrough(FORGE_NIGHT, {});
    const clear = playThrough(FORGE_NIGHT, { atmosphere: { weather: false } });
    expect(forge.weather).toBeGreaterThan(0);
    expect(clear.weather).toBe(0);
    expect(clear.state).toEqual(forge.state);
    expect(clear.enemies).toEqual(forge.enemies);
    expect(clear.bullets).toEqual(forge.bullets);
  });

  it('P10-R05: lava is not an input of the simulation: the level plays the same over water', () => {
    const lava = playThrough(FORGE_NIGHT, {}, 6, true);
    const water = playThrough(FORGE_NIGHT, {}, 6, false);
    expect(lava.lava).toBe(true);
    expect(water.lava).toBe(false);
    expect(lava.state).toEqual(water.state);
    expect(lava.enemies).toEqual(water.enemies);
    expect(lava.bullets).toEqual(water.bullets);
  });
});
