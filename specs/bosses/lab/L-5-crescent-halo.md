# Crescent Halo

> **Area:** bosses · **Prefix:** `FB-CRESCENT-HALO` · **Related:** [common](../common.md),
> [Lamprey Coil](L-5-lamprey-coil.md), [Overlord](../final/1-5-overlord.md)

The Crescent Halo is the final boss of the Lab's level L-5. **Lab boss: in the dev viewer only**
(the dev menu's Bosses list, after the 40 bosses of the worlds); no level brings it in. A living
station 4.5 L across shaped as a crescent open at its front, its two horns pointing down the
screen, its core a floating organ in the hollow tethered to the ring. Six growths round the
crescent shield the core: rotors on its horns, laser glands on its flanks, turrets either side of
its back. It fires rotating patterns: spirals from its horns and its core turning against each
other, while its flanks' lasers wall the player in. It is one of the two Lab bosses that change
shape (BOSS-45): at its first transformation its horns swing closed into a full halo, bringing in a
pair of mortars; at its second its flank plates and its crest burst off for a pair of batteries and
a gatling on its centre line. Shared rules are in [common](../common.md).

## Requirements

### Look

#### FB-CRESCENT-HALO-01 — Silhouette and size · MUST

Seen from above, the Crescent Halo is a thick ring 4.5 L across, open at its front (down the
screen) between its two horns: a C whose horns point at the player. A floating organ sits in the
hollow, tethered to the back and flanks of the ring by three sinews. Once its horns have closed it
is a full ring, a halo round the organ.

**Acceptance criteria**
- Manual validation in the boss viewer: a crescent open at its front, then a closed halo.

*Sources: Lab brief (2026-11-05).*

#### FB-CRESCENT-HALO-02 — Body · MUST

The ring is a tube of flesh (slate and graphite stretches in turn) round the back from one horn to
the other, under ridged shell plates, bone ribs arching over it, pale gold veins round its inner and
outer rims, glands on it and reactor sacs on its outer rim behind the flanks. The core is a swollen
heart of flesh floating in the hollow, a dark metal cage band round its waist with a seam of light,
veins running down from its crown, eyes and glands on it, the metal seats of its rotor (on its
crown) and of its eye turret (on its front); three bowed sinews, each with a vein, tether it to the
ring's inner side (at the back and either side of it).

**Acceptance criteria**
- Manual validation: one living station, its core an organ held by its tethers (BOSS-52).

*Sources: Lab brief, BOSS-47, BOSS-49.*

#### FB-CRESCENT-HALO-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Horn growths** (`horn-left`, `horn-right`, on the horns, 54° from the nose): swollen nodes, a
  vein ring round each, under a six-barrelled rotor on a metal seat.
- **Flank glands** (`flank-left`, `flank-right`, on the ring 120° from the nose): lit organs with
  four glands round their crowns, a laser emitter on a metal seat in each, built in and pointing
  straight down the screen.
- **Back growths** (`back-left`, `back-right`, on the ring 150° from the nose): armoured mounds
  under a twin-barrelled turret on a metal seat.
- **Halo rotor** (the core's): twelve barrels round a hub on the organ's crown (its spirals and its
  last ring).
- **Eye turret** (the core's): three barrels side by side on the organ's front (its aimed shots,
  bursts and fans).

**Acceptance criteria**
- Given its model, then it draws its six growths and every gun mount.

*Sources: Lab brief, BOSS-58.*

#### FB-CRESCENT-HALO-04 — Lights · MUST

Pale gold veins run round its rims, along its horns' edges, over its organ and its tethers; its
glands, eyes, reactors and the seams of its seats glow. Its neon colour, pale gold, shows bright
yellow ([common](../common.md), BOSS-50); its lasers take it folded into the enemy shots' family
(BOSS-32).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: Lab brief, BOSS-32, BOSS-50.*

#### FB-CRESCENT-HALO-05 — What it moves and sheds · MUST

- **Horns** (moving pieces, BOSS-45): each horn is a flat-topped armoured sleeve over the ring's
  end, drawn as a piece of its own (`horns`, mirrored), from its tip 40° from the nose back to 104°,
  tapering from 13 px either side of the ring's centre line to 4 px at its tip, a bone ridge with
  barbs along its top, metal bands across it, veins along its edges. At the first transformation
  each swings 40° round the boss's centre (about the vertical), so the two tips meet at the nose and
  the ring is closed; the ring's ends stay inside the sleeves. They leave no frame. The horn growths
  stand on them: the transformation names them (BOSS-36), so they are gone before the horns move.
- **Flank plates** (`plates`, mirrored; shed at the second transformation): three shell plates over
  each flank of the ring, from 68° to 100°, under the horns at rest and bared once they have moved;
  they burst off and leave a `shell` lattice. The batteries lie folded under them.
- **Crest** (`crest`, not mirrored; shed at the second transformation): two ridged shell plates over
  the back of the ring (168° to 192°), bone spines and a riveted plate on them; they burst off and
  leave a `shell` lattice. The gatling lies folded under it.

**Acceptance criteria**
- Given its design, then its first transformation moves the horns, and its second sheds the plates
  and the crest, each weapon lying in a region its transformation sheds or riding a horn.
- Given its model, then it holds together at rest and after each transformation.

*Sources: Lab brief, BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### FB-CRESCENT-HALO-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs slowly. While it is fought the ground scrolls at ×0.4.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.4 of the level's speed and back after it.

*Sources: BOSS-03.*

#### FB-CRESCENT-HALO-07 — Parts and core · MUST

It has six parts as it comes in, all shielding its core: `horn-left`, `horn-right`, `flank-left`,
`flank-right`, `back-left` and `back-right`. The core's guns (the halo rotor and the eye turret)
fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its six parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### FB-CRESCENT-HALO-08 — Stage patterns · MUST

The parts fire in every stage while they stand: the horns' rotors spirals of 6, turning against
each other; the flanks' lasers straight down the screen in turn (walls either side of the hollow);
the back turrets aimed fans of 3, swept. The core fires, from its halo rotor, a ring of 12 (one
bullet a barrel) turning a little more at each volley, a new turn and pace at every stage, with its
eye turret's shots:
- stage 0: the spiral turning 10°, and a single aimed shot;
- stage 1: the spiral turning the other way (12°), and an aimed fan of 3;
- stage 2: the spiral turning 14°, much faster, and an aimed fan of 3;
- stage 3: the spiral turning back (9°), and a burst of 4;
- stage 4: the spiral turning 16°, and a fan of 5 down the screen;
- stage 5: the spiral turning back (18°), and a burst of 4;
- stage 6 (every part gone): the spiral turning 7°, three times as fast as in stage 0, and a fan of
  7 down the screen.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys.

*Sources: BOSS-20, BOSS-21.*

#### FB-CRESCENT-HALO-09 — Angry · MUST

It is angry after each transformation: the weapons that transformation revealed fire all out for
`boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's pattern
([common](../common.md), BOSS-27): its mortars after the first, its batteries and gatling after the
second.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-CRESCENT-HALO-10 — First transformation: the halo closes · MUST

Once both horn growths are destroyed, it transforms: its horns strain, then swing closed round its
centre into a full halo, and a pair of **mortars** riding them rises out of them either side of the
nose. They shield the core and lob flak shells that burst into rings, in turn.

**Acceptance criteria**
- Given both horn growths destroyed, then it transforms, its horns end closed and its mortars stand
  on them (unit test on its design).

*Sources: BOSS-36, BOSS-40, BOSS-45.*

#### FB-CRESCENT-HALO-11 — Second transformation: plates and crest · MUST

Once both flank glands are destroyed, it transforms again: its flank plates and its crest burst
off, baring dark metal lattices, and a pair of **batteries** unfold on the ring's flanks and a
**gatling** on its back, on the centre line. They shield the core: the batteries sweep wide fans
straight down, the gatling bursts at the player.

**Acceptance criteria**
- Given both flank glands destroyed after both horn growths, then it transforms and its batteries
  and gatling are revealed.

*Sources: BOSS-36, BOSS-40, BOSS-41.*

#### FB-CRESCENT-HALO-12 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always
([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/crescent_halo.py` (`_CRESCENT_HALO`, `CRESCENT_HALO`) unless
named. Angles round the ring are degrees from the nose, positive towards its right (+X).

| Name | Value | Notes |
|------|-------|-------|
| size | 4.5 L (radius 76.5 px) | `stats.size` |
| ring | centre line radius 56, girth 10, axis 8 px high (top 18 px); round the back from 60° to 300° | `HALO_RADIUS`, `HALO_GIRTH`, `HALO_AXIS`, `HALO_ARC` |
| horns | 40° to 104°, girth 13 tapering to 4 over 22° at the tip, -3 px to 23 px high | `HORN_ARC`, `HORN_GIRTH`, `HORN_TIP`, `HORN_TAPER`, `HORN_TOP` |
| core | health 5 200, radius 22, drop 1; organ radius 19, crown 25 px high | `coreHealth`, `ORGAN_RADIUS`, `ORGAN_CROWN` |
| `horn-left`, `horn-right` | ±54° on the ring (∓45.3, -32.9), radius 12, health 1 500, shield, drop 0.6 | `HORN_AT` |
| `flank-left`, `flank-right` | ±120° (∓48.5, 28), radius 13, health 1 700, shield, drop 0.6 | `FLANK_AT` |
| `back-left`, `back-right` | ±150° (∓28, 48.5), radius 12, health 1 900, shield, drop 0.6 | `BACK_AT` |
| horn rotors | 6 barrels, bore 1, 5 px long, hub 4.5; 27 px high | `HORN_ROTOR` |
| flank lasers | emitter bore 2.4, 11 px long, base 5; 19 px high; fixed, pointing down the screen | `FLANK_LASER` |
| back turrets | 2 barrels 3.1 px apart, bore 1.2, 8 px long, dome 6; 20.2 px high | `BACK_GUN` |
| halo rotor (core) | (0, 0), 25 px high; 12 barrels, bore 0.9, 5 px long, hub 6 | `HALO_ROTOR` |
| eye turret (core) | (0, -17), 14 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long, dome 5 | `EYE_GUN`, `EYE_AT` |
| full health | 24 140 (5 200 + 2 × 1 500 + 2 × 1 700 + 2 × 1 900 + 2 × 1 520 + 3 × 1 900) | BOSS-54; the Overlord's is 22 760 |
| points | 15 000; 1 500 a part | |
| ground speed | ×0.4 | |
| stop height | 0.74 | `stopFraction` |
| sway / bob | 30 px over 10 s / 6 px over 5 s | |
| horn spirals | rings of 6 turning ±15°, magenta 185 px/s, every 1.6 s (first 0.6 s / 1.4 s) | |
| flank lasers | 1.6 s every 6.5 s (first 2 s / 5.25 s) | |
| back fans | aimed 3, 12° apart, red 190 px/s, every 2.2 s (first 1 s / 2.1 s) | a sweep |
| core stage 0 | ring of 12 turning 10°, orange 180 px/s, every 1.8 s; aimed 1 every 3 s | |
| core stage 1 | ring turning -12° every 1.5 s; aimed 3, 12° apart, every 2.6 s | |
| core stage 2 | ring turning 14° every 0.85 s; aimed 3 every 2.2 s | |
| core stage 3 | ring turning -9° every 1 s; burst of 4, 0.13 s apart, every 2.4 s | |
| core stage 4 | ring turning 16° every 1 s; fan of 5, 12° apart, every 2.4 s | |
| core stage 5 | ring turning -18° every 0.9 s; burst of 4, 0.12 s apart, every 2.2 s | |
| core stage 6 | ring turning 7° every 0.6 s; fan of 7, 12° apart, every 2.2 s | |
| weighted fire rate | 19.7 as it comes in, 21.3 after its first transformation, 26.3 after its second | BOSS-39 |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation 1 | `horn-left` and `horn-right` destroyed | `transformParts` |
| horns (moving region) | the horn's outline as drawn, mirrored; swing about the vertical through the centre, 8 px high, by 40° towards the nose; no frame | `moving_region`, `swing`, `HORN_SWING` |
| mortars | ±30° on the closed horns (∓28, -48.5), radius 10, health 1 520, pod 20–25.5 px, orange; first 1.2 s / 2.0 s | ride the horns, `MORTAR_AT` |
| transformation 2 | `flank-left` and `flank-right` destroyed | |
| plates region (shed) | the ring from 68° to 100°, 45 to 67 px out, mirrored, `shell`; plates 16–20.6 px | `PLATES_ARC`, `PLATES_HEIGHTS` |
| crest region (shed) | the ring from 168° to 192°, 45 to 67 px out, not mirrored, `shell`; plates 16–21 px | `CREST_ARC` |
| batteries | ±84° (∓55.7, -5.9), radius 8, health 1 900, deck 14–20 px, red; first 1.2 s / 2.0 s | |
| `gatling` | (0, 57), radius 8, health 1 900, pod 14–20 px, magenta; first 1.6 s | on the centre line |
| neon | pale gold (1, 0.95, 0.6), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered among the game's boss kinds (`game/sim/boss_kinds.py`) and models
  only so that the dev viewer lists it; no world's boss table names it. The world-wide counts of the
  common rules (BOSS-41's kinds per world, BOSS-45's "exactly eight change shape, two a world",
  BOSS-55) were written for the four worlds: with the Lab's two shape-changers the BOSS-45 count is
  ten.
- **No hatch.** Both its core guns fire from stage 0, so neither needs a hatch (BOSS-58).
- **Horns closing round the centre.** The horns slide along the ring's own circle (a swing about the
  vertical through the boss's centre), so they close the gap without leaving one at their back: the
  ring's ends stay inside the sleeves at rest and once moved.
- **Check (2026-11-05).** A simulated fight breaking a part every 12 s: 2 946 shots, every one
  leaving a barrel's tip along it, 7 lasers, dead at 146 s. Its model holds together at rest and
  after each transformation, about 5 600 triangles (BOSS-53: 10 000).
