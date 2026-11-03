# Dam Breaker (3-4 final boss)

> **Area:** bosses · **Prefix:** `FB-DAM-BREAKER` · **Related:** [common boss rules](../common.md),
> [3-4 Suburbs](../../worlds/world-3/3-4-suburbs.md), [World 3](../../worlds/world-3/world.md),
> [Mosquito](../mini/3-4-mosquito.md), [Hornet](../../enemies/hornet.md),
> [readability](../../graphics/readability.md)

The Dam Breaker is the final boss of level 3-4, met at the level's end. It is a giant armoured barge
5.5 L across, a bloated swamp beast wallowing like a barge: sluice gate houses either side of its bow
letting out waves of sludge, glowing chemical tanks on outriggers at its sides that burst into rings
when destroyed, an armour plate and a drone hangar on its bow, a pump house and its stack amidships.
It was designed for the old Jungle world's swamp and its giant dam and, since World 3 became the
factories-to-garden-villages world (D-111), it keeps its name and look and floats over the suburbs.
It transforms twice. Shared rules are in [bosses/common.md](../common.md); this file only gives what
is the Dam Breaker's own.

## Requirements

### Look

#### FB-DAM-BREAKER-01 — Silhouette · MUST

Seen from above, the Dam Breaker is a long, flat barge, bow down the screen: a hull about 116 px wide
and 146 px long with a rounded bow and a blunt stern, the pump house and its stack amidships, two
sluice gate houses either side of the bow, the armour plate and the hangar on the bow's centre line,
and a chemical tank on an outrigger out from each side (76 px out). It is a 5.5 L boss (radius
2.75 L).

**Acceptance criteria**
- Given the dev bosses viewer, then it reads as a heavy barge with side tanks (manual).

*Sources: P09-R09.*

#### FB-DAM-BREAKER-02 — Cyber-Organic body · MUST

It reads as one bloated swamp beast: a broad back of moss-skinned flesh with rusty plates, sluices
and tanks grafted on and veins of toxin pulsing through it; the plates over its flank and bow decks
are the armour it sheds (FB-DAM-BREAKER-11, FB-DAM-BREAKER-12). The pump house is a swollen hump of flesh
over bone ribs with its stack grafted on, its windows lighting up as it charges. At the stern are
three reactors, a rudder housing and the pistons of its dam-breaking ram.

**Acceptance criteria**
- Given the model, then the barge reads as one creature, not parts on a box (manual).

*Sources: P16-R06.*

#### FB-DAM-BREAKER-03 — Parts on the model · MUST

- Each **sluice cannon** (a part) is a gate house on the deck: a gland swelling out of the beast's
  back with a metal sluice gate grafted in its mouth, raised over a chute whose lip lets out the
  sludge, a dark culvert under it, a hand wheel on top and a glow inside.
- Each **chemical tank** (a part) is a fat capsule lying along the barge on cradles at its side, a
  bloated toxin bladder glowing through bands of glass, hooped with rusty straps, vines hanging off
  it, an outrigger beam back to the hull.
- The **armour plate** (a part, no weapon) is a thick, sloped, chamfered slab bolted over the bow,
  with hazard stripes along its front edge, lit slits and moss in its seams.
- The **drone hangar** (a part) is a bay at the bow, a brood pouch of flesh whose open, grafted metal
  door is framed in neon; its Hornets leave from it.

A destroyed part is hidden; a dark socket is left on the deck where each sluice and tank stood.

**Acceptance criteria**
- Given K destroys a tank, then the tank disappears and its socket and outrigger show (manual).

*Sources: P09-R09, P16-R06, D-225, D-167.*

#### FB-DAM-BREAKER-04 — Swamp growth · MUST

Moss lies on its ledges and seams, vines hang over its sides and from its tanks, and rust patches
mark its plates: the World 3 growth over its dark metal and flesh, the moss and vines clear greens.

**Acceptance criteria**
- Given the model, then moss, vines and rust are visible (manual).

*Sources: P09-R09, D-231.*

#### FB-DAM-BREAKER-05 — Lights and colours · MUST

Its neon is its own toxic green (`dam-breaker`), on the green side of the enemy colours as its hull is
overgrown with moss: the hull's lit rim, the tanks' glass bands, the sluices' glow, the plate's slits
and the hangar's door frame. White charge lights glow in the pump house's windows, at its twin guns
and at the top of the stack.

**Acceptance criteria**
- Given the model, then every neon light is bright green (unit: enemy colour family tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### FB-DAM-BREAKER-06 — Entry, place and ground speed · MUST

The Dam Breaker stops at 0.74 of the playfield's height, sways up to 32 px either side over 11 s and
bobs 5 px over 5.5 s. While it is fought the ground runs at ×0.3.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.3 (design values; common rule tests).

*Sources: P09-R09.*

#### FB-DAM-BREAKER-07 — Parts and health · MUST

The core (hit radius 22 px, 5 300 HP) has six original parts: two sluice cannons (15 px, 1 650 HP
each) and the armour plate (15 px, 1 900 HP), which shield the core; two chemical tanks (15 px,
1 300 HP each) and the drone hangar (14 px, 900 HP), which do not. Its full health is 14 000 HP with
the original parts, 20 840 HP with its four hidden weapons.

**Acceptance criteria**
- Given the design, then it has six original parts and four hidden ones, and only the sluices, the
  plate and the hidden weapons shield the core (unit: `test_dam_breaker.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### FB-DAM-BREAKER-08 — Part weapons, Hornets and tank rings · MUST

While they stand, in every stage:
- each sluice lets out waves of sludge from its spout every 4 s: a row of 5 slow, big globs (`green`,
  125 px/s, radius 7 px, 15° apart), then 0.55 s later a row of 4 between them, the left sluice 2 s
  before the right one;
- the hangar launches 2 [Hornets](../../enemies/hornet.md) every 7 s, the first 3.5 s into a stage;
- the armour plate fires nothing.

When a chemical tank is destroyed it bursts into a ring of 12 `green` bullets (190 px/s), once.

**Acceptance criteria**
- Given a tank is destroyed, then a ring of 12 bullets leaves it once (unit: `test_world_boss.py`
  break-ring rule; design values).

*Sources: P09-R09, D-081.*

#### FB-DAM-BREAKER-09 — Core patterns by stage · MUST

The core fires from the twin guns on the pump house's front and the top of its stack, a new pattern at
each stage:
- stage 0: one aimed `red` bullet (205 px/s) every 2.8 s;
- stage 1: an aimed spread of 3 `red` (12° apart) every 2.4 s;
- stage 2: bursts of 4 `orange` (195 px/s, 0.13 s apart) every 2.4 s;
- stage 3: a fan of 5 `magenta` (200 px/s, 14° apart) every 2.4 s;
- stage 4: a fan of 7 `magenta` (12° apart) every 2.2 s, and bursts of 3 `red` every 2.8 s;
- stage 5: a ring of 10 `green` (190 px/s) every 1.8 s turning 7°, and an aimed `red` every 2.6 s;
- stage 6 (alone): two spirals of 14 every 1.3 s turning opposite ways (`green` 9°, `orange` -11°).

**Acceptance criteria**
- Given the design, then it has seven stages and the last one's twin spirals are used by no earlier
  stage (unit: `test_dam_breaker.py`).

*Sources: P09-R09, D-081.*

#### FB-DAM-BREAKER-10 — Rage · MUST

After the pause that follows each destroyed part, it fires a curtain at heat 8, in `green` and
`orange`.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the curtain (unit: rage
  patterns).

*Sources: D-081, D-063.*

#### FB-DAM-BREAKER-11 — First transformation: flank armour, two batteries · MUST

At 2 of its 6 original parts destroyed, it transforms for the first time. Its **flank plating**
bursts off ([common](../common.md), BOSS-42): a plate of rusty metal drawn apart from the hull, lying
on each flank's deck from 3.7 px (sunk into the deck at 4) up to 5.2 px, from the sluice mounts (7 px
behind the centre) back to the stern (70 px), from 30 px out to the deck's edge (56 px), carrying the
deck's cross seams, a rusty patch and moss. Its region (`flanks`, mirrored) is that plate's plan; it
bursts into plates cracked from the outline and leaves a dark metal `wing` frame on the deck. Two gun
batteries come out at 50 px either side, 41 px behind the centre (radius 12 px, pods 9.4 px high,
1 520 HP each), firing `green` fans straight down, 1.2 s and 2.0 s into a stage.

**Acceptance criteria**
- Given 2 original parts are destroyed, then both flank regions burst off and the two batteries come
  out and fire (unit: `test_boss_kinds.py`).

*Sources: D-221, D-224, D-229, D-227, D-254.*

#### FB-DAM-BREAKER-12 — Second transformation: wing armour, two missile racks · MUST

At 4 original parts destroyed, it transforms again. Its **wing plating** bursts off: a plate drawn
apart on each side of the bow's deck, from 3.7 to 5.2 px, beside the armour plate and the hangar
(from 14 px out) to the deck's edge (56 px), from 21 to 71 px ahead of the centre, carrying the bow
seam and moss. Its region (`wings`, mirrored) is that plate's plan; it leaves a `wing` frame on the
deck. Two missile racks come out at 34 px either side, 55 px ahead (radius 12 px, pods 9.4 px high,
1 900 HP each), each firing 2 homing missiles every 6 s, 1.2 s and 2.0 s into a stage.
It reveals no kind twice, fires no less after each transformation than before, and stays one object
in every state.

**Acceptance criteria**
- Given 4 original parts are destroyed, then both wing regions burst off and the two racks come out
  (unit: `test_boss_kinds.py`).
- Given each state, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-229, D-227, D-254.*

#### FB-DAM-BREAKER-13 — Points and drops · MUST

Destroying the Dam Breaker scores 15 000 points, and each part destroyed 1 500. Its original parts
drop a bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.

**Acceptance criteria**
- Given the core is destroyed, then a bonus drops and the score rises by 15 000 (unit: scoring and
  bonus rules, design values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/dam_breaker.py` (`DAM_BREAKER`) unless noted. Px from the
boss's centre, X right, Y up the screen (its bow at -Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 5.5 L (radius 93.5 px) | |
| hull | ±58 px across, bow -74 to stern 72 | `src/game/view/bosses/world_3/dam_breaker_model.py` `HULL` |
| core | radius 22 px, 5 300 HP | |
| sluices | (±46, -22), radius 15, 1 650 HP, shield; spouts (±46, -38) | `DAM_SLUICE`, `DAM_SPOUT` |
| plate | (0, -32), radius 15, 1 900 HP, shield, no weapon | `DAM_PLATE` |
| tanks | (±76, 14), radius 15, 1 300 HP, no shield; ring of 12 when destroyed | `DAM_TANK`, `breakRings` |
| hangar | (0, -58), radius 14, 900 HP, no shield; 2 Hornets every 7 s, first 3.5 s | `DAM_HANGAR`, `launches` |
| full health | 14 000 (20 840 with hidden weapons) | P09-R10 band |
| stop / sway / bob | 0.74 / 32 px, 11 s / 5 px, 5.5 s | |
| ground speed | ×0.3 | |
| sludge | `green` 125 px/s, radius 7; 5 then 4 globs × 15°, every 4 s | `SLUDGE`, `waves` |
| rage | curtain, heat 8 | |
| transformations | at 2 and 4 parts destroyed | `default_transforms` |
| flank regions | the flank deck's plan, x 30..56, y 7..70 (mirrored), `wing`; plating 3.7–5.2 px | form 1 |
| wing regions | the bow deck's plan, x 14..56, y -71..-21 (mirrored), `wing`; plating 3.7–5.2 px | form 2 |
| batteries | (±50, 41), radius 12, pod 9.4, 1 520 HP, `green` | form 1 |
| missile racks | (±34, -55), radius 12, pod 9.4, 1 900 HP | form 2 |
| points | 15 000 (1 500 a part) | |
| neon | [0.3, 1, 0.1] (a lime, red 0.6, before D-231) | `BOSS_LOOK.neon["dam-breaker"]` |

## Notes

- Phase 9 fight time with the D-055 bot: 115.2 s, before the hidden weapons were added (D-221).
