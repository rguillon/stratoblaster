# Zeppelin Citadel

> **Area:** bosses · **Prefix:** `FB-ZEPPELIN-CITADEL` · **Related:** [common](../common.md),
> [Rotor Bastion](L-13-rotor-bastion.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Zeppelin Citadel is the final boss of Lab level L-13: three long gas envelopes side by side
carrying a fortified town slung under them, 5 L long. It first fires orderly volleys from its bow
towers, its stern silos and the turrets on its outer envelopes. At its first transformation the two
outer envelopes cast off and drift out wide on telescoping booms, their mooring cables stretching,
baring the town's flanks and a sweeper on each: wide lasers sweeping from its flanks. At its second
the middle envelope deflates and bursts, dropping the citadel's cover off a pair of gatlings and a
mortar on its central plaza: close, desperate flak. Shared rules are in [common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "flying fortress theme") this Lab boss is a built thing that flies,
not a creature: stretched envelope skin, dark metal, plating, rooftops, cables, propellers and neon
light lines; no flesh, eyes or veins.

## Requirements

### Look

#### FB-ZEPPELIN-CITADEL-01 — Silhouette and size · MUST

Seen from above, the Zeppelin Citadel is three long, round envelopes side by side, noses down the
screen, over a walled town deck that juts out ahead of them in a pointed, fortified bow and behind
them in a stern: about 92 px across and 128 px long (5 L). Once its outer envelopes have drifted
off it is about 150 px across, the two outer envelopes standing apart from the town on their booms;
once the middle one has burst, the town's whole top shows between them.

**Acceptance criteria**
- Manual validation in the boss viewer: three envelopes over a town at rest; the outer ones apart
  after the first transformation; the middle one gone, the plaza bared, after the second.

*Sources: Lab boss request (2026-11-06, "flying fortress theme").*

#### FB-ZEPPELIN-CITADEL-02 — Town · MUST

Its gondola is a walled deck on a tapering keel, a lit line round its edge. Its bow is ringed with
battlements; two round bow towers stand on it, a lit band and a pennant mast each, and a hexagonal
keep on its tip. Hipped-roof houses, each with a lit window, stand in rows on its flanks, its bow
and its stern, kept under the envelopes' keels. Two dark lanes run between the envelopes, lanterns
along them. Two square silo blocks stand on its stern either side of a plated pad round the stern
rotor's collar. Slots on its flanks, lit inside, with a rail out of each, show where the outer
envelopes' booms slide out; mooring bollards stand on its edges. Cradle struts on the plaza hold
the middle envelope off the deck (they stay standing once it is gone).

**Acceptance criteria**
- Manual validation: one built thing of skin, dark metal and neon lines; no creature features.

*Sources: BOSS-49, BOSS-52; departure from BOSS-47 above.*

#### FB-ZEPPELIN-CITADEL-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Dorsal turrets** (left and right, on the outer envelopes' backs): an armoured collar on a gun
  saddle hugging the skin, a lit band round it, a turret of two barrels side by side on it (its
  aimed pairs). The saddle stays on the envelope under its stump.
- **Bow towers** (left and right): a battlemented cupola on each drum, a lit band and four merlons,
  a turret of three barrels side by side (its fans).
- **Stern silos** (left and right): an armoured launcher housing on each silo block, lit along its
  sides, a block of four missile ports on top (its homing pairs).
- **Keep turret** (the core's, on the bow keep): five barrels side by side.
- **Stern rotor** (the core's): sixteen barrels round a hub on the stern deck (its last rings).
  Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes into
  use the hatch bursts off (BOSS-58), leaving a lit collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws each of its six parts and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### FB-ZEPPELIN-CITADEL-04 — Lights · MUST

Its deck edge, lanterns, windows, envelope hoops and ridge lines, fin edges, boom lines, mooring
cables, propeller tips, tower bands and the seams round its hatches glow. Its neon colour is set
violet (0.6, 0.4, 1); the viewer folds it into the enemy palette (BOSS-50), where it shows green.

**Acceptance criteria**
- Given its model, then its lights are in its neon colour.

*Sources: BOSS-50.*

#### FB-ZEPPELIN-CITADEL-05 — Envelopes · MUST

Each envelope is a long round hull of pale skin (ten facets round), a blunt nose and a tapering
tail, four dark girder hoops round it (the middle two lit), a lit line along its ridge, and cross
fins at its tail (two flat ones, one standing on its back, lit edges). The outer envelopes are
moving pieces (BOSS-45): each, with its gun saddle, its two telescoping booms (lying inside the
gondola's hull at rest, a lit line along their tops) and the pylons from them up into its keel,
slides out (28, 2, 3) px as the first transformation goes (the left one mirrored) and stays there;
they leave no frame. The middle envelope is a shed region: it bursts off at the second
transformation, leaving its own frame, the town's central plaza (dark paving, a lit border, torn
stubs of its keel girder along the centre line, the cradle struts standing empty).

A rig of the model's own (BOSS-46, `drawing.rig`, view only) adds: a propeller at each outer
envelope's tail, spinning, drifting out with it; two lit mooring cables a side, from bollards on the
town's edge to the envelope's flank, stretching as it drifts off; and the middle envelope's gas
cell, which, once its skin has burst, sags onto the plaza and deflates (it keeps 45 % of its width,
12 % of its height, 80 % of its length) by 0.8 of the transformation, and is gone. None of it fires
or is hit.

**Acceptance criteria**
- Given its design, then its first transformation slides both outer envelopes, mirrored, and no
  part the player can hit stands on them as they move (unit tests on the moving regions).
- Given its model, then it holds together at rest and after each transformation (its booms still
  in the hull once slid out).
- Manual validation: the cables stretch, the propellers spin, the gas cell deflates as the middle
  envelope bursts.

*Sources: BOSS-42, BOSS-44, BOSS-45, BOSS-46, BOSS-52.*

### Behaviour

#### FB-ZEPPELIN-CITADEL-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways and bobs
slowly: a stately drift. While it is fought the ground scrolls at ×0.4.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.4 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-ZEPPELIN-CITADEL-07 — Parts and core · MUST

It has six parts as it comes in, all shielding its core: `dorsal-left`, `dorsal-right`, `bow-left`,
`bow-right`, `stern-left` and `stern-right`. The core's guns (the keep turret and the stern rotor)
fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its six parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### FB-ZEPPELIN-CITADEL-08 — Stage patterns: orderly, then sweeping, then flak · MUST

In every stage while they stand: each dorsal turret fires an aimed pair of red bullets 6° apart,
the two in turn; each bow tower sweeps a fan of 5 orange bullets 10° apart straight down; each stern
silo launches a pair of homing missiles 30° apart. The core fires:
- stage 0: an aimed red bullet;
- stage 1: a fan of 5 straight down, 12° apart;
- stage 2: an aimed spread of 3, 8° apart;
- stage 3: a burst of 4 magenta at the player;
- stage 4: a fan of 7 straight down, 10° apart;
- stage 5: an aimed spread of 5, 9° apart, and a burst of 3;
- stage 6 and after: a ring of 16 from the stern rotor, turning 11.25° at each volley, and a fan of
  5 red, 12° apart.

Its hidden weapons change the fight's character: after the first transformation, two sweeping
lasers from its far-out flanks (the player keeps moving across); after the second, gatling bursts
and flak shells bursting into rings from the middle of its body (close and dense).

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-ZEPPELIN-CITADEL-09 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons that transformation revealed fire all
out (its sweepers, then its gatlings and mortar), `boss_rage_rate` times as often (a laser no faster
than its warning, beam and gap allow), for `boss_rage_seconds`.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-ZEPPELIN-CITADEL-10 — First transformation: the outer envelopes cast off · MUST

Once both dorsal turrets are destroyed (named: no part the player can hit stands on an outer
envelope as it moves), the outer envelopes strain, then slide out wide and a little up and back on
their telescoping booms (FB-ZEPPELIN-CITADEL-05), their cables stretching, and a **sweeper**
unfolds on each of the town's bared flanks. They shield the core and fire beams that sweep after
the player.

**Acceptance criteria**
- Given both dorsal turrets destroyed, then it transforms: its outer envelopes slide out and its two
  sweepers are revealed where they lay.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### FB-ZEPPELIN-CITADEL-11 — Second transformation: the middle envelope bursts · MUST

Once both bow towers are destroyed, the middle envelope strains and bursts (BOSS-43: its skin
thrown off in pieces), its gas cell sagging and deflating onto the plaza (FB-ZEPPELIN-CITADEL-05),
and on the bared plaza a pair of **gatlings** and a **mortar** on the centre line unfold. They
shield the core; the gatlings fire bursts at the player, the mortar flak shells that burst into
rings.

**Acceptance criteria**
- Given both bow towers destroyed, then it transforms: the middle envelope is shed and the gatlings
  and the mortar are revealed in its region.

*Sources: BOSS-35, BOSS-36, BOSS-42, BOSS-43.*

#### FB-ZEPPELIN-CITADEL-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at each transformation: 6.9 as it comes in, 8.0 after the
first, 9.8 after the second.

**Acceptance criteria**
- Given its design, then its weighted fire rate never goes down from one transformation to the
  next (unit test, every boss).

*Sources: BOSS-39.*

#### FB-ZEPPELIN-CITADEL-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/zeppelin_citadel.py` (`_ZEPPELIN_CITADEL`, `ZEPPELIN_CITADEL`)
unless named; its model in `src/game/view/bosses/lab/zeppelin_citadel_model.py`,
`zeppelin_citadel_envelopes.py` and `zeppelin_citadel_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (radius 85 px) | `stats.size` |
| town | deck outline from the bow tip (0, -68) to the stern (±24, 60), 92 px across; keel -4 px, deck 8 px | `TOWN`, `DECK` |
| outer envelopes | x ±33, radius 12.5, nose y -38, tail y 42, centre 26 px high | `OUTER` |
| middle envelope | x 0, radius 16, nose y -48, tail y 46, centre 30 px high | `MIDDLE` |
| booms | y -22 and 26, x 12..40 at rest, 3.5–6.5 px high | `BOOM_YS`, `BOOM_X`, `BOOM_H` |
| outer envelopes (moving regions) | outline round the envelope and fins, x 19.5..46.5, y -40..47; slide from (0, 0, 0) to (±28, 2, 3); no frame | `moving_region` `outer-envelope`, `DRIFT` |
| middle envelope (armour) | x -17..17, y -50..50, from 14 px up; its own frame (the plaza) | `armour_region` `middle-envelope`, form 2 |
| rig | propellers 6.5 px, 11 rad/s; cables radius 0.4 from (±45, -30 / 34, 9.6) to (±43, -30 / 34, 25) + the drift; gas cell deflating over 0.15–0.8 of the second transformation | `zeppelin_citadel_rig` |
| core | health 2 800, radius 20 | |
| `dorsal-left`, `dorsal-right` | (∓33, -8), radius 10, health 950, shield, drop 0.6 | on the outer envelopes |
| dorsal turrets | 40.5 px high; 2 barrels 3.1 px apart, bore 1.2, 8 px long; dome radius 4.8 | `DORSAL_GUN` |
| `bow-left`, `bow-right` | (∓24, -48), radius 10, health 1 150, shield, drop 0.6 | drums radius 7 to 16 px |
| bow turrets | 19 px high; 3 barrels 2.9 px apart, bore 1.1, 7.5 px long; dome radius 5 | `BOW_GUN` |
| `stern-left`, `stern-right` | (∓24, 52), radius 10, health 1 250, shield, drop 0.6 | silo blocks 12 px square to 13 px |
| stern silos | 4 missile ports each, block top 15.5 px | `missile_mount` |
| keep turret (core) | (0, -57), 14 px high; 5 barrels 2.6 px apart, bore 1, 8 px long | `KEEP_GUN` |
| stern rotor (core) | (0, 54), 11 px high; 16 barrels, bore 0.7, 3.4 px long; hub radius 5.5 | `KEEP_ROTOR` |
| rotor hatch | octagon of radius 6 round (0, 54) | `armour_region` `rotor-hatch` (`mount`) |
| sweepers | (∓33, 8) on the flanks, radius 8, health 1 000, pod 8–11.5 px, red; first 1.2 s / 2.6 s | form 1 |
| gatlings | (∓8, -24) on the plaza, radius 8, health 1 250, pod 8–11.5 px, magenta; first 1.2 s / 2.0 s | form 2 |
| mortar | (0, 10) on the plaza, radius 10, health 1 250, pod 8–12 px, orange; first 1.6 s | form 2, centre line |
| full health | 15 250 (core 2 800, parts 6 700, sweepers 2 000, gatlings and mortar 3 750) | BOSS-54; the Mesa Fortress (1-3) has 15 000 |
| points | 10 500 | |
| ground speed | ×0.4 | |
| stop height | 0.74 | `stopFraction` |
| sway / bob | 30 px over 12 s / 6 px over 6 s | |
| dorsal pairs | aimed 2, 6° apart, red 190 px/s, every 2.2 s (first 0.9 s / 2.0 s) | sweeps |
| bow fans | 5, 10° apart, straight down, orange 180 px/s, every 2.8 s (first 1.4 s / 2.8 s) | sweeps |
| stern missiles | 2 homing, 30° apart, every 7 s (first 3 s / 6.5 s) | |
| core stage 0 | aimed 1, red, every 2.6 s | keep turret |
| core stage 1 | fan of 5, 12° apart, orange, every 2.6 s | keep turret |
| core stage 2 | aimed 3, 8° apart, every 2.4 s | keep turret |
| core stage 3 | burst of 4, 0.12 s apart, magenta 175 px/s, every 2.4 s | keep turret |
| core stage 4 | fan of 7, 10° apart, every 2.6 s | keep turret |
| core stage 5 | aimed 5, 9° apart, every 2.6 s; burst of 3, 0.14 s apart, every 3.2 s | keep turret |
| core stage 6 | ring of 16 turning 11.25°, orange, every 1.4 s; fan of 5, 12° apart, red, every 2.6 s | rotor; keep turret |
| weighted fire rate | 6.9 as it comes in, 8.0 after its first transformation, 9.8 after its second | BOSS-39 |
| transformations | `dorsal-left` and `dorsal-right`; then `bow-left` and `bow-right` | `transformParts` |
| neon | violet (0.6, 0.4, 1), shown green | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about that of the 1-3
  final boss (Mesa Fortress, 15 000).
- **Not a creature** (see the departure from BOSS-47 above).
- **Transformations.** The first is a slide of moving pieces with a rig of cables and propellers
  following them; the second a shed region with a custom frame, a rig deflating a gas cell under it.
  The mini boss of its level (Rotor Bastion) swings its pieces instead.
- **The cables and booms.** Each outer envelope stays one object with the town through its booms
  (BOSS-52: they still reach into the hull once slid out); the cables are a rig of the view only. An
  engine feature to stretch a piece between two moving ends would let the cables be checked too.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 432 shots and 22
  lasers, every one from a barrel, along it; it dies at about 146 s (the Mesa Fortress, same tool:
  122 s, with three parts fewer).
