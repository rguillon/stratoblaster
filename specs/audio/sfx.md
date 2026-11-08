# Sound effects

> **Area:** Audio · **Prefix:** `AUD-SFX` · **Related:** [engine.md](engine.md), [music.md](music.md), [../gameplay/weapons.md](../gameplay/weapons.md), [../gameplay/bombs.md](../gameplay/bombs.md), [../gameplay/bonuses.md](../gameplay/bonuses.md), [../ui/menu-input.md](../ui/menu-input.md)

Every gameplay and menu event has its own sound effect, a recorded CC0 sample (D-261), chosen so the
player can tell them apart and so a busy screen stays pleasant: the guns are short and quiet,
explosions are big and low, and the player's own guns are mixed under the hits and explosions. This
file lists the sounds, their samples, their priorities and their mix. How they are loaded and
played (voices, limits, panning) is in [engine.md](engine.md).

## Requirements

### AUD-SFX-01 — A sound for every event · MUST

Every event below plays its own sound, a sample distinct from the others (the sound's name is the
sample's file name, `public/sfx/<name>.ogg`, [engine.md](engine.md) AUD-ENGINE-01):

| Group | Event (cue) | Sound |
|-------|-------------|-------|
| Player weapons | a volley of the guns (`fire:bullet`) | `gun-shot`, a minigun burst ("BRRRT") |
| | the laser starts (`beam-start:laser`) | `laser-start`, a large laser charging |
| | the laser fires (`beam:laser`) | `laser-hum`, a looping engine hum (its tail cross-faded into its head, so the loop has no seam) |
| | a volley of missiles (`fire:missile`) | `missile-launch`, a thruster firing |
| | weapon switched (`weapon-switch`) | `weapon-switch`, a heavy latch closing |
| | weapon level up (`weapon-up`) | `weapon-level-up`, a rising interface chirp |
| Enemy weapons | enemy bullet fired (`enemy-bullet`) | `enemy-shot`, a small laser shot, different from the player's |
| | enemy missile launched (`enemy-missile`) | `enemy-missile`, a thruster firing, shorter |
| | laser warning line (`laser-warning`) | `laser-warning`, a force field powering up |
| | enemy laser fires (`laser-fire`) | `enemy-laser`, a large laser blast |
| Hits | player shot hits (`hit`) | `hit`, a short metal impact |
| | player shot hits a shielded part (`hit-blocked`) | `hit-shield`, a metal impact, ringing |
| | the player ship is hit (`player-hit`) | `player-hit`, a heavy metal impact |
| Destruction | small enemy blows up (`blast-small`) | `explosion-small`, a short crunching blast, one of 3 recordings (AUD-SFX-09) |
| | large enemy blows up (`blast-large`) | `explosion-large`, a longer crunching blast, one of 3 recordings (AUD-SFX-09) |
| | boss part destroyed (`part-destroyed`) | `boss-part-destroyed`, a long crunching blast |
| | boss destroyed (`boss-destroyed`) | `boss-destroyed`, a deep, low-frequency explosion |
| Player | life lost (`life-lost`) | `life-lost`, a short low-frequency explosion |
| | extra life (`extra-life`) | `extra-life`, a rising confirmation chime |
| | bomb (`bomb`) | `bomb`, the longest crunching blast |
| | bonuses picked up (`bonus:weapon`, `bonus:life`, `bonus:bomb`, `bonus:heal`) | `weapon-bonus` (a select blip), `life-bonus` (a confirmation chime), `bomb-bonus` (a glass ring), `heal-bonus` (the confirmation chime pitched up) |
| Menus | move, confirm, back, pause, resume, slider step | `menu-move` (a tick), `menu-confirm` (a select click), `menu-back` (a back click), `pause` and `resume` (a switch thrown, two different ones), `slider-step` (a tick) |

A blast is large when the enemy's hit radius is at least `large_blast_radius` (18 px); an enemy
missile shot down blows up small. A slider step plays at the new sound volume.

**Acceptance criteria**
- Given each event of the table, then its sound plays when the event happens (unit test with a
  fake audio context, one case per event).
- Given the sound designs, then every event of the table has its own sound and its own sample name
  (unit test on the data), and each sample exists as `.ogg` and `.mp3` (`make build`).

*Sources: GD-71, P12-R09, D-095, D-097, D-261.*

### AUD-SFX-02 — The minigun · MUST

The guns sound like a minigun ("BRRRT"): each volley plays one burst sample (`gun-shot`) of
`minigun_rounds` (6) short AK-47 shots `minigun_gap` (21 ms) apart, each cut from a different real
recording (five in turn), every other round quieter. The burst is 0.165 s long (at most 0.25 s), as
long as the volley is short: the guns fire 8 volleys a second, so holding fire rattles on without a
gap, and it stops within one volley of letting go. If the guns' rate changes, the sound follows it,
as it plays once per volley.

**Acceptance criteria**
- Given the gun sound, then it is at most 0.25 s long (unit test on the data).
- Given the guns held, then the reviewer hears a continuous minigun "BRRRT" (manual check).

*Sources: P12-R09, D-101, D-261.*

### AUD-SFX-03 — One fire sound per volley · MUST

The guns and the missiles sound once per volley (when the first stream of a volley fires, their
streams firing in turn), at the ship's x; not once per shot, so a 5-stream level does not take 5
voices. The laser sounds its start once, then its hum loops while it fires and stops when it stops.

**Acceptance criteria**
- Given the guns at level 5 held for 1 s, then 8 gun sounds are asked for (unit test).
- Given the laser released, then its hum stops (unit test).

*Sources: P03-R11, D-102, D-097.*

### AUD-SFX-04 — Explosions in sizes · MUST

Explosions come in sizes, each its own sample, longer and lower as it grows: `explosion-small` for
small enemies, `explosion-large` for large enemies, `boss-part-destroyed` for boss parts,
`boss-destroyed` for bosses, and `bomb` for bombs. Most of the energy of each is low, so a busy wave
does not turn into a hiss. Small enemies blow up small, large enemies large, boss parts as parts,
bosses and bombs with their own, longer sounds.

**Acceptance criteria**
- Given the explosion sounds, then they grow in length from small to large to the boss's (unit test
  on the data).
- Given a busy wave, then the reviewer finds the explosions realistic and not tiring (manual
  check).

*Sources: P12-R09, D-108, D-261.*

### AUD-SFX-05 — Priorities · MUST

Each sound has a priority, used when the voices are full ([engine.md](engine.md) AUD-ENGINE-07):
the player's sounds and the bombs highest, the enemy shots lowest.

| Priority | Sounds |
|----------|--------|
| 7 (top) | `boss-destroyed`, `life-lost`, `extra-life`, `bomb`, the menu sounds |
| 6 | `player-hit`, `weapon-switch`, `weapon-level-up`, the bonus sounds |
| 5 | `boss-part-destroyed` |
| 4 | `explosion-small`, `explosion-large` |
| 3 | `gun-shot`, `missile-launch`, `laser-start`, `laser-hum` |
| 2 | `hit`, `hit-shield` |
| 1 | `laser-warning`, `enemy-laser` |
| 0 | `enemy-shot`, `enemy-missile` |

**Acceptance criteria**
- Given the sound designs, then the player's and the bomb sounds have a higher priority than every
  enemy shot sound (unit test on the data).

*Sources: P12-R10, D-097.*

### AUD-SFX-06 — The mix · MUST

The player's gun shots and the laser hum are mixed quieter than the hits and the explosions, so
holding fire is not tiring. The loudest sound effect's peak (its gain × the sum of the gains of the
layers that start together, × the sound effect mix) is at most `loudest_sfx` (+6 dB, twice) the
loudest instrument's peak (× the music mix) at equal volume settings.

**Acceptance criteria**
- Given the sound designs, then `gun-shot` and `laser-hum` are quieter than `hit` and every
  explosion (unit test on the data).
- Given the sound designs and the instruments, then the loudest sound is within +6 dB of the music
  (unit test on the data).

*Sources: P12-R10, D-098, D-099, D-108.*

### AUD-SFX-07 — Fit for the game · MUST

Each sound fits the darksynth look, and none is unpleasant for a child: no alarm-like siren, no long
bright hiss.

**Acceptance criteria**
- Given each sound, then the reviewer finds it fits and is not unpleasant for a child (manual
  check).

*Sources: P12-R09, D-100, D-107.*

### AUD-SFX-08 — Real recordings, free to use · MUST

The sounds are real sample recordings, not chip sounds, from packs whose license is **CC0**
(public domain), which is compatible with the project's MIT license (ENG-121). Today they come
from two packs by Kenney (Sci-Fi Sounds, Interface Sounds), the Free Firearm Sound Library (the
player gun) and the CC0 Explosions by compufox (`explosion-small-2` and `-3`, `explosion-large-2`). Each sample is made from one file
of a pack (`gun-shot` from several shots of one recording, AUD-SFX-02): mono, 44.1 kHz, cut to its length where the file was longer (with a 20 ms fade), peak
normalised to −1 dBFS, encoded as Ogg Vorbis (quality 3) and MP3 (quality 5). The laser hum's tail
is cross-faded into its head over 0.3 s so that it loops without a click. `CREDITS.md` and the
README list the packs and which file each sound comes from.

**Acceptance criteria**
- Given the sound files in `public/sfx/`, then each sound has an `.ogg` and an `.mp3` and is listed
  in `CREDITS.md` with its source file and its license (review).
- Given each sound, then the reviewer finds it sounds like a real thing rather than a chip (manual
  check, in the Dev menu's sounds viewer).

*Sources: D-239, D-261.*

### AUD-SFX-09 — Variants of the common explosions · MUST

The two explosions heard most, `explosion-small` and `explosion-large`, each have three different
recordings (`explosion-small-1` to `-3`, `explosion-large-1` to `-3`). Each time one plays, one of
its three is picked at random, never the one played last for that sound, so a busy wave does not
repeat the same blast. The pick comes from a seeded generator (`VARIANT_SEED`), so the same game
sounds the same (ENG-18, ENG-46). A sound's gain, priority and the voice limits are the sound's, not
the recording's; its length for the voice pool is that of its longest recording.

**Acceptance criteria**
- Given a sound with variants played many times, then each variant plays and none plays twice in a
  row (unit test).
- Given the same seed, then the same variants play in the same order (unit test).
- Given the sound designs, then `explosion-small` and `explosion-large` have three samples each
  and every other sound one (unit test on the data).

*Sources: reviewer request 2026-11-04, D-262.*

### AUD-SFX-10 — Blasts varied at random · MUST

A boss dying blows up at a regular pace (BOSS-19, a blast every `every` seconds), and a wave of
enemies dying together stacks blasts: the same few recordings at the same pitch and level, at a fixed
rhythm, sound like a machine. So each play of `explosion-small`, `explosion-large` and
`boss-part-destroyed` is varied at random (the seeded generator of AUD-SFX-09): its speed, so its
pitch, by up to ±`pitch` of 1 (small and large ±20 %, part ±12 %); its level, up to `gain` quieter
(30 %, 20 %); and its start, up to `delay` late (80 ms, 50 ms), which also breaks the pace. Nothing
else is varied: a sound that tells the player something (a hit, a pickup, a menu click) must sound the
same each time, and the simulation's own blast timing is untouched.

**Acceptance criteria**
- Given such a sound played many times, then its speed, level and delay stay within the spread and
  differ from one play to the next (unit test).
- Given a sound without a spread, then it plays the same each time (unit test).
- Given the sound designs, then only the small and large explosions and the boss part's have a
  spread (unit test on the data).
- Given a boss dying, then the reviewer finds its explosions irregular and not repetitive (manual
  check, K in the bosses viewer).

*Sources: reviewer request 2026-11-04, D-262.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| sound designs | per cue: sample (the sound's name), gain, priority, length, positional, loop | `src/game/view/audio/sound_designs.py` `SOUND_DESIGNS` |
| priorities | 0 (enemy shots) … 7 (top) | `sound_designs.py` `PRIORITY` |
| gains | `gun-shot` 0.14, `laser-hum` 0.1, `hit` 0.3, `explosion-small` 0.32, `explosion-large` 0.42, `bomb` 0.5, `boss-destroyed` 0.5, `player-hit` 0.36 | `SOUND_DESIGNS` (a gain is the sound's peak in the mix: the samples peak at −1 dBFS) |
| sample files | `public/sfx/<name>.ogg` and `.mp3`, mono, 44.1 kHz, 29 sounds from 33 samples, about 700 KB in all | `CREDITS.md` |
| minigun_rounds / minigun_gap | 6 / 21 ms (the burst is 0.165 s) | the `gun-shot` sample (`CREDITS.md`) |
| gun shot length | at most 0.25 s | `sound_designs.py` |
| explosion lengths | small 0.64 to 0.8 s, large 1.26 to 1.5 s, boss part 1.55 s, bomb 1.98 s, boss 2 s | `sound_designs.py` |
| explosion variants | 3 each for small and large | `sound_designs.py` `_variants` |
| blast spread | small and large: pitch ±20 %, level −30 %, delay 80 ms; boss part: ±12 %, −20 %, 50 ms | `sound_designs.py` `BLAST_JITTER`, `PART_JITTER` |
| large_blast_radius | 18 px | `src/game/view/audio/game_audio.py` `LARGE_BLAST_RADIUS` |
| loudest_sfx | +6 dB over the music | checked on the data |

## Notes

- The sounds were first synthesised: long low-pass hisses, then short muffled booms (D-107), then
  layered explosions (D-108), then filtered noise, sines and bells instead of chip sweeps (D-239).
  They were replaced by CC0 samples (D-261); the recipes (`sound_recipes.py`) and the synthesised
  designs are gone from the code, and the music is still synthesised.
- Measured offline for the synthesised sounds (D-108): a busy wave peaked at −5.8 dBFS at the default
  volume. The samples have not been measured the same way: the loudest sound (`bomb`, `boss-destroyed`)
  is kept within +6 dB of the music by the check of AUD-SFX-06.
- The sounds were picked by file name and duration, not by ear (no listening in the implementation
  session): the reviewer is expected to listen to each in the Dev menu's sounds viewer and ask for
  other files of the packs where one does not fit. Changing a sound means a new file in
  `public/sfx/` (both formats) and a new `CREDITS.md` line.
