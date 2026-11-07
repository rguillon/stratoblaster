# Monolith Array

> **Area:** bosses · **Prefix:** `MB-MONOLITH-ARRAY` · **Related:** [common](../common.md),
> [Star Engine](L-10-star-engine.md)

The Monolith Array is the mini boss of the Lab's level L-10. **Lab boss: in the dev viewer only**
(the dev menu's Bosses list, after the bosses of the worlds); no level brings it in. Three tall,
dark obelisks hover in a row over a low platform of stone and metal: the big central one is its
core, the two side ones its parts, linked at their feet by channels and beams of light, cyan glyphs
cut into their faces. It is slow, precise and ominous: long lasers from the side monoliths, rare but
dense rings from the centre and precise aimed shots; once a side monolith is down, the plinth plates
on its platform burst off and a pair of lances unfold. Shared rules are in [common](../common.md).

**Departs from BOSS-47.** On the user's request (2026-11-06, "drop the animal looking theme") the
Lab bosses of L-6 to L-10 are machines, structures and abstract geometry, not Cyber-Organic
creatures: the Monolith Array is dark stone and metal with neon light lines, with no flesh, eyes,
teeth or veins.

## Requirements

### Look

#### MB-MONOLITH-ARRAY-01 — Silhouette and size · MUST

Seen from above, the Monolith Array is a row of three obelisks 3.4 L across standing over a low,
wide platform with cut corners: the tallest in the middle, a shorter one either side. It is wider than it
is deep, flat and architectural, unlike any other boss.

**Acceptance criteria**
- Manual validation in the boss viewer: three dark obelisks in a row over a platform.

*Sources: Lab brief (2026-11-06).*

#### MB-MONOLITH-ARRAY-02 — Body · MUST

The platform is a bevelled slab of dark stone (its top 5 px high), a rim of light round its edge,
metal rails round its two ends and vents across its back; two channels of light run on its top from
the central pylon out to each side pylon. Each obelisk hovers over the platform on a dark hexagonal
pylon ringed with light: its shaft a tapering, chamfered stone frustum (its foot 13 px over the
platform for the central one), glyph strokes of light cut into its four broad faces and a lit seam
up each of its front chamfers. The central obelisk rises to 52 px and ends in a flat metal collar,
the crown rotor's seat; before it, a squat stone plinth carries the sight turret, tied to its pylon
by a buttress.

**Acceptance criteria**
- Manual validation: carved stone obelisks hovering over a platform, glyphs of light on their faces.

*Sources: Lab brief.*

#### MB-MONOLITH-ARRAY-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Side monoliths** (`monolith-left`, `monolith-right`): each a pointed obelisk on its pylon (its
  shaft up to 40 px, a pyramidion with a light on its tip), a laser emitter set in a dark socket in
  its front face, 22 px high, firing straight down the screen; two beams of light link it to the
  central obelisk's flank.
- **Crown rotor** (the core's): sixteen barrels round a hub on the central obelisk's collar (its
  rings).
- **Sight** (the core's): one long barrel on a turret on the plinth before the central obelisk (its
  aimed shots and bursts).

**Acceptance criteria**
- Given its model, then it draws both side monoliths and every gun mount.

*Sources: Lab brief, BOSS-58.*

#### MB-MONOLITH-ARRAY-04 — Lights · MUST

Its glyphs, seams, pylon rings, field channels and beams and the platform's rim glow. Its neon
colour, cyan, shows bright green ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: Lab brief, BOSS-50.*

#### MB-MONOLITH-ARRAY-05 — Plinth plates · MUST

Two stone plinth plates lie on the platform's front, either side of the sight's plinth, a glyph of
light along each: they are the armour it sheds at its transformation ([common](../common.md),
BOSS-42), drawn as a piece of their own. Their region (`plinths`, mirrored) bursts into plates
cracked from its outline and leaves a `shell` lattice frame. The two lances lie folded under them.

**Acceptance criteria**
- Given its design, then its one transformation sheds the plinths region and both lances lie in it.
- Given its model, then it draws the region's armour, and it holds together with and without it.

*Sources: Lab brief, BOSS-42, BOSS-52.*

### Behaviour

#### MB-MONOLITH-ARRAY-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs slowly (an 11 s sway, a 6 s bob). While it is fought the ground scrolls
at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.5 of the level's speed and back after it.

*Sources: BOSS-03.*

#### MB-MONOLITH-ARRAY-07 — Parts and core · MUST

It has two parts as it comes in, both shielding its core: `monolith-left` and `monolith-right`. The
core's guns (the crown rotor and the sight) fire the core's volleys and are the last the player
destroys. The sight turns the way it fires.

**Acceptance criteria**
- Given its design, then its two parts both shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-MONOLITH-ARRAY-08 — Stage patterns · MUST

The side monoliths fire in every stage while they stand: a long laser (2.2 s) straight down the
screen every 7 s, the two in turn (3.5 s apart). The core fires, from its crown rotor, a ring of 16
(one bullet a barrel), rare but dense, turning a little more at each volley, a new turn and pace at
every stage, with its sight's shots:
- stage 0: the ring every 3.4 s turning 11.25° (half a barrel's spacing), and a single aimed shot;
- stage 1: the ring every 2.9 s turning the other way (7°), and a burst of 3;
- stage 2 (both monoliths gone): the ring every 1.9 s turning 5.625°, and a burst of 4.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys.

*Sources: BOSS-20, BOSS-21.*

#### MB-MONOLITH-ARRAY-09 — Angry · MUST

It is angry after its transformation: its two lances fire all out for `boss_rage_seconds`, as often
as their warning, beam and gap allow, instead of its stage's pattern ([common](../common.md),
BOSS-27).

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two lances.

*Sources: BOSS-27.*

#### MB-MONOLITH-ARRAY-10 — Transformation · MUST

It transforms once, when one side monolith is destroyed (half of its two parts, the default
threshold): its plinth plates burst off, baring a dark metal lattice, and two **lances** unfold on
the platform's front, either side of the sight. They shield the core and fire lasers straight down
the screen, in turn.

**Acceptance criteria**
- Given one part destroyed, then it transforms and its two lances are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-40.*

#### MB-MONOLITH-ARRAY-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its lances 30 % ([common](../common.md), BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/monolith_array.py` (`_MONOLITH_ARRAY`, `MONOLITH_ARRAY`) unless
named.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.4 L (radius 57.8 px) | `stats.size` |
| platform | cut-cornered, (0, -21) to (54, 4) to (0, 17), mirrored; top 5 px high | `PLATFORM_HALF`, `PLATFORM_TOP` |
| central obelisk | (0, 4); foot 20 × 15 px at 13 px, head 11.6 × 8.6 px, collar to 52 px | `CORE_AT`, `CORE_FOOT`, `CORE_HEAD`, `CORE_HOVER`, `CORE_TOP` |
| side obelisks | (±41, 6); foot 14 × 11.2 px at 11 px, head 8 × 6.4 px at 40 px, tip 9 px over it | `SIDE_AT`, `SIDE_FOOT`, `SIDE_HEAD`, `SIDE_HOVER`, `SIDE_TOP` |
| core | health 2 100, radius 16 | `coreHealth`, `coreRadius` |
| `monolith-left`, `monolith-right` | (±41, 6), radius 13, health 1 150, shield, drop 0.5 | |
| side lasers | emitters at (±41, 2), 22 px high; dome 4, bore 2.2, 9 px long; fixed, down the screen | `SIDE_LASER`, `EMITTER_Y`, `EMITTER_HEIGHT` |
| crown rotor (core) | (0, 4), 52 px high; 16 barrels, bore 0.75, 4 px long, hub 5.5 | `CROWN_ROTOR`, `mounts` `crown` |
| sight (core) | (0, -14), 9.5 px high; 1 barrel, bore 1.1, 9 px long, dome 3.6 | `SIGHT_GUN`, `mounts` `sight` |
| full health | 6 240 (2 100 + 2 × 1 150 + 2 × 920) | BOSS-54 |
| points | 5 500; 550 a part | |
| ground speed | ×0.5 | |
| stop height | 0.74 | `stopFraction` |
| sway / bob | 34 px over 11 s / 4 px over 6 s | |
| side lasers' volleys | 2.2 s beam every 7 s (first 2 s / 5.5 s) | |
| core stage 0 | ring of 16 turning 11.25°, purple 150 px/s, every 3.4 s (first 1.2 s); aimed 1, red 215 px/s, every 2.4 s | |
| core stage 1 | ring of 16 turning -7° every 2.9 s; burst of 3, 0.22 s apart, every 2.6 s | |
| core stage 2 | ring of 16 turning 5.625° every 1.9 s; burst of 4, 0.2 s apart, every 2.2 s | |
| weighted fire rate | 7.4 as it comes in, 9.9 after its transformation | BOSS-39 |
| angry | the revealed lances, BOSS-27 | `boss_build.angry_pattern` |
| transformation | 1 part destroyed | default threshold |
| shed region | plinths: (13, -16), (32, -14), (33, -2), (13, -2), mirrored, `shell`, 4.5 to 9 px high | `PLINTH_OUTLINE`, `PLINTH_HEIGHTS` |
| lances | (±22, -9), radius 8, health 920 (0.8 × 1 150), pod 5 to 9 px, purple; first 1.2 s / 2.4 s; laser 1.4 s every 7.5 s | `LANCE_AT` |
| neon | cyan (0.1, 1, 1), shown green | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered among the game's boss kinds (`game/sim/boss_kinds.py`) and models
  only so that the dev viewer lists it; no world's boss table names it. The world-wide counts of the
  common rules (BOSS-41, BOSS-45, BOSS-55) were written for the four worlds and do not count it.
- **Lances on a laser boss.** BOSS-38 asks for hidden kinds the boss does not fire yet, where
  possible; its lances were chosen with the set's plan of hidden kinds, and they fire down the
  middle, between the side monoliths' beams.
- **No hatch.** Both its core guns fire from stage 0, so neither needs a hatch (BOSS-58).
- **Model.** Its solids are built face by face (`view/bosses/lab/monolith_array_kit.py`: faceted
  frustums and glyph strokes), shared with the [Star Engine](L-10-star-engine.md).
- **Check (2026-11-06).** A simulated fight breaking a part every 12 s: 419 shots, every one
  leaving a barrel's tip along it, 16 lasers, dead at 62 s. Its model holds together at rest and
  after its transformation, about 1 340 triangles (BOSS-53: 4 000).
