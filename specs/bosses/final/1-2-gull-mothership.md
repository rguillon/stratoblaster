# Gull Mothership

> **Area:** bosses · **Prefix:** `FB-GULL-MOTHERSHIP` · **Related:** [common](../common.md),
> [1-2 Green Coast](../../worlds/world-1/1-2-green-coast.md), [Breakwater](../mini/1-2-breakwater.md),
> [Hornet](../../enemies/hornet.md), [World 1](../../worlds/world-1/world.md)

The Gull Mothership is the final boss of 1-2: a brood-mother of the sea, 5 L across (first designed
as a wide carrier). Two brood pouches on its flanks launch groups of Hornets and two flak growths on
its front fire at the player; all four shield its core, a huge laser eye at its nose. It sheds its
flank armour for a pair of laser lances, then its wing armour for a pair of orbs. Shared rules are
in [common](../common.md).

## Requirements

### Look

#### FB-GULL-MOTHERSHIP-01 — Silhouette and size · MUST

Seen from above, the Gull Mothership is a wide mantle, 5 L across, a shelled body along its middle
ending at its nose (down the screen) in a huge eye, a brood pouch on each flank and two flak growths
on its front.

**Acceptance criteria**
- Manual validation in the boss viewer: a wide sea creature with a great eye at its nose.

*Sources: P07-R05, P16-R06.*

#### FB-GULL-MOTHERSHIP-02 — Body · MUST

Its body is a teal flesh mantle with a second fold on it, a shelled body along its middle (graphite
and slate shades) with ribs over its back and glands down its spine, swim bladders at the back of
the mantle with their reactors in flesh sacs, and at its nose the laser eye: a socket of flesh, a
grafted ring and a lens that glows as it charges.

**Acceptance criteria**
- Manual validation: a living mantle; the eye's lens brightens before each laser.

*Sources: P07-R05, P16-R06.*

#### FB-GULL-MOTHERSHIP-03 — Its parts · MUST

- **Hangar bays** (one on each flank): a swollen brood pouch on the mantle, a glowing birth slit in
  its top between fleshy lips, glands down both sides, a grafted brace on its outer side.
- **Flak turrets** (two, on the front of the mantle): a swollen, plated mound with a feeding sac
  behind it, under a twin-gun turret on its crown.
- **Laser eye** (the core's weapon): at its nose; it does not turn.

**Acceptance criteria**
- Given its model, then it draws both hangars, both flak growths and their turrets (unit test).

*Sources: P07-R05, P16-R06, D-058.*

#### FB-GULL-MOTHERSHIP-04 — Lights · MUST

A vein lines its mantle's rim; glands light its spine, its pouches and its flak growths. Its neon
colour, set green, shows bright green ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: P07-R05, P16-R06, D-231.*

#### FB-GULL-MOTHERSHIP-05 — What it sheds · MUST

Its mantle is drawn in two layers: a lower teal slab the whole mantle wide (-5 to 1.9 px) and an
upper one (1.9 to 4 px) with the graphite fold on it. The upper layer's flanks are its armour, drawn
as pieces of their own out to the mantle's rim ([common](../common.md), BOSS-42), the fold's flanks
and the veins across them on them; the upper layer runs on along the middle and over the front:

- The **rear flanks** (`flanks`, mirrored), behind its middle, are shed at its first
  transformation: they carry the swim bladders (up to 12.5 px) with their reactors in sacs. Shed,
  they burst into plates cracked from their outline and leave `wing` frames on the lower layer, out
  of which the lances rise.
- The **front flanks** (`wings`, mirrored), in front of its middle up to a line across the mantle's
  front, at its second: they carry a grafted plate each. Shed, they leave `wing` frames likewise, out
  of which the orbs rise.

**Acceptance criteria**
- Given its design, then each transformation sheds its region and its weapons lie in it (unit
  test).
- Given its model, then it draws both regions' pieces, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-224, D-254.*

### Behaviour

#### FB-GULL-MOTHERSHIP-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs. While it is fought the ground scrolls at ×0.6.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.6 of the level's speed and back after it.

*Sources: P07-R03, P07-R05.*

#### FB-GULL-MOTHERSHIP-07 — Parts and core · MUST

It has four parts as it comes in, all shielding its core: `hangar-left`, `hangar-right`,
`flak-left` and `flak-right`. Each hangar launches a group of 3 Hornets, the two in turn, out to its
own side ([common](../common.md), BOSS-25); each flak turret fires aimed green pairs, in turn, and
turns the way it fires. The laser eye fires the core's volleys, its lasers straight down.

**Acceptance criteria**
- Given its design, then each hangar launches 3 Hornets every 7 s while it stands.

*Sources: P07-R01, P07-R05, D-055, D-058.*

#### FB-GULL-MOTHERSHIP-08 — Stage patterns · MUST

The Hornets and the flak pairs go on in every stage while their parts stand. The core fires a laser
in every stage, more often from stage to stage, and:
- stage 0: the laser alone;
- stage 1: one orange bullet at the player;
- stage 2: a fan of 5 orange;
- stage 3: a ring of 8 orange;
- stage 4 (all four parts gone): a longer laser, and a ring of 12 green turning at each volley.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and the parts left fire theirs
  (unit test on its design).

*Sources: P07-R04, D-055.*

#### FB-GULL-MOTHERSHIP-09 — Angry · MUST

It is angry after each of its transformations, when the weapons that one revealed
fire all out: the two lances after the first, the two orbs after the second.
For `boss_rage_seconds` it fires only those, `boss_rage_rate` times as often, instead of its
stage's pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it
has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed
  (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-063, D-256.*

#### FB-GULL-MOTHERSHIP-10 — First transformation: lances · MUST

Once two of its parts are destroyed, its flank armour bursts off, baring a dark metal frame, and two
**lances** unfold behind its middle, either side. They shield the core and fire lasers straight
down, in turn.

**Acceptance criteria**
- Given two parts destroyed, then it transforms and its two lances are revealed.

*Sources: D-221, D-224, D-229.*

#### FB-GULL-MOTHERSHIP-11 — Second transformation: orbs · MUST

Once three of its parts are destroyed, its wing armour bursts off, baring a dark metal frame, and
two **orbs** unfold either side of its middle. They shield the core and fire green rings of 10, in
turn.

**Acceptance criteria**
- Given three parts destroyed, then it transforms a second time and its two orbs are revealed.

*Sources: D-221, D-224, D-229.*

#### FB-GULL-MOTHERSHIP-12 — Laser colour · MUST

Its lasers (the eye's and the lances') are drawn in its neon folded into the enemy shots' family: an
orange beam round a white-hot core ([common](../common.md), BOSS-32).

**Acceptance criteria**
- Given its lasers, then their colour is its neon folded into the enemy shots' family (unit
  test).

*Sources: D-072, D-231.*

#### FB-GULL-MOTHERSHIP-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, and its core always drops
one ([common](../common.md), BOSS-57). The Hornets it launched count among the level's spawned
enemies. Destroying it ends 1-2 ([level flow](../../gameplay/level-flow.md)). It scores the points
of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: P07-R07, D-055.*

## Tunable values

All in `src/game/config/bosses/final_bosses.py` (`_GULL_MOTHERSHIP`, `GULL_MOTHERSHIP`) unless
named.

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (radius 85 px) | |
| core | health 2 280, radius 20, drop 1 | laser eye at (0, -69.9), 7 px high |
| `hangar-left`, `hangar-right` | (∓62, 6), radius 18, health 1 050, shield, drop 0.6 | |
| `flak-left`, `flak-right` | (∓28, -32), radius 12, health 790, shield, drop 0.6 | turrets on their centres |
| full health | 9 740 (5 960 without the hidden weapons) | BOSS-54, BOSS-55 |
| points | 9 000; 900 a part | |
| ground speed | ×0.6 | |
| stop height | 0.74 | |
| sway / bob | 40 px over 9 s / 8 px over 4.5 s | |
| Hornets | 3 a hangar every 7 s (first 2.5 s left, 6 s right) | `launches` |
| flak pairs | aimed 2, 8° apart, green 180 px/s, every 1.9 s (first 0.9 s / 1.85 s) | |
| core stage 0 | laser 1.5 s every 7 s (first 4 s) | |
| core stage 1 | laser every 6 s; 1 aimed orange bullet, 175 px/s, every 2.6 s | |
| core stage 2 | laser every 5.5 s; fan of 5, 14° apart, every 2.6 s | |
| core stage 3 | laser every 5 s; ring of 8 every 2.2 s | |
| core stage 4 | laser 1.6 s every 4.5 s; ring of 12 turning 9°, green, every 1.5 s | |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformations | 2 and 3 parts destroyed | default thresholds |
| flank region (shed) | the rear flank out to the rim: x 18..47 at y 6..30, then along the rim to (34, 48) and (18, 54.4), `wing`, mirrored; the plate 1.9-4 px, the bladders to 12.5 px | first |
| wing region (shed) | the front flank out to the rim: x 22..47 at y 6..-20, then along the rim to (40, -32) and (33.1, -38), cut across at y -38, `wing`, mirrored; the plate 1.9-4 px | second |
| lances (`pike-*`) | (∓35, 23), radius 9, health 840, pod 9.6 px; first 1.2 s / 2.0 s | |
| orbs | (∓37, -9), radius 7, health 1 050, pod 7.6 px, green; first 1.2 s / 2.0 s | |
| neon | green (0.2, 1, 0.35) | `BOSS_LOOK.neon` |
