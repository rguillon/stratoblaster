// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { GameSession } from '../../../src/app/game-session';
import type { MenuState } from '../../../src/app/menu-flow';
import { loadSavedSupplies } from '../../../src/app/saved-supplies';
import { saveWeapons, loadSavedWeapons } from '../../../src/app/saved-weapons';
import { MemoryStorage } from '../../../src/platform/key-value-storage';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

let session: GameSession | undefined;
afterEach(() => {
  session?.dispose();
  session = undefined;
});

const GAME: MenuState = {
  screen: 'game',
  selection: 0,
  selectedId: null,
  highlightedShipId: 'cube',
  chosenShipId: 'cube',
  chosenLevelId: 'a',
  transitioning: false,
  levelResult: null,
  choice: 0,
  attempt: 1,
  resume: null,
  paused: false,
  leaving: false,
  volumes: { music: 6, sfx: 8 },
};

describe('GameSession', () => {
  it('P07-R08: a new attempt (Continue) starts the level again from its checkpoint', () => {
    session = new GameSession(
      new NullEngine(),
      SAMPLE_GAME,
      { environment: false, doc: document },
      () => undefined,
    );
    session.sync(GAME);
    const first = session.play;
    expect(first?.state.time).toBe(0);
    session.sync(GAME);
    expect(session.play).toBe(first);
    const resume = {
      progress: 100,
      bossesPassed: 0,
      score: 0,
      weapons: { weapon: 'pea', levels: { pea: 2 } },
    };
    session.sync({ ...GAME, attempt: 2, resume });
    expect(session.play).not.toBe(first);
    expect(session.play?.state.time).toBeCloseTo(5);
    expect(session.play?.state.weaponLevel).toBe(2);
    session.sync({ ...GAME, screen: 'title', chosenLevelId: null });
    expect(session.play).toBeUndefined();
  });

  it('phase 8 review: a level starts with the weapons kept when the last one was completed', () => {
    const storage = new MemoryStorage();
    const harmless = {
      ...SAMPLE_GAME,
      hull: {
        ...SAMPLE_GAME.hull,
        damage: { bullet: 0, missile: 0, laser: 0, collision: 0 },
        ramDamage: 0,
      },
    };
    session = new GameSession(
      new NullEngine(),
      harmless,
      { environment: false, doc: document, storage },
      () => undefined,
    );
    session.sync(GAME);
    const play = session.play;
    if (!play) throw new Error('the level should have started');
    expect(play.state.weaponLevel).toBe(1);
    play.run.arsenal.levelUp(1);
    // Not kept before the level is complete.
    for (let i = 0; i < 100; i++) play.frame(0.1);
    expect(loadSavedWeapons(storage, harmless.id)).toBeNull();
    for (let i = 0; i < 250; i++) play.frame(0.1);
    expect(play.run.phase).toBe('complete');
    expect(loadSavedWeapons(storage, harmless.id)).toEqual({ weapon: 'pea', levels: { pea: 2 } });
    // The next level starts with them.
    session.sync({ ...GAME, screen: 'title', chosenLevelId: null });
    saveWeapons(storage, harmless.id, { weapon: 'ray', levels: { ray: 2 } });
    session.sync({ ...GAME, chosenLevelId: 'c', attempt: 2 });
    const shots = session.play?.run.shots;
    expect([shots?.weapon.id, shots?.level]).toEqual(['ray', 2]);
  });

  it('reviewer, 2026-10-28: a level starts with the lives and bombs kept when the last one was completed', () => {
    const storage = new MemoryStorage();
    const harmless = {
      ...SAMPLE_GAME,
      hull: {
        ...SAMPLE_GAME.hull,
        damage: { bullet: 0, missile: 0, laser: 0, collision: 0 },
        ramDamage: 0,
      },
    };
    session = new GameSession(
      new NullEngine(),
      harmless,
      { environment: false, doc: document, storage },
      () => undefined,
    );
    session.sync(GAME);
    const play = session.play;
    if (!play) throw new Error('the level should have started');
    const start = play.run.supplies;
    if (!start) throw new Error('the sample game has lives and bombs');
    play.run.hull?.addLife();
    play.run.hull?.addLife();
    for (let i = 0; i < 350; i++) play.frame(0.1);
    expect(play.run.phase).toBe('complete');
    const kept = { lives: start.lives + 2, bombs: start.bombs };
    expect(loadSavedSupplies(storage, harmless.id)).toEqual(kept);
    // The next level starts with them, a Continue with the starting ones.
    session.sync({ ...GAME, screen: 'title', chosenLevelId: null });
    session.sync({ ...GAME, chosenLevelId: 'c', attempt: 2 });
    expect(session.play?.run.supplies).toEqual(kept);
    const resume = {
      progress: 10,
      bossesPassed: 0,
      score: 0,
      weapons: { weapon: 'pea', levels: {} },
    };
    session.sync({ ...GAME, chosenLevelId: 'c', attempt: 3, resume });
    expect(session.play?.run.supplies).toEqual(start);
  });

  it('P11-R03: leaving a level records its score; the HUD gets the saved high score', () => {
    const recorded: number[] = [];
    session = new GameSession(
      new NullEngine(),
      SAMPLE_GAME,
      { environment: false, doc: document },
      () => undefined,
      { highScore: () => 4200, record: (score) => recorded.push(score) },
    );
    session.sync(GAME);
    const play = session.play;
    if (!play) throw new Error('no level');
    play.run.enemies.score = 3000;
    session.sync({ ...GAME, screen: 'title', chosenLevelId: null });
    expect(recorded).toEqual([3000]);
  });

  it('P11-R06: a bomb press made before the level starts does not carry into it', () => {
    session = new GameSession(
      new NullEngine(),
      SAMPLE_GAME,
      { environment: false, doc: document },
      () => undefined,
    );
    session.controls.bomb();
    session.sync(GAME);
    expect(session.controls.read(1 / 60, 100).bomb).toBe(false);
  });
});

describe('GameSession stepped loading', () => {
  it('P13-R02, P13-R03: a level loads in steps, one per call, behind a loading screen', () => {
    const overlay = document.createElement('div');
    let loads = 0;
    session = new GameSession(
      new NullEngine(),
      SAMPLE_GAME,
      {
        environment: false,
        doc: document,
        overlay,
        steppedLoading: true,
        onLoadStart: () => loads++,
      },
      () => undefined,
    );
    session.sync(GAME);
    // The press only starts the loading: nothing heavy runs before its feedback.
    expect([session.play, session.loading, loads]).toEqual([undefined, true, 1]);
    const screen = overlay.querySelector('.level-loading');
    expect(screen).not.toBeNull();
    const progress: string[] = [];
    for (let i = 0; i < 20 && session.loading; i++) {
      session.loadStep();
      // Updated in place: a new element would fade in again, the menus showing through it.
      const shown = overlay.querySelector('.level-loading');
      if (shown) expect(shown).toBe(screen);
      const bar = overlay.querySelector('.loading-bar');
      if (bar) progress.push(bar.getAttribute('aria-valuenow') ?? '');
    }
    expect(session.loading).toBe(false);
    expect(session.play?.state.levelId).toBe('a');
    // The progress bar moved at every step, and the loading screen is gone.
    expect(progress.map(Number)).toEqual([...progress.map(Number)].sort((a, b) => a - b));
    expect(new Set(progress).size).toBe(progress.length);
    expect(overlay.querySelector('.level-loading')).toBeNull();
    // Syncing again while it plays starts nothing new.
    session.sync(GAME);
    expect(loads).toBe(1);
  });

  it('P13-R03: leaving the game screen while a level loads drops it', () => {
    const overlay = document.createElement('div');
    session = new GameSession(
      new NullEngine(),
      SAMPLE_GAME,
      { environment: false, doc: document, overlay, steppedLoading: true },
      () => undefined,
    );
    session.sync(GAME);
    session.loadStep();
    session.loadStep();
    session.sync({ ...GAME, screen: 'title', chosenLevelId: null });
    expect([session.loading, session.play]).toEqual([false, undefined]);
    expect(overlay.querySelector('.level-loading')).toBeNull();
  });

  it('P13-R03: a level started again (Retry) starts the same as the first time', () => {
    session = new GameSession(
      new NullEngine(),
      SAMPLE_GAME,
      { environment: false, doc: document },
      () => undefined,
    );
    session.sync(GAME);
    const first = session.play?.view.stage.stats;
    session.sync({ ...GAME, attempt: 2 });
    expect(session.play?.view.stage.stats).toEqual(first);
  });

  const LEVEL_SELECT: MenuState = {
    ...GAME,
    screen: 'level-select',
    selectedId: 'a',
    chosenLevelId: null,
  };

  function prebuilding(overlay: HTMLElement): GameSession {
    return new GameSession(
      new NullEngine(),
      SAMPLE_GAME,
      { environment: false, doc: document, overlay, steppedLoading: true, prebuildLevels: true },
      () => undefined,
    );
  }

  it('P13-R03: the level the level select highlight rests on is built ahead; confirming it starts it at once', () => {
    const overlay = document.createElement('div');
    session = prebuilding(overlay);
    session.sync(LEVEL_SELECT);
    for (let i = 0; i < 60; i++) session.loadStep(1 / 60);
    // Built, but not started, and no HUD or loading screen in the page.
    expect([session.play, session.loading]).toEqual([undefined, false]);
    expect(overlay.children).toHaveLength(0);
    session.sync(GAME);
    expect(session.loading).toBe(false);
    expect(session.play?.state.levelId).toBe('a');
    expect(overlay.querySelector('.level-loading')).toBeNull();
  });

  it('P13-R03: a level only passed over is not built; a level built ahead for another is not used', () => {
    const overlay = document.createElement('div');
    session = prebuilding(overlay);
    session.sync({ ...LEVEL_SELECT, selectedId: 'b' });
    for (let i = 0; i < 10; i++) session.loadStep(1 / 60);
    session.sync(LEVEL_SELECT);
    for (let i = 0; i < 60; i++) session.loadStep(1 / 60);
    // Confirming another ship's level loads it again, behind the loading screen.
    session.sync({ ...GAME, chosenShipId: 'other' });
    expect(session.loading).toBe(true);
    expect(overlay.querySelector('.level-loading')).not.toBeNull();
  });

  it('P13-R03: leaving the level select drops the level built ahead', () => {
    session = prebuilding(document.createElement('div'));
    session.sync(LEVEL_SELECT);
    for (let i = 0; i < 60; i++) session.loadStep(1 / 60);
    session.sync({ ...LEVEL_SELECT, screen: 'title', selectedId: null });
    session.loadStep(1 / 60);
    session.sync(GAME);
    expect(session.loading).toBe(true);
  });
});
