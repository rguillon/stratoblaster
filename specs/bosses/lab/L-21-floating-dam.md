# Floating Dam

> **Area:** bosses · **Prefix:** `FB-FLOATING-DAM` · **Related:** [common](../common.md),
> [Anvil Barge](L-21-anvil-barge.md), [Storm Petrel](../final/1-1-storm-petrel.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Floating Dam is the final boss of Lab level L-21: a gigantic curved concrete arch dam flying
sideways across the screen, very wide and shallow. A road runs along its crest, a bascule bridge
carries it over the spillway in its middle, a gatehouse stands at either end of the crest; sluice
gates are set in its sloping face, a turbine hall stands behind it, abutments close its ends with
power pylons on them and the lines strung over the crest, and lift fans spin under its back. It
comes in with only three guns: the fixed guns behind its two outer sluice gates, firing walls of
bullets straight down the screen, and the control tower's turret. Each part the player destroys
brings a new gun up out of a hatch. Once both outer sluices are gone its inner sluice gates lift up
its face into their hoists and a battery rolls out of each; once both gatehouses are gone the
bascule bridge raises its two leaves, the spillway's cover bursts, a cannon stands up on the weir
either side and a lance in the stilling basin below. Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme", then "10 more gigantic flying
fortress, add non rotating guns too, don't add too many start guns, 3 max, then more appear when
they are destroyed"): it is concrete, steel and water-blue light lines, no flesh, eyes or limbs.

## Requirements

### Look

#### FB-FLOATING-DAM-01 — Silhouette and size · MUST

Seen from above it is a curved wall about 230 px across (with its abutments) and only about 30 px
deep (60 with its abutments' bastions and the hall behind it), bowed so that its ends come towards
the player (its crest's line at `8 - 18 (x/100)²`): its face is concave towards the player. Its
section: a vertical back 34 px high, a crest 11 px wide at 24 px, a face sloping down 16 px to its
toe.

**Acceptance criteria**
- Manual validation in the boss viewer: a dam, read at once, unlike any other boss.

*Sources: Lab boss request (2026-11-06).*

#### FB-FLOATING-DAM-02 — Wall, crest, spillway, abutments, pylons · MUST

The wall is weathered concrete swept along its curve, its crest an asphalt road with a lit lane
line, parapets along both edges and lamps; lit contraction joints run down its face, buttresses
stand on its back. In its middle a spillway notch 28 px wide: a weir at 14 px, a chute of four
steps down the face, a walled stilling basin in front of the toe, the bascule bridge's hinges at
its sides. At its ends the abutments: a tower 30 px high and a lower bastion in front of it, lit
bands on their fronts, a lattice pylon on each tower (legs, braces, two cross arms, lit insulators)
with four power lines strung over the crest from pylon to pylon, resting on two masts by the
notch. Four lift fans in ducts under its back, their rotors spinning (faster while it transforms;
`floating_dam_rig`).

**Acceptance criteria**
- Manual validation: one machine; from above, its crest, notch and pylons readable.

*Sources: BOSS-49, user request (2026-11-06).*

#### FB-FLOATING-DAM-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Outer sluices** (`sluice-left`, `sluice-right`): concrete piers standing out of the face either
  side of an outlet sill, a steel hoist bridge across their tops with its winch, the gate hauled up
  under it, lit guides. Behind each gate a **fixed** gun of four barrels side by side on the sill
  (the core's: it stays under the stump), pointing straight down the screen.
- **Gatehouses** (`gatehouse-left`, `gatehouse-right`): concrete blocks on the crest's ends with a
  hipped steel roof, the road running through their lit arch, lit windows, a beacon. **No gun.**
- **Turbine hall** (`hall`): a long powerhouse behind the wall's middle, three generator domes on
  its roof with lit rings, penstocks into the wall's back, transformers at its ends. **No gun.**
- **Core** (the wall): the control tower's twin turret on the crest (from the start); under hatches,
  a **fixed** casemate of three barrels on each bastion raking 22° in towards the middle, a mortar
  and a 16-barrelled rotor on the crest's left, a three-barrelled road turret on its right, and a
  **fixed** three-barrelled outlet on the face either side of the spillway, straight down.

**Acceptance criteria**
- Given its design, then it has 5 parts, all shielding the core, and every volley fires from a
  mount (BOSS-13, BOSS-58).

*Sources: BOSS-12, BOSS-13, BOSS-58, user request (2026-11-06).*

#### FB-FLOATING-DAM-04 — Lights · MUST

Its neon is water blue (0.2, 0.8, 1), shown green (BOSS-50): its lane line, lamps, joints, power
lines and insulators, windows, rings, hatch seams and the spillway's torrent.

*Sources: BOSS-50.*

#### FB-FLOATING-DAM-05 — The inner gates, the bascule bridge, the cover · MUST

- **Inner sluice gates** (moving pieces, BOSS-45): a ribbed steel panel lying on the face's slope
  over a dark bay either side (x 33..49), a lit rim and lifting lugs, an outfall ledge in front of
  each bay and a hoist gantry over it on the crest. As it transforms the first time each panel
  slides 10 px back and 12 px up, up the face into its hoist.
- **Bascule bridge** (moving pieces): the road's deck over the spillway in two leaves, steel
  girders under, asphalt and rails on top, a lit seam where they meet. As it transforms the second
  time each leaf swings 78° up about its hinge on the notch's side (`along`), standing up either
  side of the open spillway.
- **Cover**: overlapping steel shutters down the chute and a lid over the basin, a lit seam down the
  middle; it bursts off at the second transformation (frame `shell`). Once it has burst, a torrent
  of light runs down the chute's steps into the basin (`floating_dam_rig`, looks only).

*Sources: BOSS-42, BOSS-45.*

### Behaviour

#### FB-FLOATING-DAM-06 — Coming in and moving · MUST

It stops at 0.74 of the playfield's height and drifts slowly: sways 30 px over 12 s, bobs 3 px over
5.2 s. Ground speed ×0.6.

*Sources: BOSS-03, BOSS-08, BOSS-10.*

#### FB-FLOATING-DAM-07 — Guns out, stage by stage · MUST

At most 3 guns at the start, and every lost part brings at least one new gun out of its hatch
(round 5's rule, user request 2026-11-06). Breaking the parts in their order (sluices, gatehouses,
hall):

| Stage | New guns | Guns out (fixed) |
|---|---|---|
| 0 | sluice guns ×2, tower turret | 3 (2) |
| 1 | bastion casemates ×2 | 4 (3), one sluice gone |
| 2 (1st transformation) | mortar, batteries ×2 | 6 (2) |
| 3 | weir outlets ×2 | 8 (4) |
| 4 (2nd transformation) | road turret, cannons ×2, lance | 12 (5, the lance counted) |
| 5 | rotor | 13 (5) |

Whatever the order, stage *k* brings out the same core gun(s).

**Acceptance criteria**
- Scratch check over its stages (2026-11-06): the counts above.

*Sources: BOSS-58, user request (2026-11-06).*

#### FB-FLOATING-DAM-08 — Stage patterns: walls of water · MUST

The outer sluices fire walls of four bullets side by side straight down (staggered); the control
tower's turret fires a new aimed pattern at every stage (pairs, bursts, spreads). The core adds: the
bastions' crossfire (three bullets along their barrels, raking inwards), then the mortar's flak
shells bursting into rings of 8, then the weir outlets' walls of three straight down, then the road
turret's bursts of 4 (outlets and casemates with it), then the rotor's spiral of 16. No fixed gun
aims.

**Acceptance criteria**
- Given each stage, then its pattern differs from the one before; the last is a spiral used by no
  earlier stage (BOSS-21).

*Sources: BOSS-20, BOSS-21, BOSS-23.*

#### FB-FLOATING-DAM-09 — Angry · MUST

After each transformation it is angry (BOSS-27): only that transformation's weapons fire, 4.5 times
as often, for 8 s (the batteries; then the cannons and the lance).

*Sources: BOSS-27.*

#### FB-FLOATING-DAM-10 — First transformation: the gates lift · MUST

Once both outer sluices are destroyed (`transformParts`), its inner gates strain, then slide up its
face into their hoists, opening dark bays; a battery rolls straight out of each bay onto its ledge
(`out_of`) and unfolds. The straight walls of the sluices give way to the batteries' wide fans
straight down, swept from the ledges, with the bastions' crossfire and the mortar's flak.

*Sources: BOSS-35, BOSS-37, BOSS-43, BOSS-45.*

#### FB-FLOATING-DAM-11 — Second transformation: the bridge opens · MUST

Once both gatehouses are destroyed, its bascule bridge strains, then raises its two leaves; at the
same time the spillway's cover bursts off. A cannon stands up on the weir either side of the centre
line and a lance in the stilling basin on it, and the torrent pours down the chute. The fight turns
to heavy aimed shells from the middle, the lance's beam straight down the centre and the outlets'
walls either side of it: the player is pushed out of the middle.

*Sources: BOSS-35, BOSS-37, BOSS-41, BOSS-45.*

#### FB-FLOATING-DAM-12 — Its spillway · MUST

The weapons of its second transformation lie in the spillway: the cannons inside the leaves'
outlines as drawn (on the weir under them, not riding them), the lance inside the cover's.

*Sources: BOSS-42.*

#### FB-FLOATING-DAM-13 — Never easier, death, drops and points · MUST

Its weighted fire rate goes 8.1 as it comes in, 10.5 after its first transformation, 19.9 after its
second (BOSS-39). It dies when its last core gun has been destroyed through its core. Its parts
drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57). 10 000
points.

*Sources: BOSS-19, BOSS-39, BOSS-57.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 6 L, core radius 18 | `stats` |
| wall | half length 100, crest line `8 - 18 (x/100)²`, section from back foot (-6, -10) round to toe (21, -6), crest 24 | `SPAN`, `CREST_Y`, `BOW`, `SECTION` |
| notch | ±14, weir 14 high; basin ±14, y -27..-13, 2 high | `NOTCH`, `WEIR_TOP`, `BASIN` |
| abutments | x 98..114, y -34..-1, 30 high; bastion top 16 | `ABUTMENT`, `BASTION_TOP` |
| outer sluices | (±66, -17), radius 11, health 900; gun at (±66, -21) on a sill 9.8 high, fixed, 4 barrels 3.2 apart | parts |
| gatehouses | (±86, -3), radius 10, health 760, no gun | parts |
| hall | (0, 24), radius 13, health 980, no gun | part |
| tower turret | (26, 10.5), 32 high, 2 barrels | `TOWER_GUN` |
| casemates | (±107, -29), 16 high, fixed, 3 barrels, ∓22°; hatches 11 × 9 | `CASEMATE` |
| mortar / road turret / rotor | (-26, 10) / (48, 7) / (-48, 7), on the crest; hatches 11 × 11 | |
| weir outlets | (±24, -6), 12.5 high, fixed, 3 barrels; hatches 9.6 × 8 | `OUTLET` |
| inner gates | x 33..49, y -32..2 (with the ledge); slide (0, 0, 0) → (0, 10, 12); no frame | `moving_region` `gate` |
| leaves | x 0..13.5, y 3..14, 21..24 high; swing `along` about (13.5, ·, 24), 0 → 78°; no frame | `moving_region` `leaf` |
| batteries | (±41, -24) on the ledges from (±41, -6), radius 8, health 780 (0.8 of the hall's); first 1.2 / 2.0 s | `out_of` |
| cannons | (±7, 8) on the weir, radius 6.5, health 980; first 1.2 / 2.0 s | |
| lance | (0, -19) in the basin, radius 7, health 980; first 1.6 s | |
| sluice walls | fan of 4 along the barrels, orange 150 px/s radius 5, every 1.1 s (first 0.5 / 1.05 s) | |
| tower turret | aimed 2 (7°) / burst 3 / aimed 2 / aimed 3 (8°) / aimed 2 / aimed 3, magenta 175 px/s | stages 0..5 |
| casemates | 3 along the barrels, red 180 px/s, every 2.6 s | stages 1, 2, 4 |
| mortar | flak 110 px/s radius 8, bursting into 8 red at 1.1 s, every 3.4 s | stages 2, 3 |
| weir outlets | 3 along the barrels, orange 150 px/s, every 1.3 s | stages 3..5 |
| road turret | burst of 4, 0.12 s apart, red, every 2.4 s | stages 4, 5 |
| rotor | ring of 16 turning 11.25°, orange 160 px/s, every 1.5 s | stage 5 |
| full health | 10 500 (core 1 700, parts 4 300, hidden 4 500) | BOSS-54; the Storm Petrel's 10 420 |
| points | 10 000 | |
| weighted fire rate | 8.1 / 10.5 / 19.9 | BOSS-39 |
| neon | water blue (0.2, 0.8, 1), shown green | `BOSS_LOOK.neon` |
| triangles | about 4 670 drawn (core, parts, armour; mounts apart), rig about 450 | BOSS-53 (scratch count) |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time is not set (its full
  health is the Storm Petrel's, as asked).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Gunless parts.** Its gatehouses and hall carry no gun (round 5: at most three guns at the
  start); their loss brings new guns and the second transformation.
- **Late guns under hatches.** Its eight late core guns are core mounts first used by stages 1 to 5,
  each under its own hatch (`armour_region(..., mount=...)`). Hatch regions have no `form`: the
  known test-helper crash on them applies.
- **Gate outlines.** Each inner gate's region outline covers its panel and the ledge in front, so
  the battery rolling out onto the ledge lies within a region its transformation moves (BOSS-42);
  only the panel is drawn and moves.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 2 039 shots and 14
  lasers, every shot from a barrel, along it (0 off); it dies at about 134 s.
