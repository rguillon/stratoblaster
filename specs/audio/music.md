# Music

> **Area:** Audio · **Prefix:** `AUD-MUSIC` · **Related:** [engine.md](engine.md), [sfx.md](sfx.md), [../gameplay/level-flow.md](../gameplay/level-flow.md), [../ui/screen-flow.md](../ui/screen-flow.md), [../ui/settings.md](../ui/settings.md), [../graphics/art-direction.md](../graphics/art-direction.md)

All the music is composed by code: one track per level, from its id, in its world's style; a more
stressful boss track per world; a menu theme; and three short jingles. Every track is energetic
darksynth, the music of the game's darksynth look ([graphics/art-direction.md](../graphics/art-direction.md)).
This file gives what the tracks are, how they sound, and when each one plays. The engine that
plays them is in [engine.md](engine.md).

## Requirements

### AUD-MUSIC-01 — Composed by code, the same every time · MUST

Every track is composed by code from data: a world style, and a seed taken from the track's id
(an FNV-1a hash of `level-2-3`, `boss-2`, `menu`). The composer is pure: the same id always gives
the same notes, never from `Math.random`. A track is composed once, the first time it is asked
for, and kept.

**Acceptance criteria**
- Given level `2-3`'s track composed twice, then both note sequences are identical (unit test).

*Sources: GD-70, P12-R06, D-098.*

### AUD-MUSIC-02 — One track per level · MUST

Every level (`1-1` to `4-5`) has its own track, composed from its id in its world's style. The five
levels of a world share the world's style (instruments, drum and bass feel, tempo range) but differ
in key, tempo, scale, chords, melody and rhythm, so no two levels sound the same.

**Acceptance criteria**
- Given the 20 levels, then their note sequences are pairwise different (unit test).

*Sources: GD-70, P12-R06, D-095, D-098.*

### AUD-MUSIC-03 — Darksynth · MUST

Every track (levels, bosses, menu, jingles) is synthwave leaning darksynth: 80s analog-style synths
(detuned saw pads and leads, plucked arpeggios with tempo-synced echoes, pumping or rolling saw
basses, a growling heavy bass in Worlds 1 and 4 and the menu), drum-machine drums with heavy kicks,
big gated snares and synth toms, and reverb; minor, harmonic minor or phrygian keys only.

**Acceptance criteria**
- Given every style, then its scales are minor, harmonic minor or phrygian (unit test on the data).
- Given every level track, then it has gated snares and sends to the echo and the reverb (unit test).
- Given the tracks, then the reviewer hears synthwave leaning darksynth (manual check).

*Sources: P12-R06, D-099, D-101.*

### AUD-MUSIC-04 — Energetic · MUST

Every track drives from its first bar: drums from the start, sixteenth-note arpeggios, no bare
breakdown (every 8-bar section has some energy), and a rising noise sweep into each section.

**Acceptance criteria**
- Given every level track, then every bar has a snare, and each section ends with a riser (unit
  test).

*Sources: P12-R06, D-100.*

### AUD-MUSIC-05 — The world styles · MUST

Each world's style matches the look of its world, and the four worlds stay apart by their drum
feel, bass, lead, arpeggio and tempo:

| World | Flavour | Tempo | Drums | Bass | Lead |
|-------|---------|-------|-------|------|------|
| 1 | outrun drive | 128–140 BPM | four on the floor | heavy, in eighths | supersaw |
| 2 | dreamwave, cold and glassy | 112–124 BPM | driving backbeat | dreamwave bass, in eighths | glassy bells, glass arpeggio |
| 3 | tom-heavy synthwave | 120–132 BPM | tribal: toms and shakers | plucked, syncopated | square |
| 4 | the heaviest darksynth | 104–116 BPM | slow heavy kicks, backbeat on 2 and 4 | heavy, rolling sixteenths | brass |

**Acceptance criteria**
- Given each world's level tracks, then their tempos are within its range (unit test).
- Given one level of each world, then the reviewer can tell the four styles apart by ear (manual
  check).

**Discrepancy:** the styles were matched to the old world themes (World 1 sea and desert, World 2
the Frozen North, "cold and airy"; World 3 the Jungle, "percussive"; World 4 the Volcanic Lands,
"dark and heavy"). The worlds were reworked since (D-110 to D-112: an industrial desert, industrial
towns, a metropolis) and the styles were not matched to their new looks.

*Sources: P12-R06, D-098, D-099, D-100, D-101.*

### AUD-MUSIC-06 — Loops of at least a minute · MUST

A track is made of whole 8-bar sections, enough for it to last at least `music_loop_min` (60 s)
before it repeats, and it loops without a gap or a click.

**Acceptance criteria**
- Given any level track, then its loop is at least 60 s long (unit test).
- Given a track looping, then its first note after the loop comes on time (unit test on the
  sequencer).

*Sources: P12-R06, D-098.*

### AUD-MUSIC-07 — Boss tracks · MUST

Each world has one boss track (`boss-1` to `boss-4`), faster and more stressful than its level
tracks: 20 to 30 BPM above the world's fastest level tempo, in a darker scale (harmonic minor in
Worlds 1 and 2, phrygian in Worlds 3 and 4), full energy with one short breath, with its own parts:
four-on-the-floor kicks pushed by off-beat sixteenths, sixteenth-note hats, snare rolls growing
louder, a bass rolling between the root and its octave, supersaw chord stabs on a 3-3-2 rhythm,
tense progressions around the root, and a riser into each section. It keeps its world's
instruments, so a boss still sounds like its world.

**Acceptance criteria**
- Given the 4 worlds, then there are 4 boss tracks, each faster than every level track of its world
  (unit test).
- Given a boss track, then it is denser than its world's level tracks, with stabs, risers and snare
  rolls (unit test).

*Sources: GD-70, P12-R07, D-095, D-098, D-100.*

### AUD-MUSIC-08 — The level's music · MUST

When a level starts, its track starts from the beginning, cross-fading in from the music before
over `music_crossfade` (1 s). When the level ends (complete or over) or is left, the music fades
out over `music_fade` (1 s). A Continue starts the level track again from its beginning.

**Acceptance criteria**
- Given a level confirmed on the level select, then the menu theme fades out and the level's track
  starts (unit test on the music state).
- Given a Continue, then the level track plays from its start (unit test).

*Sources: P12-R06, P12-R07, D-097.*

### AUD-MUSIC-09 — Boss music in the fights · MUST

When a boss fight starts (its health bar shows), the music cross-fades in 1 s to its world's boss
track. When the mini boss is destroyed, it cross-fades back to the level track, from its start.
After the final boss, the boss track plays on until the level ends.

**Acceptance criteria**
- Given a level reaching its mini boss, then the boss track plays within 1 s and the level track
  has stopped (unit test).
- Given the mini boss destroyed, then the level track plays again from its start (unit test).
- Given level 2-3 during its mini boss fight, then the track playing is `boss-2` (e2e).

*Sources: GD-70, P12-R07, D-097.*

### AUD-MUSIC-10 — Jingles · MUST

Three short jingles, composed like the music, each played once: **level complete** (a rising
fanfare, with the "Level complete" panel), **game over** (a slow falling line, with the "Game over"
panel) and **checkpoint reached** (a short bell chime when the mini boss is destroyed, over the
music).

**Acceptance criteria**
- Given a level completed, and a game over, then the matching jingle plays once (unit test).
- Given the mini boss destroyed, then the checkpoint jingle plays over the music (unit test).

*Sources: P12-R07, D-095, D-098.*

### AUD-MUSIC-11 — Menu theme · MUST

The menus (title, ship select, level select, the settings opened from the title, and the loading
of a level) play one menu theme, looping: a full, energetic darksynth track (drums, a pumping octave bass, dark pads, a
plucked arpeggio, a supersaw lead) at 100 BPM in a minor key on the i–VI–III–VII chords, slower
than every level, every section full, about as loud as the level tracks. It keeps playing, without
restarting, when moving between those screens, and fades into the level's track when a level
starts. Leaving a level brings it back on the title.

**Acceptance criteria**
- Given the title, when the player goes to ship select and level select, then the menu theme keeps
  playing without restarting (unit test).
- Given the title and ship select, then the track playing is `menu` (e2e).
- Given a level left from the pause menu, then the menu theme plays on the title (unit test).

*Sources: P12-R08, P12-R11, D-095, D-099, D-100.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| world styles | tempo, scales, roots, progressions, instruments, drums, bass | `src/game/view/audio/music_styles.py` `WORLD_STYLES` |
| level tempo ranges | World 1 128–140, World 2 112–124, World 3 120–132, World 4 104–116 BPM | `WORLD_STYLES[n].tempo` (raised by 8–14 BPM in D-100) |
| boss boost | +20 to +30 BPM over the world's top tempo | `MusicStyle.boss_boost` |
| menu theme | 100 BPM, minor, i–VI–III–VII | `MENU_STYLE` |
| music_loop_min | 60 s | `MUSIC_LOOP_MIN_SECONDS` |
| section | 8 bars of 4 beats | `SECTION_BARS`, `BEATS_PER_BAR` |
| boss progressions | `BOSS_PROGRESSIONS` | `src/game/view/audio/compose_boss.py` |
| jingles | complete 132 BPM, 8 beats; over 84 BPM, 8 beats; checkpoint 120 BPM, 3 beats | `src/game/view/audio/jingles.py` |
| music_fade / music_crossfade | 1 s / 1 s | `src/config/audio.py` `AUDIO_CONFIG.fade_seconds`, `.crossfade_seconds` |

## Notes

- The performance work of phase 13 kept the music as it was, and the world reworks (D-110 to
  D-112) did not touch it (see the discrepancy under AUD-MUSIC-05).
- Measured offline at the default volume (D-099, D-100): menu about −18 dB RMS, level tracks −16.5
  to −17.2 dB, boss tracks −13.7 to −15 dB. The by-ear checks are the reviewer's.
