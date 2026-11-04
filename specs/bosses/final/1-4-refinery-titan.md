# Refinery Titan

> **Area:** bosses · **Prefix:** `FB-REFINERY-TITAN` · **Related:** [common](../common.md),
> [1-4 Dry Lands](../../worlds/world-1/1-4-dry-lands.md), [Scorpion](../mini/1-4-scorpion.md),
> [World 1](../../worlds/world-1/world.md)

The Refinery Titan is the final boss of 1-4: a bloated industrial beetle, 5.5 L across (first
designed as a heavy tanker-gunship), plumbed with grafted pipes. Two rotary turrets on its front
apron fire spirals and shield its core; two glowing fuel bladders in its limbs burst into rings of
bullets when destroyed; a missile brood sits on its back. It sheds its back plating for a pair of
gatlings, then its spine plating for a pair of orbs. Shared rules are in [common](../common.md).

## Requirements

### Look

#### FB-REFINERY-TITAN-01 — Silhouette and size · MUST

Seen from above, the Refinery Titan is a huge beetle, 5.5 L across: a bloated shelled body, its
plated head at its front (down the screen) over a fleshy apron carrying two rotary turrets, a fuel
bladder held out in a limb on each side, a missile brood on its back and two chimneys behind it.

**Acceptance criteria**
- Manual validation in the boss viewer: a beetle holding a glowing bladder on each side.

*Sources: P07-R05, P16-R06.*

#### FB-REFINERY-TITAN-02 — Body · MUST

Its body is a huge shelled abdomen (slate and sinew shades) with ribs, a vein down its spine and
armour plates grafted on, plumbed with grafted pipes running across into the bladders and along its
back, with couplings. Two chimneys of flesh stand behind it, ringed with neon and joined by a
grafted pipe. Its head over the core is a plated skull with clustered eyes, two smoking spiracles,
mandibles at its front and the core's twin cannon grafted under its brow. Each bladder is held by a
jointed bone-and-sinew limb, its claw curled round the bladder's outer side, lit along its top
(the limbs do not move). Four reactors sit in flesh sacs at its tail.

**Acceptance criteria**
- Manual validation: a living beetle, plumbed and plated like a refinery.

*Sources: P07-R05, P16-R06.*

#### FB-REFINERY-TITAN-03 — Its parts · MUST

- **Fuel tanks** (one in each limb): a big fuel bladder, a swollen sac of flesh with orange bands of
  neon and glowing veins on it, grafted valves at its ends.
- **Rotary turrets** (two, on its front apron): a swollen growth plated round its crown under a
  turret: a housing with three barrels and charge-lit muzzles. The housing and barrels turn; the
  base stays on the part.
- **Missile battery** (on its back): a swollen mound under a grafted plate with six hatches, lit as
  it loads.
- **Twin cannon** (the core's gun): under the head's brow; it does not turn.

**Acceptance criteria**
- Given its model, then it draws its five parts and both rotary turrets (unit test).

*Sources: P07-R05, P16-R06, D-060.*

#### FB-REFINERY-TITAN-04 — Lights · MUST

Orange bands and veins glow on its bladders; neon rings its chimneys, a vein runs down its spine,
its eyes and hatches glow. Its neon colour, set orange, shows bright yellow
([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: P07-R05, P16-R06, D-231.*

#### FB-REFINERY-TITAN-05 — What it sheds · MUST

The shell of its abdomen is drawn in three lengths along it: the core keeps the length over its
tail; the two others are its armour, drawn as pieces of their own ([common](../common.md),
BOSS-42). Under them the core is its belly (up to about 5 px) between the two lobes of its apron
(either side of the belly, from 20 px out, the turrets on them).

- The **back plating** (`back`), the shell's middle length over the core (from about 4 px up to its
  ridge at 18 px), is shed at its first transformation, with the spine vein, the veins and two
  grafted plates on it and the plated skull riding it (its eyes, spiracles, mantlet and the twin
  cannon's barrels; the cannon goes on firing from its muzzles). Shed, it bursts into plates cracked
  from its outline and leaves a `shell` lattice on the belly, out of which the gatlings rise.
- The **spine plating** (`spine`), the shell's front length out to its nose (from about 5 px up to
  17 px), is shed at its second, with the front rib and the eyes at its front. Shed, it leaves a
  `shell` lattice on the belly, out of which the orbs rise.

**Acceptance criteria**
- Given its design, then each transformation sheds its region and its weapons lie in it (unit
  test).
- Given its model, then it draws each region's piece, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-224, D-254.*

### Behaviour

#### FB-REFINERY-TITAN-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs. While it is fought the ground scrolls at ×0.3.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.3 of the level's speed and back after it.

*Sources: P07-R03, P07-R05.*

#### FB-REFINERY-TITAN-07 — Parts and core · MUST

It has five parts as it comes in: `turret-left` and `turret-right`, which shield its core, and
`tank-left`, `tank-right` and the `missile-battery`, which do not. Each rotary turret fires 3-arm
spirals, the two turning opposite ways, its housing spinning with its spiral (about 27°/s). The
battery fires pairs of homing missiles. A fuel tank does not fire, but bursts into a ring of 12
orange bullets when it is destroyed. The twin cannon fires the core's volleys.

**Acceptance criteria**
- Given a tank is destroyed, then it bursts into its ring of bullets once (unit test).
- Given its design, then only its rotary turrets shield the core.

*Sources: P07-R01, P07-R05, D-060.*

#### FB-REFINERY-TITAN-08 — Stage patterns · MUST

The turrets' spirals and the battery's missiles go on in every stage while they stand. The core
fires:
- stage 0: one blue bullet at the player;
- stage 1: an aimed fan of 3;
- stage 2: a burst of 4 at the player;
- stage 3: a fan of 5;
- stage 4: a fan of 7 and an orange bullet at the player;
- stage 5 (all five parts gone): a ring of 14 blue turning at each volley, and orange bursts of 3.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and the parts left fire theirs
  (unit test on its design).

*Sources: P07-R04, D-055.*

#### FB-REFINERY-TITAN-09 — Angry · MUST

It is angry after each of its transformations, when the weapons that one revealed
fire all out: the two gatlings after the first, the two orbs after the second.
For `boss_rage_seconds` it fires only those, `boss_rage_rate` times as often, instead of its
stage's pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it
has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed
  (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-063, D-256.*

#### FB-REFINERY-TITAN-10 — First transformation: gatlings · MUST

Once two of its parts are destroyed, its back plating bursts off, baring a dark metal lattice, and
two **gatlings** unfold just in front of its core, either side of its centre line. They shield the
core and fire orange bursts of 4 at the player, in turn.

**Acceptance criteria**
- Given two parts destroyed, then it transforms and its two gatlings are revealed.

*Sources: D-221, D-224, D-229.*

#### FB-REFINERY-TITAN-11 — Second transformation: orbs · MUST

Once four of its parts are destroyed, its spine plating bursts off, baring a dark metal lattice, and
two **orbs** unfold further forward, either side of its centre line. They shield the core and fire
orange rings of 10, in turn.

**Acceptance criteria**
- Given four parts destroyed, then it transforms a second time and its two orbs are revealed.

*Sources: D-221, D-224, D-229.*

#### FB-REFINERY-TITAN-12 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, and its core always drops
one ([common](../common.md), BOSS-57). Destroying it ends 1-4
([level flow](../../gameplay/level-flow.md)). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: P07-R07.*

## Tunable values

All in `src/game/config/bosses/final_bosses.py` (`_REFINERY_TITAN`, `REFINERY_TITAN`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 5.5 L (radius 93.5 px) | |
| core | health 4 740, radius 22, drop 1 | twin cannon at (±4.5, -35.8), 19 px high |
| `tank-left`, `tank-right` | (∓66, 18), radius 17, health 1 400, no shield, drop 0.6 | |
| `turret-left`, `turret-right` | (∓32, -24), radius 14, health 1 810, shield, drop 0.6 | turrets on their centres |
| `missile-battery` | (0, 38), radius 14, health 1 530, no shield, drop 0.6 | 6 cells |
| full health | 19 210 (12 690 without the hidden weapons) | BOSS-54 |
| points | 12 000; 1 200 a part | |
| ground speed | ×0.3 | |
| stop height | 0.74 | |
| sway / bob | 30 px over 10 s / 6 px over 5 s | |
| rotary spirals | rings of 3 turning +19° (left) / -19° (right), orange 175 px/s, every 0.7 s (first 0.5 s / 0.85 s) | |
| battery missiles | 2, 30° apart, every 5.5 s (first 3 s) | |
| tank burst | ring of 12 orange | `breakRings` |
| core stage 0 | 1 aimed blue bullet, 190 px/s, every 3 s | |
| core stage 1 | aimed 3, 12° apart, every 2.6 s | |
| core stage 2 | burst of 4, 0.14 s apart, every 2.4 s | |
| core stage 3 | fan of 5, 14° apart, every 2.4 s | |
| core stage 4 | fan of 7, 12° apart, every 2.2 s; 1 aimed orange every 2.6 s | |
| core stage 5 | ring of 14 turning 9°, blue, every 1.3 s; orange burst of 3 every 2.8 s | |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformations | 2 and 4 parts destroyed | default thresholds |
| back region (shed) | the shell's middle length: y -24..20, x ±27 at its ends and ±32 at y -14..8, `shell`, not mirrored; the shell 4-18 px, the skull on it to 30 px | first |
| spine region (shed) | the shell's front length: y -24 to its nose, x ±27 to y -36, narrowing through (±20, -47), (±17, -57) and (±6, -66), `shell`, not mirrored; the shell 5-17 px | second |
| gatlings | (∓9, -13), radius 7, health 1 450, pod 25.7 px, orange; first 1.2 s / 2.0 s | |
| orbs | (∓9, -35), radius 7, health 1 810, pod 18.9 px, orange; first 1.2 s / 2.0 s | |
| neon | orange (1, 0.45, 0.05), shown yellow | `BOSS_LOOK.neon` |

## Notes

- Its missile battery sits right behind the core: while the core is shielded, shots go through
  the core and reach it (D-062); once the core can be damaged, only angled shots or missiles reach
  it. Destroying it is optional.
