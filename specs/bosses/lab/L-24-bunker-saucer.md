# Bunker Saucer

> **Area:** bosses · **Prefix:** `MB-BUNKER-SAUCER` · **Related:** [common](../common.md),
> [Clockwork Citadel](L-24-clockwork-citadel.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Bunker Saucer is the mini boss of Lab level L-24: a gigantic flying concrete pillbox shaped
like a thick saucer. Its belly is a shallow concrete lens, a lit steel belt runs round its rim, a
parapet notched with slit embrasures rings its rim deck, two stepped concrete rings rise to a
crown with an observation cupola on it, an armoured pillbox turret stands on its front step and two
lift-jet nacelles sit on its rim's back quarters. It comes in with only three guns: the pillbox's
turret and the two front slits. Each lost part opens two more slits (their shutters slide back and
a fixed gun rises in each, firing straight out along the rim's normal), so its fire spreads round
its rim as it is taken apart. Once two parts are gone its cupola splits, its halves slide apart on
the crown and a cannon unfolds on each. Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06: "drop the animal looking theme", "flying fortress theme", then "10
more gigantic flying fortress, add non rotating guns too, don't add too many start guns, 3 max,
then more appear when they are destroyed"): it is cast concrete and steel with red light lines, no
flesh, eyes or limbs.

## Requirements

### Look

#### MB-BUNKER-SAUCER-01 — Silhouette and size · MUST

Seen from above it is a round saucer 114 px across (3.6 L), its parapet's ring of notched concrete
blocks round its edge, two concentric steps (88 and 60 px across) and the cupola (24 px across) in
the middle; two lift-jet nacelles bulge over its rim's back quarters. Seen from the side it is a
thick lens: its belly 15 px under its rim deck, its crown 19 px over it. A lit steel belt runs round
its rim's face, with lamps.

**Acceptance criteria**
- Manual validation in the boss viewer: a round concrete bunker, unlike any other boss.

*Sources: Lab boss request (2026-11-06).*

#### MB-BUNKER-SAUCER-02 — Steps, crown and cupola · MUST

Its two steps are cast concrete with a darker course at their foot, a lit band round each face and
buttresses round the lower step. The crown carries the two steel rails the cupola's halves slide
on, lamps round its edge (its charge lights), a radio mast with a lit tip and the collar of the
rotor's hatch at its back. The cupola is a low concrete drum with a flat steel top, lit vision slits
round its curve and a lit seam down its middle; a periscope stands on the seam. Under the cupola
is a dark well with a ring of light and the periscope's housing (seen once it splits).

**Acceptance criteria**
- Manual validation: one bunker, its steps, crown and cupola readable from above.

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-BUNKER-SAUCER-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Slits** (the core's, eight): a fixed gun of two barrels side by side in each notch of the
  parapet, 51.5 px out, at 15°, 42°, 70° and 100° either side of the nose, pointing straight out
  along the rim's normal. They never turn (non-rotating guns). Each notch has steel cheeks, a dark
  sill and a lit lintel; until its gun first comes into use a steel shutter closes it, which slides
  sideways into the parapet as the gun rises (the model's rig).
- **Pillbox** (`pillbox`): an armoured steel collar with lit vision slits, a hooded periscope and a
  whip aerial, round a twin-barrelled turret on the concrete drum of the front step (its aimed
  pairs). Destroyed, it leaves its stump on the drum.
- **Lift jets** (`jet-left`, `jet-right`): steel nacelles over sockets in the rim deck, their
  intakes facing up (fan blades under a lit lip), armoured fairings either side, their exhausts
  glowing under the rim. No gun: they hold it up. Destroyed, they leave their sockets (a steel ring,
  a dark throat, a grille).
- **Rotor** (the core's, on the crown's back): fourteen barrels round a hub (its last spiral). Until
  its last stage it lies under a riveted steel hatch (BOSS-58), which bursts as the rotor comes out,
  leaving a steel collar.

**Acceptance criteria**
- Given its model, then it draws its three parts and every gun mount.

*Sources: BOSS-48, BOSS-58, user request (2026-11-06: "add non rotating guns too").*

#### MB-BUNKER-SAUCER-04 — Lights · MUST

Its belt, bands, lintels, parapet strips, vision slits, seams and the lift jets' lips glow. Its neon
colour, set signal red, shows bright yellow (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50.*

#### MB-BUNKER-SAUCER-05 — The cupola's halves · MUST

The cupola's two halves are moving pieces (BOSS-45): each slides 14 px straight out across the
crown on its rails at the transformation (the left one the right one's mirror image) and stays
there; they leave no frame (the well is the core's). Two hydraulic rams telescope out of their
sleeves behind each half as it slides, and the periscope sinks into the cupola as it strains (the
model's rig: not hit, fires nothing).

**Acceptance criteria**
- Given its design, then its transformation moves its two halves, mirrored (unit tests on the
  moving regions).
- Given its model, then it holds together at rest and once they have moved.

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### MB-BUNKER-SAUCER-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then drifts heavily:
a slow sway, a shallow bob. While it is fought the ground scrolls at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.5 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-BUNKER-SAUCER-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `jet-left`, `jet-right` (no gun) and
`pillbox`. The core's guns (the slits and the rotor) fire the core's volleys and are the last the
player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### MB-BUNKER-SAUCER-08 — Stage patterns: the slits open one pair at a time · MUST

At most three guns are out as it comes in, and each lost part brings two more out. While it stands
the pillbox sweeps an aimed pair of magenta bullets 8° apart every 2.4 s. Each slit fires both its
barrels at once, two parallel red bullets straight out of it, the right and left guns of a pair
half a period apart. The core fires:
- stage 0: the 15° pair, every 2 s. **Guns out: 3** (2 fixed: the 15° slits; the pillbox's turret);
- stage 1: the 15° pair every 2.6 s, the 42° pair every 2 s (they open). **Guns out: 5** (4 fixed),
  or 4 if the pillbox went first;
- stage 2: the 15° pair every 2.8 s, the 42° pair every 2.4 s, the 70° pair every 1.8 s (they open).
  **Guns out: 7 of its own** (6 fixed) and, after the transformation, its 2 cannons;
- stage 3 (all three parts gone): the rotor's ring of 14 turning half a step a volley (a spiral)
  every 1.4 s, the 15° pair every 2.6 s and the 100° pair every 2 s (they open). **Guns out: 9 of its
  own** (8 fixed) and what is left of its cannons.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel along it (a
  fight in the simulation).
- Given stage 0, then no more than three mounts are out; given each later stage, then a mount comes
  out that no earlier stage used.

*Sources: BOSS-21, BOSS-23, BOSS-58, user request (2026-11-06: "3 max, then more appear").*

#### MB-BUNKER-SAUCER-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two cannons fire all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given the transformation is over, then it is angry and fires only its cannons.

*Sources: BOSS-27.*

#### MB-BUNKER-SAUCER-10 — Its transformation: the cupola splits · MUST

It transforms once two of its parts are destroyed (BOSS-36; the lift jets first in the debug key's
order). The cupola shudders, its periscope sinks into it, then its two halves slide apart along
the crown's rails on telescoping rams, opening the dark well between them; a **cannon** unfolds on
each half's flat top: three heavy barrels on a big turret, sweeping aimed spreads of three big red
shells. They shield the core. The fight turns from slipping between parallel streams fanning out
of its rim to weaving through heavy aimed shells from its crown.

**Acceptance criteria**
- Given two parts destroyed, then it transforms, its cupola's halves slide apart and its two
  cannons are revealed on them.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### MB-BUNKER-SAUCER-11 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at its transformation (2.83 as it comes in, 8.65 after).

**Acceptance criteria**
- Given its design, then its weighted fire rate after its transformation is above the one as it
  comes in (unit test).

*Sources: BOSS-39.*

#### MB-BUNKER-SAUCER-12 — Death, drops and points · MUST

Its parts drop a weapon bonus half the time, its cannons 30 % (BOSS-57). It scores the points of
Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/bunker_saucer.py` (`_BUNKER_SAUCER`, `BUNKER_SAUCER`); its
model in `src/game/view/bosses/lab/bunker_saucer_model.py` and `bunker_saucer_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.6 L (radius 61.2 px) | `stats.size` |
| rim, deck | radius 57, deck 8 px high, belly 15 px under it | `RIM`, `DECK` |
| parapet | 50–56 px out, top 11.5 px; notches 9.2 px wide | `PARAPET`, `NOTCH_HALF` |
| steps | radius 44 (top 14), crown radius 30 (top 19) | `STEP`, `CROWN` |
| cupola | radius 12, top 24; halves slide 14 px out | `CUPOLA_RADIUS`, `CUPOLA_TOP`, `CUPOLA_SLIDE` |
| core | radius 18, health 1 600 | `coreRadius`, `coreHealth` |
| lift jets | (±38, 38), radius 10, health 660 each, no gun | `JET_AT`, `JET_RADIUS` |
| pillbox | (0, -37), radius 9, health 720; twin turret 4.2 px, barrels 6.5 px, on a drum 18 px high | `PILLBOX_AT`, `PILLBOX_GUN` |
| slits | 8 fixed guns, 51.5 px out at ±15°, ±42°, ±70°, ±100°; 2 barrels 2.4 px apart, 5.6 px long | `SLIT_DEGS`, `SLIT_RADIUS`, `SLIT_GUN` |
| rotor | (0, 22) on the crown, 14 barrels, under a hatch 5.6 px round | `ROTOR_AT`, `CORE_ROTOR`, `HATCH_RADIUS` |
| cannons | (±20, 0) once out, radius 6.5, health 580 each (0.8 × the pillbox's), first 1.2 s / 2 s | `CANNON_AT` |
| bullets | slits red 175 px/s; pillbox magenta 170; spiral orange 160 | `SLIT_SHOT`, `TURRET_SHOT`, `SPIRAL` |
| full health | 4 800 | core and parts, cannons included (BOSS-54) |
| points | 4 000 | `stats.points` |
| ground speed | ×0.5 | `stats.groundSpeed` |
| stop, sway, bob | 0.72; 45 px over 9 s; 4 px over 4.4 s | `stopFraction`, `sway`, `bob` |
| drawn triangles | about 3 600 (body, parts, cannons) and 316 (rig), budget 4 000 | BOSS-53 |
