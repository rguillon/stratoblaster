import { describe, expect, it } from 'vitest';
import { LevelCues } from '../../../src/audio/level-cues';
import type { LevelRun } from '../../../src/core/systems/level-run';

/** The parts of a level run the cues read, as plain data a test changes between steps. */
function fakeRun() {
  return {
    ship: { x: 240 },
    shots: {
      projectiles: [] as { alive: boolean; x: number; weapon: { id: string } }[],
      beam: [] as unknown[],
      weapon: { id: 'bullet' },
      level: 1,
    },
    enemies: {
      shots: {
        bullets: [] as { alive: boolean; x: number }[],
        missiles: [] as { alive: boolean; id: number; x: number }[],
        lasers: [] as { phase: 'warning' | 'firing'; x: number }[],
      },
      brokenParts: [] as { x: number }[],
    },
    impacts: [] as { x: number; blocked?: boolean }[],
    blasts: [] as { kind: 'enemy' | 'missile'; x: number; radius: number }[],
    hits: [] as { x: number; event: string }[],
    bonuses: { picked: [] as { kind: string; x: number }[] },
    hull: { lives: 3 },
    bombs: { fired: 0 },
    fights: { defeated: [] as { rank: string }[] },
  };
}

type FakeRun = ReturnType<typeof fakeRun>;

/** Cues of a step after `change`, the first step having taken the starting state. */
function cuesAfter(change: (run: FakeRun) => void, run = fakeRun(), cues = new LevelCues(18)) {
  cues.observe(run as unknown as LevelRun);
  change(run);
  return cues.observe(run as unknown as LevelRun).map((c) => c.cue);
}

describe('LevelCues', () => {
  const cases: [string, (run: FakeRun) => void][] = [
    [
      'fire:bullet',
      (r) => r.shots.projectiles.push({ alive: true, x: 1, weapon: { id: 'bullet' } }),
    ],
    [
      'fire:missile',
      (r) => r.shots.projectiles.push({ alive: true, x: 1, weapon: { id: 'missile' } }),
    ],
    [
      'beam-start:laser',
      (r) => {
        r.shots.weapon.id = 'laser';
        r.shots.beam.push({});
      },
    ],
    ['weapon-switch', (r) => (r.shots.weapon.id = 'missile')],
    ['weapon-up', (r) => (r.shots.level = 2)],
    ['enemy-bullet', (r) => r.enemies.shots.bullets.push({ alive: true, x: 1 })],
    ['enemy-missile', (r) => r.enemies.shots.missiles.push({ alive: true, id: 1, x: 1 })],
    ['laser-warning', (r) => r.enemies.shots.lasers.push({ phase: 'warning', x: 1 })],
    ['hit', (r) => r.impacts.push({ x: 1 })],
    ['hit-blocked', (r) => r.impacts.push({ x: 1, blocked: true })],
    ['player-hit', (r) => r.hits.push({ x: 1, event: 'hit' })],
    ['life-lost', (r) => r.hits.push({ x: 1, event: 'lifeLost' })],
    ['blast-small', (r) => r.blasts.push({ kind: 'enemy', x: 1, radius: 10 })],
    ['blast-large', (r) => r.blasts.push({ kind: 'enemy', x: 1, radius: 20 })],
    ['part-destroyed', (r) => r.enemies.brokenParts.push({ x: 1 })],
    ['boss-destroyed', (r) => r.fights.defeated.push({ rank: 'final' })],
    ['extra-life', (r) => (r.hull.lives = 4)],
    ['bomb', (r) => (r.bombs.fired = 1)],
    ['bonus:weapon', (r) => r.bonuses.picked.push({ kind: 'weapon', x: 1 })],
    ['bonus:life', (r) => r.bonuses.picked.push({ kind: 'life', x: 1 })],
    ['bonus:bomb', (r) => r.bonuses.picked.push({ kind: 'bomb', x: 1 })],
  ];
  for (const [cue, change] of cases) {
    it(`P12-R09: ${cue} is heard when it happens`, () => {
      expect(cuesAfter(change)).toContain(cue);
    });
  }

  it('P12-R09: a laser firing after its warning line is heard once', () => {
    const run = fakeRun();
    const cues = new LevelCues(18);
    const laser = { phase: 'warning' as 'warning' | 'firing', x: 1 };
    expect(cuesAfter((r) => r.enemies.shots.lasers.push(laser), run, cues)).toEqual([
      'laser-warning',
    ]);
    laser.phase = 'firing';
    expect(cues.observe(run as unknown as LevelRun).map((c) => c.cue)).toEqual(['laser-fire']);
    expect(cues.observe(run as unknown as LevelRun)).toEqual([]);
  });

  it('P12-R09: the first step only takes the starting state; a volley is one cue, with its x', () => {
    const run = fakeRun();
    run.shots.projectiles.push({ alive: true, x: 5, weapon: { id: 'bullet' } });
    const cues = new LevelCues(18);
    expect(cues.observe(run as unknown as LevelRun)).toEqual([]);
    run.shots.projectiles.push(
      { alive: true, x: 100, weapon: { id: 'bullet' } },
      { alive: true, x: 120, weapon: { id: 'bullet' } },
    );
    expect(cues.observe(run as unknown as LevelRun)).toEqual([{ cue: 'fire:bullet', x: 100 }]);
    // Shots seen before make no new sound; a missile shot down is a small blast.
    run.blasts.push({ kind: 'missile', x: 7, radius: 30 });
    expect(cues.observe(run as unknown as LevelRun)).toEqual([{ cue: 'blast-small', x: 7 }]);
  });

  it('P12-R09: the beam weapon firing is reported while it fires, for its hum', () => {
    const run = fakeRun();
    const cues = new LevelCues(18);
    cues.observe(run as unknown as LevelRun);
    run.shots.weapon.id = 'laser';
    run.shots.beam.push({});
    cues.observe(run as unknown as LevelRun);
    expect(cues.beam).toBe('laser');
    expect(cues.observe(run as unknown as LevelRun).map((c) => c.cue)).not.toContain(
      'beam-start:laser',
    );
    run.shots.beam.length = 0;
    cues.observe(run as unknown as LevelRun);
    expect(cues.beam).toBeUndefined();
  });
});
