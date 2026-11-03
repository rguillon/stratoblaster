# Broodmother

> **Area:** Enemies (tier 3, carrier) · **Prefix:** `ENM-BROODMOTHER` · **Related:** [common rules](common.md),
> [Phantom](phantom.md), [Carrier](carrier.md), [Hive](hive.md)

The Broodmother is the carrier kind of tier 3 (World 3, [common.md](common.md)): a huge, slow brood
body that flies straight down the screen without ever shooting, launching [Phantoms](phantom.md)
one at a time from a hatch on its belly, until it gets too close to the player.

## Requirements

### Look

#### ENM-BROODMOTHER-01 — A huge brood body · MUST

The Broodmother is about `size` L (2 L) long: a huge, swollen body of four fat segments under a
ridged shell, much bigger than the other tier 3 kinds.

*Sources: tier 3 rework (ENM-01).*

#### ENM-BROODMOTHER-02 — Flesh body under armour plates · MUST

Its body is flesh ([common.md](common.md), Cyber-Organic), with metal grafted on: armour plates on
its back (a riveted middle plate and a plate on each shoulder), a cradle under each egg sac, and its
reactors set in flesh sacs, with veins and eyes lit in its neon.

**Acceptance criteria**
- Unit test: the model has flesh, metal, lit veins and two reactors.

*Sources: tier 3 rework.*

#### ENM-BROODMOTHER-03 — Egg sacs that glow · MUST

Three egg sacs sit along each flank. They are charge lights: they glow as the next launch nears,
following `Enemy.charge` (0 to 1 over each launch interval), and are dark below the lowest height it
launches from.

**Acceptance criteria**
- Unit test: the model's charge lights are on both flanks.
- Given a Broodmother over the playfield, then its charge rises towards each launch and resets
  after it.

*Sources: tier 3 rework, ENM-23.*

#### ENM-BROODMOTHER-04 — A hatch on its belly · MUST

A dark hatch collar hangs on its belly near the front, its mouth a charge light. The hatch is the
muzzle (`launch`) where Phantoms come out: the model and the simulation read the same `port`.

**Acceptance criteria**
- Unit test: the model has one `launch` muzzle at the configured port.

*Sources: tier 3 rework.*

#### ENM-BROODMOTHER-05 — Triangle budget · MUST

The Broodmother's model (reactors included) stays within the tier 3 budget,
`ENEMY_LOOK.budget.tier3` (900, [common.md](common.md)).

**Acceptance criteria**
- Unit test: its triangle count is at most the tier 3 budget.

*Sources: tier 3 rework, ENM-03.*

### Behaviour

#### ENM-BROODMOTHER-06 — A slow, straight descent; it never shoots · MUST

The Broodmother comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) and flies straight down at `speed`, nose down, then leaves at the bottom. It never
fires a bullet, missile or laser.

**Acceptance criteria**
- Given a Broodmother, then its X never changes, it moves down at `speed`, and it never fires.

*Sources: tier 3 rework.*

#### ENM-BROODMOTHER-07 — It launches Phantoms, one at a time · MUST

While its centre is over the playfield and above `lastFraction` of its height, every
`launchInterval` (7 s; the first `firstLaunch` after it is over the playfield) it launches one
[Phantom](phantom.md) from the hatch. The Phantom is an ordinary Phantom, made through its public
constructor, coming in `launchDrop` below the hatch; it is an enemy of its own and stays when the
Broodmother is destroyed.

**Acceptance criteria**
- Given a Broodmother over the playfield, when its launch timer runs out, then one Phantom is
  spawned at the hatch.

*Sources: tier 3 rework, ENM-07.*

#### ENM-BROODMOTHER-08 — The Phantom's model is a child model · MUST

The Phantom's model is one of the child models built with every level's own
(`CHILD_MODELS` in `src/game/view/enemies/enemy_bindings.py`), so no model is built in play when
the Broodmother launches.

**Acceptance criteria**
- Unit test: `phantom` is among the child models and the models.

*Sources: tier 3 rework, PERF-21.*

#### ENM-BROODMOTHER-09 — Quiet in the lower part · MUST

Below `lastFraction` (30 %) of the playfield height, too close to the player, it stops launching and
its charge is 0; it flies on down and off the screen.

**Acceptance criteria**
- Given a Broodmother below 30 % of the height, then it launches no Phantom.

*Sources: tier 3 rework.*

#### ENM-BROODMOTHER-10 — Tier 3 colours · MUST

It is a tier 3 kind: its lights and reactor flames are the chartreuse neon of the tier and its hull
is tinted indigo, applied by the model builder from the tier table (ENM-49).

*Sources: tier 3 rework, ENM-49.*

#### ENM-BROODMOTHER-11 — Health and points · MUST

A Broodmother has `hp` health and scores `points`. Its hit circle is 0.8 of the usual one for its
size.

**Acceptance criteria**
- Given a Broodmother, then it takes 700 damage to destroy and scores 1200 points.

*Sources: tier 3 rework, GD-21.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 2 L | `src/game/config/enemy_broodmother.py` `BROODMOTHER_CONFIG` |
| `hp` / `points` | 700 / 1200 | `stats` |
| hit radius | `radius(2) * 0.8` | |
| `speed` | 22 px/s | straight down |
| `launchInterval` / `firstLaunch` | 7 s / 2.5 s | not scaled by the level's fire rate |
| `port` | (0, −22) | the hatch, ahead of the centre |
| `launchDrop` | 60 px | where a launched Phantom comes in to, below the hatch |
| `lastFraction` | 0.3 | no launch below it |
| `xRange` | 0.3–0.7 | of the ship's reach |
| triangle budget | 900 (tier 3) | `ENEMY_LOOK.budget.tier3` |
| `neon` | tier 3's | `ENEMY_LOOK.neon.broodmother` |

## Notes

**Appears in:** World 3 (`src/game/config/wave_plans.py`).

- Model: `src/game/view/enemies/tier3_broodmother_model.py`. Sim: `src/game/sim/enemies/broodmother.py`.
- It launches like the [Hive](hive.md) launches Wasps, one at a time.
