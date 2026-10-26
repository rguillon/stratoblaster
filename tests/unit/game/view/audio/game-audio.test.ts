import { describe, expect, it } from 'vitest';
import {
  trackSeconds,
  type SoundDesign,
  type ToneLayer,
  type Track,
} from '../../../../../src/audio/audio-types';
import { composeTrack, seedOf } from '../../../../../src/game/view/audio/compose-track';
import { GAME_AUDIO, gameMusic, worldOf } from '../../../../../src/game/view/audio/game-audio';
import { INSTRUMENTS } from '../../../../../src/game/view/audio/instruments';
import { JINGLES } from '../../../../../src/game/view/audio/jingles';
import {
  MENU_STYLE,
  WORLD_STYLES,
  type MusicStyle,
} from '../../../../../src/game/view/audio/music-styles';
import { SOUND_DESIGNS } from '../../../../../src/game/view/audio/sound-designs';
import { GAME } from '../../../../../src/game/index';

const LEVEL_IDS = GAME.levels.levels.map((l) => l.id);

function level(id: string) {
  const track = gameMusic({ kind: 'level', levelId: id });
  if (!track) throw new Error(`no track for ${id}`);
  return track;
}

function bossTrack(levelId: string) {
  const track = gameMusic({ kind: 'boss', levelId });
  if (!track) throw new Error(`no boss track for ${levelId}`);
  return track;
}

/** The loudest a sound can get: its gain times its layers' gains, all at their peak. */
const peak = (sound: SoundDesign): number =>
  sound.gain * sound.layers.reduce((sum: number, l: ToneLayer) => sum + l.gain, 0);

describe('game music', () => {
  it('P12-R06: the 20 levels 1-1 … 4-5 each have a track, and their note sequences differ pairwise', () => {
    expect(LEVEL_IDS).toHaveLength(20);
    const sequences = LEVEL_IDS.map((id) => JSON.stringify(level(id).notes));
    expect(new Set(sequences).size).toBe(20);
    expect(level('2-3').id).toBe('level-2-3');
  });

  it('P12-R06: the same level always plays the same music (level 2-3 composed twice)', () => {
    const style = WORLD_STYLES[2];
    if (!style) throw new Error('no style');
    const request = { id: 'level-2-3', style, seed: seedOf('level-2-3') };
    expect(composeTrack(request)).toEqual(composeTrack(request));
    expect(seedOf('level-2-3')).toBe(seedOf('level-2-3'));
    expect(seedOf('level-2-3')).not.toBe(seedOf('level-2-4'));
  });

  it('P12-R06: every level track loops after at least music_loop_min (60 s), on whole bars', () => {
    for (const id of LEVEL_IDS) {
      const track = level(id);
      expect(track.loop).toBe(true);
      expect(trackSeconds(track), id).toBeGreaterThanOrEqual(60);
      expect(track.beats % 4).toBe(0);
      expect(track.notes.every((n) => n.beat >= 0 && n.beat < track.beats)).toBe(true);
    }
  });

  it('P12-R06: each world plays in its tempo range and its own instruments', () => {
    const ranges: Record<number, [number, number]> = {
      1: [120, 132],
      2: [100, 112],
      3: [112, 124],
      4: [90, 104],
    };
    for (const id of LEVEL_IDS) {
      const [min, max] = ranges[worldOf(id)] ?? [0, 0];
      expect(level(id).bpm, id).toBeGreaterThanOrEqual(min);
      expect(level(id).bpm, id).toBeLessThanOrEqual(max);
    }
    const leads = [1, 2, 3, 4].map((w) => WORLD_STYLES[w]?.instruments.lead);
    expect(new Set(leads).size).toBe(4);
  });

  it('P12-R07: 4 boss tracks, each 20–30 BPM faster than every level track of its world', () => {
    for (const world of [1, 2, 3, 4]) {
      const boss = bossTrack(`${String(world)}-2`);
      expect(boss.id).toBe(`boss-${String(world)}`);
      expect(bossTrack(`${String(world)}-5`)).toBe(boss);
      const levels = LEVEL_IDS.filter((id) => worldOf(id) === world).map((id) => level(id).bpm);
      expect(boss.bpm).toBeGreaterThan(Math.max(...levels));
      const top = WORLD_STYLES[world]?.tempo[1] ?? Infinity;
      expect(boss.bpm - top).toBeGreaterThanOrEqual(20);
      expect(boss.bpm - top).toBeLessThanOrEqual(30);
      expect(trackSeconds(boss)).toBeGreaterThanOrEqual(60);
    }
    expect(gameMusic({ kind: 'boss', levelId: '9-1' })).toBeUndefined();
    expect(gameMusic({ kind: 'level', levelId: '9-1' })).toBeUndefined();
  });

  it('P12-R08: a calm menu theme, looping, slower than every level', () => {
    const menu = gameMusic({ kind: 'menu' });
    expect(menu).toMatchObject({ id: 'menu', loop: true });
    expect(menu?.bpm ?? 999).toBeLessThan(90);
    expect(trackSeconds(menu ?? level('1-1'))).toBeGreaterThanOrEqual(60);
  });

  it('P12-R07: three short jingles that play once', () => {
    for (const jingle of ['complete', 'over', 'checkpoint'] as const) {
      const track = gameMusic({ kind: 'jingle', jingle });
      expect(track).toBe(JINGLES[jingle]);
      expect(track?.loop).toBe(false);
      expect(trackSeconds(track ?? level('1-1'))).toBeLessThan(6);
    }
  });

  it('P12-R06: every note names an instrument of the game, in a sensible range', () => {
    const tracks = [
      ...LEVEL_IDS.map(level),
      ...[1, 2, 3, 4].map((w) => gameMusic({ kind: 'boss', levelId: `${String(w)}-1` })),
      gameMusic({ kind: 'menu' }),
      ...Object.values(JINGLES),
    ].filter((t): t is Track => t !== undefined);
    expect(tracks).toHaveLength(28);
    const notes = tracks.flatMap((t) => t.notes);
    const unknown = notes.filter((n) => !(n.instrument in INSTRUMENTS)).map((n) => n.instrument);
    expect(unknown).toEqual([]);
    const low = notes.reduce((min, n) => Math.min(min, n.pitch), Infinity);
    const high = notes.reduce((max, n) => Math.max(max, n.pitch), -Infinity);
    expect(low).toBeGreaterThanOrEqual(24);
    expect(high).toBeLessThanOrEqual(108);
    expect(notes.every((n) => n.velocity > 0 && n.velocity <= 1)).toBe(true);
  });
});

describe('synthwave (reviewer, 2026-10-26)', () => {
  const styles = [...[1, 2, 3, 4].map((w) => WORLD_STYLES[w]), MENU_STYLE].filter(
    (s): s is MusicStyle => s !== undefined,
  );
  const send = (name: string, kind: 'echo' | 'reverb'): number => INSTRUMENTS[name]?.[kind] ?? 0;

  it('P12-R06: every style plays a drum machine with big gated snares, and synth parts sent to the echo and reverb', () => {
    expect(styles).toHaveLength(5);
    for (const { instruments } of styles) {
      expect(instruments.snare).toBe('snare-gated');
      expect(send(instruments.arp, 'echo')).toBeGreaterThan(0);
      expect(send(instruments.lead, 'echo')).toBeGreaterThan(0);
      expect(send(instruments.pad, 'reverb')).toBeGreaterThan(0);
    }
    expect(GAME_AUDIO.effects).toMatchObject({ echoBeats: 0.75 });
  });

  it('P12-R06: section ends roll down the synth toms', () => {
    const toms = level('1-1').notes.filter((n) => n.instrument === 'tom');
    expect(new Set(toms.map((n) => n.pitch)).size).toBeGreaterThan(2);
  });

  it('P12-R08: the menu theme is a full track: drums, bass, pad, arpeggio and lead in every section', () => {
    const menu = gameMusic({ kind: 'menu' });
    const { instruments } = MENU_STYLE;
    const bars = (menu?.beats ?? 0) / 4;
    for (const part of [instruments.snare, instruments.bass, instruments.pad, instruments.arp]) {
      const used = new Set(
        menu?.notes.filter((n) => n.instrument === part).map((n) => Math.floor(n.beat / 4)),
      );
      expect(used.size, part).toBe(bars);
    }
    expect(menu?.notes.some((n) => n.instrument === instruments.lead)).toBe(true);
  });
});

describe('game sounds', () => {
  const TABLE = {
    'Player weapons': [
      'fire:bullet',
      'beam-start:laser',
      'beam:laser',
      'fire:missile',
      'weapon-switch',
      'weapon-up',
    ],
    'Enemy weapons': ['enemy-bullet', 'enemy-missile', 'laser-warning', 'laser-fire'],
    Hits: ['hit', 'hit-blocked', 'player-hit'],
    Destruction: ['blast-small', 'blast-large', 'part-destroyed', 'boss-destroyed'],
    Player: ['life-lost', 'extra-life', 'bomb', 'bonus:bomb', 'bonus:weapon', 'bonus:life'],
    Menus: ['menu-move', 'menu-confirm', 'menu-back', 'pause', 'resume', 'slider'],
  };

  for (const [group, cues] of Object.entries(TABLE)) {
    it(`P12-R09: every event of the "${group}" group has its own sound`, () => {
      for (const cue of cues) expect(SOUND_DESIGNS[cue], cue).toBeDefined();
    });
  }

  it('P12-R09: every sound is told apart by its name; the weapons map to the player weapons', () => {
    const names = Object.values(SOUND_DESIGNS).map((s) => s.name);
    expect(new Set(names).size).toBe(names.length);
    expect(SOUND_DESIGNS['fire:bullet']?.name).toBe('gun-shot');
    const weapons = GAME.playerWeapons.map((w) => w.id);
    expect(weapons).toEqual(['bullet', 'laser', 'missile']);
  });

  it('P12-R09: shots, hits and explosions follow their position; menu sounds do not', () => {
    for (const cue of ['fire:bullet', 'enemy-bullet', 'hit', 'blast-small', 'blast-large']) {
      expect(SOUND_DESIGNS[cue]?.positional, cue).toBe(true);
    }
    expect(SOUND_DESIGNS['menu-move']?.positional).toBeUndefined();
  });

  it('P12-R10: player and bomb sounds have the highest priority, enemy shots the lowest', () => {
    const priority = (cue: string) => SOUND_DESIGNS[cue]?.priority ?? -1;
    const enemy = Math.max(priority('enemy-bullet'), priority('enemy-missile'));
    const lowest = Math.min(...Object.values(SOUND_DESIGNS).map((s) => s.priority));
    expect(enemy).toBe(lowest);
    for (const cue of ['bomb', 'life-lost', 'extra-life', 'player-hit', 'bonus:life']) {
      expect(priority(cue)).toBeGreaterThan(priority('blast-large'));
    }
  });

  it('P12-R10: the gun shots and the laser hum are quieter than hits and explosions', () => {
    const quiet = ['fire:bullet', 'beam:laser'].map((c) => SOUND_DESIGNS[c]);
    const loud = ['hit', 'blast-small', 'blast-large'].map((c) => SOUND_DESIGNS[c]);
    for (const q of quiet) {
      for (const l of loud) {
        if (!q || !l) throw new Error('missing sound');
        expect(peak(q), `${q.name} vs ${l.name}`).toBeLessThan(peak(l));
      }
    }
  });

  it('P12-R10: the loudest sound is at most +6 dB over the music at equal volume settings', () => {
    const music = Math.max(
      ...Object.values(INSTRUMENTS).map((i) => i.gain * Math.max(...i.layers.map((l) => l.gain))),
    );
    const loudest = Math.max(...Object.values(SOUND_DESIGNS).map(peak));
    const ratio = (loudest * GAME_AUDIO.mix.sfx) / (music * GAME_AUDIO.mix.music);
    expect(20 * Math.log10(ratio)).toBeLessThanOrEqual(6);
  });

  it('P12-R05: the game registers its audio, all generated (no file)', () => {
    expect(GAME.view.audio).toBe(GAME_AUDIO);
    expect(GAME_AUDIO.largeBlastRadius).toBeGreaterThan(0);
    expect(JSON.stringify(GAME_AUDIO.sounds)).not.toMatch(/\.(ogg|mp3|wav)/);
  });
});
