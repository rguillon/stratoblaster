# Star Engine

> **Area:** bosses · **Prefix:** `FB-STAR-ENGINE` · **Related:** [common](../common.md),
> [Monolith Array](L-10-monolith-array.md)

The Star Engine is the final boss of the Lab's level L-10, the last of the Lab. **Lab boss: in the
dev viewer only** (the dev menu's Bosses list, after the bosses of the worlds); no level brings it
in. A five-pointed star of a reactor 4.5 L across: a spiky pentagonal core under a domed reactor,
five long armoured thruster arms radiating from it, each tipped by an emitter, and a containment
ring clamped over the arms round the core. It is the Lab's final exam: five-fold patterns, a ring
spinning from every arm, pentagram spirals from the heart, the densest bullet hell of the set; it
sheds its vanes for a pair of orbs, then its cowls and keel for a pair of gatlings and a lance.
Shared rules are in [common](../common.md).

**Departs from BOSS-47.** On the user's request (2026-11-06, "drop the animal looking theme") the
Lab bosses of L-6 to L-10 are machines, structures and abstract geometry, not Cyber-Organic
creatures: the Star Engine is a reactor of dark metal with crimson light lines, with no flesh, eyes,
teeth or veins.

## Requirements

### Look

#### FB-STAR-ENGINE-01 — Silhouette and size · MUST

Seen from above, the Star Engine is a five-pointed star 4.5 L across, one point down the screen at
its nose, two to its sides and two behind, its arms' blades the star's points; a ring round its
core crosses the five arms. It is the only boss shaped as a star.

**Acceptance criteria**
- Manual validation in the boss viewer: a five-pointed star with a ring round its middle.

*Sources: Lab brief (2026-11-06).*

#### FB-STAR-ENGINE-02 — Body · MUST

- **Deck**: a low pentagon of dark metal (its top 7 px high), its corners between the arms and cut,
  a rim of light round its edge; three reactor nozzles and vents at its back.
- **Core**: a pentagon of metal on the deck (its top 13 px high), a band of light round it, a spike
  rising from each of its five corners (a light along its tip), and a reactor dome on it up to
  26 px, two bands of light round it, the heart rotor's seat on its crown; a metal seat on its front
  carries the star turret.
- **Arms**: five long bevelled housings from the core out to the emitters (63 px out), narrowing
  from 18 px to 11 px across, three armour plates along their tops and a channel of light down
  their middles, two pairs of thruster nozzles on their flanks and, under each emitter, a dark mast
  up to its rotor's seat (the gun's stump stays on it once the emitter is gone).
- **Containment ring**: a dark metal hoop 43 px out at 15.5 px over the arms, a band of light round
  it, clamped onto each arm.

**Acceptance criteria**
- Manual validation: a machined reactor star, dark metal under crimson (shown yellow) light.

*Sources: Lab brief.*

#### FB-STAR-ENGINE-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Emitters** (`tip-nose`, `tip-right`, `tip-left`, `tip-back-right`, `tip-back-left`, one at each
  arm's tip): each a hexagonal housing, a ring of light round it, a five-barrelled rotor on its top
  and three blades fanning out past it, the long one the star's point, lit at its tip.
- **Heart rotor** (the core's): fifteen barrels round a hub on the reactor dome (its rings).
- **Star turret** (the core's): five barrels side by side on the core's front (its aimed shots,
  bursts and fans).

**Acceptance criteria**
- Given its model, then it draws its five emitters and every gun mount.

*Sources: Lab brief, BOSS-58.*

#### FB-STAR-ENGINE-04 — Lights · MUST

Its rims, bands, channels, nozzles' mouths, spikes' and blades' tips glow. Its neon colour,
crimson, shows bright yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: Lab brief, BOSS-50.*

#### FB-STAR-ENGINE-05 — Armour · MUST

It sheds three armour regions ([common](../common.md), BOSS-42), each drawn as a piece of its own:
- **Vanes** (`vanes`, mirrored, first transformation): a plate over the deck's sector between the
  nose arm and each side arm, a ridge along its middle and strokes of light on its outer edge; the
  orbs lie folded under them; `shell` frame.
- **Cowls** (`cowls`, mirrored, second transformation): a vented plate over the deck's sector
  between each side arm and back arm; the gatlings lie folded under them; `shell` frame.
- **Keel** (`keel`, not mirrored, second transformation): a ridged plate along the nose arm, three
  chevrons of light on it; the lance lies folded under it; `wing` frame.

Each bursts into plates cracked from its outline.

**Acceptance criteria**
- Given its design, then each transformation sheds a region and every hidden weapon lies in one its
  transformation sheds.
- Given its model, then it draws each region's armour, and it holds together at rest and after each
  transformation.

*Sources: Lab brief, BOSS-42, BOSS-52.*

### Behaviour

#### FB-STAR-ENGINE-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs slowly. While it is fought the ground scrolls at ×0.3.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.3 of the level's speed and back after it.

*Sources: BOSS-03.*

#### FB-STAR-ENGINE-07 — Parts and core · MUST

It has five parts as it comes in, its emitters, all shielding its core. The core's guns (the heart
rotor and the star turret) fire the core's volleys and are the last the player destroys. The star
turret turns the way it fires; the rotors spin with their rings.

**Acceptance criteria**
- Given its design, then its five parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### FB-STAR-ENGINE-08 — Stage patterns · MUST

Each emitter fires in every stage while it stands: a ring of 5 (one bullet a barrel) every 1.9 s,
turning 14° a volley, the nose and back ones one way, the side ones the other; their first volleys
0.4 s apart round the star, so the rings ripple round it (pentagram spirals from every arm). The
core fires, from its heart rotor, a ring of 15 turning by fifths and halves of a barrel's spacing,
faster at every stage, with its star turret's shots:
- stage 0: the ring every 2.4 s turning 12°, and a single aimed shot;
- stage 1: every 2 s turning -12°, and an aimed fan of 3, 12° apart, swept;
- stage 2: every 1.6 s turning 4.8°, and a burst of 4;
- stage 3: every 1.3 s turning -4.8°, and a fan of 5, 12° apart;
- stage 4: every 1.1 s turning 9.6°, and a burst of 5;
- stage 5 (every emitter gone): every 0.65 s turning 7.2°, and a fan of 5.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys.

*Sources: BOSS-20, BOSS-21.*

#### FB-STAR-ENGINE-09 — Angry · MUST

It is angry after each transformation: the weapons it revealed fire all out for
`boss_rage_seconds`, instead of its stage's pattern ([common](../common.md), BOSS-27).

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-STAR-ENGINE-10 — First transformation · MUST

It transforms the first time once both side emitters (`tip-left`, `tip-right`) are destroyed,
whatever else is lost: its vanes burst off, baring a dark metal lattice, and two **orbs** unfold on
the deck between the nose arm and the side arms. They shield the core and fire turning rings of 10.

**Acceptance criteria**
- Given both side emitters destroyed, then it transforms and its two orbs are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-40.*

#### FB-STAR-ENGINE-11 — Second transformation · MUST

It transforms the second time once both back emitters (`tip-back-left`, `tip-back-right`) are
destroyed: its cowls and its keel burst off, and two **gatlings** unfold on the deck between the
side arms and the back arms and a **lance** on the nose arm, on the centre line. They shield the
core; the gatlings fire bursts at the player, the lance a laser straight down the screen.

**Acceptance criteria**
- Given both back emitters destroyed, then it transforms again and its gatlings and lance are
  revealed.

*Sources: BOSS-35, BOSS-36, BOSS-40, BOSS-41.*

#### FB-STAR-ENGINE-12 — Death, drops and points · MUST

Its emitters drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always
([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances, its core's and its points are those of Tunable
  values.

*Sources: BOSS-57.*

#### FB-STAR-ENGINE-13 — Health · MUST

Its full health is in line with the 1-5 final boss's (the Overlord, 22 760): 22 940.

**Acceptance criteria**
- Given its design, then its full health is that of Tunable values.

*Sources: Lab brief, BOSS-54.*

## Tunable values

All in `src/game/config/bosses/lab/star_engine.py` (`_STAR_ENGINE`, `STAR_ENGINE`) unless named.
Angles round the star in degrees from its nose, positive towards its right (+X).

| Name | Value | Notes |
|------|-------|-------|
| size | 4.5 L (radius 76.5 px) | `stats.size` |
| arms | at 0°, ±72°, ±144°; emitters 63 px out; 18 → 11 px across; top 12 px high | `ARM_ANGLES`, `ARM_REACH`, `ARM_ROOT`, `ARM_TIP`, `ARM_TOP` |
| deck / core | pentagons 44 px / 27 px to their corners (at 36° + 72° k); deck top 7 px | `DECK_RADIUS`, `CORE_RADIUS`, `DECK_TOP` |
| reactor dome | up to 26 px | `DOME_TOP` |
| containment ring | 43 px out, girth 2.4, axis 15.5 px high | `RING_RADIUS`, `RING_GIRTH`, `RING_AXIS` |
| core | health 5 700, radius 24, drop 1 | `coreHealth`, `coreRadius`, `coreDrop` |
| `tip-nose` | (0, -63), radius 12, health 1 900, shields, drop 0.6 | |
| `tip-right`, `tip-left` | (±59.9, -19.5), radius 12, health 1 600, shield, drop 0.6 | |
| `tip-back-right`, `tip-back-left` | (±37, 51), radius 12, health 1 700, shield, drop 0.6 | |
| emitter rotors | 19 px high; 5 barrels, bore 1.1, 5 px long, hub 4.6 | `TIP_ROTOR`, `TIP_ROTOR_HEIGHT` |
| heart rotor (core) | (0, 0), 26 px high; 15 barrels, bore 0.85, 5 px long, hub 6 | `HEART_ROTOR`, `mounts` `heart` |
| star turret (core) | (0, -17), 15 px high; 5 barrels 2.34 px apart, bore 0.9, 7 px long, dome 6.1 | `STAR_GUN`, `mounts` `star-gun` |
| full health | 22 940 (5 700 + 1 900 + 2 × 1 600 + 2 × 1 700 + 2 × 1 520 + 3 × 1 900) | BOSS-54 |
| points | 16 000; 1 600 a part | |
| ground speed | ×0.3 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 26 px over 12 s / 5 px over 5.5 s | |
| emitter rings | 5, magenta 165 px/s, every 1.9 s, turning 14° (nose, back) or -14° (sides); first 0.6, 1.0, 1.4, 1.8, 2.2 s | `TIP_EVERY`, `TIP_TURN`, `TIP_FIRST` |
| core stage 0 | ring of 15 turning 12°, orange 195 px/s, every 2.4 s; aimed 1, red 175 px/s, every 3 s | |
| core stage 1 | ring of 15 turning -12° every 2 s; aimed 3, 12° apart, every 2.6 s | star turret: a sweep |
| core stage 2 | ring of 15 turning 4.8° every 1.6 s; burst of 4, 0.13 s apart, every 2.4 s | |
| core stage 3 | ring of 15 turning -4.8° every 1.3 s; fan of 5, 12° apart, every 2.4 s | |
| core stage 4 | ring of 15 turning 9.6° every 1.1 s; burst of 5, 0.12 s apart, every 2.2 s | |
| core stage 5 | ring of 15 turning 7.2° every 0.65 s; fan of 5, 12° apart, every 2 s | |
| weighted fire rate | 19.7 as it comes in, 26.6 after its first transformation, 30.9 after its second | BOSS-39 |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformations | both side emitters; both back emitters | `transformParts` |
| shed regions | vanes: the deck's sector 21° to 51°, 26 to 37 px out, mirrored, `shell`; cowls: 93° to 123°, likewise; both 6.5 to 12 px high. Keel: (±8, -28) to (±7, -48), `wing`, 11.5 to 15.5 px high | `VANE_OUTLINE`, `COWL_OUTLINE`, `KEEL_OUTLINE`, `PLATE_HEIGHTS`, `KEEL_HEIGHTS` |
| orbs | 33 px out at ±36° (±19.4, -26.7), radius 9, health 1 520 (0.8 × 1 900), pod 7 to 11 px, magenta; first 1.2 s / 2 s; rings of 10 every 2.6 s | `ORB_AT` |
| gatlings | 33 px out at ±108° (±31.4, 10.2), radius 8, health 1 900, pod 7 to 11 px, red; first 1.2 s / 2 s; bursts of 4 every 2.2 s | `GATLING_AT` |
| lance | (0, -38), radius 8, health 1 900, pod 12 to 15 px, red; first 1.6 s; laser 1.4 s every 7.5 s | `LANCE_AT` |
| neon | crimson (1, 0.1, 0.35), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered among the game's boss kinds (`game/sim/boss_kinds.py`) and models
  only so that the dev viewer lists it; no world's boss table names it. The world-wide counts of the
  common rules (BOSS-41, BOSS-45, BOSS-55) were written for the four worlds and do not count it.
- **No hatch.** Both its core guns fire from stage 0, so neither needs a hatch (BOSS-58).
- **Model.** Its emitters and armour are in `view/bosses/lab/star_engine_parts.py`; it shares the
  [Monolith Array](L-10-monolith-array.md)'s shades (`monolith_array_kit.py`).
- **Check (2026-11-06).** A simulated fight breaking a part every 12 s: 2 931 shots, every one
  leaving a barrel's tip along it, 12 lasers, dead at 134 s. Its model holds together at rest and
  after each transformation, about 3 460 triangles (BOSS-53: 10 000).
