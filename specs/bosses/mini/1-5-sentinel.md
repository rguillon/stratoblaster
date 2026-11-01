# Sentinel

> **Area:** bosses · **Prefix:** `MB-SENTINEL` · **Related:** [common](../common.md),
> [1-5 Deep Desert](../../worlds/world-1/1-5-deep-desert.md), [Overlord](../final/1-5-overlord.md),
> [Hornet](../../enemies/hornet.md), [World 1](../../worlds/world-1/world.md)

The Sentinel is the mini boss of 1-5, the hardest mini boss of World 1: a twin-bodied city hunter,
3.5 L across (first designed as a twin-hull police interceptor), its two bodies lit in two colours
like police lights. A gun on each body and a drone bay at its nose, launching Hornets, shield its
core. Once two of its parts are gone it sheds its back plating and unfolds a pair of missile racks.
Shared rules are in [common](../common.md).

## Requirements

### Look

#### MB-SENTINEL-01 — Silhouette and size · MUST

Seen from above, the Sentinel is 3.5 L across: two long bodies side by side, pointing down the
screen, joined through a thorax by a membrane, a hull gun on each body's outer flank and a brood
pouch at the nose, between the bodies. Each body ends in a tail fin.

**Acceptance criteria**
- Manual validation in the boss viewer: two bodies joined in the middle, a gun on each, a pouch at
  the nose.

*Sources: P07-R05, P16-R05.*

#### MB-SENTINEL-02 — Body · MUST

Each body is a long segmented worm (slate and graphite shades) with a shell plated on its back, lit
veins along its flanks and a tail fin of membrane on bone struts; a reactor in a flesh sac at each
tail, a third behind the thorax. The thorax carries glands and the core's two guns, built into it.
Grafts differ between the bodies: a radome and a mast on one, a searchlight and an extra plate on
the other, and a whip antenna off-centre on the thorax.

**Acceptance criteria**
- Manual validation: the two bodies are not alike in their grafts.

*Sources: P07-R05, P16-R05.*

#### MB-SENTINEL-03 — Its parts · MUST

- **Hull guns** (one on each body's outer flank): an armoured growth under a twin-barrelled turret.
- **Drone bay** (at the nose, in front of the core): a swollen brood pouch, its slit lit, launch
  glands at its corners and two drones hatching from it, a grafted rim plate behind.

**Acceptance criteria**
- Given its model, then it draws both hull guns, their turrets and the drone bay (unit test).

*Sources: P07-R05, P16-R05, D-058.*

#### MB-SENTINEL-04 — Lights · MUST

Its left body (the screen's left) is lit in its neon, set blue, which shows bright green; its right
body is lit in a police red, which shows bright yellow ([common](../common.md), BOSS-50). Police-
light glands on its back, its eyes, its drones and its reactors take the colour of their side.

**Acceptance criteria**
- Given its model, then its left body's lights are green and its right body's yellow.

*Sources: P07-R05, P16-R05, D-231.*

#### MB-SENTINEL-05 — Back plating · MUST

The plating over the middle of its thorax, between the two bodies, is the armour it sheds at its
transformation (a `shell` lattice frame beneath); the pair of racks lies folded under it.

**Acceptance criteria**
- Given its design, then its one transformation sheds the back region and both racks lie in it
  (unit test).

*Sources: D-221, D-224.*

### Behaviour

#### MB-SENTINEL-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs. While it is fought the ground scrolls at ×0.6.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.6 of the level's speed and back after it.

*Sources: P07-R03, P07-R05.*

#### MB-SENTINEL-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `gun-left`, `gun-right` and the
`drone-bay`, which hangs in front of the core so shots from below reach it. Each hull gun's turret
fires aimed pairs at the player, blue from the left and red from the right, in turn. The drone bay
launches Hornets ([common](../common.md), BOSS-25) in every stage while it stands. The core's two
fixed guns fire the core's volleys.

**Acceptance criteria**
- Given its design, then its drone bay launches 2 Hornets every 5.5 s while it stands.

*Sources: P07-R01, P07-R05, D-053, D-055, D-058.*

#### MB-SENTINEL-08 — Stage patterns · MUST

The hull guns' pairs and the bay's Hornets go on in every stage while they stand. The core fires:
- stage 0: a fan of 3 blue bullets;
- stage 1: a fan of 5 red;
- stage 2: a fan of 7 blue;
- stage 3 (all three parts gone): a ring of 14 red turning at each volley, and a fan of 5 blue.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and the parts left fire theirs
  (unit test on its design).

*Sources: P07-R04, D-055.*

#### MB-SENTINEL-09 — Angry · MUST

Its angry pattern is a **curtain** at heat 4 (blue fans sweeping across and back, a red ring under
them), the densest of the World 1 mini bosses.

**Acceptance criteria**
- Given its design, then its rage is that pattern at that heat, fired from its core.

*Sources: D-063.*

#### MB-SENTINEL-10 — Transformation · MUST

It transforms once, when two of its parts are destroyed: the plating of its thorax bursts off,
baring a dark metal lattice, and two **racks** unfold either side of its centre line. They shield
the core and fire pairs of homing missiles, in turn.

**Acceptance criteria**
- Given two parts destroyed, then it transforms and its two racks are revealed.

*Sources: D-221, D-224, D-229.*

#### MB-SENTINEL-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its racks 30 %; it drops a life bonus as a mini boss
([common](../common.md), BOSS-57). The Hornets it launched count among the level's spawned enemies.
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: P07-R07, D-055.*

## Tunable values

All in `src/game/config/bosses/mini_bosses.py` (`_SENTINEL`, `SENTINEL`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.5 L (radius 59.5 px) | |
| core | health 1 570, radius 18 | twin guns at (±15, -12.5), 1 px high, fixed |
| `gun-left`, `gun-right` | (∓40, -8), radius 13, health 780, shield, drop 0.5 | turrets on their centres |
| `drone-bay` | (0, -36), radius 15, health 780, shield, drop 0.5 | |
| full health | 5 150 | BOSS-54 |
| points | 5 000; 500 a part | |
| ground speed | ×0.6 | |
| stop height | 0.74 | |
| sway / bob | 70 px over 6.5 s / 8 px over 3 s | |
| hull gun pairs | aimed 2, 8° apart, blue 185 / red 190 px/s, every 1.7 s (first 0.8 s / 1.65 s) | |
| Hornets | 2 every 5.5 s (first 3 s), 14 px apart | `launches`; `src/game/sim/bosses/boss_launches.py` |
| core stage 0 | fan of 3, 16° apart, blue, every 2.8 s | |
| core stage 1 | fan of 5, 14° apart, red, every 2.4 s | |
| core stage 2 | fan of 7, 12° apart, blue, every 2.2 s | |
| core stage 3 | ring of 14 turning 7°, red, every 1.3 s; fan of 5 blue every 2.6 s | |
| angry | curtain, heat 4 (52 bullets a second, 152 px/s), blue and red | |
| transformation | 2 parts destroyed | default threshold |
| shed region | back: x -28..28, y -35..21, above 4.2 px, `shell`, not mirrored | |
| racks | (∓12, -7), radius 8, health 620, pod 6.1 px; first 1.2 s / 2.0 s | |
| neon | blue (0.15, 0.4, 1), shown green; other body police red (1, 0.08, 0.1), shown yellow | `BOSS_LOOK.neon`; `src/game/view/bosses/sentinel_model.py` `POLICE_RED` |

## Notes

- The drone bay had no place in the first spec; it hangs in front of the core so that shots from
  below reach it (D-053, D-055).
- Its city-hunter look comes from the first spec, written when 1-5 ended over a city; 1-5 is now
  the deep desert (no city in World 1, reviewer 2026-10-27; D-200). Re-theming it is the reviewer's
  call.
