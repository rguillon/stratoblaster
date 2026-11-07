# Star Fort

> **Area:** bosses · **Prefix:** `FB-STAR-FORT` · **Related:** [common](../common.md),
> [Mortar Raft](L-25-mortar-raft.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Star Fort is the final boss of Lab level L-25 and the climax of the fifth round: a gigantic
flying star fort about 5.5 L across, a five-pointed Vauban fortress on a slab of floating rock
ringed by a moat of glowing energy: angled bastions round a central keep and its parade ground, a
ravelin in front of each forward curtain, a gatehouse in the rear curtain. It comes in with three
guns; every part it loses opens more embrasures along its bastions' faces, fixed guns firing along
the faces' normals, so it bristles more and more. Once the moat's two pylons are down its rear
bastions swing out on their pivots like wings, a sweeper laser riding each; once both ravelins are
down its keep rises on a pinnacle of rock, a gatling on its roof, and the flagstones either side of
it burst off on a battery each. A fortress first, a laser cross-fire next, at last a keep raining
fire from high above. Shared rules are in [common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "10 more gigantic flying fortress, add non rotating guns too, don't
add too many start guns, 3 max, then more appear when they are destroyed") this Lab boss is
architecture, not a creature: dressed stone, rock, iron and neon lights, no flesh, eyes or veins.

## Requirements

### Look

#### FB-STAR-FORT-01 — Silhouette and size · MUST

Seen from above, its nose down the screen, it is a five-pointed star: bastions on capitals 0°
(the nose), ±72° and ±144°, their salients 68 px out, shoulders 40 px out 20° off the capital,
flank roots 35 px out 24° off; a triangular ravelin on ±36° (apex 53 px out); all on a lumpy round
slab of rock about 80 px in radius, a moat of energy round it (70.5 to 74 px). About 5.5 L across.
After its first transformation its rear bastions stand swung out sideways like wings; after its
second its keep stands high on a pinnacle of rock.

**Acceptance criteria**
- Manual validation in the boss viewer: a star fort on its rock; wings out after the first
  transformation; a tall keep after the second.

*Sources: Lab boss request (2026-11-06, "gigantic flying fortress").*

#### FB-STAR-FORT-02 — Body · MUST

The rock is dark, tapering away beneath, boulders on its rim; the moat is a dark channel with a band
of energy in it and lit dashes running round it (its rig). The fort's platform is scarped stone at
the parade ground's height (5 px); its nose and side bastions and its curtains' ramparts rise to
10 px, merlons along their parapets, the nose bastion's lit; the ravelins are scarped earthworks
(9 px). On the parade ground: two barracks behind the forward curtains, wells, paths, the rotor's
pit and the keep's footing.

**Acceptance criteria**
- Manual validation: one stone fortress on its rock; no creature features.

*Sources: BOSS-49, BOSS-52; departure from BOSS-47 above.*

#### FB-STAR-FORT-03 — Its parts and guns · MUST

Its 6 parts, each with its own glowing edge trim (BOSS-48):
- the two **moat pylons** (radius 8, at (±29.4, 40.5) on the rear bastions): energy spires ringed
  by glowing coils; no gun;
- the two **ravelin redoubts** (radius 9, at (±26.5, -36.4)): squat blockhouses, each behind a
  **fixed twin gun** (mounts `ravelin-left`, `ravelin-right`) on the ravelin's top firing along its
  front face's normal (33° off straight down, towards the centre line: their streams cross under
  it);
- the **cavalier** (radius 9, at (0, -40) in the nose bastion): a horseshoe parapet round its
  **three-barrelled turret** (mount `cavalier`), a rangefinder post;
- the **gatehouse** (radius 9, at (0, 36) on the rear curtain): twin towers over a lit gate; no gun.

The core's guns, each under an iron shutter on the rampart until a stage first uses it
(FB-STAR-FORT-09), all fixed but the rotor: the **nose embrasures** (3 barrels on each face of the
nose bastion, ±65.8°), the **side embrasures** (3 barrels on the front face of each side bastion,
±6.2°), the **side mortars** (one fat barrel in each side bastion, 40° out from straight down), the
**salient laser** (at the nose bastion's point, straight down), the **curtain embrasures** (2
barrels on each forward curtain, ±36°) and the parade ground's **rotor** (16 barrels).

**Acceptance criteria**
- Given its design, then it has 6 parts and these 13 mounts, 11 of them fixed; a destroyed part's
  mounts leave stumps on the stone under them.

*Sources: BOSS-12, BOSS-13, BOSS-48, BOSS-58, round 5 brief (non-rotating guns).*

#### FB-STAR-FORT-04 — Lights · MUST

Its neon is rose, `[1, 0.35, 0.6]` (shown yellow, BOSS-50): the moat, the nose bastion's parapet,
the pylons' coils, the shutters' crosses, the keep's band and crown, the gates.

**Acceptance criteria**
- Given the boss look, then its neon is `[1, 0.35, 0.6]`.

*Sources: BOSS-50.*

#### FB-STAR-FORT-05 — Its moving pieces · MUST

Its rear bastions (BOSS-45): each turns about the vertical through its outer flank root, from 0° to
-40° for the right one (its salient swinging out to the side), the left one its mirror image; a
great hinge drum stands at the pivot. Its keep: an octagonal tower (radius 11, roof 20 px high)
that slides 16 px straight up; the rock pinnacle (its rig) rises under it so it stands on rock.

**Acceptance criteria**
- Given the design, then its rear bastions and keep are moving regions; its sweepers ride the
  bastions and its gatling the keep (unit test, BOSS-45).

*Sources: BOSS-45, round 3 to 5 briefs.*

### Behaviour

#### FB-STAR-FORT-06 — Coming in and moving · MUST

It stops at 0.7 of the playfield's height, sways ±18 px over 14 s and bobs ±3 px over 6 s: a
mountain of stone barely drifting. Its fight ground speed is ×0.2.

*Sources: BOSS-03, BOSS-08, BOSS-10.*

#### FB-STAR-FORT-07 — Parts and core · MUST

Every part shields the core (BOSS-14); the core carries the last guns (its embrasures and rotor),
so it dies when they are destroyed. Health: core 5 000; pylons 1 500, ravelins 1 600, cavalier
1 800, gatehouse 1 500; sweepers 1 440 (0.8 of the sturdiest part), batteries and gatling 1 800:
22 780 in all, as the 1-5 final boss (Overlord, 22 760).

*Sources: BOSS-12, BOSS-14, BOSS-38, BOSS-54, BOSS-55, BOSS-56.*

#### FB-STAR-FORT-08 — Stage patterns · MUST

Its parts' volleys, in every stage while they stand: the cavalier sweeps aimed spreads of 3 every
2.6 s; each ravelin's fixed gun fires its 2 parallel shots along its face every 2.8 s. The core's,
stage by stage (each keeps the earlier ones, 0.1 s slower a stage):

| Stage | Core volleys added | Guns in use (design order) |
|-------|--------------------|----------------------------|
| 0 | none | 3 (2 fixed): cavalier turret, ravelin guns |
| 1 | nose embrasures: 3 parallel shots each every 2.7 s, half a beat apart | 5 |
| 2 | side embrasures: 3 parallel shots nearly straight down | 9: + the 2 sweepers of transformation 1 |
| 3 | side mortars: flak along 40° out, bursting into 8 | 10 (a ravelin lost) |
| 4 | the salient laser, 1.6 s every 6.5 s | 13: + 2 batteries and the gatling of transformation 2 |
| 5 | curtain embrasures: 2 parallel shots along ±36° | 14 |
| 6 | the rotor's spiral of 16 every 1.3 s, turning 8° | 15 |

Every lost part brings at least one new gun into use (FB-STAR-FORT-09).

*Sources: BOSS-20, BOSS-21, BOSS-58, round 5 brief.*

#### FB-STAR-FORT-09 — Its embrasures open · MUST

Each core gun lies under an octagonal iron shutter (a hatch, BOSS-58): the shutter bursts as the
gun first comes into use, leaving a lit-rimmed pit, and the gun rises out of it. The fort bristles
more with each part it loses.

*Sources: BOSS-58.*

#### FB-STAR-FORT-10 — First transformation: the bastions swing out · MUST

Once both pylons are destroyed (named parts, BOSS-36) its rear bastions turn out on their hinge
drums like wings, and a **sweeper** (a laser turret following the player) unfolds in each pylon's
socket, ending at (±44.4, 35.7). Angry, their beams sweep after the player. The fight turns from
straight radiating streams into sweeping beams to outrun among them.

*Sources: BOSS-35 to BOSS-41, BOSS-45.*

#### FB-STAR-FORT-11 — Second transformation: the keep rises · MUST

Once both ravelins are destroyed its keep's roof stays on while the keep slides up 16 px on a
pinnacle of rock pushing up out of the parade ground, and a **gatling** unfolds on its roof (centre
line, (0, 6)); the flagstone terraces either side of it burst off and a **battery** (wide fans of 7
straight down) rises from each ((±19, 8)). Angry, they fire all out. The fight turns into fans and
bursts from high above, under the salient laser and, last, the rotor's spiral.

*Sources: BOSS-35 to BOSS-41, BOSS-45.*

#### FB-STAR-FORT-12 — Angry · MUST

After each transformation it is angry for 8 s (BOSS-27): only that transformation's weapons fire,
4.5 times as often.

*Sources: BOSS-27.*

#### FB-STAR-FORT-13 — Death, drops and points · MUST

It scores 17 000 points; its core always drops a weapon bonus, its parts 60 % of the time, its
hidden weapons 30 %.

*Sources: BOSS-19, BOSS-57.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 5.5 L | `stats.size` |
| health | core 5 000; parts 1 500 / 1 500 / 1 600 / 1 600 / 1 800 / 1 500; hidden 1 440 ×2, 1 800 ×3 | 22 780 in all |
| points | 17 000 | |
| ground speed | ×0.2 | |
| stop, sway, bob | 0.7; ±18 px / 14 s; ±3 px / 6 s | |
| bastion swing | 0° → -40° about the outer flank root (mirrored) | `BASTION_SWING` |
| keep rise | 16 px | `KEEP_RISE` |
| fire rate (weighted) | 2.6 coming in, 8.9 after the first transformation, 17.7 after the second | BOSS-39 |
| triangles | about 4 000 drawn (budget 10 000) | BOSS-53 |

## Notes

- Simulated fight check (a part broken every 12 s): 2 110 shots and 36 lasers, every one from a
  barrel, dead at 146 s.
- Config: `src/game/config/bosses/lab/star_fort.py`; model:
  `src/game/view/bosses/lab/star_fort_model.py`, `star_fort_parts.py`, `star_fort_rig.py`.
