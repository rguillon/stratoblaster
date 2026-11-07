# Mortar Raft

> **Area:** bosses · **Prefix:** `MB-MORTAR-RAFT` · **Related:** [common](../common.md),
> [Star Fort](L-25-star-fort.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Mortar Raft is the mini boss of Lab level L-25: a gigantic flying raft about 3.6 L across, an
old barge hull lashed to a jumble of pontoons and a second, boxy hull section, plank decks over
them, deck shacks, cargo under nets, a mast with a patched sail and a dozen small lift propellers
round its edges. Nothing on it matches its other side. It comes in with only three guns (a row of
two fixed mortar tubes on its forward hull section, a turret by its wheelhouse) and every part it
loses uncovers more from under its tarpaulins. Once two parts are lost, the lashings of its stern
outriggers snap and the two pontoons swing out like gates, a missile rack riding each. Shared rules
are in [common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "10 more gigantic flying fortress, add non rotating guns too, don't
add too many start guns, 3 max, then more appear when they are destroyed") this Lab boss is a built
flying thing, not a creature: rusty dark metal, timber, canvas, rope and neon lights, no flesh,
eyes or veins.

## Requirements

### Look

#### MB-MORTAR-RAFT-01 — Silhouette and size · MUST

Seen from above, its nose down the screen, it is a lopsided raft about 3.6 L across: the barge hull
down its middle a little to the left (y -48 to 44), two pontoons under a plank deck on its left (out
to x -38), a pontoon under a little deck on its right, a boxy hull section lashed on its right bow
(x 17 to 40, y -52 to -20), and two outrigger pontoons along its stern quarters (x ±19 to ±29,
y 24 to 60). Once transformed its outriggers stand splayed out behind it like a swallow's tail.

**Acceptance criteria**
- Manual validation in the boss viewer: a raft of lashed hulls, irregular, no side matching the
  other; its stern outriggers splayed out once it has transformed.

*Sources: Lab boss request (2026-11-06, "gigantic flying fortress").*

#### MB-MORTAR-RAFT-02 — Body · MUST

The barge hull is a scarped slab of dark plating with seams, hatch covers, bollards and a lit line
along each gunwale, a deckhouse aft and a little shed forward left. The pontoons are riveted drums
with rounded ends, rope lashings and a lit band; the plank decks are timber, their planks' joints
dark, cargo crates under rope nets on them. The forward hull section is lashed to the barge by
ropes over timber fenders, the right pontoon's deck by two timber beams. Nine small ducted lift
propellers on arms round its edges (two more on each outrigger) spin all the time.

**Acceptance criteria**
- Manual validation: one built raft of metal, timber, canvas and neon lines; no creature
  features; the propellers spin.

*Sources: BOSS-49, BOSS-52; departure from BOSS-47 above.*

#### MB-MORTAR-RAFT-03 — Its parts and guns · MUST

Its 3 parts, each with its own glowing edge trim (BOSS-48):
- the **mortar emplacement** on its forward hull section (centre (28.5, -36), radius 12): a U of
  blast walls round its two **fixed mortar tubes** (mounts `mortar-1`, `mortar-2` at (23, -44) and
  (34, -44) on the section's deck, splayed 6° out from straight down), ammunition lockers, a crew
  hut with a rangefinder;
- the **wheelhouse** cabin on its deckhouse (centre (-5.5, 25), radius 10): smoked windows, a whip
  aerial, and its **twin turret** in front of it (mount `wheelhouse-gun` at (-5.5, 19.5));
- the **mast** (centre (3, -10), radius 10): no gun; its pole, crow's nest, yard, stays and a
  patched sail heeled over to the left, fluttering.

The core's guns, each under a tarpaulin until a stage first uses it (MB-MORTAR-RAFT-09): the
**fixed bow guns** (three barrels side by side pointing down the screen, (-3, -39)), the **deck
turret** on the left planks ((-27, -12), twin), the **stern mortar** turret ((7, 38)) and the
**flak rotor** on the right pontoon's deck ((24, 3), 12 barrels). Fixed guns: the two mortars and
the bow guns (three of its seven mounts); turrets: the wheelhouse's, the deck turret, the stern
mortar; the flak rotor turns its spiral.

**Acceptance criteria**
- Given its design, then it has 3 parts and these 7 mounts; a destroyed part's mounts leave
  stumps standing on the deck under them (the mast leaves none).

*Sources: BOSS-12, BOSS-13, BOSS-48, BOSS-58, round 5 brief (non-rotating guns).*

#### MB-MORTAR-RAFT-04 — Lights · MUST

Its neon is a pale green, `[0.6, 1, 0.4]` (shown green, BOSS-50): gunwale lines, pontoon bands,
propeller ducts' rims, lamps on its corners, the tarpaulins' tags, the crow's nest and mast-head
lamps.

**Acceptance criteria**
- Given the boss look, then its neon is `[0.6, 1, 0.4]` (unit test of the look table).

*Sources: BOSS-50.*

#### MB-MORTAR-RAFT-05 — Its stern outriggers · MUST

Each stern outrigger is a long pontoon under a strip of decking (its top 8.6 px high), two small
lift propellers off its outer side, lashed at its bow to the barge's quarter by three ropes (its
rig) and hinged to a post there at its front inner corner. It is a moving piece (BOSS-45): the
right one swings about the vertical through (19, 25) from 0° to -60° (its stern out to the right),
the left one its mirror image. No part stands on them.

**Acceptance criteria**
- Given the design, then its outriggers are moving regions of its transformation, and its racks
  ride them (unit test, BOSS-45).

*Sources: BOSS-45, round 3 and 5 briefs (visible mechanical transformations).*

### Behaviour

#### MB-MORTAR-RAFT-06 — Coming in and moving · MUST

It stops at 0.72 of the playfield's height, sways ±36 px over 8 s and bobs ±4 px over 3.6 s: a
heavy, lazy drift. Its fight ground speed is ×0.6.

*Sources: BOSS-03, BOSS-08, BOSS-10.*

#### MB-MORTAR-RAFT-07 — Parts and core · MUST

Every part shields its core (BOSS-14); its core carries the last guns (bow guns, deck turret, stern
mortar, flak rotor), so it dies when they are destroyed. Health: core 1 200, mortar emplacement
950, wheelhouse 900, mast 850, each rack 760 (0.8 of the sturdiest part): 5 420 in all.

*Sources: BOSS-12, BOSS-14, BOSS-38, BOSS-54, BOSS-55.*

#### MB-MORTAR-RAFT-08 — Stage patterns · MUST

Its parts' volleys, in every stage while they stand: each fixed mortar lobs a flak shell straight
out of its tube every 3.4 s (one after the other), bursting into 8 after 1.1 s; the wheelhouse
turret fires bursts of 3 at the player every 2.6 s. The core's, stage by stage:

| Stage | Core volleys | Guns in use |
|-------|--------------|-------------|
| 0 | none | 3: the two mortars (fixed) and the wheelhouse turret |
| 1 | the bow guns' three parallel shots every 2.6 s; the deck turret's aimed shot every 2.4 s | +2: bow guns (fixed), deck turret |
| 2 | bow guns every 2.2 s; deck turret's bursts of 3; the stern mortar's heavy flak (bursting into 10) every 3.8 s | +1: stern mortar, and the 2 racks of its transformation |
| 3 | the flak rotor's spiral of 12 every 1.5 s, turning 9°; bow guns, deck turret's bursts of 4, stern mortar | +1: flak rotor |

So every lost part brings a new gun into use; the guns in use (parts destroyed in design order,
racks standing) go 3, 3, 5, 6.

*Sources: BOSS-20, BOSS-21, BOSS-58, round 5 brief (at most 3 guns at start, more as parts go).*

#### MB-MORTAR-RAFT-09 — Its tarpaulins · MUST

Each core gun lies under a tarpaulin roped down over it (a hatch, BOSS-58): the tarpaulin bursts as
the gun first comes into use, leaving a lit gun pit, and the gun rises out of it.

*Sources: BOSS-58.*

#### MB-MORTAR-RAFT-10 — Transformation: the lashings snap · MUST

Once two of its parts are destroyed (BOSS-36) it transforms: its outriggers' lashings strain,
shuddering, then snap (only their frayed ends are left hanging from the barge's cleats) and the
outriggers swing out on their hinges, a **rack** (4 missile ports) riding each, which unfolds on its
decking at (±42.3, 32.7). Angry (BOSS-27), the racks fire their homing missiles all out. The fight
turns from lobbed flak and parallel streams into homing missiles to shoot down among them.

*Sources: BOSS-35 to BOSS-39, BOSS-45.*

#### MB-MORTAR-RAFT-11 — Death, drops and points · MUST

It scores 5 300 points; its parts drop a weapon bonus half the time, its racks 30 % of the time.

*Sources: BOSS-19, BOSS-57.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 3.6 L | `stats.size` |
| health | core 1 200; parts 950 / 900 / 850; racks 760 | 5 420 in all |
| points | 5 300 | |
| ground speed | ×0.6 | |
| stop, sway, bob | 0.72; ±36 px / 8 s; ±4 px / 3.6 s | |
| outrigger swing | 0° → -60° about (19, 25) (mirrored) | `OUTRIGGER_SWING` |
| flak | 105 px/s, radius 7, bursting into 8 at 150 px/s after 1.1 s | `FLAK` |
| heavy flak | 95 px/s, radius 8, bursting into 10 at 150 px/s after 1.3 s | `HEAVY_FLAK` |
| triangles | about 2 750 drawn (budget 4 000) | BOSS-53 |

## Notes

- Simulated fight check (a part broken every 12 s): 509 shots, every one from a barrel, dead at
  74 s.
- Config: `src/game/config/bosses/lab/mortar_raft.py`; model:
  `src/game/view/bosses/lab/mortar_raft_model.py`, `mortar_raft_parts.py`, `mortar_raft_rig.py`.
