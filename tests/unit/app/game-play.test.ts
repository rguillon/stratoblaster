// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { GamePlay, type GamePlayOptions } from '../../../src/app/game-play';
import type { LevelResult } from '../../../src/core/systems/level-run';
import { GameControls } from '../../../src/input/game-controls';
import { GAME_CONTROLS_CONFIG } from '../../../src/config/game-controls';
import { bonusFrames, SAMPLE_GAME } from '../../fixtures/sample-game';

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
    doc: document,
    onComplete: (result) => results.push(result),
    ...overrides,
  });
  play = game;
  return { game, controls, results };
}

/** The sample game where hits and rams do no damage, for tests of other things on level a. */
const HARMLESS = {
  ...SAMPLE_GAME,
  hull: {
    ...SAMPLE_GAME.hull,
    damage: { bullet: 0, missile: 0, laser: 0, collision: 0 },
    ramDamage: 0,
  },
};

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

  it('phase 6 review: weapon bonuses are drawn, and picking one up raises the weapon level', () => {
    const bonuses = { chance: { perHealth: 0, min: 1, max: 1 }, fallSpeed: 100, pickupRadius: 15 };
    const { game } = start({}, 'a', { ...SAMPLE_GAME, bonuses });
    expect(game.state).toMatchObject({ weaponLevel: 1, bonuses: 0, bonusesDropped: 0 });
    const { x, y } = game.run.ship;
    game.run.bonuses?.drop([{ id: 1, x, y: y + 60, radius: 5, health: 0, maxHealth: 10 }]);
    game.frame(0.1);
    expect(game.state).toMatchObject({ bonuses: 1, bonusesDropped: 1 });
    expect(bonusFrames.at(-1)?.bonuses).toHaveLength(1);
    frames(game, 1);
    expect(game.state).toMatchObject({ weaponLevel: 2, bonuses: 0 });
    expect(bonusFrames.some((f) => f.picked.length === 1)).toBe(true);
  });

  it('GD-20..GD-22: a hit takes health and the ship blinks; out of lives, "Game over" comes', () => {
    const hud = document.createElement('div');
    // Level c has no waves: only the bullets fired here hit the ship.
    const { game, results } = start({ hudParent: hud }, 'c');
    const pivot = game.view.scene.getTransformNodeByName('playfield-ship');
    const shoot = () => {
      const { x, y } = game.run.ship;
      game.run.enemies.shots.fireBullet(x, y, 0, { speed: 0, radius: 2, style: 's' });
    };
    expect(game.state).toMatchObject({ health: 3, lives: 2, invincible: 0 });
    shoot();
    game.frame(0.1);
    expect(game.state).toMatchObject({ health: 2, lives: 2 });
    expect(hud.querySelector('.hud-health-text')?.textContent).toBe('Life 2 / 3');
    expect(hud.querySelector('.hud-lives')?.textContent).toBe('L2');
    // Blinking while invincible (1 s in the sample game).
    const shown = Array.from({ length: 8 }, () => {
      game.frame(0.05);
      return pivot?.isEnabled(false);
    });
    expect(shown).toContain(true);
    expect(shown).toContain(false);
    frames(game, 1);
    expect(pivot?.isEnabled(false)).toBe(true);
    // Five more hits (3 health per life, 2 lives), one a second.
    for (let i = 0; i < 5; i++) {
      shoot();
      frames(game, 1.2);
    }
    expect(game.state.phase).toBe('over');
    expect(game.state.lives).toBe(0);
    expect(pivot?.isEnabled(false)).toBe(false);
    expect(results).toEqual([]);
    frames(game, 2.1);
    expect(results).toEqual([{ levelId: 'c', destroyed: 0, spawned: 0, outcome: 'over' }]);
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
    const { game, results } = start({}, 'a', HARMLESS);
    frames(game, 35);
    expect(game.state.phase).toBe('complete');
    expect(results).toEqual([{ levelId: 'a', destroyed: 0, spawned: 5, outcome: 'complete' }]);
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
    const { game, controls } = start({ hudParent }, 'a', HARMLESS);
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
