# Obsidian Golem (4-3 final boss)

> **Area:** bosses · **Prefix:** `FB-OBSIDIAN-GOLEM` · **Related:** [common boss rules](../common.md),
> [4-3 Midtown](../../worlds/world-4/4-3-midtown.md), [World 4](../../worlds/world-4/world.md),
> [Magma Salamander](../mini/4-3-magma-salamander.md), [readability](../../graphics/readability.md),
> [shots](../../graphics/shots.md)

The Obsidian Golem is the final boss of level 4-3, met at the end of the level. It is a massive
armoured flying fortress 5.5 L across shaped like a hunched giant: a broad torso of black obsidian
plates split by glowing magma seams, a small helmed head low on its chest, a furnace stack on its
back, and two arms bending at the shoulder and the elbow down to huge fists that pump in turn. It
was designed for the Volcanic Lands' lava fields; since World 4 became the Metropolis (D-112) it
keeps its name and its look and flies over midtown. It transforms twice: first its flank slabs lift
like gull-wing doors over two heavy cannons; then its spine plating bursts off for a sweeper and two
mortars. Everything shared by all bosses is in [bosses/common.md](../common.md); this file only gives
what is the Golem's own. Positions are px from the boss's centre, X right, Y up the screen (its chest
faces down the screen, at -Y); heights are above the playfield.

## Requirements

### Look

#### FB-OBSIDIAN-GOLEM-01 — Silhouette · MUST

Seen from above, the Golem is a hunched giant about 5.5 L across (radius 2.75 L), its chest down the
screen: a broad torso about 80 px wide and 66 px deep, a hump over it rising about 28 px, heavy
pauldrons on its shoulders, two arms reaching out and forward from the shoulders (40 px out) through
the elbows (60 px out) to the fists (72 px out, 42 px ahead of the centre), the shoulder cannons
behind the pauldrons, a small helm low on its chest, the armour plate and the chest emitter on its
front and the furnace stack on its back.

**Acceptance criteria**
- Given the dev bosses viewer, when the Golem is shown, then it reads as a hunched giant with two huge
  fists (manual).

*Sources: P10-R11.*

#### FB-OBSIDIAN-GOLEM-02 — Cyber-Organic body · MUST

It is a living hunched giant (Cyber-Organic): its flesh torso and hump ribbed in bone and veined with
magma, obsidian growths for its pauldrons, knuckles and chest plate, its armour black volcanic glass
(matte, a touch of violet) split by glowing magma seams across its back; a metal helm with a glowing
visor, the twin guns under its brow, the furnace stack (its glowing top where the core's rings leave)
and the guns grafted on. Its three reactors sit in glowing flesh sacs under its back. The pauldrons
are domes of obsidian ringed with neon. Each upper arm is a thick, plated strut down to the elbow,
each forearm a massive tapering block of armour down to the wrist.

**Acceptance criteria**
- Given the model, then it reads as one giant creature, not as parts stuck on a box (manual).

*Sources: P10-R11, P16-R06.*

**Discrepancy:** P16-R06 asks for the world's theme to stay recognisable ("a metropolis boss feels
like a city-sized organism"); the model keeps the volcanic theme of its design (D-112 left the World 4
bosses unchanged) and nothing in it reads as a city.

#### FB-OBSIDIAN-GOLEM-03 — Fists · MUST

Each fist is a huge block of obsidian with four knuckles, magma glowing between them, a thumb on its
inner side and the magma vent in the middle of its knuckles. The arms belong to the body (they flash
with the core): a destroyed fist is hidden and leaves nothing in its place; its arm stays, still
pumping.

**Acceptance criteria**
- Given the dev viewer, when K destroys a fist, then the fist disappears and its arm stays (manual;
  `test_boss_models.py` checks every part is drawn).

*Sources: P10-R11, P16-R06, D-225, D-167.*

#### FB-OBSIDIAN-GOLEM-04 — Shoulder cannons · MUST

Each shoulder cannon sits on a low armoured ring on the back of its shoulder; on it a turret, a
faceted dome with two heavy barrels, turns the way its spreads fire next. Destroyed, a cannon and its
mount are hidden and leave nothing in their place.

**Acceptance criteria**
- Given a cannon stands, then its turret turns to follow the player (manual; unit: turret rule in
  [common](../common.md)).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-OBSIDIAN-GOLEM-05 — Armour plate and chest emitter · MUST

The armour plate is a thick chevron of obsidian on its chest, cracked with magma, bolted on with dark
studs; it carries no weapon. The chest emitter is a heavy housing on its prow under the plate, ringed
with neon, its lens glowing as its laser charges. Destroyed, each is hidden and leaves nothing in its
place.

**Acceptance criteria**
- Given the model, then the emitter's lens sits at its laser muzzle, 68 px ahead of the centre (unit:
  `test_boss_models.py`; manual).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-OBSIDIAN-GOLEM-06 — Lights and colours · MUST

Its registered neon is the deep orange of its magma seams (`obsidian-golem`); like every boss's warm
lights it is drawn bright yellow (see [readability](../../graphics/readability.md)). Neon rings the
pauldrons and the emitter and lights the visor; its magma seams, cracks and veins (hotter in the
design) are in the same yellow family. White charge lights sit at the barrels' mouths, the fists'
vents, the stack's top and the emitter's lens.

**Acceptance criteria**
- Given the model, then every neon and glowing seam is bright yellow (unit: enemy colour family
  tests).

*Sources: P10-R11, D-231.*

#### FB-OBSIDIAN-GOLEM-07 — Pumping arms · MUST

The two arms are moving limbs on two joints each: a shoulder joint (40 px out, 2 px ahead of the
centre) swinging 9° either way and an elbow joint on it (60 px out, 16 px ahead) swinging 14° either
way, both once every 4.2 s, the elbow a quarter swing behind its shoulder and the right arm half a
swing behind the left, so the fists pump in turn. The fists' hit circles and vents move with their
arms.

**Acceptance criteria**
- Given the boss is in place, then the fists pump in turn, bending at shoulder and elbow (manual, dev
  viewer); their muzzles move with the joints (unit: joint rule).

*Sources: P10-R11, D-061.*

### Behaviour

#### FB-OBSIDIAN-GOLEM-08 — Entry, place and ground speed · MUST

The Golem comes in from above the top edge and stops at 0.74 of the playfield's height. In place it
sways up to 24 px either side over 12 s and bobs 5 px over 6 s. While it is fought the ground runs
at ×0.3 the level's speed.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.3 and the boss stops at 0.74 of the playfield
  height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P10-R11.*

#### FB-OBSIDIAN-GOLEM-09 — Parts and health · MUST

The Golem has a core (hit radius 24 px, 5 200 HP) and six original parts: two fists (17 px, 1 600 HP
each) and the armour plate (16 px, 1 000 HP), which shield the core, and two shoulder cannons (13 px,
1 100 HP each) and the chest emitter (12 px, 800 HP), which do not; hanging in front of the plate, the
emitter can always be shot. Its full health is 12 400 HP with the original parts, 19 760 HP with its
five hidden weapons, which count in the health bar from the start.

**Acceptance criteria**
- Given the design, then it has six original parts and five hidden ones, and only the fists, the
  plate and the hidden weapons shield the core (unit: `test_obsidian_golem.py`).

*Sources: P10-R11, D-088, D-221.*

#### FB-OBSIDIAN-GOLEM-10 — Fist magma rings · MUST

While they stand, in every stage, each fist throws a ring of 8 slow, big globs of magma (`orange`,
110 px/s, radius 9 px) from its vent every 4.4 s, the left ring turning 11° each time and the right
one -11°, the left first 1.6 s and the right 3.8 s into a stage.

**Acceptance criteria**
- Given a fist stands, then its rings leave its knuckles, wherever its arm has swung (unit: design
  guns, joints).

*Sources: P10-R11.*

#### FB-OBSIDIAN-GOLEM-11 — Shoulder cannon spreads · MUST

While they stand, in every stage, each shoulder cannon fires an aimed spread of 3 `magenta` bullets
(210 px/s, 12° apart) every 3 s from its twin barrels, turning to aim, the left one 1 s and the right
one 2.5 s into a stage.

**Acceptance criteria**
- Given a cannon stands, then its spreads leave its barrels' tips as its turret has turned (unit:
  turret volleys in `boss_build.py`).

*Sources: P10-R11.*

#### FB-OBSIDIAN-GOLEM-12 — Chest emitter laser · MUST

While it stands, in every stage, the chest emitter fires a laser straight down the screen every 7 s
(1.6 s long, after its 1 s warning line), first 4 s into a stage.

**Acceptance criteria**
- Given the emitter stands, then its beam leaves its lens and does not turn (unit: design guns).

*Sources: P10-R11.*

#### FB-OBSIDIAN-GOLEM-13 — Core patterns by stage · MUST

The core fires from the twin guns under its brow and from its furnace stack, a new pattern at each
stage (stage k: k parts destroyed; from the sixth on, its last pattern):
- stage 0: a single aimed `red` bullet (215 px/s) every 2.6 s;
- stage 1: bursts of 4 `red` (0.13 s apart) every 2.5 s;
- stage 2: a fan of 5 `orange` (205 px/s, 14° apart) every 2.5 s;
- stage 3: a ten-armed spiral (rings of 10 `purple`, 200 px/s, every 1.6 s, turning 8°);
- stage 4: a fan of 7 `orange` (12° apart) every 2.3 s and bursts of 3 `red` every 2.9 s;
- stage 5: a ring of 12 `purple` every 1.5 s, turning -9°, and aimed spreads of 3 `red` (12° apart)
  every 2.4 s;
- stage 6: magma bombs (slow `red` globs, 120 px/s, radius 8 px, bursting after 1.1 s into a ring of
  10 `orange` at 170 px/s) aimed every 2.4 s, and two counter-turning spirals of 12 (`orange` turning
  11° and `purple` turning -13°, every 1.3 s), used by no earlier stage.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, and the last stage's bombs and
  spirals are used by no earlier stage (unit: `test_obsidian_golem.py`).

*Sources: P10-R11, D-088.*

#### FB-OBSIDIAN-GOLEM-14 — Laser colour · MUST

Its lasers (the emitter's and the hidden sweeper's) are drawn in its own colour: its deep orange neon
moved into the enemy shots' family, a deep orange (about [1, 0.31, 0.04]) round a white-hot core.

**Acceptance criteria**
- Given the emitter fires, then its beam is deep orange (unit: `enemy_lasers.color_of`).

*Sources: P10-R11, D-072.*

#### FB-OBSIDIAN-GOLEM-15 — Rage · MUST

After the pause that follows each destroyed part, the Golem is angry: it fires a flower (a dense,
slowly turning ring and small aimed fans) and a vortex (a fast-turning spiral and bursts at the
player) at once, at heat 12, each at half the rate (`orange` and `red`, `red` and `magenta`): about
116 bullets a second in all, at 216 px/s.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires both angry patterns for the
  rage time (unit: `test_boss_rage.py`, `test_obsidian_golem.py`).

*Sources: D-088, D-063.*

#### FB-OBSIDIAN-GOLEM-16 — First transformation: the flank slabs lift · MUST

Once both shoulder cannons are destroyed, the Golem transforms: its two flank slabs (from 14 px to
56.3 px out either side, from 25 px ahead of the centre to 35 px behind it, above 8.8 px high) lift
70° on hinges along their outer edges (56.3 px out, 20 px high), turning about the boss's length,
like gull-wing doors, and stay up. Dark metal `wing` frames show where they lay, and two heavy
cannons stand in the dark metal beneath. The shoulder cannons, which stood on the slabs, are gone
before they move. The boss stays one object after the move.

**Acceptance criteria**
- Given both shoulder cannons are destroyed, then the boss transforms and its flank slabs swing up
  70° (unit: `test_boss_kinds.py`: transform parts, no hit part on a moving piece).
- Given the boss after this transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-230, D-221, D-224, D-227.*

#### FB-OBSIDIAN-GOLEM-17 — First hidden weapons: two heavy cannons · MUST

The first transformation reveals two heavy cannons under the lifted slabs, 34 px either side of the
centre and 5 px behind it (radius 10 px, pods 29.6 px high, 1 280 HP each, 30 % drop chance). They
shield the core and fire `orange` spreads of large, slow shells at the player as every cannon does
(see [common](../common.md)), turning to aim; the left one 1.2 s and the right one 2.0 s into a stage.

**Acceptance criteria**
- Given the first transformation is over, then both heavy cannons are live targets that fire (unit:
  `test_boss_kinds.py` weapon checks).

*Sources: D-221, D-229, D-230.*

#### FB-OBSIDIAN-GOLEM-18 — Second transformation: spine plating bursts off · MUST

Once the armour plate and the chest emitter are destroyed, the Golem transforms again: its spine
plating bursts off, one region across the centre line, 14 px either side, from 38 px ahead of the
centre to 16 px behind it, above 10.6 px high. Under it a dark metal `shell` frame (a lattice) shows.
The boss stays one object after it.

**Acceptance criteria**
- Given the plate and the emitter are destroyed, then the boss transforms a second time and its spine
  region bursts off (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given the boss after its second transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227, D-230.*

#### FB-OBSIDIAN-GOLEM-19 — Second hidden weapons: a sweeper and two mortars · MUST

The second transformation reveals, on the bared spine, a sweeper on the centre line 12 px ahead of
the centre (radius 10 px, pod 29.2 px high, 1 600 HP), firing its sweeping laser, and two mortars
8 px either side of the centre line, 7 px behind the centre (radius 7 px, pods 29.2 px high, 1 600 HP
each), firing `red` flak shells, as those kinds do (see [common](../common.md)); first 1.6 s, 1.2 s
and 2.6 s into a stage. They shield the core and drop a bonus 30 % of the time. Its fire goes up at
each transformation (about 7.2, then 9.3, then 11.8 weighted shots a second).

**Acceptance criteria**
- Given the second transformation is over, then the sweeper and the mortars are live targets that
  fire, of kinds not revealed at the first (unit: `test_boss_kinds.py`).

*Sources: D-221, D-229.*

#### FB-OBSIDIAN-GOLEM-20 — Points and drops · MUST

Destroying the Golem scores 16 000 points, and each part destroyed 1 600. Its original parts drop a
bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.

**Acceptance criteria**
- Given a fist is destroyed, then the score rises by 1 600 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/obsidian_golem.py` (`OBSIDIAN_GOLEM`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-3, final | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 5.5 L (radius 93.5 px) | `stats.size` |
| core | radius 24 px, 5 200 HP | `coreRadius`, `coreHealth` |
| fists | (±72, -42), radius 17, 1 600 HP, shield, on their elbows | `GOLEM_ARM.fist` |
| shoulder cannons | (±46, 20), radius 13, 1 100 HP, no shield, on turrets | `GOLEM_PARTS.cannon` |
| chest emitter | (0, -58), radius 12, 800 HP, no shield | `GOLEM_PARTS.emitter` |
| armour plate | (0, -34), radius 16, 1 000 HP, shield, no weapon | `GOLEM_PARTS.plate` |
| full health | 12 400 (19 760 with hidden weapons) | D-088 |
| stop / sway / bob | 0.74 / 24 px, 12 s / 5 px, 6 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×0.3 | `groundSpeed` |
| arms | shoulders (±40, -2) ±9°, elbows (±60, -16) ±14°; 4.2 s, elbow lag 0.25, right +0.5 | `GOLEM_ARM`, `PUMP` |
| muzzles | knuckles (±72, -57, 7), cannons (±46 ∓ 2.6, 5, 15), lens (0, -68, 6), brow (±6, -24, 22), stack (0, 30, 30) | `GOLEM_*` |
| fist rings | 8 globs, every 4.4 s, turn ±11°, first 1.6 / 3.8 s; 110 px/s, radius 9 | `MAGMA` |
| cannon spreads | 3 × 12°, every 3 s, first 1 / 2.5 s | stage volleys |
| emitter laser | every 7 s, 1.6 s, first 4 s, straight down | `volley.laser("emitter", …)` |
| magma bomb | 120 px/s, radius 8, bursts after 1.1 s into 10 at 170 px/s | `BOMB` |
| bullets | `red` 215, `orange` 205, `magenta` 210, `purple` 200 px/s | radius 4 |
| rage | flower + vortex, heat 12, half each | `rage.flower`, `rage.vortex` |
| transformations | both shoulder cannons; then plate and emitter | `transformParts` |
| flank slabs (moving) | x 14..56.3 (mirrored), y -25..35, above 8.8; swing about the length at (±56.3, 5, 20), 0 → 70° | `moving_region("flanks", …)`, `src/game/config/bosses/moving_regions.py` |
| spine | x -14..14, y -38..16, above 10.6, `shell` | `armour_region("spine", …)` |
| heavy cannons | (±34, 5), radius 10, pod 29.6, 1 280 HP, `orange`, first 1.2 / 2.0 s | form 1 |
| sweeper | (0, -12), radius 10, pod 29.2, 1 600 HP, first 1.6 s | form 2 |
| mortars | (±8, 7), radius 7, pod 29.2, 1 600 HP, `red`, first 1.2 / 2.6 s | form 2 |
| drops | parts 0.6, hidden weapons 0.3, core 1 | `fpart`, `coreDrop` |
| points | 16 000 (1 600 a part) | `points`, `boss_part_points` |
| neon | [1, 0.32, 0.04], drawn [1, 1, 0.04]; laser [1, 0.31, 0.04] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["obsidian-golem"]` |

## Notes

- Phase 10 fight time with the D-055 bot: 112.4 s, before the hidden weapons (D-221).
- D-230's design asked for "slabs swinging forward like arms"; the Golem already has arms, so its
  slabs lift like gull-wing doors instead.
- Its full health takes its place in World 4's boss ordering (P10-R12, see
  [World 4](../../worlds/world-4/world.md)).
