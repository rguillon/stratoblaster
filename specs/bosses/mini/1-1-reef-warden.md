# Reef Warden

> **Area:** bosses · **Prefix:** `MB-REEF-WARDEN` · **Related:** [common](../common.md),
> [1-1 Open Sea](../../worlds/world-1/1-1-open-sea.md), [Storm Petrel](../final/1-1-storm-petrel.md),
> [World 1](../../worlds/world-1/world.md)

The Reef Warden is the mini boss of 1-1, the first boss of the game: a wide ray-like reef creature,
3 L across, met over the open sea. Two side cannons on its flanks shield its core; once one is gone
it sheds its back plating and unfolds a pair of gatlings. It is the easiest boss of the game. Every
shared rule (parts, shield, stages, rage, transformations, death) is in [common](../common.md).

## Requirements

### Look

#### MB-REEF-WARDEN-01 — Silhouette and size · MUST

Seen from above, the Reef Warden is a wide ray, 3 L across: a mantle pointed at its snout (down the
screen), widest at its flanks, where its two side cannons grow, and cut broad at its tail, with short
tentacles trailing behind.

**Acceptance criteria**
- Manual validation in the boss viewer: a wide ray-like creature, its cannons on its flanks.

*Sources: P07-R05, P16-R05.*

#### MB-REEF-WARDEN-02 — Body · MUST

Its body is a teal flesh mantle with a second, darker fold on it, a dark shelled back (slate and
membrane shell, sinew belly) along its spine, bone ribs across its back, coral barbs on its back and
before its cannons, gill glands either side (on its back plating, MB-REEF-WARDEN-05) and two eyes
over its snout. Metal is grafted on: a
riveted nose plate, a back plate, a plate on each flank, sockets for the cannons, a short mast off
the centre line, and a prow cannon on its snout. Two reactors sit in flesh sacs at its tail, with a
third reactor between them.

**Acceptance criteria**
- Manual validation: a living mantle with metal grafts; the mast off-centre.

*Sources: P07-R05, P16-R05.*

#### MB-REEF-WARDEN-03 — Its parts · MUST

- **Side cannons** (left and right, on its flanks): each an armoured coral growth with a feeding sac
  behind it and barbs before it, under a twin-barrelled turret.
- **Prow cannon** (the core's gun): a single-barrelled turret grafted on its snout.

**Acceptance criteria**
- Given its model, then it draws both side cannons and their turrets where its design puts them
  (unit test).

*Sources: P07-R05, P16-R05, D-060.*

#### MB-REEF-WARDEN-04 — Lights · MUST

A neon vein ring runs round its mantle's rim; veins run out across its back to its flanks, along its
spine and round each cannon's foot; its glands and eyes glow. Its neon colour, set as cyan, shows
bright green ([common](../common.md), BOSS-50). Navigation lamps sit at its tail, port (the
screen's left) and starboard; set red and green, they show yellow and green.

**Acceptance criteria**
- Given its model, then its lights are bright green, its port lamp yellow.

*Sources: P07-R05, P16-R05, D-231.*

#### MB-REEF-WARDEN-05 — Back plating · MUST

Its back plating, from just behind its snout to its middle, is the armour it sheds at its
transformation ([common](../common.md), BOSS-42): a dark fold of plating drawn as a piece of its own,
a horseshoe round its shelled back lying on the mantle's back (from 2.7 px, sunk into the mantle, up
to 4.5 px), a gill gland on each of its arms and a vein running out across each. Its region is that
horseshoe (`back`, not mirrored); it bursts into plates cracked from that outline and leaves a
`shell` lattice frame on the mantle. The pair of gatlings lies folded under its arms.

**Acceptance criteria**
- Given its design, then its one transformation sheds the back region and both gatlings lie in it
  (unit test).
- Given its model, then it draws the back region's armour, and it holds together with and without
  it (unit tests).

*Sources: D-221, D-224, D-254.*

### Behaviour

#### MB-REEF-WARDEN-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs (`sway`, `bob`). While it is fought the ground scrolls at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to half the level's speed.

*Sources: P07-R03, P07-R05.*

#### MB-REEF-WARDEN-07 — Parts and core · MUST

It has two parts as it comes in, both shielding its core: `cannon-left` and `cannon-right`. Each
side cannon's turret fires bursts of 3 red bullets at the player, the two in turn; the prow cannon
on its turret fires the core's volleys. Both turrets turn the way they fire.

**Acceptance criteria**
- Given its design, then it has two parts, both shielding the core, with the health and places of
  Tunable values.

*Sources: P07-R01, P07-R05, D-058, D-060.*

#### MB-REEF-WARDEN-08 — Stage patterns · MUST

The side cannons' bursts go on in every stage while they stand. The core fires:
- stage 0: a fan of 3 orange bullets straight down;
- stage 1: a fan of 5;
- stage 2 (both cannons gone): a ring of 8 turning a little at each volley (a spiral).

**Acceptance criteria**
- Given each stage, then the core fires that stage's volley (unit test on its design).

*Sources: P07-R04, D-055.*

#### MB-REEF-WARDEN-09 — Angry · MUST

It is angry after its transformation, when the two gatlings it revealed fire all out,
for `boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's
pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it has no
angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only the two gatlings it
  revealed (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-063, D-256.*

#### MB-REEF-WARDEN-10 — Transformation · MUST

It transforms once, when one of its side cannons is destroyed: its back plating bursts off, baring a
dark metal lattice, and two **gatlings** unfold just in front of its core, on either side of its
centre line. They shield the core and fire red bursts of 4 at the player, in turn.

**Acceptance criteria**
- Given one side cannon destroyed, then it transforms and its two gatlings are revealed (unit test
  on its thresholds).

*Sources: D-221, D-224, D-229.*

#### MB-REEF-WARDEN-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its gatlings 30 % of the time; its core follows the
regular enemies' chance and it drops a life bonus ([common](../common.md), BOSS-57). It scores the
points of Tunable values.

**Acceptance criteria**
- Given its design, then its cannons' drop chance is 0.5 and its gatlings' 0.3.

*Sources: P07-R07.*

## Tunable values

All in `src/game/config/bosses/mini_bosses.py` (`_REEF_WARDEN`, `REEF_WARDEN`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (radius 51 px) | `stats.size` |
| core | health 960, radius 20 | `coreHealth`, `coreRadius` |
| `cannon-left`, `cannon-right` | (∓36, -2), radius 14, health 620, shield, drop 0.5 | turrets on their centres |
| full health | 3 200 (core, cannons, gatlings) | BOSS-54 |
| points | 3 000; 300 a part | `stats.points`; `src/game/config/scoring.py` |
| ground speed | ×0.5 | `groundSpeed` |
| stop height | 0.72 of the playfield | `stopFraction` |
| sway / bob | 70 px over 7 s / 8 px over 3.5 s | `sway`, `bob` |
| side cannon bursts | 3 red, 0.18 s apart, 190 px/s, every 2.6 s (first 1 s / 2.3 s) | |
| core stage 0 | fan of 3, 18° apart, orange 170 px/s, every 3.2 s | prow turret pivot (0, -27) |
| core stage 1 | fan of 5, 14° apart, every 2.2 s | |
| core stage 2 | ring of 8 turning 11°, every 1.8 s | |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation | 1 part destroyed | default threshold |
| shed region | back: a horseshoe round the shelled back, y -33..-2, its arms x 15..23 at the rear narrowing towards the snout, joined by a bar y -33..-27 at the centre line; `shell`, not mirrored; plating 2.7–4.5 px | `armour_region` |
| gatlings | (∓13, -25), radius 11, health 500, pod 8 px; red bursts, first 1.2 s / 2.0 s | `hidden_weapon` |
| neon | cyan (0.1, 0.9, 1), shown green | `src/game/config/boss_look.py` `BOSS_LOOK.neon` |
