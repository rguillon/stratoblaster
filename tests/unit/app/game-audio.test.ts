import { describe, expect, it } from 'vitest';
import { GameAudio } from '../../../src/app/game-audio';
import type { MusicRequest } from '../../../src/audio/audio-bindings';
import type { LevelRun } from '../../../src/core/systems/level-run';
import { FakeAudioContext } from '../../helpers/fake-audio';
import { bindings, MENU, run } from '../../helpers/sample-audio';

/** A `GameAudio` on a fake context (none with `{ webAudio: false }`), and its clock. */
function setup({ webAudio = true } = {}) {
  const context = webAudio ? new FakeAudioContext() : undefined;
  let now = 0;
  const requests: MusicRequest[] = [];
  const audio = new GameAudio(bindings(requests), {
    ...(context ? { createContext: () => context.asContext() } : {}),
    clock: () => now,
    screenWidth: 480,
  });
  return {
    audio,
    requests,
    context,
    later: (seconds: number) => {
      now += seconds;
      if (context) context.currentTime += seconds;
      audio.update();
    },
  };
}

const step = (audio: GameAudio, r: ReturnType<typeof run>): void => {
  audio.levelStep(r as unknown as LevelRun);
};

describe('GameAudio', () => {
  it('P12-R08: the menu theme plays on the title, ship and level select and settings, without restarting', () => {
    const { audio, requests } = setup();
    audio.menuChanged({ ...MENU, screen: 'loading' });
    expect(audio.state.music).toBeNull();
    audio.menuChanged(MENU);
    const theme = audio.music.track;
    expect(audio.state.music).toBe('menu');
    for (const screen of ['ship-select', 'level-select', 'settings'] as const) {
      audio.menuChanged({ ...MENU, screen });
      expect(audio.music.track).toBe(theme);
    }
    expect(requests.filter((r) => r.kind === 'menu').length).toBeGreaterThan(1);
  });

  it('P12-R08, P12-R07: a level confirmed fades the menu theme out and starts its track; Continue starts it again', () => {
    const { audio } = setup();
    audio.menuChanged(MENU);
    audio.levelStarted('1-2');
    const first = audio.music.track;
    expect(audio.state.music).toBe('level-1-2');
    audio.menuChanged({ ...MENU, screen: 'game', chosenLevelId: '1-2' });
    expect(audio.music.track).toBe(first);
    audio.levelStarted('1-2');
    expect(audio.state.music).toBe('level-1-2');
    expect(audio.music.track).not.toBe(first);
  });

  it('P12-R07: the boss bar brings the boss track; the mini boss destroyed brings the level track back from its start, with the checkpoint jingle', () => {
    const { audio, later } = setup();
    audio.unlock();
    audio.levelStarted('2-3');
    const r = run();
    step(audio, r);
    later(5);
    r.fights.bar = {};
    step(audio, r);
    expect(audio.state.music).toBe('boss-2-3');
    step(audio, r);
    expect(audio.state.music).toBe('boss-2-3');
    r.fights.bar = undefined;
    r.fights.defeated.push({ rank: 'mini' });
    step(audio, r);
    expect(audio.state.music).toBe('level-2-3');
    audio.update();
    later(0.1);
    expect(audio.music.position).toBeCloseTo(0.1);
  });

  it('P12-R07: after the final boss its track goes on until the level ends; then the jingle plays once', () => {
    const { audio, requests } = setup();
    audio.levelStarted('1-1');
    const r = run();
    step(audio, r);
    r.fights.bar = {};
    step(audio, r);
    r.fights.bar = undefined;
    r.fights.finalDefeated = true;
    r.fights.defeated.push({ rank: 'final' });
    step(audio, r);
    expect(audio.state.music).toBe('boss-1-1');
    audio.levelEnded({ levelId: '1-1', destroyed: 1, spawned: 1, outcome: 'complete', score: 0 });
    expect(audio.state.music).toBeNull();
    expect(requests.filter((q) => q.kind === 'jingle')).toEqual([
      { kind: 'jingle', jingle: 'complete' },
    ]);
    step(audio, r);
    audio.menuChanged({
      ...MENU,
      screen: 'game',
      levelResult: { levelId: '1-1', destroyed: 0, spawned: 0, outcome: 'complete', score: 0 },
    });
    expect(audio.state.music).toBeNull();
    audio.levelEnded({ levelId: '1-1', destroyed: 1, spawned: 1, outcome: 'over', score: 0 });
    expect(requests.filter((q) => q.kind === 'jingle').at(-1)).toEqual({
      kind: 'jingle',
      jingle: 'over',
    });
  });

  it('P12-R09: level cues play their sounds, listed by name; the laser hum plays while it fires', () => {
    const { audio, later } = setup();
    audio.unlock();
    audio.levelStarted('1-1');
    const r = run();
    step(audio, r);
    r.shots.projectiles.push({ alive: true, x: 0, weapon: { id: 'gun' } });
    step(audio, r);
    expect(audio.state.sounds).toEqual(['gun-shot']);
    later(0.5);
    r.shots.weapon.id = 'laser';
    r.shots.beam.push({});
    step(audio, r);
    step(audio, r);
    expect(audio.state.sounds.filter((s) => s === 'hum')).toHaveLength(1);
    r.shots.beam.length = 0;
    step(audio, r);
    later(0.1);
    r.shots.beam.push({});
    step(audio, r);
    expect(audio.state.sounds.filter((s) => s === 'hum')).toHaveLength(2);
  });

  it('P12-R11: pausing pauses the music at its position and stops the sounds; menu sounds still play', () => {
    const { audio, later } = setup();
    audio.unlock();
    audio.levelStarted('1-1');
    audio.update();
    later(30);
    const paused = { ...MENU, screen: 'pause' as const, paused: true, chosenLevelId: '1-1' };
    audio.menuChanged(paused);
    later(10);
    expect(audio.music.position).toBeCloseTo(30);
    audio.menuFeedback('down', 'moved', paused.volumes);
    expect(audio.state.sounds.at(-1)).toBe('move');
    audio.menuChanged({ ...paused, screen: 'settings' });
    expect(audio.music.position).toBeCloseTo(30);
    audio.menuChanged({ ...paused, screen: 'game', paused: false });
    later(1);
    expect(audio.music.position).toBeCloseTo(31);
    expect(audio.state.music).toBe('level-1-1');
  });

  it('P12-R11: leaving from the pause menu fades the level music and starts the menu theme', () => {
    const { audio } = setup();
    audio.levelStarted('1-1');
    audio.menuChanged({ ...MENU, screen: 'pause', paused: true });
    audio.menuChanged(MENU);
    expect(audio.state.music).toBe('menu');
  });

  it('P12-R09: menu commands play their sounds', () => {
    const { audio, later } = setup();
    const v = MENU.volumes;
    const feedback: [
      Parameters<GameAudio['menuFeedback']>[0],
      Parameters<GameAudio['menuFeedback']>[1],
    ][] = [
      ['confirm', 'screen'],
      ['cancel', 'screen'],
      ['back', 'locked'],
      ['pause', 'paused'],
      ['confirm', 'resumed'],
      ['right', 'adjusted'],
      ['right', 'none'],
    ];
    for (const [command, result] of feedback) {
      audio.menuFeedback(command, result, v);
      later(0.1);
    }
    expect(audio.state.sounds).toEqual(['confirm', 'back', 'back', 'pause', 'resume', 'slider']);
  });

  it('P12-R05: before the first gesture there is no context; a gesture that may not start audio creates none', () => {
    const context = new FakeAudioContext();
    let allowed = false;
    const audio = new GameAudio(bindings(), {
      createContext: () => context.asContext(),
      canStart: () => allowed,
      clock: () => 0,
      screenWidth: 480,
    });
    expect(audio.state.context).toBe('none');
    audio.unlock();
    expect(audio.state.context).toBe('none');
    allowed = true;
    audio.unlock();
    expect(audio.state.context).toBe('running');
    audio.setHidden(true);
    expect(audio.state.context).toBe('suspended');
  });

  it("P12-R05: without Web Audio, or without the game's audio, everything works silently", () => {
    const { audio } = setup({ webAudio: false });
    audio.unlock();
    audio.menuChanged(MENU);
    audio.levelStarted('1-1');
    step(audio, run());
    audio.setVolumes({ music: 0, sfx: 0 });
    expect(audio.state).toMatchObject({ music: 'level-1-1', context: 'none' });
    const silent = new GameAudio(undefined, { clock: () => 0, screenWidth: 480 });
    silent.menuChanged(MENU);
    silent.levelStarted('1-1');
    silent.levelStep(run() as unknown as LevelRun);
    silent.levelEnded({ levelId: '1-1', destroyed: 0, spawned: 0, outcome: 'over', score: 0 });
    silent.menuFeedback('down', 'moved', MENU.volumes);
    expect(silent.state).toEqual({ music: null, sounds: [], context: 'none' });
  });
});
