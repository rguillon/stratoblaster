# Scorpion

> **Area:** bosses · **Prefix:** `MB-SCORPION` · **Related:** [common](../common.md),
> [1-4 Dry Lands](../../worlds/world-1/1-4-dry-lands.md),
> [Refinery Titan](../final/1-4-refinery-titan.md), [World 1](../../worlds/world-1/world.md)

The Scorpion is the mini boss of 1-4: a living desert scorpion, 3.5 L across, its tail arched over
its back. Its arms swing out to two claw cannons and its stinger hangs in front of its head; all
three shield its core. Once both claws are gone it turns round, sheds its back plating and unfolds
its tail straight out behind it, towards the player, into a cannon firing a giant laser. It is the
only World 1 boss with moving limbs. Shared rules are in [common](../common.md).

## Requirements

### Look

#### MB-SCORPION-01 — Silhouette and size · MUST

Seen from above, the Scorpion is 3.5 L across: a long segmented body, two jointed arms reaching
forward (down the screen) to big claws, bone legs at its sides, and a tail of shelled beads arched
over its back, its stinger hanging in front of its head, between the claws.

**Acceptance criteria**
- Manual validation in the boss viewer: a scorpion, claws forward, its tail arched over its back.

*Sources: P07-R05, P16-R05, D-053.*

#### MB-SCORPION-02 — Body · MUST

Its body is a swollen, segmented abdomen under a ridged shell (sinew, slate and graphite shades),
its head plated with grafted armour, glowing eyes, bone legs and a plate grafted on its abdomen. It
is not symmetrical: its right hind leg is missing, a torn stump in its place, and its left claw (the
screen's left) is the bigger one, a fiddler crab's.

**Acceptance criteria**
- Manual validation: the missing hind leg and the unequal claws show.

*Sources: P07-R05, P16-R05.*

#### MB-SCORPION-03 — Arms and claws · MUST

Each arm is an upper arm on its shoulder and a forearm on its elbow, overlapping under the elbow's
cog, each with its bed, a grafted armour plate, a light, a hydraulic ram and a lit conduit. Each
**claw cannon** is a swollen knuckle under a grafted cap, a cannon between its two pincers, and the
sinews that work them; its two jaws open and close on their own hinges.

**Acceptance criteria**
- Given its model, then each arm has jointed limbs and a jaw on each side of its claw (unit test).

*Sources: P07-R05, P16-R05, D-061.*

#### MB-SCORPION-04 — Stinger, tail and tail cannon · MUST

The **stinger** is a venom bulb hanging from the tail's tip, its emitter at its front. The tail is a
rig of six shelled beads with a sinew ring at each root and lights along its back and belly, drawn
apart from the core so it can unfold. The **tail cannon** at its end, hidden until the
transformation, is the venom bulb swollen into a barrel ringed with neon, a great lens at its mouth
that brightens as the giant laser charges.

**Acceptance criteria**
- Given its tail at rest and unfolded, then it holds together (unit test).

*Sources: P07-R05, P16-R05, D-228.*

#### MB-SCORPION-05 — Lights · MUST

Yellow veins and lights run along its shell, arms, tail and claws; its eyes glow. Its neon colour,
set yellow, shows bright yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then it is lit in its yellow neon (unit test).

*Sources: P07-R05, P16-R05, D-231.*

### Behaviour

#### MB-SCORPION-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs. While it is fought the ground scrolls at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.5 of the level's speed and back after it.

*Sources: P07-R03, P07-R05.*

#### MB-SCORPION-07 — Moving arms · MUST

Its arms move on joints all the time it is there ([common](../common.md), BOSS-33): each swings at
the shoulder, bends at the elbow and turns its claw at the wrist, while the claw's jaws open and
close. The right arm is the left's mirror image, a little out of step, so the two never move
together. The claws' hit circles and barrels move with them.

**Acceptance criteria**
- Given the Scorpion mid-swing, then each claw's hit circle and barrel tip are where its model draws
  them (unit test).

*Sources: D-061.*

#### MB-SCORPION-08 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `claw-left` and `claw-right` on their
wrists, and the `stinger`, hanging in front of the core so shots from below reach it. Each claw
fires an aimed fan of 3 blue bullets, the two in turn; the stinger fires a laser straight down,
locked once it fires; the core's gun fires the core's volleys. None of its guns is on a turret.

**Acceptance criteria**
- Given its design, then its claws hang on joints and its stinger sits in front of the core.

*Sources: P07-R01, P07-R05, D-053, D-055.*

#### MB-SCORPION-09 — Stage patterns · MUST

The claws' fans and the stinger's laser go on in every stage while they stand. The core fires:
- stage 0: one purple bullet at the player;
- stage 1: a ring of 6;
- stage 2: a ring of 8 turning at each volley;
- stage 3: a ring of 12 turning at each volley, and a blue bullet at the player.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and the parts left fire theirs
  (unit test on its design).

*Sources: P07-R04, D-055.*

#### MB-SCORPION-10 — Angry · MUST

Its angry pattern is a **flower** at heat 3 (a dense purple ring, blue fans at the player).

**Acceptance criteria**
- Given its design, then its rage is that pattern at that heat, fired from its core.

*Sources: D-063.*

#### MB-SCORPION-11 — It turns round and its tail becomes a giant laser · MUST

It transforms once, when both its claws are destroyed (whatever else is lost). Over the
transformation it turns round by 180°, its parts and guns turning with it; its stinger retires at
once (it leaves the fight without being destroyed, its laser stops and its health leaves the
gauge); its back plating bursts off, baring a dark metal lattice; and its tail swings back over the
top and straightens out behind it, now towards the player, a little longer than when arched. The
**tail cannon** at its end rises into place: it shields the core and fires a **giant laser**
straight down the screen, four times as wide as the usual ones, its warning line first.

**Acceptance criteria**
- Given both claws destroyed, then it transforms, turning by pi, and its stinger retires (unit
  test).
- Given its tail cannon revealed, then it fires a 44 px wide laser every 7 s.
- Manual validation: the Scorpion turns round and its tail unfolds into the cannon.

*Sources: D-224, D-228.*

#### MB-SCORPION-12 — Laser colour · MUST

Its lasers (the stinger's and the giant laser) are drawn in its neon folded into the enemy shots'
family: an orange beam round a white-hot core ([common](../common.md), BOSS-32).

**Acceptance criteria**
- Given its lasers, then their colour is its neon folded into the enemy shots' family (unit
  test).

*Sources: D-072, D-231.*

#### MB-SCORPION-13 — Death, drops and points · MUST

Its claws and stinger drop a weapon bonus half of the time, its tail cannon 30 %; it drops a life
bonus as a mini boss ([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: P07-R07.*

## Tunable values

All in `src/game/config/bosses/mini_bosses.py` (`_SCORPION`, `SCORPION`, `scorpion_arm`) unless
named.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.5 L (radius 59.5 px) | |
| core | health 1 470, radius 18 | gun at (0, -26), 2 px high |
| `claw-left`, `claw-right` | (∓42, -24), radius 14, health 730, shield, drop 0.5, on `wrist-left` / `wrist-right` | |
| `stinger` | (0, -34), radius 13, health 730, shield, drop 0.5, retires at transformation 1 | |
| shoulder | (∓14, -10), ±7°, 4.4 s | joints; the right arm 0.37 of a period late |
| elbow | (∓27.5, -18), ±12°, 3.2 s, phase 0.25 | |
| wrist | (∓40, -22), ±16°, 2.4 s, phase 0.5 | |
| jaws | ±12°, 1.1 s, on the wrist | |
| full health | 4 760 | BOSS-54 |
| points | 4 500; 450 a part | |
| ground speed | ×0.5 | |
| stop height | 0.74 | |
| sway / bob | 60 px over 7.5 s / 8 px over 3.2 s | |
| claw fans | aimed 3, 10° apart, blue 185 px/s, every 2.2 s (first 1 s / 2.1 s) | |
| stinger laser | 1.4 s, every 5.5 s (first 2.5 s) | |
| core stage 0 | 1 aimed purple bullet, 195 px/s, every 3 s | |
| core stage 1 | ring of 6, every 2.4 s | |
| core stage 2 | ring of 8 turning 10°, every 2 s | |
| core stage 3 | ring of 12 turning 8° every 1.4 s, and 1 aimed blue every 2.4 s | |
| angry | flower, heat 3 (44 bullets a second, 144 px/s), purple and blue | |
| transformation | when `claw-left` and `claw-right` are destroyed; turns by pi | `transformParts`, `turns` |
| shed region | back: x -20..20, y -2..35.5, above 4 px, `shell`, not mirrored | |
| `tail-cannon` | ends at (0, 108), radius 15, health 1 100, shield, drop 0.3; first shot 1.5 s | `SCORPION_TAIL_CANNON`, `tail_cannon` |
| giant laser | 44 px wide, 2.4 s, every 7 s | `src/game/config/bosses/weapon_kinds.py` `BEAM` |
| tail rig | 6 beads, 10 % longer unfolded | `src/game/view/bosses/scorpion_tail.py` |
| neon | yellow (1, 0.9, 0.1) | `BOSS_LOOK.neon`; `src/game/view/bosses/scorpion_look.py` |

## Notes

- The stinger was first spec'd on the tail's back; it hangs in front of the core because a
  shielding part behind the shielded core could not be hit (D-053; since D-062 shots go through a
  shielded core).
- Its arms were first part of its still body; the reviewer asked for the claws and arms to move
  (phase 7 review, D-061).
