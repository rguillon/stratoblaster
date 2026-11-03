# Mangrove Croc (3-1 mini boss)

> **Area:** bosses · **Prefix:** `MB-MANGROVE-CROC` · **Related:** [common boss rules](../common.md),
> [3-1 Canal works](../../worlds/world-3/3-1-canal-works.md), [World 3](../../worlds/world-3/world.md),
> [River Leviathan](../final/3-1-river-leviathan.md), [readability](../../graphics/readability.md)

The Mangrove Croc is the mini boss of level 3-1, met at the middle of the level. It is a long, low
hover-gunboat shaped like a crocodile, 3 L long, whose jaws open and close around a cannon in its
throat, with a side pontoon on each flank. It was designed for the old Jungle world (a chase up a
river delta); since World 3 became the factories-to-garden-villages world (D-111) it keeps its name
and its look and flies over the canal works. It transforms once (see [common](../common.md)): its
back plating bursts off and two gatling turrets come out. Everything shared by all bosses (parts and
core, stages, rage, turrets, joints, transformations, colours, death, checkpoint) is in
[bosses/common.md](../common.md); this file only gives what is the Croc's own.

## Requirements

### Look

#### MB-MANGROVE-CROC-01 — Silhouette · MUST

Seen from above, the Croc is a crocodile about 3 L long, nose down the screen: a tapering tail, a
long, low, broad body on a hover skirt, a broad head, and two jaws in front of it reaching to about
53 px ahead of its centre. A long pontoon float runs along each side of the body, level with its
middle. The boss is a 3 L boss (its radius is 1.5 L).

**Acceptance criteria**
- Given the dev bosses viewer, when the Croc is shown, then it reads as a crocodile-shaped gunboat
  with two side floats, its jaws at the front (manual).

*Sources: P09-R09.*

#### MB-MANGROVE-CROC-02 — Cyber-Organic body · MUST

Its body is a living crocodile's (Cyber-Organic): a swollen, moss-skinned body of dark jungle-green
flesh, with grafted metal on it. The hover skirt is a grafted metal belly with a mud-coloured rim.
A pulsing vein runs down its spine under bone rib arches. Rows of armour scutes run either side of
the spine. The head has two bulging flesh eye sockets, each holding a gland under a neon slit, a
brow ridge, and nostrils at the snout. Its two reactors sit in flesh sacs at the tail. Metal plates
and pylons on its flanks carry the pontoons. The head and the back's growth lie on the back plating
(MB-MANGROVE-CROC-13), the ring dome on the hump behind it.

**Acceptance criteria**
- Given the model, then its body is drawn in the flesh layer with grafted hull pieces (skirt, scutes,
  plates), and it reads as one creature (manual).

*Sources: P16-R05.*

#### MB-MANGROVE-CROC-03 — Parts on the model · MUST

Each destroyable part is drawn where it sits in the design (see Tunable values), with a clear
outline:
- the **jaw cannon** in the throat between the jaws: a ribbed housing with a neon collar, its barrel
  reaching for the jaws' tips, a charge light glowing in its maw, a throat gland fed by veins
  swelling behind it;
- the two **pontoons**: long float-bladders ridged like a crocodile's flank and plated at their bow,
  their twin fan guns at the bow, a green neon stripe along the outer side, moss on the back and a
  vine trailing from each.

A destroyed part is hidden and leaves nothing in its place; the jaws stay, as they belong to the
core.

**Acceptance criteria**
- Given the dev viewer, when K destroys the parts one by one, then each part's model disappears
  and the jaws keep moving (manual; `test_boss_models.py` checks every part is drawn).

*Sources: P09-R09, P16-R05, D-225, D-167.*

#### MB-MANGROVE-CROC-04 — Jaws that open and close · MUST

The two jaws are moving limbs on hinges either side of the throat, 7 px out and 27 px ahead of the
centre. Each jaw is an armoured flesh wedge, wide at its hinge and tapering to its tip, with a row
of bone fangs along its inner edge, a metal plate grafted on its back, green neon along its outer
edge and moss on top. Drawn half open, each swings 9° either way (from shut to wide open) once every
2.4 s, the left one opening clockwise on screen and the right one the mirror way.

**Acceptance criteria**
- Given the boss is in place, then the jaws open and close together every 2.4 s (manual, dev
  viewer).

*Sources: P09-R09, D-081, D-061.*

#### MB-MANGROVE-CROC-05 — River growth · MUST

As every World 3 boss, its dark metal and flesh carry the World 3 growth: moss patches on its back
and on its jaws and pontoons, vines hanging from the body to the pontoon pylons, mossy river stones
set into its hull, and a vent on its back. The moss is a clear green and the mud a grey (no olive or
brown).

**Acceptance criteria**
- Given the model, then moss, vines and stones are visible on its back and floats (manual).

*Sources: P09-R09, D-231.*

#### MB-MANGROVE-CROC-06 — Lights and colours · MUST

Its neon is its own green (`mangrove-croc`), shown bright green under the enemy colour rule (see
[readability](../../graphics/readability.md)). Neon lines its hull's chines from tail to head, the
eye slits, the jaws' outer edges, the pontoons' outer sides and the ring round its back dome. White
charge lights sit on the brow, on top of the back dome and at the barrels' mouths; they strobe and
flicker as the [common](../common.md) stage and rage rules say.

**Acceptance criteria**
- Given the model, then every neon light is bright green (unit: enemy colour family tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### MB-MANGROVE-CROC-07 — Entry, place and ground speed · MUST

The Croc comes in from above the top edge and stops at 0.72 of the playfield's height. In place it
sways up to 70 px either side over 7 s and bobs 8 px over 3.4 s. While it is fought the ground runs
at ×1.4 the level's speed: a chase, the only one in World 3.

**Acceptance criteria**
- Given the fight starts, then the ground speeds up to ×1.4 and the boss stops at 0.72 of the
  playfield height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P09-R09.*

#### MB-MANGROVE-CROC-08 — Parts and health · MUST

The Croc has a core (hit radius 15 px, 1 450 HP) and three original parts: two pontoons (12 px,
625 HP each) that shield the core, and the jaw cannon (10 px, 500 HP) that does not. Its full health
is 3 200 HP with the original parts, 4 200 HP with its two hidden gatlings (500 HP each), which
count in the health bar from the start.

**Acceptance criteria**
- Given the design, then it has exactly three original parts and two hidden ones, and only the
  pontoons and the gatlings shield the core (unit: `test_mangrove_croc.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### MB-MANGROVE-CROC-09 — Part weapons · MUST

While they stand, in every stage:
- the jaw cannon fires aimed bursts of 3 `green` bullets (205 px/s, 0.14 s apart) every 2.4 s,
  first 1.2 s into a stage;
- each pontoon fires a fan of 3 `orange` bullets (195 px/s, 14° apart) every 2.8 s from its twin
  bow guns, the left one leaning 12° one way, the right one 12° the other, 1.4 s apart.

**Acceptance criteria**
- Given the jaw cannon stands, then it fires its bursts from its barrel's tip in the throat (unit:
  design guns).

*Sources: P09-R09, D-081.*

#### MB-MANGROVE-CROC-10 — Jaws in time with the bursts · SHOULD

The jaws' swing is timed from the boss's entry (about 4.3 s) so that they are wide open at the
middle of each jaw-cannon burst in the first stage. Later stages restart their volleys at a stage
change, so the jaws and the bursts may drift apart after the first part is destroyed.

**Acceptance criteria**
- Given stage 0, then the jaws are at their widest in the middle of each burst (manual).

*Sources: P09-R09, D-081.*

#### MB-MANGROVE-CROC-11 — Core patterns by stage · MUST

The core fires from the ring dome on its back, a new pattern at each stage (stage k: k original parts
destroyed):
- stage 0: a ring of 10 `blue` bullets (192 px/s) every 3 s, turning 18° each time;
- stage 1: a ring of 12 `blue` every 2.5 s, turning 15°;
- stage 2: two rings of 10 every 2.4 s, one `blue` and one `purple` (200 px/s) turned 18°, 1.2 s
  apart;
- stage 3 (alone): a fast spiral (rings of 4 `green` every 0.42 s, turning 23°) over a slow ring of
  14 `purple` every 2.6 s, turning 7°.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, and the last stage's spiral
  is used by no earlier stage (unit: `test_mangrove_croc.py`).

*Sources: P09-R09, D-081.*

#### MB-MANGROVE-CROC-12 — Rage · MUST

After the pause that follows each destroyed part, the Croc is angry: it fires a vortex (one
fast-turning spiral and bursts at the player) at heat 4.5, in `green` and `orange`, the coolest
rage of World 3.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the vortex for the rage
  time (unit: rage patterns built from `boss_rage`).

*Sources: D-081, D-063.*

#### MB-MANGROVE-CROC-13 — Transformation: back plating bursts off · MUST

The Croc transforms once, when half of its original parts (2 of 3) are destroyed. Its back plating
bursts off ([common](../common.md), BOSS-42): a ridged carapace drawn as a piece of its own over the
flattened keel, from just under the keel's top (3.3 px) up to the hull's back (10.5 px at its
widest, 6 px at the snout), from 8 px behind the centre (just ahead of the ring dome's hump) to the
snout, 30 px ahead. It carries the head (the eye sockets and their neon slits, the brow ridge, the
nostrils), the chines and spine along it and the back's growth (scutes, moss, a river stone, the
vent); the ring dome stays on the keel's hump behind it. Its region (`back`, one across the centre
line) is the carapace's own plan, the hull's taper from 17 px either side at its rear to 7.5 px at
the snout; it bursts into plates cracked from that outline and leaves a dark metal `shell` frame (a
lattice) on the keel. The boss stays one object at rest and after its transformation.

**Acceptance criteria**
- Given two original parts are destroyed, then the boss transforms once and its back region bursts
  off, leaving the shell frame (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given its model, then it draws the back region's armour, and the boss holds together with and
  without it (unit: `test_boss_52_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227, D-254.*

#### MB-MANGROVE-CROC-14 — Hidden weapons: two gatlings · MUST

The transformation reveals two gatling turrets at 9 px either side of the centre line, 15 px ahead
of the centre (radius 7 px, pods 13.1 px high, 500 HP each, 30 % drop chance), which shield the core
and fire `orange` bursts as every gatling does (see [common](../common.md)), the left one 1.2 s and
the right one 2.0 s into a stage. The Croc fires no less once it has transformed than before.

**Acceptance criteria**
- Given the transformation is over, then both gatlings are live targets that fire (unit:
  `test_boss_kinds.py` escalation and weapon checks).

*Sources: D-221, D-229.*

#### MB-MANGROVE-CROC-15 — Points and drops · MUST

Destroying the Croc scores 7 500 points, and each part destroyed 750. Its original parts drop a
bonus half of the time, its hidden weapons 30 % of the time; its core drops one by the game's rule.

**Acceptance criteria**
- Given the jaw cannon is destroyed, then the score rises by 750 (unit: scoring rule, design
  values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/mangrove_croc.py` (`MANGROVE_CROC`) unless noted. Px from the
boss's centre, X right, Y up the screen (its nose at -Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (radius 51 px) | `stats.size` |
| core | radius 15 px, 1 450 HP | `coreRadius`, `coreHealth` |
| pontoons | (±27, 4), radius 12, 625 HP, shield | `CROC_PARTS.pontoon` |
| jaw cannon | (0, -37), radius 10, 500 HP, no shield | `CROC_PARTS.jaw` |
| full health | 3 200 (4 200 with hidden weapons) | P09-R10 band (original parts) |
| stop / sway / bob | 0.72 / 70 px, 7 s / 8 px, 3.4 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×1.4 | `groundSpeed` |
| jaws | hinge (±7, -27), tip (±5, -53); ±9°, 2.4 s, entry 4.28 s | `CROC_JAW`, `CROC_JAW_SWING` |
| jaw burst | 3 shots, 0.14 s apart, every 2.4 s, first 1.2 s | `BURST` |
| pontoon fans | 3 × 14°, every 2.8 s, lean ±12° | stage volleys |
| bullets | `green` 205, `orange` 195, `blue` 192, `purple` 200 px/s | radius 4 |
| rage | vortex, heat 4.5 | `rage.vortex` |
| transformation | once, at 2 parts destroyed | `boss_build.default_transforms` |
| back region | the carapace's plan: x ±17 at y 8, ±15 at y -10, ±11 at y -22, ±7.5 at y -30, `shell`, not mirrored; plating 3.0–10.5 px over the keel (top 3.3) | `armour_region("back", …)`; `mangrove_croc_model.py` `KEEL`, `PLATING` |
| gatlings | (±9, -15), radius 7, pod 13.1, 500 HP, `orange`, first 1.2 / 2.0 s | `hidden_weapon` |
| points | 7 500 (750 a part) | `points`, `boss_part_points` |
| neon | [0.25, 1, 0.3] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["mangrove-croc"]` |

## Notes

- Phase 9 fight time with the D-055 bot (guns level 3, always on target): 41.6 s, before the hidden
  weapons were added (D-221), which made the fight longer.
- The Croc was built as "a chase up the delta"; World 3 has no sea or delta any more (D-111), so it
  now chases up the canal works.
