# Sound effects

> **Area:** Audio · **Prefix:** `AUD-SFX` · **Related:** [engine.md](engine.md), [music.md](music.md), [../gameplay/weapons.md](../gameplay/weapons.md), [../gameplay/bombs.md](../gameplay/bombs.md), [../gameplay/bonuses.md](../gameplay/bonuses.md), [../ui/menu-input.md](../ui/menu-input.md)

Every gameplay and menu event has its own generated sound effect, designed so the player can tell
them apart and so a busy screen stays pleasant: the guns rattle like a minigun, explosions are
layered like real blasts, and the player's own guns are mixed under the hits and explosions. This
file lists the sounds, their design rules, their priorities and their mix. How they are played
(voices, limits, panning) is in [engine.md](engine.md).

## Requirements

### AUD-SFX-01 — A sound for every event · MUST

Every event below plays its own generated sound, distinct from the others:

| Group | Event (cue) | Sound |
|-------|-------------|-------|
| Player weapons | a volley of the guns (`fire:bullet`) | `gun-shot`, a minigun burst |
| | the laser starts (`beam-start:laser`) | `laser-start`, a rising zap |
| | the laser fires (`beam:laser`) | `laser-hum`, a looping hum |
| | a volley of missiles (`fire:missile`) | `missile-launch`, a whoosh |
| | weapon switched (`weapon-switch`) | `weapon-switch`, a two-note chime |
| | weapon level up (`weapon-up`) | `weapon-level-up`, a four-note rising chime |
| Enemy weapons | enemy bullet fired (`enemy-bullet`) | `enemy-shot`, a falling blip |
| | enemy missile launched (`enemy-missile`) | `enemy-missile`, a band-passed hiss |
| | laser warning line (`laser-warning`) | `laser-warning`, two short beeps |
| | enemy laser fires (`laser-fire`) | `enemy-laser`, a falling growl |
| Hits | player shot hits (`hit`) | `hit`, a short crack |
| | player shot hits a shielded part (`hit-blocked`) | `hit-shield`, a metallic ping |
| | the player ship is hit (`player-hit`) | `player-hit`, a falling buzz |
| Destruction | small enemy blows up (`blast-small`) | `explosion-small` |
| | large enemy blows up (`blast-large`) | `explosion-large` |
| | boss part destroyed (`part-destroyed`) | `boss-part-destroyed`, a large explosion and a falling tone |
| | boss destroyed (`boss-destroyed`) | `boss-destroyed`, a chain of three explosions |
| Player | life lost (`life-lost`) | `life-lost`, a falling tone over a large explosion |
| | extra life (`extra-life`) | `extra-life`, a bright four-note chime |
| | bomb (`bomb`) | `bomb`, a huge explosion and a falling sweep |
| | bonuses picked up (`bonus:weapon`, `bonus:life`, `bonus:bomb`) | `weapon-bonus`, `life-bonus`, `bomb-bonus` |
| Menus | move, confirm, back, pause, resume, slider step | `menu-move`, `menu-confirm`, `menu-back`, `pause`, `resume`, `slider-step` |

A blast is large when the enemy's hit radius is at least `large_blast_radius` (18 px); an enemy
missile shot down blows up small. A slider step plays at the new sound volume.

**Acceptance criteria**
- Given each event of the table, then its sound plays when the event happens (unit test with a
  fake audio context, one case per event).
- Given the sound designs, then every event of the table has its own sound (unit test on the data).

*Sources: GD-71, P12-R09, D-095, D-097.*

### AUD-SFX-02 — The minigun · MUST

The guns sound like a minigun ("BRRRT"): each volley plays one burst of `minigun_rounds` (6) short
rounds `minigun_gap` (21 ms) apart, each a gritty band-passed noise crack over a short falling
thump, every other round quieter. A burst lasts until the next volley (the guns fire 8 volleys a
second), so holding fire rattles on without a gap, and it stops within one volley of letting go.
If the guns' rate changes, the burst follows it.

**Acceptance criteria**
- Given the gun sound and the guns' rate, then one burst covers one volley with at least 5 rounds
  (unit test).

*Sources: P12-R09, D-101.*

### AUD-SFX-03 — One fire sound per volley · MUST

The guns and the missiles sound once per volley (when the first stream of a volley fires, their
streams firing in turn), at the ship's x; not once per shot, so a 5-stream level does not take 5
voices. The laser sounds its start once, then its hum loops while it fires and stops when it stops.

**Acceptance criteria**
- Given the guns at level 5 held for 1 s, then 8 gun sounds are asked for (unit test).
- Given the laser released, then its hum stops (unit test).

*Sources: P03-R11, D-102, D-097.*

### AUD-SFX-04 — Layered explosions · MUST

Every explosion uses one layered recipe, in three sizes (small, large, huge): a 12 ms high-passed
noise crack (the shock front), a low-passed noise body closing from a few kHz to 180 Hz over the
blast (the fireball), a sub-bass thump gliding down by half, a low-passed rumble tail for the large
and huge sizes, and 3 to 8 short band-passed debris crackles at fixed, uneven delays, so a sound is
the same every time. Most of its energy is low, so a busy wave does not turn into a hiss. Small
enemies blow up small, large enemies and boss parts large, bosses and bombs huge; a boss dies in a
chain of three (huge, then two large).

**Acceptance criteria**
- Given each explosion size, then its layers are those of the recipe (unit test on the data).
- Given a busy wave, then the reviewer finds the explosions realistic and not tiring (manual
  check).

*Sources: P12-R09, D-108.*

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

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| sound designs | per cue: layers, gain, priority, positional, loop, hold | `src/game/view/audio/sound_designs.py` `SOUND_DESIGNS` |
| priorities | 0 (enemy shots) … 7 (top) | `sound_designs.py` `PRIORITY` |
| gains | `gun-shot` 0.14, `laser-hum` 0.1, `hit` 0.3, `explosion-small` 0.32, `explosion-large` 0.42, `bomb` 0.5, `boss-destroyed` 0.55 | `SOUND_DESIGNS` |
| minigun_rounds / minigun_gap | 6 / 21 ms | `src/game/view/audio/sound_recipes.py` `MINIGUN` |
| explosion sizes | small 0.3 s, large 0.6 s (0.9 s tail), huge 1.1 s (2 s tail); 3 / 5 / 8 debris | `sound_designs.py` `BLAST_SMALL`, `BLAST_LARGE`, `BLAST_HUGE` |
| large_blast_radius | 18 px | `src/game/view/audio/game_audio.py` `LARGE_BLAST_RADIUS` |
| loudest_sfx | +6 dB over the music | checked on the data |

## Notes

- The enemy explosions were first long low-pass hisses, then short muffled booms (D-107), then the
  layered recipe of AUD-SFX-04 for every blast (D-108, which replaced the booms).
- Measured offline (D-108): a busy wave peaks at −5.8 dBFS at the default volume.
