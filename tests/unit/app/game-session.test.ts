// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { GameSession } from '../../../src/app/game-session';
import type { MenuState } from '../../../src/app/menu-flow';
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
