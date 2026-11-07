# Cathedral Engine

> **Area:** bosses · **Prefix:** `FB-CATHEDRAL-ENGINE` · **Related:** [common](../common.md),
> [Arrow Lance](L-8-arrow-lance.md)

The Cathedral Engine is the Lab's L-8 final boss. **Lab boss: in the dev viewer only** (no level
brings it in; it is listed after the World bosses in the dev viewer's Bosses list). A gothic
machine-church seen from above, 4.5 L long: a cross of nave and transept on a plinth, its west front
with two spires at the front, flying buttresses along its nave and choir, a great rose window over
the crossing, an organ-pipe bank in each transept arm and a round apse at the back. It fights like a
choir: its organ banks play chords (two rings at once from one rotor, a slow one and a fast one),
its spires toll aimed shots, its core sings rings and spirals of different speeds, all on one
rhythm, while the rose window's laser sweeps in on the beat. Shared rules are in
[common](../common.md).

**Departs from BOSS-47.** On the user's request (2026-11-06, "drop the animal looking theme") this
Lab boss is architecture and machinery, not a Cyber-Organic creature: dark metal walls, slate roofs,
pinnacles, glass and light lines, no flesh, eyes or veins. The other look rules (BOSS-48 to BOSS-53)
hold.

## Requirements

### Look

#### FB-CATHEDRAL-ENGINE-01 — Silhouette and size · MUST

Seen from above, the Cathedral Engine is a Latin cross 4.5 L long and about 3.8 L across its
transept: its west front at the front (down the screen) between two square towers with tall
needle spires, the nave behind it, the transept across with flat-topped arms, the crossing tower
under the round rose window, the choir and a round apse at the back ringed with chapels, flying
buttresses standing out along the nave and the choir.

**Acceptance criteria**
- Manual validation in the boss viewer: a cathedral in plan, its west front down the screen, its
  silhouette unlike any other boss's.

*Sources: user request (2026-11-06, the Lab bosses, "drop the animal looking theme").*

#### FB-CATHEDRAL-ENGINE-02 — Body · MUST

Its body is dark metal: a bevelled plinth in the cross's footprint; the west front's towers and
terrace, lancets of light on the towers' fronts, a pointed portal arch of light under the terrace,
the nave's gable behind; the nave's aisle vaults and the high vessel's deck between them, a violet
line along each aisle's outer wall, two flying buttresses either side (a pier and its pinnacle, a
leaning arch to the high wall, a footing); the crossing tower with a pinnacle on each corner; each
transept arm a flat deck with a parapet of light, a short ribbed gabled roof from the crossing to
the organ, pinnacles at its end; the choir's aisle vaults and its flat-topped high vessel carrying
the lantern rotor's hatch, two flying buttresses either side; the apse, a faceted half dome with ribs
of light and the apse rotor on its crown, four chapels round it and the engine's two exhausts at its
back.

**Acceptance criteria**
- Manual validation: a machine-church of dark metal, slate and light, no creature.

*Sources: user request (2026-11-06).*

#### FB-CATHEDRAL-ENGINE-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Spires** (left and right, on the west front's towers): each an octagonal belfry ringed in light
  with a pinnacle on each corner, its bell gun on a turret at its front (one long barrel), and a
  tall octagonal needle behind ringed with light.
- **Organ banks** (in the transept arms): each a dark console on the transept's deck, its rotor on
  top (eight barrels on the left, ten on the right: the notes of its chords), and a half ring of
  nine pipes round its outer side, the tallest in the middle, each with a lit mouth and a dark lip,
  a wind chest under them.
- **Rose window** (over the crossing): a great round window, a dark metal rim round smoked glass,
  tracery of light (three rings and twelve spokes), a pale glass petal in each light that brightens
  as it charges, and the laser's emitter on a turret on its hub.
- **Portal gun** (the core's): a fan turret of three barrels on the west front's terrace (its aimed
  shots, fans and bursts).
- **Apse rotor** (the core's): a rotor of twelve barrels on the apse's crown (its rings and spirals).
- **Lantern rotor** (the core's): a rotor of sixteen barrels on the choir's high vessel (its last
  stage's ring). Until then it lies under a hatch, a domed octagonal cap with a seam of light, which
  bursts off as the rotor comes into use (BOSS-58), leaving a collar round the opening.

**Acceptance criteria**
- Given its model, then it draws both spires, both organ banks, the rose window and every gun mount
  (unit test).

*Sources: user request (2026-11-06).*

#### FB-CATHEDRAL-ENGINE-04 — Lights · MUST

Light runs along its roof ridges, eaves, parapets and terrace, its portal arch and lancets, its
spires' rings and its pinnacles' tips, the apse's ribs and the rose window's tracery. Its neon colour,
set violet, shows as its nearest enemy hue ([common](../common.md), BOSS-50); its laser is its neon
folded into the enemy shots' family (BOSS-32).

**Acceptance criteria**
- Given its model, then its lights are one of the two enemy hues.

*Sources: user request (2026-11-06).*

#### FB-CATHEDRAL-ENGINE-05 — Roofs it sheds · MUST

Its armour ([common](../common.md), BOSS-42), each drawn as a piece of its own:
- **Aisle roofs** (`aisles`, mirrored, shed at its first transformation): a lean-to slate roof over
  each of the nave's aisles, from the high wall's foot (13.5 px) down to the outer eaves (8 px),
  ribbed across, a line of light along its eaves; it leaves a `shell` lattice over the aisle's
  vault. The batteries lie under them.
- **Choir aisle roofs** (`choir-aisles`, mirrored, shed at its second): the same over the choir's
  aisles; the sweepers lie under them.
- **High vault** (`vault`, on the centre line, shed at its second): the nave's steep gabled roof
  (10 px to its ridge at 17 px), ribbed, a line of light along its ridge; it leaves a `wing` frame.
  The orb lies under it.

They burst into plates cracked from their outlines.

**Acceptance criteria**
- Given its design, then each transformation sheds a region and every hidden weapon lies in one its
  transformation sheds (unit test).
- Given its model, then it draws each region's armour, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-221, D-224, D-254.*

### Behaviour

#### FB-CATHEDRAL-ENGINE-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs slowly, a sway every four bars. While it is fought the ground stops
(×0).

**Acceptance criteria**
- Given the fight, then the ground eases to a stop and back after it.

*Sources: BOSS-03.*

#### FB-CATHEDRAL-ENGINE-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `spire-left`, `spire-right`,
`organ-left`, `organ-right` and `rose`. The core's guns (the portal gun, the apse rotor and the
lantern rotor) fire the core's volleys and are the last the player destroys. The turrets turn the way
they fire; the rose window's laser turret aims at the player only at `boss_laser_turn` through its
warning line, then holds still (BOSS-31).

**Acceptance criteria**
- Given its design, then its five parts all shield the core (unit test on its design).

*Sources: BOSS-12, BOSS-14, BOSS-58.*

#### FB-CATHEDRAL-ENGINE-08 — Stage patterns: a choir · MUST

Every volley fires on the beats of one bar (`BAR`, 3.2 s, four beats of 0.8 s), so its rings and
spirals of different speeds layer into chords. The parts fire in every stage while they stand:
- each organ bank plays a chord once a bar: two rings at once from its rotor along the same barrels,
  a slow purple one and a fast orange one, turning at each bar (the left bank 8 bullets each,
  turning 11.25°, on the second beat; the right bank 10 each, turning -9°, on the fourth);
- each spire tolls a single red bullet at the player twice a bar, the right one a beat after the
  left;
- the rose window fires its laser (1 s warning line, then a 1.8 s beam 16 px wide) every two bars
  and a half.

The core fires:
- stage 0: a ring of 12 magenta bullets from the apse rotor once a bar, turning 7.5°;
- stage 1: the ring twice a bar, turning -10° (a spiral the other way);
- stage 2: the ring once a bar turning 15°, and an aimed fan of 3, 10° apart, from the portal gun;
- stage 3: a chord of two rings of 12 at once (slow and fast) once a bar, and a burst of 3 from the
  portal gun;
- stage 4: a fast spiral (the ring every second, turning 9°), and the portal gun's aimed fans;
- stage 5 (all five parts gone): a ring of 16 from the lantern rotor and a ring of 12 from the apse
  rotor turning the other way, each twice a bar, a beat apart, and a single aimed bullet from the
  portal gun once a bar.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys, each from its mount (unit test).

*Sources: BOSS-20, BOSS-21, BOSS-58.*

#### FB-CATHEDRAL-ENGINE-09 — Angry · MUST

It is angry after each transformation, when the weapons it revealed fire all out for
`boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's pattern
([common](../common.md), BOSS-27). A lost part does not anger it.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed (unit
  test).

*Sources: BOSS-27.*

#### FB-CATHEDRAL-ENGINE-10 — First transformation · MUST

It transforms the first time when both spires are destroyed (`transformParts`): its aisle roofs
burst off, baring dark metal lattices over the aisles, and two **batteries** unfold on them, either
side of the nave. They shield the core and sweep wide fans of 7 purple bullets straight down.

**Acceptance criteria**
- Given both spires destroyed, then it transforms and its two batteries are revealed (unit test).

*Sources: D-221, D-224, D-228, D-229.*

#### FB-CATHEDRAL-ENGINE-11 — Second transformation · MUST

It transforms the second time when both organ banks are destroyed: its choir aisle roofs and its
nave's high vault burst off; two **sweepers** unfold on the choir's aisles, their beams sweeping
after the player, and an **orb** unfolds on the centre line in the nave, firing turning rings of 10
magenta bullets.

**Acceptance criteria**
- Given both organ banks destroyed, then it transforms and its two sweepers and its orb are revealed
  (unit test).

*Sources: D-221, D-224, D-228, D-229.*

#### FB-CATHEDRAL-ENGINE-12 — Fire rate · MUST

Its weighted fire rate (BOSS-39) never goes down from one transformation to the next and is highest
after the last one (Tunable values).

**Acceptance criteria**
- Given its design, then its fire rate as it comes in and after each transformation goes up (unit
  test, every boss).

*Sources: BOSS-39.*

#### FB-CATHEDRAL-ENGINE-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, and its core always drops
one ([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/cathedral_engine.py` (`_CATHEDRAL_ENGINE`, `CATHEDRAL_ENGINE`)
unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 4.5 L (radius 76.5 px); 145 px long, 128 px across its transept | `stats.size` |
| core | health 2 900, radius 22, drops a bonus | `coreHealth`, `coreRadius`, `coreDrop` |
| `spire-left`, `spire-right` | (∓20, -63), radius 11, health 950, shield, drop 0.6 | `SPIRE_AT` |
| bell guns | (∓20, -67), 15 px high; 1 barrel, bore 1.2, 8 px long; dome radius 3.6 | `BELL_GUN`, `BELL_AT` |
| `organ-left`, `organ-right` | (∓44, 0), radius 14, health 1 200, shield, drop 0.6 | `ORGAN_AT` |
| organ rotors | 17 px high; 8 barrels (hub 5) / 10 barrels (hub 5.4), bore 1, 4 px long | `ORGAN_ROTOR_LEFT`, `ORGAN_ROTOR_RIGHT` |
| `rose` | (0, 0), radius 15, health 1 400, shields, drop 0.6 | `ROSE_AT` |
| rose laser | (0, 0), 19 px high; turret, base radius 5.5, bore 2.6, 12 px long | `ROSE_LASER` |
| portal gun (core) | (0, -66), 10 px high; 3 barrels, bore 1, 7 px long; dome radius 4.8 | `mounts` `portal` |
| apse rotor (core) | (0, 50), 16 px high; 12 barrels, bore 0.9, 3.6 px long; hub radius 5.5 | `mounts` `apse-rotor` |
| lantern rotor (core) | (0, 31), 16 px high; 16 barrels, bore 0.7, 3 px long; hub radius 5.2 | `mounts` `lantern-rotor` |
| lantern hatch | octagon of radius 6.5 round (0, 31); bursts as the rotor comes into use | `armour_region` `lantern-hatch` (`mount`) |
| full health | 15 040 (core 2 900, parts 5 700, batteries 2 240, sweepers and orb 4 200) | BOSS-54; the 1-3 final boss (Mesa Fortress) has 15 000 |
| points | 11 000; 1 100 a part | |
| ground speed | ×0 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 26 px over 12.8 s / 4 px over 6.4 s | |
| rhythm | a bar of 3.2 s, four beats of 0.8 s | `BAR`, `BEAT` |
| bullets | low: purple 110 px/s radius 4.5; mid: magenta 135; high: orange 175; bell: red 200 | `LOW`, `MID`, `HIGH`, `BELL` |
| spires | 1 aimed bell bullet every 1.6 s (first 0.4 s / 1.2 s) | |
| organ chords | left: rings of 8 low + 8 high turning 11.25°, every 3.2 s (first 0.8 s); right: rings of 10 low + 10 high turning -9°, every 3.2 s (first 2.4 s) | |
| rose laser | 1.8 s beam 16 px wide, every 8 s (first 3.2 s) | `volley.laser` |
| core stage 0 | ring of 12 mid turning 7.5°, every 3.2 s (first 1.6 s) | apse rotor |
| core stage 1 | ring of 12 mid turning -10°, every 1.6 s (first 0.8 s) | apse rotor |
| core stage 2 | ring of 12 mid turning 15°, every 3.2 s; aimed fan of 3 bell, 10° apart, every 3.2 s | apse rotor; portal gun |
| core stage 3 | rings of 12 low + 12 high turning 7.5°, every 3.2 s; burst of 3 bell, 0.12 s apart, every 3.2 s | apse rotor; portal gun |
| core stage 4 | ring of 12 mid turning 9°, every 1 s; aimed fan of 3, every 3.2 s | apse rotor; portal gun |
| core stage 5 | ring of 16 mid turning 11.25°, every 1.6 s (first 0.4 s); ring of 12 high turning -7.5°, every 1.6 s (first 1.2 s); 1 aimed bell every 3.2 s | lantern rotor; apse rotor; portal gun |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformations | both spires destroyed; then both organ banks | `transformParts` |
| shed regions | aisles: x 11..24, y -56..-18, 8..13.5 px, `shell`, mirrored; choir-aisles: x 10..23, y 18..46, 8..13.5 px, `shell`, mirrored; vault: x -11..11, y -56..-18, 10..17 px, `wing` | `armour_region`, `AISLE_ROOF`, `CHOIR_ROOF`, `VAULT` |
| batteries | (∓17.5, -37), radius 7, health 1 120, pod from 8 to 11 px; fans of 7 purple, 9° apart, straight down, 180 px/s, every 2 s; first 1.2 s / 2.0 s | `hidden_weapon`, first transformation |
| sweepers | (∓16.5, 32), radius 7, health 1 400, pod from 8 to 11 px; sweeping laser 2 s every 8 s; first 1.2 s / 2.4 s | `hidden_weapon`, second transformation |
| orb | (0, -37), radius 8, health 1 400, pod from 10 to 13.5 px; rings of 10 magenta 175 px/s turning 13°, every 2.6 s; first 1.6 s | `hidden_weapon`, second transformation, centre line |
| fire rate (BOSS-39) | 17.3 as it comes in, 23.9 after its first transformation, 26.8 after its second | weighted shots a second |
| neon | violet (0.75, 0.3, 1) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered in `BOSS_DESIGNS`, `BOSS_MODELS` and `BOSS_LOOK.neon` after the
  World bosses, and no level's boss table names it.
- **Not a creature (2026-11-06).** BOSS-47's Cyber-Organic look is set aside for this boss on the
  user's request; it is drawn from hull metal, slate and glass, with no flesh but the rose window's
  smoked glass (drawn on the flesh layer for its waxier finish).
- **Simulated fight (2026-11-06, a part broken every 12 s):** 2 438 shots and 24 lasers, every one
  from a barrel's tip along it (0 off); dead at 134 s.
- **Triangles (scratch count, 2026-11-06):** about 8 480 seen from above for its body, parts,
  armour, hidden weapons and gun mounts (its eight mounts, four of them rotors of 8 to 16 barrels,
  about 3 400 of them), of the 10 000 budget (BOSS-53).
