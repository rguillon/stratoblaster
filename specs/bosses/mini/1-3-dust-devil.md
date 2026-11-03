# Dust Devil

> **Area:** bosses · **Prefix:** `MB-DUST-DEVIL` · **Related:** [common](../common.md),
> [1-3 Green Country](../../worlds/world-1/1-3-green-country.md),
> [Mesa Fortress](../final/1-3-mesa-fortress.md), [World 1](../../worlds/world-1/world.md)

The Dust Devil is the mini boss of 1-3: a desert whirl-jelly, 3 L across (first designed as a gyro
gunship with a turning blade ring). A ring of sinew turns slowly round its fleshy bell, carrying
three blade pods that fire spirals and shield its core. Once two pods are gone it sheds its back
plating and unfolds a pair of orbs. Shared rules are in [common](../common.md).

## Requirements

### Look

#### MB-DUST-DEVIL-01 — Silhouette and size · MUST

Seen from above, the Dust Devil is round, 3 L across: a swollen bell in its middle and a ring round
it carrying three blade pods 120° apart, the ring turning slowly clockwise.

**Acceptance criteria**
- Manual validation in the boss viewer: a round creature whose outer ring and pods turn.

*Sources: P07-R05, P16-R05.*

#### MB-DUST-DEVIL-02 — Body · MUST

Its core is a swollen fleshy bell (a gyro disc grown over, slate and sinew shades) with plated ribs
radiating across its cap (the plating of MB-DUST-DEVIL-05, round the hub on its middle), a charge
gland on its crown (its ring emitter, on the hub), eyes at its front and its reactors in flesh sacs
behind. The ring is a sinew collar round the bell, a fleshy rim, three
tentacle spokes out to the pods and membrane fins between them.

**Acceptance criteria**
- Manual validation: a fleshy bell with grafted ribs, its ring of sinew and membrane.

*Sources: P07-R05, P16-R05.*

#### MB-DUST-DEVIL-03 — Its parts · MUST

- **Blade pods** (three, on the ring): each a sand ray clinging to the rim, its wide fleshy wings
  plated at the front, a bone barb at each wing tip carrying a muzzle. They turn with the ring.
- **Crown emitter** (the core's gun): the gland on the bell's crown; it does not turn.

**Acceptance criteria**
- Given its model, then the three pods are on its ring and turn with the boss's spin (unit test).

*Sources: P07-R05, P16-R05.*

#### MB-DUST-DEVIL-04 — Lights · MUST

Amber veins and glands light its bell, ring and pods. Its neon colour, set amber, shows bright
yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: P07-R05, P16-R05, D-231.*

#### MB-DUST-DEVIL-05 — Back plating · MUST

The plating over the middle of its bell is the armour it sheds at its transformation
([common](../common.md), BOSS-42): the bell's domed cap, a shell of revolution drawn as a piece of its
own over the flattened disc (the disc up to 2.2 px; the cap from 2 px at its rim, 15.2 px out, sunk
into the disc, up to 7.7 px round the hub that carries the emitter), the bone ribs radiating down it
to its rim, the plated ribs and the nose plate grafted on it, a vein down each side. Its region is
two half-rings round the hub, from 4.8 to 15.2 px out (`back`, the right one mirrored); it bursts
into plates cracked from those outlines and leaves a `shell` lattice frame on the disc, round the
hub. The pair of orbs lies folded under it.

**Acceptance criteria**
- Given its design, then its one transformation sheds the back region and both orbs lie in it
  (unit test).
- Given its model, then it draws the back region's armour, and it holds together with and without
  it (unit tests).

*Sources: D-221, D-224, D-254.*

### Behaviour

#### MB-DUST-DEVIL-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, its ring already turning, then sways and bobs. Its ring turns at `spinRate` all the time.
While it is fought the ground scrolls at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.5 of the level's speed and back after it.

*Sources: P07-R03, P07-R05.*

#### MB-DUST-DEVIL-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `blade-1`, `blade-2` and `blade-3`, on
the turning ring ([common](../common.md), BOSS-34). Each pod fires a ring of 2 green bullets turning
at each volley (a 2-way spiral) from its barbs, the three one after the other. The crown emitter
fires the core's volleys.

**Acceptance criteria**
- Given its design, then its three pods orbit and shield the core (unit test on its design).

*Sources: P07-R01, P07-R05.*

#### MB-DUST-DEVIL-08 — Stage patterns · MUST

The pods' spirals go on in every stage while they stand. The core fires:
- stage 0: one orange bullet at the player;
- stage 1: an aimed fan of 3;
- stage 2: a burst of 4 at the player;
- stage 3 (all three pods gone): a ring of 12 turning at each volley (a spiral).

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and the parts left fire theirs
  (unit test on its design).

*Sources: P07-R04, D-055.*

#### MB-DUST-DEVIL-09 — Angry · MUST

Its angry pattern is a **vortex** at heat 2 (a fast green spiral, purple bursts at the player).

**Acceptance criteria**
- Given its design, then its rage is that pattern at that heat, fired from its core.

*Sources: D-063.*

#### MB-DUST-DEVIL-10 — Transformation · MUST

It transforms once, when two pods are destroyed: the plating of its bell bursts off, baring a dark
metal lattice, and two **orbs** unfold either side of its centre. They shield the core and fire
green rings of 10, in turn.

**Acceptance criteria**
- Given two pods destroyed, then it transforms and its two orbs are revealed.

*Sources: D-221, D-224, D-229.*

#### MB-DUST-DEVIL-11 — Death, drops and points · MUST

Its pods drop a weapon bonus half of the time, its orbs 30 %; it drops a life bonus as a mini boss
([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: P07-R07.*

## Tunable values

All in `src/game/config/bosses/mini_bosses.py` (`_DUST_DEVIL`, `DUST_DEVIL`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (radius 51 px) | |
| core | health 1 230, radius 18 | crown emitter at (0, 0), 10 px high |
| `blade-1`, `blade-2`, `blade-3` | (0, -40), (34.6, 20), (-34.6, 20); radius 14, health 620, shield, drop 0.5, orbiting | |
| `spinRate` | 0.7 rad/s | ring turn |
| full health | 4 090 | BOSS-54 |
| points | 4 000; 400 a part | |
| ground speed | ×0.5 | |
| stop height | 0.72 | |
| sway / bob | 60 px over 9 s / 10 px over 3 s | |
| pod spirals | rings of 2 turning 23°, green 180 px/s, every 1 s (first 0.4 / 0.73 / 1.06 s) | |
| core stage 0 | 1 aimed orange bullet, 170 px/s, every 3 s | |
| core stage 1 | aimed 3, 12° apart, every 2.6 s | |
| core stage 2 | burst of 4, 0.14 s apart, every 2.4 s | |
| core stage 3 | ring of 12 turning 15°, every 1.5 s | |
| angry | vortex, heat 2 (36 bullets a second, 136 px/s), green and purple | |
| transformation | 2 parts destroyed | default threshold |
| shed region | back: two half-rings round the hub, 4.8..15.2 px out, mirrored, `shell`; cap 2–7.7 px | `armour_region` |
| orbs | (∓12, 5), radius 8, health 500, pod 10.2 px; first 1.2 s / 2.0 s | |
| neon | amber (1, 0.75, 0.15), shown yellow | `BOSS_LOOK.neon` |
