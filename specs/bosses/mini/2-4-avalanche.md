# Avalanche — 2-4 mini boss

> **Area:** bosses · **Prefix:** `MB-AVALANCHE` · **Related:** [common.md](../common.md), [2-4 Industrial belt](../../worlds/world-2/2-4-industrial-belt.md), [World 2](../../worlds/world-2/world.md), [Glacier Colossus (2-4 final)](../final/2-4-glacier-colossus.md)

The Avalanche is the mini boss of 2-4, met at half the level, and its fight is a chase (the ground
scrolls faster). It is a 3.5 L burrowing beast: a squat body of flesh under a ridged shell crawling
on segmented flanks, two fleshy arms swinging in front of it that end in grafted drills, and a crop
sac of rock and ice on its back that drops lines of big rocks, in yellow neon. It was designed as a
drilling machine chasing down a glacier of the Frozen North; World 2 became the Industrial Desert
(D-110) and the boss kept its name and its frost. Everything all bosses share is in
[common.md](../common.md).

## Requirements

### Look

#### MB-AVALANCHE-01 — Silhouette and size · MUST

The Avalanche is `size` across. Seen from above it is a heavy, blunt-nosed body between two crawling
flanks, its head at the front, its two drill arms reaching forward from its shoulders either side of
the head, their drills pointing down the screen, and the crop sac on its back behind the middle.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Avalanche, then it reads as a squat crawler with two drills ahead of it and a heap of rocks on its back.

*Sources: P08-R10, P16-R05.*

#### MB-AVALANCHE-02 — A burrowing beast · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code:
- a squat body of sinew under a ridged teal shell, bone ribs across it, a row of ice spines down it;
- its head in front (the old cab) of graphite flesh, angry yellow eyes on it, a metal plate grafted
  on top;
- a crawling flank of five swollen teal segments either side (where the tracks were), a metal fender
  over each, short clawed legs of bone digging under it;
- two spiracles breathing out of the shell, each capped by a sooted metal valve;
- a weathered metal patch on its deck, reactor sacs at its tail.

*Sources: P08-R10, P16-R05.*

#### MB-AVALANCHE-03 — Its parts and guns on the body · MUST

- Each drill arm: an upper arm on the shoulder and a forearm on the elbow, each a muscle of flesh
  along the bone with an armour plate grafted on top and a ram working it, a cog at the elbow.
- Each drill: a swollen fist of flesh, a fluted metal bit driven into it pointing down the screen, a
  yellow collar round its housing, its gun on a bracket along its outer side.
- The rock hopper: a crop sac of membrane on its back, its mouth gaping with rocks and ice, a metal
  rim grafted on it with a yellow band, a chute at its front where the rocks drop from.
- The core's guns: twin guns on a mount under the head's chin.

*Sources: P08-R10, P16-R05.*

#### MB-AVALANCHE-04 — Lights and colours · MUST

Its neon is yellow (`neon`): a band round the body's rim, stripes along the head, the eyes, glowing
veins and glands down its back, lamps on its flanks, the drills' collars and the arms' lights, the
hopper's band, the reactor sacs.

*Sources: P08-R10, P16-R05.*

#### MB-AVALANCHE-05 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: snow caps on its deck and head, snow
drifted on the fenders' rear halves and packed in the treads at their front, rocks and snow heaped
in the hopper, icicles under its nose, its flanks and the drills, ice crystals on its back.

*Sources: P08-R10, D-110.*

#### MB-AVALANCHE-06 — Swinging drill arms · MUST

Its two drill arms are moving limbs on two joints each (the limb rules of
[common.md](../common.md)): each swings at its shoulder (`shoulder_swing`) and bends at its elbow
(`elbow_swing`), the drill riding the elbow; the right arm mirrors the left one a little out of step
(`right_late`). The drills' hit circles and muzzles move with them.

*Sources: P08-R10, D-061.*

#### MB-AVALANCHE-07 — What its transformation sheds · MUST

At its transformation the armour of both flanks (region `flanks`: from 10 to 44 px out either side,
from 12 px ahead of the centre to 38 px behind it) bursts off, baring dark metal ribs and spars
(`wing`), and its two heavy cannons rise from it. The keel stays under the cut and the boss stays one
object.

*Sources: D-221, D-224, D-227, D-229.*

### Behaviour

#### MB-AVALANCHE-08 — Entry and movement: a chase · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height. In
place it sways by up to `sway` and bobs by `bob`. The fight is a chase: the ground scrolls at
`ground_speed` of 2-4's speed, faster than the level.

*Sources: P08-R10.*

#### MB-AVALANCHE-09 — Drills · MUST

Parts `drill-left` and `drill-right`, at the arms' tips (at rest ±42 px across and 36 px ahead of the
centre), `drill_radius` round with `drill_hp` each, each on its arm's elbow joint. Both shield the
core. Each fires aimed bursts of 3 red bullets, 0.16 s apart, every 2.4 s (first at 1 s and 2.2 s).

*Sources: P08-R10, D-061.*

#### MB-AVALANCHE-10 — Rock hopper · MUST

Part `hopper`, on its back 31 px behind the centre, `hopper_radius` round with `hopper_hp`. It does
not shield the core. Every 4 s it drops three rows of slow, big violet rocks straight down from its
chute, 26° apart, half a second apart: a row of 3 (at 1.5 s), a row of 2 offset between them (at
2 s), a row of 3 (at 2.5 s), so they make a lattice the player weaves through.

*Sources: P08-R10.*

#### MB-AVALANCHE-11 — Core and stage patterns · MUST

Its core (`core_radius`, `core_hp`) fires orange fans from its chin guns. One pattern per stage:
- stage 0: a fan of 3, 16° apart, every 3.2 s;
- stage 1: a fan of 5, 14° apart, every 2.6 s;
- stage 2: a fan of 7, 12° apart, every 2.2 s;
- stage 3 (the last): a ring of 12 orange every 1.6 s turning 9° a volley, and a fan of 5 red, 14°
  apart, every 2.6 s.

The last stage's ring is fired by no earlier stage.

*Sources: P08-R10, D-068.*

#### MB-AVALANCHE-12 — Rage · MUST

It is angry as every boss with `spirals` at heat `rage_heat` (two crossing spirals, orange and red).

*Sources: D-068.*

#### MB-AVALANCHE-13 — Transformation · MUST

It transforms once, when 2 of its 3 original parts are destroyed. The transformation sheds its flank
armour (MB-AVALANCHE-07) and reveals a pair of heavy cannons, `cannon-left` and `cannon-right`, at
±29 px across and 21 px behind the centre, `weapon_radius` round with `weapon_hp` each (0.8 of a
drill's), firing aimed spreads of big violet shells ([common.md](../common.md)), first 1.2 s and
2.0 s into each stage. They shield the core.

*Sources: D-221, D-224, D-229.*

#### MB-AVALANCHE-14 — Health, points and death · MUST

Its full health is `full_hp` (core and original parts), `full_hp_with_weapons` with its cannons. It
is worth `points`. Its parts drop a bonus as mini boss parts do, its cannons as hidden weapons do. It
dies as every boss.

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 3.5 L (119 px) | `src/game/config/bosses/world_2/avalanche.py` `_AVALANCHE["stats"]` |
| neon | yellow (1, 0.85, 0.1) | `src/game/config/boss_look.py` `BOSS_LOOK.neon["avalanche"]` |
| stop_fraction | 0.74 | `stopFraction` |
| sway | 60 px, 7.5 s | `sway` |
| bob | 8 px, 3.2 s | `bob` |
| ground_speed | ×1.4 | `groundSpeed` (a chase) |
| core_radius / core_hp | 18 px / 1 400 | `coreRadius`, `coreHealth` |
| arm rest points | shoulder (±20, −12), elbow (±34, −24), drill (±42, −36) | `AVALANCHE_ARM` |
| shoulder_swing | ±7°, 4.2 s | `drill_arm` |
| elbow_swing | ±12°, 2.8 s, phase 0.25 | `drill_arm` |
| right_late | 0.37 of a period | `drill_arm` |
| drill_radius / drill_hp | 14 px / 900 | `part("drill-…")` |
| hopper_radius / hopper_hp | 14 px / 600 | `part("hopper" …)` |
| rocks | violet, 110 px/s, radius 7 | `ROCK` |
| bullets | orange 180, red 190 px/s | `ORANGE`, `RED`; times the level's factors |
| rage_heat | 5.5 (`spirals`, orange / red) | `rage` |
| transformation | after 2 of 3 parts | `boss_build.default_transforms` |
| weapon_radius / weapon_hp | 11 px / 720 | `hidden_weapon("cannon-…")`, pod 12.2 px high |
| region `flanks` | x 10…44 (mirrored), y −12…38, from 4.2 px up, `wing` | `armour_region("flanks", 1, …)` |
| full_hp / full_hp_with_weapons | 3 800 / 5 240 | core + parts |
| points | 7 000 (700 a part) | `points` |
