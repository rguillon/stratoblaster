# River Leviathan (3-1 final boss)

> **Area:** bosses · **Prefix:** `FB-RIVER-LEVIATHAN` · **Related:** [common boss rules](../common.md),
> [3-1 Canal works](../../worlds/world-3/3-1-canal-works.md), [World 3](../../worlds/world-3/world.md),
> [Mangrove Croc](../mini/3-1-mangrove-croc.md), [readability](../../graphics/readability.md)

The River Leviathan is the final boss of level 3-1, met at the level's end. It is a segmented
serpent-ship 6 L long: an armoured head (its core) and, trailing behind it, four body segments and a
tail on a chain of hinges, a wave running down the body as it swims. Each segment carries a ring
turret; the tail carries a missile rack. It was designed for the old Jungle world's river delta and,
since World 3 became the factories-to-garden-villages world (D-111), it keeps its name and look and
flies over the canal works. It transforms twice. Shared rules are in [bosses/common.md](../common.md);
this file only gives what is the Leviathan's own.

## Requirements

### Look

#### FB-RIVER-LEVIATHAN-01 — Silhouette · MUST

Seen from above, the Leviathan is a serpent about 6 L long, nose down the screen: a wedge-shaped
head at the boss's centre, a crest on its back, then four body segments, each a little narrower than
the one before (half widths 15, 14, 13 and 12 px), and a tapering tail ending in two flukes, about
180 px behind the head. A short sponson stands out from each segment, on alternate sides (left,
right, left, right), so that no turret hides behind the head. The boss is a 6 L boss (radius 3 L).

**Acceptance criteria**
- Given the dev bosses viewer, then it reads as a long segmented serpent with a sponson turret on
  each segment (manual).

*Sources: P09-R09.*

#### FB-RIVER-LEVIATHAN-02 — Cyber-Organic body · MUST

It reads as one living serpent with armour grafted on: a head of teal flesh (its skull, flat-backed, under the plating it sheds), its
scutes and jaw line grafted armour, a membrane fin on its back rooted in the skull with the crest
emitter grafted at its top; segments of
swollen teal flesh with bone ribs over them and a vein along the spine, their scutes and sponsons
grafted armour; a tapering flesh tail with membrane flukes on bone and its reactors in flesh sacs. A
round collar stands on each hinge so the bend between two segments never opens a gap.

**Acceptance criteria**
- Given the model, then the body reads as one creature, not parts stuck on a box, at rest and while
  it sways (manual).

*Sources: P16-R06.*

#### FB-RIVER-LEVIATHAN-03 — Head · MUST

The head is an armoured wedge with glaring neon eyes, a dark jaw line round the snout under them,
teeth under the lip, twin fang guns at its cheeks (9 px either side, 24 px ahead), a laser lens at
the tip of its snout (31 px ahead) and, on its crest, a ring emitter (19 px high) for its spirals.

**Acceptance criteria**
- Given the model, then the fang guns, the lens and the crest emitter stand where the design's
  muzzles are (unit: `test_boss_models.py`).

*Sources: P09-R09.*

#### FB-RIVER-LEVIATHAN-04 — Parts on the model · MUST

- Each **segment turret** (a part) is a swollen gland on the serpent's flank with a round metal mount
  and a neon ring grafted on top, and a dome ringed with four stubby vanes turning on it, its ring
  emitter glowing on its axis at the top.
- The **tail rack** is an egg sac swelling on the tail, capped by a grafted armoured box of four
  missile cells, each with a charge light round its mouth, a neon band round it.

A destroyed part is hidden and leaves nothing in its place; the segments and the tail, which belong
to the core, stay and keep swaying.

**Acceptance criteria**
- Given K destroys a segment turret, then its turret and mount disappear and the segment stays
  (manual, dev viewer).

*Sources: P09-R09, P16-R06, D-225, D-167.*

#### FB-RIVER-LEVIATHAN-05 — Swaying body · MUST

The body hangs on five joints in a chain, each on the one before: the neck (20 px behind the centre),
three spine hinges (52, 84, 116 px) and the tail's (148 px). Every hinge swings the same way, over
4.8 s, each 0.11 of a period behind the one before, by 8°, 9°, 10°, 12° and 14° from neck to tail,
so a wave runs from the head to the tail as a swimming snake's. The segment turrets and the tail
rack ride their joints: their hit circles and muzzles move with the body.

**Acceptance criteria**
- Given a long fight, then each part's centre follows its joint chain and the parts stay within the
  ship's reach, the swaying segments included (joint and sway rules: unit tests in
  [common](../common.md); manual: the sway is smooth).

**Gap:** no unit test runs a long simulated fight of the Leviathan checking that its swaying parts
stay within the ship's reach (the phase 9 one was not carried over to the Python port).

*Sources: P09-R09, D-081, D-061.*

#### FB-RIVER-LEVIATHAN-06 — River growth · MUST

Moss lies on the head, the segments and the tail, and a vine hangs from each segment: the World 3
growth over its dark metal and flesh, in clear greens.

**Acceptance criteria**
- Given the model, then moss and hanging vines are visible on its body (manual).

*Sources: P09-R09, D-231.*

#### FB-RIVER-LEVIATHAN-07 — Lights and colours · MUST

Its neon is its own teal (`river-leviathan`), shown bright green under the enemy colour rule: a light
down the back of the head and of each segment, the eyes, the turret mounts' rings and the rack's
band. White charge lights glow at the lens, the fang guns, the crest emitter and the missile cells.
Its lasers are drawn in its own neon, moved into the enemy shots' colours (see
[common](../common.md)).

**Acceptance criteria**
- Given the model, then every neon light is bright green (unit: enemy colour family tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### FB-RIVER-LEVIATHAN-08 — Entry, place and ground speed · MUST

The Leviathan comes in from above the top edge and stops at 0.72 of the playfield's height, high
enough to be in place within the common entry time with its tail still on screen. In place it sways
up to 55 px either side over 9.6 s and bobs 6 px over 4.8 s. While it is fought the ground runs at
×0.5.

**Acceptance criteria**
- Given the fight starts, then the boss is in place in under 6.5 s and the ground slows to ×0.5
  (unit: entry rule; design values).

*Sources: P09-R09.*

#### FB-RIVER-LEVIATHAN-09 — Parts and health · MUST

The core (the head, hit radius 22 px, 2 500 HP) has five original parts: four segment turrets (14 px,
900 HP each) that shield the core, and the tail rack (13 px, 700 HP) that does not. Its full health is
6 800 HP with the original parts, 10 040 HP with its four hidden weapons.

**Acceptance criteria**
- Given the design, then it has five original parts and four hidden ones, the segment turrets
  shielding the core (unit: `test_river_leviathan.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### FB-RIVER-LEVIATHAN-10 — Part weapons · MUST

While they stand, in every stage:
- each segment turret fires a ring of 8 `green` bullets (195 px/s) every 4.4 s, turning 11° each
  time, the four in turn from the neck to the tail, 1.1 s apart; each turret turns with its rings
  but fires from the emitter on its axis;
- the tail rack fires 2 homing missiles (30° apart) every 6 s.

**Acceptance criteria**
- Given all segments stand, then their rings leave one after the other from the neck back (unit:
  design volleys).

*Sources: P09-R09, D-081, D-060.*

#### FB-RIVER-LEVIATHAN-11 — Core patterns by stage · MUST

The head fires its laser (from the snout's lens) at every stage, with something new beside it from
its fang guns or its crest:
- stage 0: the laser (1.5 s) every 7 s;
- stage 1: the laser every 6.5 s, and 3 aimed `magenta` bullets (200 px/s, 12° apart) every 2.8 s;
- stage 2: the laser every 6 s, and a fan of 5 `magenta` (14° apart) every 2.6 s;
- stage 3: the laser (1.6 s) every 6 s, and bursts of 4 `blue` (205 px/s, 0.14 s apart) every 2.6 s;
- stage 4: the laser every 5.5 s, and a fan of 7 `magenta` (12° apart) every 2.4 s;
- stage 5 (alone): the laser every 5 s under two spirals from its crest turning opposite ways (rings
  of 4 `blue` every 0.5 s turning 19°, rings of 4 `purple` at 210 px/s turning -23°).

**Acceptance criteria**
- Given the design, then it has six stages and the last one's twin spirals are used by no earlier
  stage (unit: `test_river_leviathan.py`).

*Sources: P09-R09, D-081.*

#### FB-RIVER-LEVIATHAN-12 — Rage · MUST

After the pause that follows each destroyed part, it fires two crossing spirals at heat 5, in `blue`
and `green`.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the spirals for the rage
  time (unit: rage patterns).

*Sources: D-081, D-063.*

#### FB-RIVER-LEVIATHAN-13 — First transformation: back plating, two sweepers · MUST

At 2 of its 5 original parts destroyed, the Leviathan transforms for the first time. The **back
plating** of its head bursts off ([common](../common.md), BOSS-42): a piece drawn apart from the
skull, the head's shoulders and back behind the split 1 px ahead of the centre, from 4.7 px (sunk
into the skull's flat back at 5 px) up to the head's top (10 to 13.5 px), carrying the worn edges
along its shoulders, the scutes, the moss and the river stone. Its region (`back`) is a half of the
head's own plan either side of the crest (x 1.6..17 at the split, narrowing to 12.3 at 24 px behind
the centre), mirrored; it bursts into plates cracked from that outline and leaves a dark metal
`shell` frame on the skull's back, the crest standing between the halves. Two sweepers come out at 7
px either side of the centre line, 19 px behind it (radius 5 px, pods 15.7 px high, 720 HP each),
each firing a laser that sweeps after the player (see [common](../common.md)), 1.2 s and 2.0 s into a
stage.

**Acceptance criteria**
- Given 2 original parts are destroyed, then the first transformation sheds the back region and
  reveals the two sweepers, which shield the core and fire (unit: `test_boss_kinds.py`).

*Sources: D-221, D-224, D-229, D-227, D-254.*

#### FB-RIVER-LEVIATHAN-14 — Second transformation: spine plating, two orbs · MUST

At 4 original parts destroyed, it transforms again. The **spine plating** over the front of its head
bursts off: the piece drawn apart from the skull ahead of the split, the head's shoulders and back
from 4.7 px up to the head's top (13.5 px, tapering to 6 at the snout), the teal glands and the
glaring eyes on it. Its region (`spine`) is a half of the head's plan either side of the spine (x
1.6..17 at the split, tapering to 5 at 29 px ahead), mirrored; it bursts into plates cracked from
that outline and leaves a `shell` frame on the skull, the fang guns and the lens staying on the
snout under it. Two orbs come out at 7 px either side, 21 px ahead (radius 5 px, pods 10.8 px high,
900 HP each), firing `green` rings of 10, 1.2 s and 2.0 s into a stage. It reveals no kind twice, it
fires no less after each transformation than before, and it stays one object in every state.

**Acceptance criteria**
- Given 4 original parts are destroyed, then the spine region bursts off and the two orbs come out
  (unit: `test_boss_kinds.py`).
- Given each state, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-229, D-227, D-254.*

#### FB-RIVER-LEVIATHAN-15 — Points and drops · MUST

Destroying the Leviathan scores 20 000 points, and each part destroyed 2 000. Its original parts
drop a bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.

**Acceptance criteria**
- Given the core is destroyed, then a bonus drops and the score rises by 20 000 (unit: scoring and
  bonus rules, design values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/river_leviathan.py` (`RIVER_LEVIATHAN`) unless noted. Px from
the boss's centre, X right, Y up the screen (the tail at +Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 6 L (radius 102 px) | |
| core (head) | radius 22 px, 2 500 HP | |
| segment turrets | (-28, 36), (28, 68), (-28, 100), (28, 132); radius 14, 900 HP, shield | `LEVIATHAN_BODY` |
| tail rack | (0, 166), radius 13, 700 HP, no shield | on the `tail` joint |
| full health | 6 800 (10 040 with hidden weapons) | P09-R10 band |
| stop / sway / bob | 0.72 / 55 px, 9.6 s / 6 px, 4.8 s | |
| ground speed | ×0.5 | |
| spine | hinges at 20, 52, 84, 116, 148 px; 8 / 9 / 10 / 12 / 14°, 4.8 s, lag 0.11 | `SWAY`, `spine()` |
| segment rings | 8 × `green` 195 px/s, every 4.4 s, turn 11°, 1.1 s apart | |
| tail missiles | 2, 30° apart, every 6 s | `MISSILE` |
| core laser | 1.5–1.6 s, every 7 → 5 s | stage volleys |
| rage | spirals, heat 5 | |
| transformations | at 2 and 4 parts destroyed | `default_transforms` |
| back region | a half of the head's plan, x 1.6..17 at y -1 to 12.3 at y 24, mirrored, `shell`; plating 4.7 px to the head's top | form 1 |
| spine region | a half of the head's plan, x 1.6..17 at y -1 to 5 at y -29, mirrored, `shell`; plating 4.7 px to the head's top | form 2 |
| sweepers | (±7, 19), radius 5, pod 15.7, 720 HP | form 1 |
| orbs | (±7, -21), radius 5, pod 10.8, 900 HP, `green` | form 2 |
| points | 20 000 (2 000 a part) | |
| neon | [0.05, 0.9, 0.8] | `BOSS_LOOK.neon["river-leviathan"]` |

## Notes

- Phase 9 fight time with the D-055 bot: 87.5 s, before the hidden weapons were added (D-221). Its
  core went from 2 800 to 2 500 HP and its stop from lower to 0.72 at validation, to come in within
  6.5 s (it took 7.1 s).
- The segment turrets turn with their rings but their emitter stays on the axis, so the rings do not
  leave from the vanes (D-081).
