# Aqueduct Leviathan

> **Area:** bosses · **Prefix:** `FB-AQUEDUCT-LEVIATHAN` · **Related:** [common](../common.md),
> [Drill Fort](L-23-drill-fort.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Aqueduct Leviathan is the final boss of Lab level L-23: a gigantic flying viaduct spanning
across the screen, about 6.7 L wide and 2 L deep. Five stone piers with pointed cutwaters carry iron
arch ribs and a channel of glowing water along its whole length; a crenellated keep stands over its
middle pier, a gate tower on each abutment, and a lift engine is slung before each outer pier. It
comes in with only three guns (two fixed, hung under its middle arches) and brings out a new gun or
pair from under a hatch with every part it loses. Its sluice houses slide back to free a pair of
lances, then its channel breaks at the keep and its middle sections swing forward like gates,
baring a gatling on each arch, while the keep's cutwater bursts off on an orb. Shared rules are in
[common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "10 more gigantic flying fortress, add non rotating guns too, don't
add too many start guns, 3 max, then more appear when they are destroyed") this Lab boss is a built
structure, not a creature: dressed stone, iron, glowing water and neon light lines, no flesh, eyes
or veins.

## Requirements

### Look

#### FB-AQUEDUCT-LEVIATHAN-01 — Silhouette and size · MUST

Seen from above: a long, thin bridge across the screen (x ±114, y ±13 for its deck), its piers at
x 0, ±36, ±72 (12 px wide) sticking out front and back as pointed cutwaters (to y ±31), its
abutments at x ±94 to ±114 with a square gate tower on each. Between the piers, open spans: an iron
arch rib at the front and one at the back (y ±10 to ±14, voussoirs on a half circle, a lit keystone
at the crown), stringers along their tops, ties across, and the water channel (y ±6) along the
middle, its glowing water lit along its centre and its walls' tops. The keep (x ±9, y ±11, 44 high)
over the middle pier: merlons, corner pinnacles, lit slits, dark gates where the channel runs
through. The lift engines' ducts before the outer piers' front cutwaters.

**Acceptance criteria**
- Manual validation in the boss viewer: a viaduct of arches and piers carrying a glowing channel,
  towers at its ends and a keep in its middle; no other boss is a bridge.

*Sources: Lab boss request (2026-11-06, "gigantic flying fortress").*

#### FB-AQUEDUCT-LEVIATHAN-02 — Parts · MUST

- `arch-gun-left`, `arch-gun-right`: armoured housings hung under the ribs of the spans at x ±54,
  each carrying a fixed triple gun;
- `engine-left`, `engine-right`: ducted lift fans at (±72, -40), on pylons from the outer piers'
  cutwaters (no gun);
- `tower-left`, `tower-right`: the gate towers on the abutments, at (±104, 0) (no gun): crenellated,
  lit bands and slits, a beacon on the roof.

Gunless parts still read as targets (lit outlines, BOSS-48) and their loss brings out new guns.

*Sources: BOSS-13, BOSS-48, user request (2026-11-06).*

#### FB-AQUEDUCT-LEVIATHAN-03 — Guns · MUST

Its gun mounts (BOSS-58); fixed ones point straight down the screen:

| Mount | Piece | Where | Kind | First used |
|-------|-------|-------|------|------------|
| `arch-gun-left`, `-right` | arch gun parts | (∓54, -20), 9 high | **fixed** triple gun | stage 0 |
| `keep-gun` | core | (0, 0) on the keep's roof, 44 high | twin turret | stage 0 |
| `outer-gun-left`, `-right` | core | (∓86, -20) under the outer arches, in shrouds | **fixed** triple gun | stage 1 |
| `pier-turret-left`, `-right` | core | (∓72, 26) on the outer piers' back cutwaters, under caps | twin turret | stage 2 |
| `keep-laser` | core | (0, -13) on the keep's face, 26 high, behind a shutter | **fixed** laser | stage 3 |
| `missile-left`, `-right` | core | (∓36, 26) on the inner piers' back cutwaters, under caps | 2-port missile block | stage 4 |
| `cut-gun-left`, `-right` | core | (∓36, -26) on the inner piers' front cutwaters, under caps | **fixed** twin gun | stage 5 |
| `rotor` | core | (0, 26) on the keep pier's back cutwater, under a cap | rotor of 14 | stage 6 |

Every late core gun lies under a hatch (`armour_region(..., mount=...)`) that bursts as it first
comes into use.

*Sources: BOSS-58, user request (2026-11-06).*

#### FB-AQUEDUCT-LEVIATHAN-04 — Lights · MUST

Its neon is steel blue (0.5, 0.7, 1), shown green (BOSS-50): keystones, the water's centre line,
the channel's walls, seams on the piers, slits and bands on the towers and keep.

*Sources: BOSS-50.*

#### FB-AQUEDUCT-LEVIATHAN-05 — Lift fans · MUST

Its view rig (`aqueduct_leviathan_rig`) spins five blades in each lift engine's duct (9 rad/s, 2.2
times faster while it transforms), hidden once that engine is destroyed. Visual only.

*Sources: Lab boss request.*

### Behaviour

#### FB-AQUEDUCT-LEVIATHAN-06 — Coming in and moving · MUST

It stops at 0.76 of the playfield's height; very wide, it drifts only a little: an 18 px sway over
12 s (cut further to keep its towers in the ship's reach, BOSS-10), a 3 px bob over 5.5 s. Its fight
ground speed is ×0.4.

*Sources: BOSS-03, BOSS-10.*

#### FB-AQUEDUCT-LEVIATHAN-07 — Parts and core · MUST

Arch guns 950 each (radius 9), engines 1 100 (radius 11), towers 1 250 (radius 13); core 2 650
(radius 14). Every part shields the core (BOSS-14).

*Sources: BOSS-12, BOSS-14.*

#### FB-AQUEDUCT-LEVIATHAN-08 — Stage patterns and guns out · MUST

Its parts' volleys: each arch gun fires three parallel bullets straight down every 2.6 s. The core's
pattern per stage, the guns already out staying in use:

| Stage | New in the core's pattern | Guns out (fixed), the parts' guns as in the fight's order |
|-------|---------------------------|----------------------------------------|
| 0 | keep turret aimed singles | 3 (2) |
| 1 | keep aimed pairs; outer arch guns' parallel triples | 4 (3) |
| 2 (1st transformation) | keep bursts of 3; pier turrets' aimed shots | 5 (2) + 2 lances |
| 3 | keep aimed spreads of 3; the keep's laser | 6 (3) + lances |
| 4 (2nd transformation) | keep bursts of 4; missile pairs | 8 (3) + gatlings, orb |
| 5 | keep aimed singles; front cutwater guns' parallel pairs | 10 (5) + the weapons left |
| 6 (last) | the rotor's spiral of 14 (new); keep bursts of 3 | 11 (5) + the weapons left |

(With the arch guns destroyed first; if a gunless part goes first the count is one or two higher.)

**Acceptance criteria**
- Given each stage, then its pattern differs from the one before, and the last stage's ring is used
  in no earlier stage (BOSS-21); at most three mounts in use in stage 0.

*Sources: BOSS-20, BOSS-21, BOSS-58, user request (2026-11-06).*

#### FB-AQUEDUCT-LEVIATHAN-09 — Angry · MUST

After each transformation it is angry (BOSS-27): first its lances, then its gatlings and orb fire,
4.5 times as often, for 8 s.

*Sources: BOSS-27.*

#### FB-AQUEDUCT-LEVIATHAN-10 — First transformation: the sluices open · MUST

Once two of its parts are destroyed (BOSS-36's default), the sluice house over each inner pier (a
stone gatehouse with an iron roof and a gate wheel, straddling the channel) slides 13 px back along
the pier (a moving piece, BOSS-45 `slide`), leaving a dark lattice floor, and a lance (BOSS-40)
unfolds out of the lock it covered at (±36, -4), pointing down the screen. The fight gains lasers to
outrun on top of its walls of straight-down fire.

*Sources: BOSS-35, BOSS-45.*

#### FB-AQUEDUCT-LEVIATHAN-11 — Second transformation: the channel breaks · MUST

Once four of its parts are destroyed, the channel breaks at the keep: each of its two middle
sections (from the keep's face to the inner pier, x ±9.5 to ±29.5) swings 90° forward about its
outer front corner like a gate (BOSS-45 `swing` about the vertical), ending as a prong pointing down
the screen either side of the keep; a gatling (BOSS-40) unfolds on each bared arch at (±19.5, 0),
and the keep pier's front cutwater bursts off (BOSS-42) on an orb at (0, -24), on its centre line.
The bridge's silhouette changes from a straight line to a line with two jaws; the fight turns from
lanes to dodge into aimed bursts and turning rings.

*Sources: BOSS-35, BOSS-41, BOSS-42, BOSS-45.*

#### FB-AQUEDUCT-LEVIATHAN-12 — Death, drops and points · MUST

Its points are 10 000; its core always drops a bonus; its parts 60 %, its hidden weapons 30 %
(BOSS-57).

*Sources: BOSS-19, BOSS-57.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| full health | 15 000 (core 2 650; parts 2 × 950, 2 × 1 100, 2 × 1 250; lances 2 × 1 000; gatlings 2 × 1 250, orb 1 250) | as the 1-3 final boss (Mesa Fortress, 15 000) |
| stop height | 0.76 | `stopFraction` |
| sway / bob | 18 px over 12 s / 3 px over 5.5 s | |
| arch guns, outer guns | 3 red at 185 px/s, parallel, straight down, every 2.6 s / 2.8 s | fixed |
| keep turret | aimed 1 / 2 (6°) / 3 (8°) orange at 175 px/s, or bursts of 3-4, every 2.4-2.8 s | |
| pier turrets | aimed 1 orange every 2.8 s | |
| keep laser | 1.4 s beam every 7 s, straight down | fixed |
| missiles | 2 homing, 20° apart, every 6.5 s from each block | |
| cutwater guns | 2 orange shells (radius 5, 160 px/s), parallel, straight down, every 2.4 s | fixed |
| rotor | rings of 14 orange turning 12.9°, every 1.6 s | last stage |
| lances | (±36, -4), radius 7, pod 17 to 19 px; first 1.2 s / 2.4 s | `lance` kind |
| gatlings | (±19.5, 0), radius 7, pod 17.6 to 19.4 px; first 1.2 s / 2 s | `gatling` kind |
| orb | (0, -24), radius 7, pod 8.6 to 11 px; first 1.6 s | `orb` kind |
| sluice slide | 13 px back (+Y) | `SLUICE_SLIDE` |
| channel swing | 90° about (±29.5, -6) | `LEAF_SWING` |
| weighted fire rate | 2.72 as it comes in, 6.14 after its first transformation, 16.28 after its second | BOSS-39 |
| neon | steel blue (0.5, 0.7, 1) | `BOSS_LOOK.neon` |
| triangles | about 5 600 (core 3 060, parts 1 104, armour 1 134, rig 296) | BOSS-53: 10 000 |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time (BOSS-56) is not set. Its
  full health matches the 1-3 final boss's.
- **Not a creature** (see the departure from BOSS-47 above).
- **Hatches** (ten) have no transformation (`form` None): the known test-helper crash on hatch
  regions applies.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 869 shots and 38
  lasers, every shot from a barrel, along it; it dies at about 146 s.
