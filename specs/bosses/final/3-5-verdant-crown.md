# Verdant Crown (3-5 final boss)

> **Area:** bosses · **Prefix:** `FB-VERDANT-CROWN` · **Related:** [common boss rules](../common.md),
> [3-5 Garden villages](../../worlds/world-3/3-5-garden-villages.md),
> [World 3](../../worlds/world-3/world.md), [Jaguar](../mini/3-5-jaguar.md),
> [readability](../../graphics/readability.md)

The Verdant Crown is the final boss of level 3-5 and World 3's last boss, met at the level's end. It
is a city-ship 6 L across, a colossal living plant-beast: an overgrown deck carrying a glass garden
dome over its core, a city of overgrown towers round the dome, two thorn cannons on outriggers, two
seed batteries aft, two root generators ahead that shield the core, and a gun deck on its bow. Its
core fires every kind of attack. It was designed as the old Jungle world's canopy city and, since
World 3 became the factories-to-garden-villages world (D-111), it keeps its name and look and flies
over the garden villages under the night rain. It transforms twice. Shared rules are in
[bosses/common.md](../common.md); this file only gives what is the Crown's own.

## Requirements

### Look

#### FB-VERDANT-CROWN-01 — Silhouette · MUST

Seen from above, the Crown is a broad deck, bow down the screen, with the round glass dome (31 px in
radius) at its centre, a gun deck on its bow (about 80 px ahead of the centre), an engine block across
its stern, and an outrigger out from each side to a thorn cannon's turntable 82 px out. It is a 6 L
boss (radius 3 L).

**Acceptance criteria**
- Given the dev bosses viewer, then it reads as a flying city round a glass dome, with an outrigger
  each side (manual).

*Sources: P09-R09.*

#### FB-VERDANT-CROWN-02 — Cyber-Organic body · MUST

It reads as one living plant-beast with a city grafted on it: its deck a broad body of moss-skinned
flesh, its outriggers fleshy limbs ending in swollen knuckles under the grafted turntables, and veins
pulsing out from under the dome across the deck. The stone plating over its flank and aft decks,
carrying part of the city, is the armour it sheds (FB-VERDANT-CROWN-12, FB-VERDANT-CROWN-13).

**Acceptance criteria**
- Given the model, then the deck and outriggers read as living flesh carrying the city (manual).

*Sources: P16-R06.*

#### FB-VERDANT-CROWN-03 — Garden dome and city · MUST

The glass garden dome over the core is a lattice of 8 dark ribs up to an oculus, glowing mullions
round it and a lit rim, with a garden of trees inside (trunks and faceted crowns of leaves, a flower
or two in them). The tallest tree rises through the oculus; its bloom, 44 px high, is the core's ring
emitter. Round the dome stands a city of overgrown towers: chamfered blocks with lit windows (a few
dark), moss on their roofs and vines up their sides, with moss patches and vines across the deck.

**Acceptance criteria**
- Given the model, then the dome shows its lattice and trees, the great tree rising through its top,
  towers round it (manual).

*Sources: P09-R09.*

#### FB-VERDANT-CROWN-04 — Bow and hatches · MUST

The gun deck on its bow carries twin cannons (8 px either side, 82 px ahead) and, between them, a
laser lens (86 px ahead), charging before they fire. Behind the dome, a block holds its four missile
hatches (7 px either side, 48 and 56 px behind the centre), lit as missiles load.

**Acceptance criteria**
- Given the model, then the cannons, the lens and the hatches stand at the design's muzzles (unit:
  `test_boss_models.py`).

*Sources: P09-R09.*

#### FB-VERDANT-CROWN-05 — Parts on the model · MUST

- Each **thorn cannon** (a part) turns on its outrigger's turntable (a low drum ringed with neon): a
  mossy pod crowned with spikes, a long barrel bristling with thorns, its lens glowing as its laser
  charges.
- Each **seed battery** (a part) is a living seed pod of dark flesh lying on the deck, mossy and
  armoured, with six grafted hatches lit as its missiles load, neon strips down its sides and leaves
  sprouting at its ends.
- Each **root generator** (a part, no weapon) is a glowing seed on a stone pedestal, gnarled roots of
  living sinew arching from it into the deck, a neon ring round its foot.

A destroyed part is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given K destroys a root generator, then the seed, its pedestal and its roots disappear (manual).

*Sources: P09-R09, P16-R06, D-225, D-167.*

#### FB-VERDANT-CROWN-06 — Lights and colours · MUST

Its neon is its own emerald (`verdant-crown`) and a magenta: under the enemy colour rule the emerald
shows bright green and the magenta bright yellow. The deck's lit rim, the veins, the dome's mullions
and foot, the lines along the thorn pods and the root generators' rings are emerald; the oculus rim,
the outriggers' edges, the bow's strip, the thorn crowns, the turntables' rings, the seed batteries'
strips, the root seeds and the dome's flowers are magenta. Its lasers are drawn in its own neon, moved
into the enemy shots' colours (see [common](../common.md)).

**Acceptance criteria**
- Given the model, then every neon light is bright green or bright yellow (unit: enemy colour family
  tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### FB-VERDANT-CROWN-07 — Entry, place and ground speed · MUST

The Crown stops at 0.75 of the playfield's height, sways up to 25 px either side over 11 s and bobs
6 px over 5 s. While it is fought the ground runs at ×0.25, the slowest of the World 3 fights that
keep the ground moving.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.25 (design values; common rule tests).

*Sources: P09-R09.*

#### FB-VERDANT-CROWN-08 — Parts and health · MUST

The core (hit radius 26 px, 6 900 HP) has six original parts: two thorn cannons (15 px, 2 100 HP each)
and two seed batteries (14 px, 1 900 HP each), which do not shield the core, and two root generators
(14 px, 2 300 HP each), which do. The root generators stand 64 px apart so that a ship's spread can
reach them. Its full health is 19 500 HP with the original parts, 27 780 HP with its four hidden
weapons: the highest of World 3.

**Acceptance criteria**
- Given the design, then it has six original parts and four hidden ones, and of the original parts
  only the root generators shield the core (unit: `test_verdant_crown.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### FB-VERDANT-CROWN-09 — Part weapons · MUST

While they stand, in every stage:
- each thorn cannon fires a laser (1.6 s) every 6 s from its lens, the two 3 s apart; its turret turns
  to aim at the player during the warning line and holds still while the beam fires;
- each seed battery fires 2 homing missiles (24° apart) every 5 s, the two 2.5 s apart;
- the root generators fire nothing.

**Acceptance criteria**
- Given a thorn cannon's warning line shows, then it follows the player at the laser turret rate (unit:
  turret rules; design guns).

*Sources: P09-R09, D-073.*

#### FB-VERDANT-CROWN-10 — Core patterns by stage: every attack kind · MUST

The core fires every kind of attack, a new one at each stage, from its bow cannons, its lens, its
hatches and its bloom. A seed pod is a slow, big `green` bullet (115 px/s, radius 7 px) that bursts
into a ring of 8 small `magenta` ones (190 px/s) 1.1 s after it is fired.
- stage 0: bursts of 4 `magenta` (210 px/s, 0.12 s apart) every 2.4 s;
- stage 1: a fan of 5 `green` (205 px/s, 13° apart) every 2.3 s;
- stage 2: an aimed seed pod every 3 s, and 3 aimed `purple` (200 px/s, 10° apart) every 2.2 s;
- stage 3: 2 homing missiles every 4.5 s, and bursts of 3 `green` every 2.2 s;
- stage 4: a laser (1.4 s) every 5 s, and a fan of 7 `magenta` (11° apart) every 2.3 s;
- stage 5: a ring of 12 `green` every 1.8 s, and an aimed seed pod every 2.6 s;
- stage 6 (alone): all of them at once with a spiral of its own: rings of 16 `magenta` every 1.1 s
  turning 10°, a laser every 5 s, 2 missiles every 5.5 s, a fan of 3 seed pods (30° apart) every 3 s,
  and bursts of 3 `purple` every 2.6 s.

**Acceptance criteria**
- Given the design, then it has seven stages, bullets, seed pods, missiles and lasers among them, and
  the last one's spiral is used by no earlier stage (unit: `test_verdant_crown.py`).

*Sources: P09-R09, D-081.*

#### FB-VERDANT-CROWN-11 — Rage · MUST

After the pause that follows each destroyed part, it fires a flower and two crossing spirals together,
each at half the rate, at heat 9 (`green` and `magenta`, `magenta` and `purple`): the hottest rage of
World 3.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the flower and the spirals
  (unit: rage patterns).

*Sources: D-081, D-063.*

#### FB-VERDANT-CROWN-12 — First transformation: flank armour, two orbs · MUST

At 2 of its 6 original parts destroyed, it transforms for the first time. Its **flank plating**
bursts off ([common](../common.md), BOSS-42): a plate of old stone drawn apart from the deck, lying on
each flank's deck from 5.7 px (sunk into the deck at 6) up to 7.2 px, from the dome's rim (34 px out)
to the deck's edge (61 px), from 24 px behind the centre to 50 px ahead, clear of the root generator
ahead of it; the three towers of the city there (at (44, -30), (52, 4) and (56, -20)), two moss
patches and a vine stand on it. Its region (`flanks`, mirrored) is that plate's plan; it bursts into
plates cracked from the outline and leaves a dark metal `wing` frame on the deck. Two orbs come out
at 47 px either side, 17 px ahead of the centre (radius 11 px, pods 11 px high, 1 840 HP each),
firing `green` rings, 1.2 s and 2.0 s into a stage.

**Acceptance criteria**
- Given 2 original parts are destroyed, then both flank regions burst off and the two orbs come out and
  fire (unit: `test_boss_kinds.py`).

*Sources: D-221, D-224, D-229, D-227, D-254.*

#### FB-VERDANT-CROWN-13 — Second transformation: spine plating, two mortars · MUST

At 4 original parts destroyed, it transforms again. Its **spine plating** aft of the dome bursts off:
a plate drawn apart over the aft deck, from 5.7 to 7.2 px, 32 px either side of the centre line from
36 px behind the centre, narrowing to 24 px at the deck's tail (85 px), round the missile hatches'
block (which stays, the core's); the two towers of the city there (at (±20, 40) and (±18, 76)) and a
moss patch stand on it. Its region (`spine`, not mirrored) is that plate's plan; it leaves a `shell`
frame on the deck. Two flak mortars come out at 13 px either side, 69 px behind the centre (radius
11 px, pods 11 px high, 2 300 HP each), lobbing `green` flak, 1.2 s and 2.0 s into a stage. It reveals no kind twice, fires no less after each transformation than before, and stays one
object in every state.

**Acceptance criteria**
- Given 4 original parts are destroyed, then the spine region bursts off and the two mortars come out
  (unit: `test_boss_kinds.py`).
- Given each state, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-229, D-227, D-254.*

#### FB-VERDANT-CROWN-14 — Points and drops · MUST

Destroying the Crown scores 22 000 points, and each part destroyed 2 200. Its original parts drop a
bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.

**Acceptance criteria**
- Given the core is destroyed, then a bonus drops and the score rises by 22 000 (unit: scoring and
  bonus rules, design values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/verdant_crown.py` (`VERDANT_CROWN`) unless noted. Px from the
boss's centre, X right, Y up the screen (its bow at -Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 6 L (radius 102 px) | |
| dome | radius 31 px, 8 ribs; bloom 44 px high | `src/game/view/bosses/world_3/verdant_crown_garden.py` `DOME`; `VERDANT_BLOOM` |
| core | radius 26 px, 6 900 HP | |
| thorn cannons | (±82, -6), radius 15, 2 100 HP, no shield; lenses (±82, -40), 9 px high | `VERDANT_PARTS.thorn`, `VERDANT_THORN` |
| seed batteries | (±52, 40), radius 14, 1 900 HP, no shield; 6 cells each | `VERDANT_PARTS.seed`, `VERDANT_SEEDS` |
| root generators | (±32, -48), radius 14, 2 300 HP, shield | `VERDANT_PARTS.root` |
| full health | 19 500 (27 780 with hidden weapons) | P09-R10 band |
| stop / sway / bob | 0.75 / 25 px, 11 s / 6 px, 5 s | |
| ground speed | ×0.25 | |
| thorn lasers | 1.6 s every 6 s, first 2 / 5 s | on turrets |
| seed missiles | 2 × 24°, every 5 s, first 3.5 / 6 s | |
| seed pod | `green` 115 px/s, radius 7, bursts after 1.1 s into 8 `magenta` at 190 px/s | `SEED_POD` |
| rage | flower + spirals, heat 9, half share each | |
| transformations | at 2 and 4 parts destroyed | `default_transforms` |
| flank regions | the flank deck's plan, x 34..61, y -50..24 (mirrored), `wing`; plating 5.7–7.2 px | form 1 |
| spine region | the aft deck's plan, x ±32 at y 36 to ±24 at y 85, `shell`; plating 5.7–7.2 px | form 2 |
| orbs | (±47, -17), radius 11, pod 11, 1 840 HP, `green` | form 1 |
| mortars | (±13, 69), radius 11, pod 11, 2 300 HP, `green` | form 2 |
| points | 22 000 (2 200 a part) | |
| neon | emerald [0.1, 1, 0.45]; magenta | `BOSS_LOOK.neon["verdant-crown"]`; `verdant_crown_garden.py` `MAGENTA` |

## Notes

- Phase 9 fight time with the D-055 bot: 127.1 s, before the hidden weapons were added (D-221).
