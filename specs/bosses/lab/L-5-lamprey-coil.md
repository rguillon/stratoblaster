# Lamprey Coil

> **Area:** bosses · **Prefix:** `MB-LAMPREY-COIL` · **Related:** [common](../common.md),
> [Crescent Halo](L-5-crescent-halo.md)

The Lamprey Coil is the mini boss of the Lab's level L-5. **Lab boss: in the dev viewer only** (the
dev menu's Bosses list, after the 40 bosses of the worlds); no level brings it in. A serpentine
lamprey 3.5 L across, lying coiled in an S across the screen, its round sucker mouth at its front
ringed with hooked teeth and a rotor spinning in its throat. Two gill clusters on its flanks and a
stinger at its tail's tip shield its core. Its gills weave aimed bursts, its stinger and its mouth
spin spirals against each other; once two of its parts are gone it sheds its dorsal armour and
unfolds a pair of sweepers. Shared rules are in [common](../common.md).

## Requirements

### Look

#### MB-LAMPREY-COIL-01 — Silhouette and size · MUST

Seen from above, the Lamprey Coil is a lamprey 3.5 L across coiled in an S lying across the screen:
its tail at the left, a lobe dipping towards the player, a lobe rising behind it on the right, and
its neck hooking back down to the round sucker mouth at its front (down the screen), right of the
centre line. A gill cluster swells from the flank of each lobe and a bony stinger tips its tail.

**Acceptance criteria**
- Manual validation in the boss viewer: an S-shaped serpent, its round mouth at its front, unlike
  any other boss.

*Sources: Lab brief (2026-11-05).*

#### MB-LAMPREY-COIL-02 — Body · MUST

Its body is a round tube of flesh (slate and graphite segments in turn) along the S, thickest at
its head and tapering to its tail. Metal scutes run down its back, metal collars are grafted round
it and a riveted plate on its nape. Seven gill pores a side (dark holes ringed with light) line its
neck behind the head; eyes sit on the head. The sucker mouth is a round disc of flesh in front of
the head, a lip of light round its rim, a ring of fourteen hooked bone teeth curling into its dark
throat and a ring of twelve smaller teeth round its outer rim. Reactor sacs ride the rising lobe.

**Acceptance criteria**
- Manual validation: a living lamprey under grafted metal, its sucker mouth ringed with teeth.

*Sources: Lab brief.*

#### MB-LAMPREY-COIL-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Gill clusters** (`gill-left` on the dipping lobe's front flank, `gill-right` on the rising
  lobe's back flank): each a swollen gill sac with six lit pores round its crown and a vein ring at
  its foot, under a twin-barrelled turret on a metal seat.
- **Stinger** (at the tail's tip): a bony bulb, a barbed spike of bone curling back from it, a
  four-barrelled rotor on a metal seat on its top.
- **Mouth rotor** (the core's): ten barrels round a hub in the sucker's throat (its spirals, the
  boss's signature).
- **Crown turret** (the core's): three barrels side by side on the back of its head (its aimed
  shots and bursts).

**Acceptance criteria**
- Given its model, then it draws both gill clusters, the stinger and every gun mount.

*Sources: Lab brief, BOSS-58.*

#### MB-LAMPREY-COIL-04 — Lights · MUST

A pink vein runs down its back and along each flank (its lateral lines); its gill pores, lips, eyes,
glands and the seams of its seats glow. Its neon colour, pink, shows bright yellow
([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: Lab brief, BOSS-50.*

#### MB-LAMPREY-COIL-05 — Dorsal armour · MUST

The scutes over the middle of the S (the stretch of its back from the dipping lobe to the rising
one) are the armour it sheds at its transformation ([common](../common.md), BOSS-42): seven
overlapping metal scutes drawn as a piece of their own over the back, a pink vein along them, a
gland at each end and veins running down its sides. Its region is the band 9 px either side of the
centre line over that stretch (`back`, not mirrored: the S is turned, not mirrored, about its
centre); it bursts into plates cracked from that outline and leaves a `shell` lattice frame. The two
sweepers lie folded under it.

**Acceptance criteria**
- Given its design, then its one transformation sheds the back region and both sweepers lie in it.
- Given its model, then it draws the back region's armour, and it holds together with and without
  it.

*Sources: Lab brief, BOSS-42, BOSS-52.*

### Behaviour

#### MB-LAMPREY-COIL-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs, quicker than the World 1 mini bosses. While it is fought the ground
scrolls at ×0.7.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.7 of the level's speed and back after it.

*Sources: BOSS-03.*

#### MB-LAMPREY-COIL-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `gill-left`, `gill-right` and `stinger`.
The core's guns (the mouth rotor and the crown turret) fire the core's volleys and are the last the
player destroys. The turrets turn the way they fire.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-LAMPREY-COIL-08 — Stage patterns · MUST

The parts fire in every stage while they stand: each gill cluster a burst of 3 at the player, the
two in turn (they weave across the mouth's spiral); the stinger a ring of 4 turning against the
mouth's, a small fast spiral. The core fires, from its mouth rotor, a ring of 10 (one bullet a
barrel) turning a little more at each volley, a new turn and pace at every stage, with its crown
turret's shots:
- stage 0: the spiral turning 12° a volley, and a single aimed shot;
- stage 1: the spiral turning the other way (15°), and an aimed fan of 3, swept;
- stage 2: the spiral turning 18°, faster, and a burst of 3;
- stage 3 (every part gone): the spiral turning 8°, twice as fast as in stage 0, and a burst of 4.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys.

*Sources: BOSS-20, BOSS-21.*

#### MB-LAMPREY-COIL-09 — Angry · MUST

It is angry after its transformation: its two sweepers fire all out for `boss_rage_seconds`, as
often as their warning, beam and gap allow, instead of its stage's pattern ([common](../common.md),
BOSS-27).

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two sweepers.

*Sources: BOSS-27.*

#### MB-LAMPREY-COIL-10 — Transformation · MUST

It transforms once, when two of its parts are destroyed: its dorsal armour bursts off the middle
of the S, baring a dark metal lattice, and two **sweepers** unfold on its back's centre line, either
side of its middle. They shield the core and fire lasers that sweep after the player, in turn.

**Acceptance criteria**
- Given two parts destroyed, then it transforms and its two sweepers are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-40.*

#### MB-LAMPREY-COIL-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its sweepers 30 % ([common](../common.md),
BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/lamprey_coil.py` (`_LAMPREY_COIL`, `LAMPREY_COIL`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.5 L (radius 59.5 px) | `stats.size` |
| body | centre line 7 px high through 13 points from the tail (-58, 8) to the head (17, -34), girth 5.4 → 12.6 | `LAMPREY_SPINE`, `LAMPREY_AXIS` |
| sucker mouth | centre (7, -39), radius 12.5, throat 10.5 px high | `LAMPREY_MOUTH`, `LAMPREY_MOUTH_RADIUS`, `LAMPREY_THROAT` |
| core | health 1 600, radius 18 | `coreHealth`, `coreRadius` |
| `gill-left`, `gill-right` | (-27, -26) and (40, 28), radius 12, health 780, shield, drop 0.5 | |
| `stinger` | (-64, 12), radius 11, health 820, shields, drop 0.5 | |
| gill turrets | 2 barrels 2.86 px apart, bore 1.1, 7 px long, dome 5; 14.6 px high | `GILL_GUN` |
| stinger rotor | 4 barrels, bore 1, 4.5 px long, hub 4; 11 px high | `STINGER_ROTOR` |
| mouth rotor (core) | (7, -39), 10.5 px high; 10 barrels, bore 0.8, 4 px long, hub 4.5 | `MOUTH_ROTOR`, `mounts` `mouth` |
| crown turret (core) | (26, -30), 19 px high; 3 barrels 2.6 px apart, bore 1, 6 px long, dome 4.5 | `CROWN_GUN`, `mounts` `crown` |
| full health | 5 300 (1 600 + 2 × 780 + 820 + 2 × 660) | BOSS-54 |
| points | 5 000; 500 a part | |
| ground speed | ×0.7 | |
| stop height | 0.73 | `stopFraction` |
| sway / bob | 55 px over 6 s / 9 px over 2.6 s | |
| gill bursts | 3, 0.16 s apart, red 185 px/s, every 2.6 s (first 1 s / 2.3 s) | |
| stinger spiral | ring of 4 turning -21°, orange 175 px/s, every 0.9 s (first 0.5 s) | |
| core stage 0 | ring of 10 turning 12°, purple 180 px/s, every 1.6 s; aimed 1, red, every 3 s | |
| core stage 1 | ring of 10 turning -15° every 1.4 s; aimed 3, 12° apart, every 2.6 s | crown: a sweep |
| core stage 2 | ring of 10 turning 18° every 1.2 s; burst of 3, 0.15 s apart, every 2.4 s | |
| core stage 3 | ring of 10 turning 8° every 0.8 s; burst of 4, 0.13 s apart, every 2.2 s | |
| weighted fire rate | 13.3 as it comes in, 16.0 after its transformation | BOSS-39 |
| angry | the revealed sweepers, BOSS-27 | `boss_build.angry_pattern` |
| transformation | 2 parts destroyed | default threshold |
| shed region | back: the band 9 px either side of the centre line from (-23, -14) to (29, 18), `shell`, not mirrored; scutes from the back's top -1.2 px to +2 px | `armour_region`, `ARMOUR_SPAN`, `ARMOUR_HALF` |
| sweepers | (-9, -9) and (14, 13), radius 7, health 660, pod 19.5 px, purple; first 1.2 s / 3.4 s; sweeping laser 2 s every 8 s | `SWEEPER_SPOTS` |
| neon | pink (1, 0.2, 0.6), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered among the game's boss kinds (`game/sim/boss_kinds.py`) and models
  only so that the dev viewer lists it; no world's boss table names it. The world-wide counts of the
  common rules (BOSS-41, BOSS-45, BOSS-55) were written for the four worlds and do not count it.
- **No hatch.** Both its core guns fire from stage 0, so neither needs a hatch (BOSS-58).
- **Check (2026-11-05).** A simulated fight breaking a part every 12 s: 791 shots, every one
  leaving a barrel's tip along it, 11 sweeping lasers, dead at 74 s. Its model holds together at
  rest and after its transformation, about 3 800 triangles (BOSS-53: 4 000).
