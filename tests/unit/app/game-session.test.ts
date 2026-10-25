// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { GameSession } from '../../../src/app/game-session';
import type { MenuState } from '../../../src/app/menu-flow';
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
      weapons: { weapon: 'pea', levels: { pea: 2 } },
    };
    session.sync({ ...GAME, attempt: 2, resume });
    expect(session.play).not.toBe(first);
    expect(session.play?.state.time).toBeCloseTo(5);
    expect(session.play?.state.weaponLevel).toBe(2);
    session.sync({ ...GAME, screen: 'title', chosenLevelId: null });
    expect(session.play).toBeUndefined();
  });
});
