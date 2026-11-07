# Orbital Foundry

> **Area:** bosses · **Prefix:** `FB-ORBITAL-FOUNDRY` · **Related:** [common](../common.md),
> [Prism Gate](L-6-prism-gate.md)

The Orbital Foundry is the final boss of the Lab's level L-6: an industrial space station seen from
above, 4.6 L across. An armoured reactor sphere sits in its middle; round it a fixed inner ring of
plated deck carries gantry cranes and two crucibles on four spokes, and round that an outer track
ring turns on roller arms, carrying three rotor carriages (BOSS-34). Its fight is orbiting spirals:
the rotors riding the turning ring paint spirals, the crucibles lob molten shells that burst into
rings. All five parts shield its core. Once both crucibles are gone the front fairings of its inner
ring burst off for a pair of sweepers; once the three carriages are gone its rear fairings burst
off for a pair of cannons and a hangar on its centre line. Shared rules are in
[common](../common.md).

**Lab boss: in the dev viewer only.** It is listed after the World bosses in the dev viewer's
Bosses list; no level brings it in.

**A machine, not a creature.** On the user's request (2026-11-06: "make 10 more, drop the animal
looking theme"), the Lab's second set departs from BOSS-47's Cyber-Organic creature: the Orbital
Foundry is built from dark metal plating, bronze armour, girders, crane gantries, a reactor and neon
light lines, with no flesh, eyes or veins. Its parts still read as targets (BOSS-48) and its armour
still lies over a darker mechanism (BOSS-49).

## Requirements

### Look

#### FB-ORBITAL-FOUNDRY-01 — Silhouette and size · MUST

Seen from above, the Orbital Foundry is round and open, 4.6 L across: a sphere in the middle, two
concentric rings round it with empty space between them, a cross of four spokes from the sphere to
the inner ring, the outer ring's carriages and the inner ring's crucibles and fairings standing out
on them. It has no nose to speak of: only the turret on the sphere's front tells its front.

**Acceptance criteria**
- Manual validation in the boss viewer: a sphere inside two rings, clearly not a drum on a rim (the
  Carapace Drum), a spoked jelly (the Dust Devil), an open crescent (the Crescent Halo) or a hub
  under a dish (the Aurora Station).

*Sources: Lab request (2026-11-06: "make 10 more, drop the animal looking theme").*

#### FB-ORBITAL-FOUNDRY-02 — Body · MUST

- **Reactor sphere**: a faceted ball plated in two staggered bands of bronze armour, a heavy dark
  belt round its waist, light seams between the bands and reactor ports glowing round its shoulders.
- **Inner ring** (fixed): a dark plated deck from 33 to 47 px out, rails along its edges, deck plates
  across it and a light line round its outer lip.
- **Spokes**: four box girders (at its nose, flanks and tail) from the sphere's belt to the deck, a
  light down each one's back; each goes on under the outer ring as a low roller arm, a roller truck
  at its end holding the ring up.
- **Gantries**: three crane gantries straddling the deck (at its nose and either side of its tail),
  each two pairs of legs, a girder across, a trolley and its hook block.
- **Outer ring** (turning): a heavy track annulus from 61.5 to 70.5 px out, rails along its top,
  ribs across it, a light line round its outer lip and six tie-down blocks with lamps; under each
  carriage a pedestal its stump stands on once the carriage is gone.

**Acceptance criteria**
- Manual validation: one station, its outer ring visibly turning round the rest.

*Sources: Lab request.*

#### FB-ORBITAL-FOUNDRY-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Rotor carriages** (`rotor-1` at the nose at rest, `rotor-2`, `rotor-3`, 120° apart on the outer
  ring, orbiting with it): each a bronze hexagonal housing clamped over the ring, skirts down its
  edges and a light ring round its waist; on top a **rotor** with six barrels (its rings).
- **Crucibles** (`crucible-left`, `crucible-right`, on the inner ring at its flanks): squat bronze
  pots banded with dark hoops, a pouring lip on their outer side with a glowing spill, trunnion
  blocks in A-frames on the deck either side, a lake of molten metal glowing in their mouths; in it,
  on the pot's trunnion pillar, a **mortar** (one fat barrel in a cradle on a turntable) lobbing its
  shells. A destroyed crucible leaves its pillar and the mortar's stump on it.
- **Reactor turret** (the core's): a gun turret with three barrels side by side on the sphere's
  front (its aimed shots, fans and bursts).
- **Reactor rotor** (the core's): a rotor with fourteen barrels on the sphere's crown (its last
  stage's ring). Until then it lies under a hatch, a bronze octagonal cap with a seam of light; the
  hatch bursts off as the rotor comes into use (BOSS-58), leaving a collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws its five parts and every gun mount (unit test).

*Sources: Lab request.*

#### FB-ORBITAL-FOUNDRY-04 — Lights · MUST

The rings' lips, the spokes' backs, the sphere's seams and ports, the carriages' and fairings'
stripes, the crucibles' molten mouths and spills and the deck's lamps glow. Its neon colour, set
copper, shows bright yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: Lab request.*

#### FB-ORBITAL-FOUNDRY-05 — What it sheds · MUST

Bronze fairings clad the inner ring's deck at five places: either side of its nose, either side of
its tail and on its centre line behind. They are the armour it sheds (BOSS-42): each a bevelled
housing down over the deck's edges, vent slats and a light stripe on top. Its regions:
- `front-fairings` (shed at the first transformation): the ring from 30° to 60° either side of the
  nose, 32 to 48 px out; the sweepers lie folded in them;
- `rear-fairings` (shed at the second): from 119° to 151° either side; the cannons lie in them;
- `hangar-fairing` (shed at the second): from 166° to 194°, not mirrored; the hangar lies in it.

Each bursts into plates cracked from its outline and leaves a `shell` frame on the deck.

**Acceptance criteria**
- Given its design, then each transformation sheds a region and every hidden weapon lies in one its
  transformation sheds (unit test).
- Given its model, then it draws each region, and it holds together at rest and after each
  transformation (unit tests).

*Sources: Lab request, D-254.*

### Behaviour

#### FB-ORBITAL-FOUNDRY-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then drifts slowly from side to side (its sway cut to keep its turning ring in the ship's
reach, BOSS-10) and bobs, its outer ring turning all the while at `spinRate`. While it is fought the
ground scrolls at ×0.3.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.3 of the level's speed and back after it.

*Sources: Lab request.*

#### FB-ORBITAL-FOUNDRY-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `crucible-left`, `crucible-right` (fixed)
and `rotor-1`, `rotor-2`, `rotor-3` (orbiting). The core's guns (the reactor turret and the reactor
rotor) fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core and its three carriages orbit (unit test
  on its design).

*Sources: Lab request.*

#### FB-ORBITAL-FOUNDRY-08 — Stage patterns · MUST

Its parts fire in every stage while they stand:
- each carriage's rotor fires a ring of 6 magenta bullets, the three in turn, each ring turned a
  little more than the last: with the ring's own turn sweeping the carriages round, they paint
  spirals round the station;
- the crucibles lob a big molten shell at the player in turn, which bursts into a ring of 8 after
  1.2 s.

The core fires, from the reactor turret unless named:
- stage 0: an aimed spread of 3 red bullets 10° apart;
- stage 1: a fan of 5, 12° apart, straight down;
- stage 2: a burst of 4 at the player;
- stage 3: a fan of 7, 10° apart, and a single aimed orange shot;
- stage 4: a burst of 5 and a fan of 5 orange;
- stage 5 (all five parts gone): a ring of 14 orange bullets from the reactor rotor turning 9° a
  volley (a spiral, its first ring), and an aimed spread of 3.

Its turret sweeps its fans and spreads one bullet at a time (BOSS-58).

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys (BOSS-21 unit tests).

*Sources: Lab request.*

#### FB-ORBITAL-FOUNDRY-09 — Angry · MUST

It is angry after each transformation: the weapons that transformation revealed fire all out for
`boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's pattern (the hangar's
Hornets too; the sweepers no faster than their warning, beam and gap allow) ([common](../common.md),
BOSS-27).

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed (unit
  test).

*Sources: Lab request, D-256.*

#### FB-ORBITAL-FOUNDRY-10 — First transformation: sweepers · MUST

It transforms the first time when both crucibles are destroyed: the front fairings burst off,
baring the deck under a dark metal frame, and two **sweepers** unfold on the deck either side of the
nose. They shield the core and fire lasers that sweep after the player, in turn.

**Acceptance criteria**
- Given both crucibles destroyed, then it transforms and its two sweepers are revealed (unit test on
  its thresholds).

*Sources: Lab request, D-221, D-229.*

#### FB-ORBITAL-FOUNDRY-11 — Second transformation: cannons and hangar · MUST

It transforms the second time when its three carriages are destroyed: the rear fairings and the
hangar fairing burst off, and two **cannons** unfold on the deck either side of its tail, a
**hangar** on its centre line between them. The cannons sweep aimed spreads of 3 big red shells;
the hangar's doors slide apart and it launches Hornets.

**Acceptance criteria**
- Given its three carriages destroyed, then it transforms a second time and its cannons and hangar
  are revealed (unit test on its thresholds).

*Sources: Lab request, D-221, D-229.*

#### FB-ORBITAL-FOUNDRY-12 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %; its core always drops one
([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances, its core's and its points are those of Tunable
  values.

*Sources: Lab request.*

## Tunable values

All in `src/game/config/bosses/lab/orbital_foundry.py` (`_ORBITAL_FOUNDRY`, `ORBITAL_FOUNDRY`); its
model in `src/game/view/bosses/lab/orbital_foundry_model.py` and `orbital_foundry_parts.py`. Angles
round the rings are degrees from the nose, positive towards its right (+X).

| Name | Value | Notes |
|------|-------|-------|
| size | 4.6 L (radius 78.2 px) | `stats.size` |
| reactor sphere | radius 19, centre 6 px high (top 25 px) | `SPHERE_RADIUS`, `SPHERE_CENTRE` |
| inner ring (fixed) | centre line radius 40, 7 px either side, deck 8 px high (3 px underneath) | `INNER_RADIUS`, `INNER_HALF`, `INNER_DECK` |
| outer ring (turning) | centre line radius 66, 4.5 px either side, 3 to 7 px high | `OUTER_RADIUS`, `OUTER_HALF`, `OUTER_TOP` |
| ring spin | 0.35 rad/s | `spinRate` |
| core | health 1 800, radius 20, drop 1 | `coreHealth`, `coreRadius` |
| `crucible-left`, `crucible-right` | ∓90° on the inner ring (∓40, 0), radius 12, health 900, shield, drop 0.6 | `CRUCIBLE_ANGLE` |
| `rotor-1`, `rotor-2`, `rotor-3` | 0°, 120°, 240° on the outer ring at rest ((0, -66), (57.2, 33), (-57.2, 33)), radius 11, health 760, shield, orbit, drop 0.6 | `ROTOR_ANGLES` |
| carriage rotors | 6 barrels, bore 1, 4.5 px long, hub 4.5; 12.5 px high | `ROTOR`, `ROTOR_HEIGHT` |
| crucible mortars | one barrel, bore 3.4, 4.5 px long, cradle 6, axis 0.8; on the pots' pillars 16 px high | `CRUCIBLE_MORTAR`, `CRUCIBLE_TOP` |
| reactor turret (core) | (0, -10), 22.5 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long; dome 5 | `REACTOR_GUN` |
| reactor rotor (core) | (0, 4), 24.2 px high; 14 barrels, bore 0.7, 3.2 px long; hub 4.6 | `REACTOR_ROTOR` |
| rotor hatch | octagon of radius 7 round (0, 4) on the sphere's crown; bursts as the rotor comes into use | `armour_region` `rotor-hatch` (`mount`) |
| full health | 10 020 (1 800 + 2 × 900 + 3 × 760 + 2 × 720 + 3 × 900) | BOSS-54; the Storm Petrel's (1-1) is 10 420 |
| points | 8 000; 800 a part | |
| ground speed | ×0.3 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 30 px over 11 s (cut by BOSS-10) / 5 px over 5 s | |
| carriage spirals | rings of 6 turning 13°, magenta 170 px/s, every 2.2 s (first 0.6 s / 1.35 s / 2.1 s) | one bullet a barrel |
| molten shells | aimed 1, orange 100 px/s radius 8, bursting into 8 orange at 155 px/s after 1.2 s, every 3.4 s (first 1.8 s / 3.5 s) | mortars |
| core stage 0 | aimed 3, 10° apart, red 185 px/s, every 2.6 s | a sweep |
| core stage 1 | fan of 5, 12° apart, every 2.6 s | |
| core stage 2 | burst of 4, 0.13 s apart, every 2.2 s | |
| core stage 3 | fan of 7, 10° apart, every 2.4 s; aimed 1 orange 175 px/s every 3 s | |
| core stage 4 | burst of 5, 0.12 s apart, every 2 s; fan of 5 orange, 12° apart, every 2.8 s | |
| core stage 5 | ring of 14 orange, turning 9°, every 1.3 s; aimed 3, 10° apart, every 2.4 s | reactor rotor; turret |
| weighted fire rate | 9.9 as it comes in, 12.0 after its first transformation, 17.1 after its second | BOSS-39 |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation 1 | `crucible-left` and `crucible-right` destroyed | `transformParts` |
| front fairings (shed) | the inner ring from 30° to 60°, 32 to 48 px out, mirrored, `shell`; 8–13 px (drawn down to 4 px over the deck's edges) | `FAIRING_RADII`, `FAIRING_HEIGHTS` |
| sweepers | ±45° on the inner ring (∓28.3, -28.3), radius 7, health 720, pod 8–11 px, orange; first 1.2 s / 4.2 s; sweeping laser 2 s every 8 s | `SWEEPER_ANGLE` |
| transformation 2 | `rotor-1`, `rotor-2` and `rotor-3` destroyed | |
| rear fairings (shed) | from 119° to 151°, mirrored, `shell`; 8–13 px | `CANNON_ANGLE` |
| hangar fairing (shed) | from 166° to 194°, not mirrored, `shell`; 8–13 px | `HANGAR_ARC` |
| cannons | ±135° (∓28.3, 28.3), radius 8.5, health 900, pod 8–11.5 px, red; first 1.4 s / 2.6 s; aimed spreads of 3 shells every 2.4 s | |
| `hangar` | (0, 40), radius 9, health 900, pod 8–11.5 px; first 2.2 s; 2 Hornets every 7 s | on the centre line |
| neon | copper (1, 0.55, 0.2), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered among the game's boss kinds and models only so that the dev viewer
  lists it; no world's boss table names it.
- **Two rings, one turning.** The engine has one turning ring a boss (BOSS-34): the outer ring is it
  (its model is the drawing's `ring`, its carriages orbit), while the inner ring is part of the
  core. The outer ring rests on roller trucks at the ends of the spokes' roller arms, so the station
  holds together whatever its turn.
- **Pillars and pedestals.** Its parts' guns stand high (the crucibles' mortars in the pots' mouths,
  the carriages' rotors on their housings), so the core keeps a pillar inside each pot and the ring a
  pedestal inside each carriage: a destroyed part's stump (BOSS-18) stands on them, not in the air.
- **Health.** Its full health is in line with the 1-1 final boss's (the Storm Petrel, 10 420). Its
  fight time was not simulated (the boss-bot of BOSS-56 was not ported).
- **Check (2026-11-06).** A simulated fight breaking a part every 12 s: 1 283 shots and 15 lasers,
  every shot leaving a barrel's tip along it, dead at 134 s. Its model holds together at rest and
  after each transformation, about 7 200 triangles with its gun mounts (BOSS-53: 10 000).
