# Hatchery

> **Area:** enemies · **Prefix:** `ENM-HATCHERY` · **Related:** [common.md](common.md),
> [carrier.md](carrier.md), [hive.md](hive.md), [wasp.md](wasp.md)

The Hatchery is the carrier of **tier 2** (World 2, lime neon on a teal hull, over a rust/concrete
industrial desert): a big, slow egg-pod that flies straight down the screen without ever shooting,
launching a group of three [Wasps](wasp.md) from its ventral hatch every 6 s, until it gets too
close to the player. Wasps are tier 2's diver.

## Requirements

### Look

#### ENM-HATCHERY-01 — An armoured egg pod · MUST

The Hatchery is a big egg-shaped pod about `size` L long: a swollen flesh body of three segments
under three metal armour plates on its back, each with two lime neon bands, and two bone ribs
arched over it.

*Sources: tier 2 brief.*

#### ENM-HATCHERY-02 — A launch hatch under its belly · MUST

A launch hatch (dark doors in a ring of charge light) sits under its belly towards the player's
side, where `hatch` says; the Wasps come out of it (the model and the simulation read the same
`hatch`).

*Sources: tier 2 brief.*

#### ENM-HATCHERY-03 — A charge light that brightens before each launch · MUST

The hatch's ring and a lamp on each flank are charge lights: they brighten as the next launch nears
(`Enemy.charge`, ENM-23).

*Sources: tier 2 brief.*

#### ENM-HATCHERY-04 — Two reactors, lime · MUST

Two reactors sit at the back, each in a flesh sac. Every light and the reactor flames are tier 2's
lime neon (ENM-48).

*Sources: tier 2 brief, ENM-48.*

### Behaviour

#### ENM-HATCHERY-05 — A slow, straight descent · MUST

The Hatchery comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) and flies straight down at `speed`, nose down, then leaves at the bottom.

*Sources: tier 2 brief.*

#### ENM-HATCHERY-06 — It never shoots · MUST

The Hatchery never fires a bullet, missile or laser.

**Acceptance criteria**
- Given a Hatchery, then it never fires.

*Sources: tier 2 brief.*

#### ENM-HATCHERY-07 — A group of three Wasps from the hatch · MUST

While it is over the playfield, the Hatchery launches every `launchInterval` (the first
`firstLaunch` after it comes over the playfield) a group of 3 [Wasps](wasp.md) from its hatch,
spread across `group`, each flying down `launchDrop` before its pause, then attacking as an
ordinary Wasp. Its launches do not follow the level's fire-rate factor.

**Acceptance criteria**
- Given a Hatchery over the playfield, when its launch timer runs out, then three Wasps appear at
  its hatch.

*Sources: tier 2 brief.*

#### ENM-HATCHERY-08 — No launch low on the screen · MUST

The Hatchery stops launching once it is below `lastLaunchFraction` of the playfield height, too
close to the player.

*Sources: tier 2 brief.*

#### ENM-HATCHERY-09 — Health and points · MUST

The Hatchery has 400 health and scores 700 points. Its hit radius is a little smaller than its
size.

*Sources: tier 2 brief, GD-21.*

#### ENM-HATCHERY-10 — Triangle budget · MUST

Its model stays within `ENEMY_LOOK.budget.tier2` (600 triangles, reactors counted as about 40).

*Sources: ENM-03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1.7 L | `src/game/config/enemy_hatchery.py` `HATCHERY_CONFIG` |
| `hp` / `points` | 400 / 700 | |
| hit radius | 19.7 px | `radius(1.7) × 0.8` |
| `speed` | 32 px/s | |
| `launchInterval` / `firstLaunch` | 6 s / 2.5 s | |
| `hatch` | (0, −14, 0) px | from its centre: towards the player's side |
| `group` | (−13, 0), (0, −7), (13, 0) px | where each Wasp of a group starts, from the hatch |
| `launchDrop` | 55 px | each Wasp's flight down before its pause |
| `lastLaunchFraction` | 0.3 | of the playfield height |
| `xRange` | 0.3–0.7 | of the ship's reach |
| `neon` | tier 2's, `[0.25, 1, 0.1]` | `ENEMY_TIERS`, ENM-48 |

## Notes

**Tier:** 2 (carrier). **Appears in:** World 2 (see `src/game/config/wave_plans.py`).
