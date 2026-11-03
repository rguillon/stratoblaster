# Canopy Spider (3-2 final boss)

> **Area:** bosses · **Prefix:** `FB-CANOPY-SPIDER` · **Related:** [common boss rules](../common.md),
> [3-2 Docklands](../../worlds/world-3/3-2-docklands.md), [World 3](../../worlds/world-3/world.md),
> [Toucan](../mini/3-2-toucan.md), [Hornet](../../enemies/hornet.md),
> [readability](../../graphics/readability.md)

The Canopy Spider is the final boss of level 3-2, met at the level's end. It is a four-legged
walker-ship 5 L across: an armoured cephalothorax carrying its head, a big abdomen behind with an egg
sac at its tip that launches Hornets, and four legs stepping in turn, a gun pod at each foot. It was
designed to hang over the old Jungle world's canopy and, since World 3 became the
factories-to-garden-villages world (D-111), it keeps its name and look and walks over the docklands.
It transforms twice. Shared rules are in [bosses/common.md](../common.md); this file only gives what
is the Spider's own.

## Requirements

### Look

#### FB-CANOPY-SPIDER-01 — Silhouette · MUST

Seen from above, the Spider is a spider nose down the screen: a cephalothorax from about 10 px behind
the centre to 30 px ahead, its head at the front; a big round abdomen behind it out to about 47 px,
the egg sac hanging at its tip; and four legs, two fore legs raised forward (their feet about 28 px
out and 62 px ahead) and two aft legs spread wide and back (feet about 70 px out and 36 px behind).
Each leg rises from its hip to a raised knee and drops to its foot. It is a 5 L boss (radius 2.5 L).

**Acceptance criteria**
- Given the dev bosses viewer, then it reads as a four-legged spider with an egg sac at its tail
  (manual).

*Sources: P09-R09, D-081.*

#### FB-CANOPY-SPIDER-02 — Cyber-Organic body · MUST

It reads as one living spider with metal grafted on: a chitin-shelled cephalothorax, a swollen dark
abdomen with bone ribs and pulsing veins, a sinew waist between them, and metal plates and vents
grafted on both; the shell and the abdomen's back are the plating it sheds (FB-CANOPY-SPIDER-12,
FB-CANOPY-SPIDER-13), drawn over flat-topped lower bodies. An hourglass mark is drawn in neon on the abdomen's back. Its head has two big eyes
at the front and smaller ones behind, all neon, and fangs (flesh chelicerae with bone fangs and a
metal cap) curving down in front of it.

**Acceptance criteria**
- Given the model, then the body reads as one creature (manual).

*Sources: P09-R09, P16-R06.*

#### FB-CANOPY-SPIDER-03 — Legs that step in turn · MUST

Each leg is two moving limbs: an upper leg on its hip (an armoured strut of dark chitin over sinew
rising to the knee, a neon line along it, spines along its back) and a lower leg on its knee (a
tapering shin dropping to the foot, a vine round it), with a faceted armour ball on the knee and a
light on top. The hip swings 11° and the knee 15° once every 3.2 s; the knee lags a quarter step
behind the hip, so the foot swings forward with the knee bent and comes back with it straight. The
four legs step in a walking order (fore-left, aft-right, fore-right, aft-left), a quarter step apart,
never together. The legs belong to the core: they stay and keep stepping when their gun pod is
destroyed.

**Acceptance criteria**
- Given the boss is in place, then the legs step one after the other (manual, dev viewer).

*Sources: P09-R09, D-081, D-061.*

#### FB-CANOPY-SPIDER-04 — Parts on the model · MUST

- Each **leg gun pod** (a part) is at its leg's foot: a swollen flesh foot gripping with three bone
  claws, a gland and a neon ring round it, and a grafted metal gun pointing forward.
- The **egg sac** (a part) is a cocoon of pale grey-green silk hanging from the abdomen's tip, tied
  to it by silk threads, wrapped in metal bands ringed with neon and veined, its eggs glowing through
  the silk as the next brood charges, and a hatch on top that the Hornets leave from.

A destroyed part is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given K destroys a leg gun pod, then the pod disappears and the leg keeps stepping (manual).

*Sources: P09-R09, P16-R06, D-225, D-167.*

#### FB-CANOPY-SPIDER-05 — Canopy growth · MUST

Moss lies on its armour plates and vines wind round its lower legs: the World 3 growth over its dark
metal and flesh, in clear greens.

**Acceptance criteria**
- Given the model, then moss and vines are visible (manual).

*Sources: P09-R09, D-231.*

#### FB-CANOPY-SPIDER-06 — Lights and colours · MUST

Its neon is its own red (`canopy-spider`), shown bright yellow under the enemy colour rule: the eyes,
the hourglass, the lines along the legs, the knee lights, the foot rings and the egg sac's bands.
White charge lights glow at the leg guns, the crown emitter on its back and the eggs. Its lasers are
drawn in its own neon, moved into the enemy shots' colours (see [common](../common.md)).

**Acceptance criteria**
- Given the model, then every neon light is bright yellow (unit: enemy colour family tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### FB-CANOPY-SPIDER-07 — Entry, place and ground speed · MUST

The Spider stops at 0.74 of the playfield's height, sways up to 30 px either side over 11 s and bobs
6 px over 5 s. While it is fought the ground runs at ×0.4.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.4 (design values; common rule tests).

*Sources: P09-R09.*

#### FB-CANOPY-SPIDER-08 — Parts and health · MUST

The core (hit radius 22 px, 3 150 HP) has five original parts: four leg gun pods (12 px, 1 250 HP
each), which shield the core and ride their knee joints (their hit circles and guns step with the
legs), and the egg sac (15 px, 900 HP), which does not shield it. The fore legs are raised forward so
that a ship's spread can reach their pods. Its full health is 9 050 HP with the original parts,
13 550 HP with its four hidden weapons.

**Acceptance criteria**
- Given the design, then it has five original parts and four hidden ones, the leg pods shielding the
  core (unit: `test_canopy_spider.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### FB-CANOPY-SPIDER-09 — Part weapons and Hornets · MUST

While they stand, in every stage:
- each leg gun fires 3 aimed `red` bullets (205 px/s, 12° apart) every 3.4 s, the four 0.85 s apart
  (fore-left, fore-right, aft-left, aft-right);
- the egg sac launches a group of 3 [Hornets](../../enemies/hornet.md) every 7 s, the first 3 s into a
  stage.

**Acceptance criteria**
- Given the egg sac stands, then 3 Hornets leave it every 7 s; once it is destroyed, no more come
  (unit: launches; `test_boss_launches.py` for the rule).

*Sources: P09-R09, D-081.*

#### FB-CANOPY-SPIDER-10 — Core patterns by stage · MUST

The core fires from the crown emitter on its back (21 px high), a new ring pattern at each stage:
- stage 0: rings of 8 `purple` (195 px/s) every 1.5 s, turning 13°;
- stage 1: rings of 9 `magenta` (200 px/s) every 1.4 s, turning -15°;
- stage 2: rings of 10 `purple` every 1.3 s, turning 17°;
- stage 3: two spirals of 8 every 1.5 s turning opposite ways (`purple` 12°, `magenta` -12°);
- stage 4: rings of 11 `magenta` every 1.2 s turning 19°, and a slow ring of 7 `purple` every 2.4 s
  turning -9°;
- stage 5 (alone): a double spiral of 12 `green` (190 px/s) every 1.1 s, turning 9° and -13°.

**Acceptance criteria**
- Given the design, then it has six stages and the last one's double spiral is used by no earlier
  stage (unit: `test_canopy_spider.py`).

*Sources: P09-R09, D-081.*

#### FB-CANOPY-SPIDER-11 — Rage · MUST

It is angry after each of its transformations, when the weapons that one revealed
fire all out: the two gatlings after the first, the two lances after the second.
For `boss_rage_seconds` it fires only those, `boss_rage_rate` times as often, instead of its
stage's pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it
has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed
  (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-081, D-063, D-256.*

#### FB-CANOPY-SPIDER-12 — First transformation: back plating, two gatlings · MUST

At 2 of its 5 original parts destroyed, it transforms for the first time. The **back plating** over
its abdomen bursts off ([common](../common.md), BOSS-42): a piece drawn apart from the belly (the
abdomen's lower half, flat-topped at 7 px), the chitin over it from 6.7 px up to the abdomen's back
(21 px), carrying its bone ribs and pulsing veins, the red hourglass, the grafted seams, the moss and
the patch. Its region (`back`, not mirrored) is the abdomen's own plan from the waist (8 px behind the
centre) to its tip (47 px), 15.3 px either side at its widest; it bursts into plates cracked from
that outline and leaves a dark metal `shell` frame on the belly, the vines still hanging on its
flanks. Two gatling turrets come out at 13 px either side, 25 px behind the centre (radius 7 px, pods
22.3 px high, 1 000 HP each), firing `red` bursts, 1.2 s and 2.0 s into a stage.

**Acceptance criteria**
- Given 2 original parts are destroyed, then the back region bursts off and the two gatlings come out
  and fire (unit: `test_boss_kinds.py`).

*Sources: D-221, D-224, D-229, D-227, D-254.*

#### FB-CANOPY-SPIDER-13 — Second transformation: spine plating, two lances · MUST

At 4 original parts destroyed, it transforms again. The **spine plating** over its cephalothorax
bursts off: the ridged chitin shell drawn apart from the lower shell (flat-topped at 4.6 px), from
4.3 px up to the ridge (15 px), carrying its eyes, the grafted seams, vents and moss. Its region
(`spine`, not mirrored) is the cephalothorax's own plan from the waist (8 px behind the centre) to the
head (30 px ahead), 15 px either side at its widest; it bursts into plates cracked from that outline
and leaves a `shell` frame on the lower shell, the fangs and the crown emitter (on a stalk rooted in
the lower shell) staying up. Two laser lances unfold at 9 px either side, 21 px ahead (radius 7 px,
pods 12.8 px high, 1 250 HP each), firing their lasers 1.2 s and 2.0 s into a stage. It reveals no
kind twice, fires no less after each transformation than before, and stays one object in every state.

**Acceptance criteria**
- Given 4 original parts are destroyed, then the spine region bursts off and the two lances come out
  (unit: `test_boss_kinds.py`).
- Given each state, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-229, D-227, D-254.*

#### FB-CANOPY-SPIDER-14 — Points and drops · MUST

Destroying the Spider scores 14 000 points, and each part destroyed 1 400. Its original parts drop a
bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.

**Acceptance criteria**
- Given the core is destroyed, then a bonus drops and the score rises by 14 000 (unit: scoring and
  bonus rules, design values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/canopy_spider.py` (`CANOPY_SPIDER`) unless noted. Px from the
boss's centre, X right, Y up the screen (its head at -Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (radius 85 px) | |
| core | radius 22 px, 3 150 HP | |
| fore legs | hip (±11, -20), knee (±24, -40), foot / pod (±28, -62) | `LEG_REST.fore` |
| aft legs | hip (±16, 6), knee (±48, 18), foot / pod (±70, 36) | `LEG_REST.aft` |
| leg heights | hip 8, knee 22, foot 4 | `LEG_HEIGHT` |
| leg gun pods | radius 12, 1 250 HP, shield, on `knee-*` joints | |
| egg sac | (0, 50), radius 15, 900 HP, no shield | |
| full health | 9 050 (13 550 with hidden weapons) | P09-R10 band |
| stop / sway / bob | 0.74 / 30 px, 11 s / 6 px, 5 s | |
| ground speed | ×0.4 | |
| stepping | hip 11°, knee 15°, 3.2 s; phases 0 / 0.25 / 0.5 / 0.75 | `STEP`, `PHASE` |
| leg guns | 3 aimed × 12°, every 3.4 s, 0.85 s apart | |
| Hornets | 3 every 7 s, first 3 s into a stage | `launches` |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformations | at 2 and 4 parts destroyed | `default_transforms` |
| back region | the abdomen's plan, y 8..47, x ±15.3 at its widest, `shell`; plating 6.7–21 px over a belly flat at 7 | form 1 |
| spine region | the cephalothorax's plan, y -30..8, x ±15 at its widest, `shell`; plating 4.3–15 px over a shell flat at 4.6 | form 2 |
| gatlings | (±13, 25), radius 7, pod 22.3, 1 000 HP, `red` | form 1 |
| lances | (±9, -21), radius 7, pod 12.8, 1 250 HP | form 2 |
| points | 14 000 (1 400 a part) | |
| neon | [1, 0.12, 0.15] | `BOSS_LOOK.neon["canopy-spider"]` |

## Notes

- Phase 9 fight time with the D-055 bot: 90.6 s, before the hidden weapons were added (D-221).
