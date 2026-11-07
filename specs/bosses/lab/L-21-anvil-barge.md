# Anvil Barge

> **Area:** bosses · **Prefix:** `MB-ANVIL-BARGE` · **Related:** [common](../common.md),
> [Floating Dam](L-21-floating-dam.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Anvil Barge is the mini boss of Lab level L-21: a gigantic flying iron bunker shaped like an
anvil. Seen from above: a horn at its front, a lower step, a flat working face of hardened steel
plates with glowing seams, a heel overhanging its back, all on a heavy waisted base whose feet
flare out under it, held up by a bank of downward lift jets along each foot. It comes in with only
three guns, two of them fixed cannons in the face's front; each part the player destroys brings a
new gun up out of a hatch in its face. Once both jet banks are gone its horn splits lengthwise and
its halves swing apart like jaws, a gatling riding each. Shared rules are in
[common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme", then "10 more gigantic flying
fortress, add non rotating guns too, don't add too many start guns, 3 max, then more appear when
they are destroyed"): it is riveted iron and steel with ember light lines, no flesh, eyes or limbs.

## Requirements

### Look

#### MB-ANVIL-BARGE-01 — Silhouette and size · MUST

Seen from above it is an anvil about 60 px across its feet and 104 px long from its horn's tip to
its heel: the horn (26 px wide at its root, 32 px long, tapering to a point) at its front, the step
(28 px wide), the face (40 by 50 px, 22 px high), the heel (28 px wide, 14 px deep) behind; under
them the base, waisted (24 px across) and then flaring into feet 60 by 66 px, their corners cut,
showing all round the face. A lift jet bank runs along each foot's flank.

**Acceptance criteria**
- Manual validation in the boss viewer: an anvil, read at once from above, unlike any other boss.

*Sources: Lab boss request (2026-11-06).*

#### MB-ANVIL-BARGE-02 — Plate, seams and base · MUST

Its hull is blackened iron, chamfered; its working face three plates of paler hardened steel, a
glowing seam between each two and rivets along their front rims; glowing seams along the face's
and heel's flanks, on the feet's slopes and front, a lit vent band across the heel's back. The
fixed cannons sit on iron cradles in the face's front; casemate lips stand on the face's flanks;
mooring bollards with lit tips on the feet's back corners. Under the horn lies the forge throat: a
dark channel with a molten groove glowing along its middle and iron ribs across it, shown once the
horn splits.

**Acceptance criteria**
- Manual validation: one machine, armour over a darker mechanism (BOSS-49).

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-ANVIL-BARGE-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Lift jet banks** (`jets-left`, `jets-right`): long armoured nacelles on pylons along the feet's
  flanks, three intake fans in each top with lit rings, glowing nozzles under them, a lit stripe
  along the outer flank and warning lights at the ends. They carry **no gun**: they hold the barge
  up, and their loss brings new guns out and, both gone, the transformation.
- **Forge** (`forge`): a riveted furnace on the heel, a glowing grate in its back, two stacks with
  hot mouths; a twin-barrelled turret on top (aimed pairs). Its pedestal is the core's, so its
  stump stands on it once it is gone.
- **Core** (the face): two **fixed** cannons in the face's front, two barrels each, pointing
  straight down the screen (from the start); under hatches, a three-barrelled turret in the face's
  front plate (round plate), two **fixed** casemates on the face's flanks pointing 40° out and down
  (square plates), and a 12-barrelled rotor in its hardy hole (square plate with a lit cross).

**Acceptance criteria**
- Given its design, then it has 3 parts, all shielding the core, and every volley fires from a
  mount (unit test, BOSS-58).

*Sources: BOSS-12, BOSS-13, BOSS-58, user request (2026-11-06).*

#### MB-ANVIL-BARGE-04 — Lights · MUST

Its neon is ember orange (1, 0.5, 0.25), shown yellow (BOSS-50): its seams, its jets' rings and
nozzles, its forge's grate and stacks, its hatches' lit seams.

**Acceptance criteria**
- Given its look, then its lights are the enemy yellow (unit test, BOSS-50).

*Sources: BOSS-50.*

#### MB-ANVIL-BARGE-05 — The horn and its rams · MUST

The horn is drawn as two halves split along the centre line, hardened steel with a flat top, iron
bands across and a glowing seam along the outer edge, a lit cut face along the centre line. Each
half rests closed and swings 40° outwards about the vertical through its root's outer corner as it
transforms (a moving piece, BOSS-45). Two hydraulic rams in the throat push them apart: each a
cylinder on its seat by the step and a lit rod telescoping out to its half's inner side, following
it (`anvil_barge_rig`, looks only).

**Acceptance criteria**
- Manual validation: the horn splits open like jaws, the throat glowing between the halves.

*Sources: BOSS-45, user request (2026-11-06).*

### Behaviour

#### MB-ANVIL-BARGE-06 — Coming in and moving · MUST

It stops at 0.72 of the playfield's height and drifts slowly: sways 45 px over 9.5 s, bobs 3 px
over 3.6 s. Ground speed ×0.5.

*Sources: BOSS-03, BOSS-08, BOSS-10.*

#### MB-ANVIL-BARGE-07 — Guns out, stage by stage · MUST

At most 3 guns at the start, and every lost part brings a new one out of its hatch (round 5's rule,
user request 2026-11-06). Breaking the parts in their order (jets left, jets right, forge):

| Stage | New guns | Guns out (fixed) |
|---|---|---|
| 0 | face cannons ×2, forge turret | 3 (2) |
| 1 | face turret (its hatch bursts) | 4 (2) |
| 2 (transformation) | casemates ×2 (hatches), gatlings ×2 | 8 (4) |
| 3 | rotor (hardy plate bursts) | 8 (4), the forge's turret gone |

Whatever the order, stage *k* brings out the same core gun(s).

**Acceptance criteria**
- Scratch check over its stages (2026-11-06): the counts above.

*Sources: BOSS-58, user request (2026-11-06).*

#### MB-ANVIL-BARGE-08 — Stage patterns: it hammers · MUST

The fixed face cannons fire two heavy slugs side by side straight down at every stage, one after
the other; the forge's turret sweeps aimed pairs. The core adds at each stage: an aimed spread of 3
from the face turret, then bursts of 3 from it with the casemates' pairs along their barrels (out
and down), then the rotor's spiral of 12 with the casemates. No fixed gun aims.

**Acceptance criteria**
- Given each stage, then its pattern differs from the one before; the last is a spiral used by no
  earlier stage (unit test, BOSS-21).

*Sources: BOSS-20, BOSS-21, BOSS-23.*

#### MB-ANVIL-BARGE-09 — Angry · MUST

After its transformation it is angry (BOSS-27): only its gatlings fire, 4.5 times as often, for 8 s.

*Sources: BOSS-27.*

#### MB-ANVIL-BARGE-10 — Its transformation: the horn splits · MUST

Once both lift jet banks are destroyed (`transformParts`), its horn strains, then its two halves
swing apart like jaws, the rams pushing them, the forge throat glowing between them; a gatling
rides each half, standing on its flat top, and unfolds. The fight changes from heavy straight-down
slugs to the gatlings' bursts chasing the player from the front corners, with the flank casemates
raking out and down.

**Acceptance criteria**
- Given its design, then it transforms once and each gatling ends up on its half (unit tests,
  BOSS-35, BOSS-45).
- Manual validation: the horn visibly splits and swings open.

*Sources: BOSS-35, BOSS-37, BOSS-45.*

#### MB-ANVIL-BARGE-11 — Never easier · MUST

Its weighted fire rate goes from 3.3 as it comes in to 9.9 after its transformation (BOSS-39).

*Sources: BOSS-39.*

#### MB-ANVIL-BARGE-12 — Death, drops and points · MUST

It dies when its rotor, the last core gun, has been destroyed through its core (BOSS-12, BOSS-19).
Its parts drop a weapon bonus half the time, its gatlings 30 % (BOSS-57). 3 600 points.

*Sources: BOSS-19, BOSS-57.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 3.6 L, core radius 16 | `stats` |
| face | x ±20, y -24..26, top 22, underside 13 | `FACE_*` |
| step / heel | x ±14 y -32..-24 top 18 / x ±14 y 26..40 | `STEP_*`, `HEEL_*` |
| base | waist ±12 (y -18..22, 1..13 high); feet ±30, y -30..36, -9..1 high | `WAIST`, `FEET` |
| horn | root ±13 at y -32, tip y -64, 6..17 high | `HORN*` |
| horn halves | swing `up` about (±13, -32), 0 → ±40°; no frame | `moving_region` `horn` |
| jet banks | (±34, 3), radius 11, health 560, no gun | parts |
| forge | (0, 33), radius 10, health 720; turret 2 barrels, 27 high | part |
| face cannons | (±14, -20), fixed, 2 barrels 3.4 apart, bore 1.3, 10 long | `FACE_CANNON` |
| face turret | (0, -8), 3 barrels; round hatch radius 6.5 | `FACE_TURRET` |
| casemates | (±17, 6), fixed, 2 barrels, ±40° out; hatches 9 × 10 | `CASEMATE` |
| rotor | (0, 15), 12 barrels; hatch 12 × 12 | `ROTOR` |
| gatlings | (±14.7, -46.2) on the halves, radius 5.5, health 580 (0.8 of the forge's), pod 17–20 px, red; first 1.2 s / 2.0 s | BOSS-38 |
| face cannons' slugs | 2 parallel, orange 165 px/s radius 6, every 1.6 s (first 0.6 s / 1.4 s) | every stage |
| forge's pairs | aimed 2, 7° apart, red 185 px/s, every 2.4 s | sweeps |
| core stage 1 | aimed 3, 10° apart, magenta 175 px/s, every 2.4 s | face turret |
| core stage 2 | burst of 3, 0.14 s apart, every 2.6 s; casemates 2 red 175 px/s every 2.2 s | |
| core stage 3 | ring of 12 turning 15°, orange 160 px/s, every 1.5 s; casemates | rotor |
| full health | 4 000 (core 1 000, parts 1 840, gatlings 1 160) | BOSS-54 |
| points | 3 600 | |
| weighted fire rate | 3.3 as it comes in, 9.9 after its transformation | BOSS-39 |
| neon | ember (1, 0.5, 0.25), shown yellow | `BOSS_LOOK.neon` |
| triangles | about 1 540 drawn (core, parts, armour; mounts apart), rig a few hundred | BOSS-53 (scratch count) |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set.
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Gunless parts.** Its jet banks carry no gun (round 5: at most three guns at the start); they
  read as targets by their lit rings, nozzles and stripes.
- **Late guns under hatches.** The face turret, casemates and rotor are core mounts first used by
  stages 1 to 3; each lies under its own hatch (`armour_region(..., mount=...)`), which bursts as
  it comes out (BOSS-58). Hatch regions have no `form`: the known test-helper crash on them applies.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 716 shots, every one
  from a barrel, along it (0 off); it dies at about 74 s.
