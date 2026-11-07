# Tri-Wing Hydra

> **Area:** bosses · **Prefix:** `FB-TRI-WING-HYDRA` · **Related:** [common](../common.md),
> [Carapace Drum](L-1-carapace-drum.md)

The Tri-Wing Hydra is the final boss of the Lab's level L-1: a three-headed hydra seen from above,
4.5 L across. Three long necks fan out in front of its plated body (two forward-diagonal, one
straight ahead), each swaying at its root and ending in a turret head; a shoulder plate on each
flank, membrane wings behind them and a finned tail (its three wings). Its widely spaced heads
catch the player in a crossfire. Once its two outer heads are gone it sheds its back plating for a
pair of missile racks; once both shoulders are gone it sheds its breastplate for a pair of gun
batteries and an orb on its centre line. Its core carries no gun: it dies with its last weapon.
Shared rules are in [common](../common.md).

**Lab boss: in the dev viewer only.** It is listed after the 40 World bosses in the dev viewer's
Bosses list; no level brings it in.

## Requirements

### Look

#### FB-TRI-WING-HYDRA-01 — Silhouette and size · MUST

Seen from above, the Tri-Wing Hydra is a Ψ on a body: a long plated body, three long necks
spreading from its front (the outer two out and forward, nearly 60° off its axis, the middle one
straight ahead, down the screen), a head at the end of each, a broad shoulder plate on each flank,
a membrane wing swept back behind each shoulder and a tail ending in a fin. It is clearly
three-headed.

**Acceptance criteria**
- Manual validation in the boss viewer: three necks with a head each, fanned out in front of a
  winged body, unlike any other boss.

*Sources: Lab request (2026-11-05: "create 5 new mini bosses and 5 new final bosses").*

#### FB-TRI-WING-HYDRA-02 — Body, necks and wings · MUST

Its body is a long graphite belly flattened under its plating (the back plating and the
breastplate, FB-TRI-WING-HYDRA-05), with a dark metal collar at each neck's root. Each neck is a
thick sinew bowed up, riveted vertebra plates down its back and a lime vein along each side; it
swings to and fro at its root (a joint, BOSS-33), out of step with the others, carrying its head.
The necks are limbs of the body: a neck stays when its head is destroyed. Its wings are dark
membranes on bone struts, lime veins along two of them; its tail tapers to a bevelled membrane fin.
Reactor sacs sit at the tail's root.

**Acceptance criteria**
- Given its design, then its three heads hang on their necks' joints (unit test on its design).
- Manual validation: its necks visibly sway, its heads and their turrets with them.

*Sources: Lab request.*

#### FB-TRI-WING-HYDRA-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Heads** (`head-left`, `head-right`, `head-centre`, at the necks' ends): each a long armoured
  skull looking along its neck, its jaw hanging open over bone fangs and tusks, two eyes each side
  of its brow, swept-back bone horns, a riveted crest, lime veins along its cheeks; on its crown a
  gun turret with three barrels side by side (the outer heads' aimed spreads, the middle head's
  fans and bursts).
- **Missile shoulder** (`shoulder-left`): a broad bone pauldron over the flank, ringed by a lime
  vein, bone spurs on its outer edge; a block of four missile ports grafted on its top.
- **Laser shoulder** (`shoulder-right`): the same pauldron, a laser emitter on a plate at its front
  pointing down the screen, a gland of light behind it.

The core carries no gun (BOSS-58): it is never hit and dies with its last weapon.

**Acceptance criteria**
- Given its model, then it draws the three heads, both shoulders, the necks and every gun mount
  (unit test).

*Sources: Lab request.*

#### FB-TRI-WING-HYDRA-04 — Lights · MUST

Lime veins run along its necks, its heads' cheeks, its wings, its flanks, its tail and its
plating; its eyes, glands and reactors glow. Its neon colour, set lime, shows bright green
([common](../common.md), BOSS-50). Its laser is drawn in that colour folded into the enemy shots'
family (BOSS-32).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: Lab request.*

#### FB-TRI-WING-HYDRA-05 — What it sheds · MUST

Its plating is two armour regions (BOSS-42), each a ridged carapace drawn as a piece of its own
over the flattened belly (the belly up to 8.9 px, the carapace from 7.6 px to 18 px):
- `back` (first transformation): the rear of the body, from its middle (y 9) to its tail's root
  (y 46), x ±26 at its widest; bone ribs clamped over it, a lime vein down its spine, glands on its
  flanks, a riveted plate. The racks lie under it.
- `breast` (second transformation): the front of the body, from its middle to the necks' roots
  (y -31), x ±26 at its widest; a riveted keel plate, lime veins fanning out towards the necks,
  armour bands on its flanks. The batteries and the orb lie under it.

Neither is mirrored; each bursts into plates cracked from its outline and leaves a `shell` lattice
frame over the belly.

**Acceptance criteria**
- Given its design, then each transformation sheds its region and its weapons lie in it (unit
  test).
- Given its model, then it draws both regions, and it holds together at rest and after each
  transformation (unit tests).

*Sources: Lab request, D-254.*

### Behaviour

#### FB-TRI-WING-HYDRA-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs, its necks swinging all the while. While it is fought the ground
scrolls at ×0.8.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.8 of the level's speed and back after it.

*Sources: Lab request.*

#### FB-TRI-WING-HYDRA-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `head-left`, `head-right`,
`shoulder-left`, `shoulder-right` and `head-centre`, in that order (the order the debug key breaks
them). Its core has no gun: once its last weapon is destroyed (none still hidden), it dies
(BOSS-58), and its core's health does not count in its health bar.

**Acceptance criteria**
- Given its design, then its five parts all shield the core and its core has no mount (unit test on
  its design).

*Sources: Lab request.*

#### FB-TRI-WING-HYDRA-08 — Stage patterns · MUST

Its parts fire in every stage while they stand:
- the outer heads: aimed spreads of 3 green bullets, 10° apart, swept from their turrets, the two in
  turn, so their shots cross at the player from either side;
- the middle head: fans of 5 orange bullets, 12° apart, straight down;
- the missile shoulder: pairs of homing missiles;
- the laser shoulder: a laser straight down, with its warning line.

Each stage adds a volley of its own from the heads left (the core has no gun), so the pattern of a
stage is never that of the stage before it:
- stage 0: nothing more;
- stage 1: a burst of 3 at the player from the middle head;
- stage 2: a burst of 4;
- stage 3: an aimed spread of 3;
- stage 4: a burst of 5;
- stage 5 (every part there from the start gone): a second spiral from the orb, turning the other
  way from its own (its last stage's ring, used in no earlier stage).

**Acceptance criteria**
- Given each stage, then it fires that stage's volleys (BOSS-21 unit tests).

*Sources: Lab request.*

#### FB-TRI-WING-HYDRA-09 — Angry · MUST

It is angry after each transformation: the weapons that transformation revealed fire all out for
`boss_rage_seconds`, `boss_rage_rate` times as often (the racks three times as many missiles),
instead of its stage's pattern ([common](../common.md), BOSS-27).

**Acceptance criteria**
- Given each transformation is over, then it is angry and fires only the weapons it revealed (unit
  test).

*Sources: Lab request, D-256.*

#### FB-TRI-WING-HYDRA-10 — First transformation: back plating · MUST

Once both outer heads are destroyed, its back plating bursts off, baring a dark metal lattice, and
two **racks** unfold either side of its spine. They shield the core and fire pairs of homing
missiles, in turn.

**Acceptance criteria**
- Given both outer heads destroyed, then it transforms and its racks are revealed (unit test on its
  `transformParts`).

*Sources: Lab request, D-221, D-229.*

#### FB-TRI-WING-HYDRA-11 — Second transformation: breastplate · MUST

Once both shoulders are destroyed, its breastplate bursts off, baring a dark metal lattice, and two
**batteries** unfold either side of its centre line, sweeping fans of 7 straight down, and an
**orb** on its centre line, firing turning rings of 10.

**Acceptance criteria**
- Given both shoulders destroyed, then it transforms and its batteries and orb are revealed (unit
  test on its `transformParts`).

*Sources: Lab request, D-221, D-229.*

#### FB-TRI-WING-HYDRA-12 — Laser colour · MUST

Its laser (warning line, beam, base flare) is drawn in its own neon colour folded into the enemy
shots' family ([common](../common.md), BOSS-32).

**Acceptance criteria**
- Given its laser, then its colour is its neon folded into the enemy shots' family (unit test).

*Sources: Lab request.*

#### FB-TRI-WING-HYDRA-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its revealed weapons 30 %, its core always one
([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: Lab request.*

## Tunable values

All in `src/game/config/bosses/lab/tri_wing_hydra.py` (`_TRI_WING_HYDRA`, `TRI_WING_HYDRA`); its
model in `src/game/view/bosses/lab/tri_wing_hydra_model.py` and `tri_wing_hydra_parts.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 4.5 L (radius 76.5 px) | |
| core | radius 22, drop 1; never hit (no gun) | `coreRadius`, `coreDrop`; `coreHealth` 2 000 unused |
| necks (joints) | roots at (∓15, -22) swinging ±9° over 4.4 s (the right one half a swing late, 0.45), and (0, -27) swinging ±7° over 3.6 s (0.2) | `stats.joints` |
| `head-left`, `head-right` | (∓54, -46), radius 12, health 800, shield, drop 0.6, on their necks | |
| `head-centre` | (0, -70), radius 12, health 800, shield, drop 0.6, on its neck | |
| `shoulder-left`, `shoulder-right` | (∓30, -6), radius 13, health 850, shield, drop 0.6 | |
| head turrets | on the heads' centres, 10.5 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 5; at rest the outer ones 35° out | `HEAD_GUN`, `mounts` |
| missile block | (-30, -4), 13 px high; 4 ports | `mounts` `shoulder-left` |
| laser | (30, -10), 13 px high; bore 2.2, 10 px long, base radius 4.5; fixed, down the screen | `mounts` `shoulder-right` |
| full health | 8 010 (4 100 without the hidden weapons), the core left out | BOSS-54, BOSS-58; the Storm Petrel's 8 410 |
| points | 8 000; 800 a part | |
| ground speed | ×0.8 | |
| stop height | 0.73 | |
| sway / bob | 40 px over 9 s / 8 px over 4.2 s | |
| outer heads | aimed 3, 10° apart, green 180 px/s, every 2.2 s (first 0.8 s / 1.9 s) | a sweep |
| middle head | fan of 5, 12° apart, orange 175 px/s, every 2.6 s (first 1.4 s) | a sweep |
| shoulder missiles | 2, 30° apart, every 6 s (first 3 s) | |
| shoulder laser | 1.4 s beam every 6.5 s (first 4.5 s) | |
| stage 1 | middle head: burst of 3, 0.16 s apart, every 2.8 s | |
| stage 2 | middle head: burst of 4, 0.14 s apart, every 2.4 s | |
| stage 3 | middle head: aimed 3, 10° apart, every 2.4 s | |
| stage 4 | middle head: burst of 5, 0.12 s apart, every 2.2 s | |
| stage 5 | orb: ring of 10 green, turning -13°, every 2.6 s (first 2 s) | |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation 1 | `head-left` and `head-right` destroyed | `transformParts` |
| back region (shed) | x ±23 at y 9 widening to ±26 at y 18, narrowing to (0, 46), `shell`, not mirrored | `armour_region` `back` |
| racks | (∓12, 25), radius 8, health 680, pod from 8 px to 12 px, green; first 1.2 s / 2.0 s | |
| transformation 2 | `shoulder-left` and `shoulder-right` destroyed | |
| breast region (shed) | x ±23 at y 9 widening to ±26 at y -4, narrowing to (0, -31), `shell`, not mirrored | `armour_region` `breast` |
| batteries | (∓15, -13), radius 8, health 850, deck from 8 px to 12 px, orange; first 1.2 s / 2.0 s | |
| orb | (0, 3), radius 7, health 850, pod from 8 px to 11 px, green; first 1.6 s | on the centre line |
| fire rate (BOSS-39) | 6.5, 6.8 and 16.4 weighted shots a second as it comes in and after each transformation | |
| neon | lime (0.6, 1, 0.1), shown green | `BOSS_LOOK.neon` |
