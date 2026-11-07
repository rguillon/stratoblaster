# Drill Fort

> **Area:** bosses · **Prefix:** `MB-DRILL-FORT` · **Related:** [common](../common.md),
> [Aqueduct Leviathan](L-23-aqueduct-leviathan.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Drill Fort is the mini boss of Lab level L-23: a gigantic flying mining fortress, about 3.4 L
long. A huge spiralled drill head spins at its front; behind it a boxy armoured body rides on two
long track pontoons, a conveyor belt runs down its back from the drill's intake to the control cab,
two ore hoppers stand either side of the belt and two exhaust stacks smoke at its back corners. It
comes in with only three guns (two of them fixed) and brings out more with every part it loses:
turrets rise out of its rear hoppers' ore, a fixed spitter out of the conveyor's head, a rotor out of
its tail. Halfway through, its front hoppers tip over its sides, dumping their ore, and a mortar
rises out of each. Shared rules are in [common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "10 more gigantic flying fortress, add non rotating guns too, don't
add too many start guns, 3 max, then more appear when they are destroyed") this Lab boss is a
machine, not a creature: dark metal plating, tracks, rock, pipes and neon light lines, no flesh,
eyes or veins.

## Requirements

### Look

#### MB-DRILL-FORT-01 — Silhouette and size · MUST

Seen from above, its nose down the screen: a cone (the drill, from y -37 to its tip at y -76) on
the front of a rectangular body (x ±24, y -30 to 38) flanked by two track pontoons (x ±25 to ±35,
y -26 to 34); about 3.4 L long and 2 L across. On the body's deck: the conveyor down its centre line
(x ±3.6, y -30 to 24) rising into an intake housing over the drill's collar, two hoppers either side
of it, two banded exhaust stacks at (±19, 29) with glowing mouths, and the control cab at its back
(x ±11, y 25 to 38) with lit windows and two aerials. Tread plates across the pontoons, a sprocket
drum at each of their ends, lit seams round the deck and along the pontoons, vents along its walls.

**Acceptance criteria**
- Manual validation in the boss viewer: a tracked mining fortress with a drill at its front; no
  other boss has a drill head or tracks.

*Sources: Lab boss request (2026-11-06, "gigantic flying fortress").*

#### MB-DRILL-FORT-02 — The drill head · MUST

The drill head is a 12-sided cone (base radius 12, axis 7.5 px high) on a bearing in a thick
armoured collar (radius 13, y -29 to -37) braced to the body. Three spiral flutes wind 1.25 turns
round it, hardened blade segments with lit cutting edges, and turn about its axis (MB-DRILL-FORT-05).

**Acceptance criteria**
- Manual validation: the drill's flutes visibly spin.

*Sources: Lab boss request (2026-11-06).*

#### MB-DRILL-FORT-03 — Hoppers · MUST

Four ore hoppers stand on the deck either side of the conveyor, tapered bins with lit rims full of
dark ore lumps: the front pair (x ±5 to ±19, y -22 to -7) carry the mortars beneath them
(MB-DRILL-FORT-10); the rear pair (y 2 to 17) carry a turret each under a barred grate
(MB-DRILL-FORT-04).

**Acceptance criteria**
- Manual validation: four hoppers, ore in each.

*Sources: Lab boss request (2026-11-06).*

#### MB-DRILL-FORT-04 — Its parts and guns · MUST

Its gun mounts (BOSS-58), the fixed ones pointing straight down the screen:

| Mount | Piece | Where | Kind | First used |
|-------|-------|-------|------|------------|
| `gun-left`, `gun-right` | cheek casemates (parts) | (∓19, -39), 12 high | **fixed** twin cannon, barrels 2.6 px apart | stage 0 |
| `cab-gun` | core | (0, 31.5) on the cab's roof, 20 high | twin turret | stage 0 |
| `hopper-gun-left`, `-right` | core | (∓12, 9.5) in the rear hoppers, 18.5 high, under their grates | triple turret | stage 1 |
| `spitter` | core | (0, -28) on the intake housing, 21 high, under its cowl | **fixed** triple gun | stage 2 |
| `rotor` | core | (0, 19) on the conveyor's tail, under its cowl | rotor of 10 barrels | stage 3 |

Its parts: the two cheek casemates (armoured wedge sponsons on the body's front corners, either
side of the drill, each carrying its fixed cannon) and the drill head (no gun: a target whose loss
still brings out new guns). Each grate and cowl over a late gun is a hatch (`armour_region(...,
mount=...)`) that bursts as its gun first comes into use.

**Acceptance criteria**
- Given its design, then three parts there from the start, at most three mounts in use in stage 0
  (two fixed), and each later stage uses at least one mount no earlier stage used.
- Manual validation: each late gun bursts its hatch and rises out.

*Sources: user request (2026-11-06, "3 max, then more appear", "non rotating guns too").*

#### MB-DRILL-FORT-05 — Lights and moving looks · MUST

Its neon is amber (1, 0.75, 0.1), shown yellow (BOSS-50). Its view rig (`drill_fort_rig`) turns the
drill's flutes all the time (5 rad/s, 2.6 times faster while it transforms), hides them once the
drill head is destroyed, and carries ore lumps back along the conveyor belt. Visual only.

**Acceptance criteria**
- Manual validation: amber-yellow lights; the flutes turn and the ore rides the belt.

*Sources: BOSS-50, Lab boss request.*

### Behaviour

#### MB-DRILL-FORT-06 — Coming in and moving · MUST

It stops at 0.74 of the playfield's height and grinds slowly: a 45 px sway over 8 s, a 3 px bob
over 3.4 s. Its fight ground speed is ×0.6.

*Sources: BOSS-03, BOSS-08, BOSS-10.*

#### MB-DRILL-FORT-07 — Parts and core · MUST

Its parts: `gun-left` and `gun-right` (radius 8, 700 each), `drill` (at (0, -55), radius 13, 850);
its core 1 100 (radius 16). Every part shields the core (BOSS-14); its last guns are the core's.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### MB-DRILL-FORT-08 — Stage patterns and guns out · MUST

Its parts' volleys: each cheek cannon fires a pair of parallel bullets straight down along its
barrels every 2.4 s. The core's pattern per stage, the guns brought out staying in use:

| Stage | Core fires | Guns out (fixed) |
|-------|------------|------------------|
| 0 | `cab-gun`: aimed singles | 3 (2) |
| 1 | `cab-gun` aimed spreads of 3; both hopper turrets' bursts of 3 | 4 (1) with a cheek cannon lost, 5 (2) with the drill lost |
| 2 (transformed) | `cab-gun` aimed; hopper turrets' bursts; `spitter` parallel triples of shells straight down | 4-5 + 2 mortars |
| 3 (last) | `rotor` rings of 10 (new); spitter; cab spreads; hopper bursts | 5 + the mortars left |

**Acceptance criteria**
- Given each stage, then its pattern differs from the one before, and the last stage's ring is used
  in no earlier stage (BOSS-21).
- Given the fixed guns, then they fire only along their barrels.

*Sources: BOSS-20, BOSS-21, BOSS-58, user request (2026-11-06).*

#### MB-DRILL-FORT-09 — Angry · MUST

After its transformation it is angry (BOSS-27): only its two mortars fire, 4.5 times as often, for
8 s.

*Sources: BOSS-27.*

#### MB-DRILL-FORT-10 — Transformation: the hoppers tip · MUST

Once two of its parts are destroyed (BOSS-36's default), its front hoppers tip out over its sides:
each swings 118° about its outer bottom edge (a moving piece, BOSS-45, `swing` along the boss), its
ore load bursts into lumps (an armour region shed, BOSS-42, leaving a dark lattice floor) and a
mortar (hidden weapon, BOSS-40) unfolds out of the deck where the hopper stood, at (±12, -14.5). The
tipped bins come to rest lying over the tracks. The fight changes from straight-down walls and aimed
shots to flak bursting into rings across the screen.

**Acceptance criteria**
- Manual validation: the hoppers tip over the sides as the ore bursts, the mortars rise.

*Sources: BOSS-35, BOSS-42, BOSS-45, Lab round-3 request ("get creative on how the boss
transforms").*

#### MB-DRILL-FORT-11 — Death, drops and points · MUST

Its points are 4 400; its parts drop a bonus half the time, its mortars 30 % (BOSS-57).

*Sources: BOSS-19, BOSS-57.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| full health | 4 710 (core 1 100, parts 700 / 700 / 850, mortars 680 each) | BOSS-54 |
| stop height | 0.74 | `stopFraction` |
| sway / bob | 45 px over 8 s / 3 px over 3.4 s | |
| cheek cannons | 2 red at 185 px/s, parallel, straight down, every 2.4 s (first 1 s / 2.2 s) | fixed |
| cab turret | aimed 1 orange at 175 px/s every 2.6 s; spreads of 3, 8° apart, every 2.8 s | |
| hopper turrets | bursts of 3 red, 0.13 s apart, every 2.8 s (first 0.8 s / 2.2 s) | |
| spitter | 3 orange shells (radius 5, 160 px/s), parallel, straight down, every 2.2 s | fixed |
| rotor | rings of 10 orange turning 9°, every 1.6 s | last stage |
| mortars | (±12, -14.5), radius 7, health 680, pod 12 to 14.5 px; first 1.2 s / 2 s | `mortar` kind |
| hopper tip | 118° about (±19, -14.5, 12), along the boss | `HOPPER_TIP` |
| weighted fire rate | 2.05 as it comes in, 4.52 after its transformation | BOSS-39 |
| neon | amber (1, 0.75, 0.1) | `BOSS_LOOK.neon` |
| triangles | about 3 360 (core 1 916, parts 324, armour 616, rig 504) | BOSS-53: 4 000 |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is near the 1-3 mini boss's.
- **Not a creature** (see the departure from BOSS-47 above).
- **Hatches** (four: grates and cowls) have no transformation (`form` None): the known test-helper
  crash on hatch regions applies.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 468 shots, every one from
  a barrel, along it; it dies at about 74 s.
