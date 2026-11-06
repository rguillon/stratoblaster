# Windmill Ram

> **Area:** bosses · **Prefix:** `MB-WINDMILL-RAM` · **Related:** [common](../common.md),
> [Sky Arsenal](L-14-sky-arsenal.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Windmill Ram is the mini boss of Lab level L-14: a wedge-shaped flying siege engine. An
armoured battering-ram prow (two halves meeting on its centre line) leads a timber-and-iron hull
with a siege belfry amidships, and a huge four-sailed windmill turns over its stern, driving it on.
It lunges and sways like a ram charging, its cheek guns firing aimed bursts. At its transformation
its **prow splits open**: the two halves swing apart sideways like doors, baring the iron-headed
ram inside, a lance riding out on each half's inner face, and its sails spin up: from then on two
lances fire straight down from the open prow, their beams sweeping across the screen as it sways.
Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "flying fortress theme"): it is a
built flying machine of timber, iron plating, rivets, sails and neon light lines, with no flesh,
eyes or limbs.

## Requirements

### Look

#### MB-WINDMILL-RAM-01 — Silhouette and size · MUST

Seen from above it is a wedge about 130 px long, its prow's point down the screen (at -68 px), its
hull widening from 42 px across behind the prow to 66 px at its stern, the windmill's cross of
four sails (76 px from tip to tip) turning over its stern. Shut, its prow is one pointed ram; once
open, its two halves stand out either side like opened doors.

**Acceptance criteria**
- Manual validation in the boss viewer: a siege ram with a windmill, unlike any other boss.

*Sources: Lab boss request (2026-11-06, "flying fortress theme").*

#### MB-WINDMILL-RAM-02 — Hull, ram and belfry · MUST

Its hull is an iron-skinned wedge with plank decking (seams along it, riveted iron bands across
it), a gunwale and a lit strake along each flank, buttress ribs down its sides, a row of pavise
shields hung on each gunwale (a light on each) and a lantern on each stern corner. Under the prow
its keel houses the battering ram: an iron-banded log on cradles along the centre line, its iron
head at the prow's point with a lit collar. Amidships stands the belfry's tower: square timber on an
iron plinth, iron corner posts, lit arrow slits, a pedestal on its roof under its fighting top.
The core's ram gun sits on a lit ring on the fore deck, the rotor's well amidships behind the
belfry.

**Acceptance criteria**
- Manual validation: one machine; the ram shows once the prow opens.

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-WINDMILL-RAM-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Cheek guns** (`cheek-left`, `cheek-right`), on the shut prow's halves: an armoured octagonal
  cowl on a seat, lit, a twin-barrelled turret on it (its bursts).
- **Belfry** (`belfry`): the tower's crenellated fighting top, lit round its gun's ring, a
  three-barrelled turret on it (its fans).
- **Ram gun** (the core's, on the fore deck): two barrels side by side (its aimed shots, spreads
  and bursts).
- **Deck rotor** (the core's, amidships): twelve barrels round a hub (its last ring). Until its last
  stage it lies under an octagonal hatch with a seam of light round it; as the rotor comes into use
  the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

A destroyed part's stump stands on its seat (the cheeks' on the prow, the belfry's on its tower's
roof).

**Acceptance criteria**
- Given its model, then it draws its three parts and every gun mount.

*Sources: BOSS-18, BOSS-48, BOSS-58.*

#### MB-WINDMILL-RAM-04 — Windmill and lights · MUST

A stout octagonal timber tower on its stern carries the windmill's cap; an axle leans out of it to
the hub, in front of the cap and above the belfry's roof. The four sails (lattice frames of dark
cloth on iron-capped spars, a light along each leading edge, a beacon at each tip) form a disc
leaning `SAIL_TILT` forward from flat, so the cross reads from above. They are a rig of the model
(no part, no gun): they turn slowly as it fights shut, spin up through its transformation and turn
faster once its prow is open, and wind down as it dies. Its lights take its neon colour, amber,
shown yellow (BOSS-50).

**Acceptance criteria**
- Given its model, then its sails turn round their hub, faster from its transformation on.
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50, user request (2026-11-06, "get creative on how the boss transforms").*

#### MB-WINDMILL-RAM-05 — The prow halves · MUST

Its prow is two moving pieces (`prow-right` and its mirror image `prow-left`, BOSS-45): each a
thick plated half-wedge from its keel to its armoured top, riveted plates and a lit seam over it,
an iron cap at its point, a lit edge where the halves meet, a dark recess on its inner face, a
hinge knuckle on its back outer corner, where it swings on an iron hinge post of the hull. Its
cheek gun stands on it at rest; its lance's pod lies on its inner face. The deck rotor's hatch is a
shed region of its own (BOSS-58).

**Acceptance criteria**
- Given its design, then its transformation moves both halves and each lance rides one of them
  (unit test).
- Given its model, then it holds together at rest and once the prow is open.

*Sources: BOSS-45, BOSS-52.*

### Behaviour

#### MB-WINDMILL-RAM-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways wide
and bobs hard and quick, lunging like a ram. While it is fought the ground scrolls at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.5 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-WINDMILL-RAM-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `cheek-left`, `cheek-right` and
`belfry`. The core's guns (the ram gun and the deck rotor) fire the core's volleys and are the last
the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-WINDMILL-RAM-08 — Stage patterns: the charge · MUST

Shut, it fights like a ram charging: in every stage while they stand, each cheek gun fires bursts
of 3 red bullets at the player, and the belfry sweeps fans of 5 orange bullets, 12° apart, straight
down. The core fires:
- stage 0: an aimed red bullet;
- stage 1: an aimed spread of 3, 10° apart;
- stage 2: a burst of 4 orange bullets at the player;
- stage 3 (all three parts gone): a ring of 12 from the deck rotor, turning 8° at each volley (a
  spiral), and an aimed red bullet.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-WINDMILL-RAM-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two lances fire all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two lances.

*Sources: BOSS-27.*

#### MB-WINDMILL-RAM-10 — Transformation: the prow splits open · MUST

It transforms once, when both cheek guns are destroyed (`transformParts`, BOSS-36). As an event:
the prow strains, then its two halves swing apart about their hinges, 55° each way about the
vertical, like doors opening, baring the ram and its keel; a **lance** pod on each half's inner face
unfolds as they open and rides into place, pointing down the screen; the sails spin up. From then
on the fight changes character: instead of aimed bursts from the prow, two fixed lasers fire
straight down from the open doors (1.4 s every 7.5 s, staggered), and as it sways their beams sweep
across the screen, so the player must find the gap between them. The lances shield the core.

**Acceptance criteria**
- Given both cheek guns destroyed, then it transforms, its prow halves swing open and its two lances
  are revealed on them.

*Sources: BOSS-35, BOSS-36, BOSS-40, BOSS-45.*

#### MB-WINDMILL-RAM-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its lances 30 %; it drops a life bonus as a mini
boss (BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/windmill_ram.py` (`_WINDMILL_RAM`, `WINDMILL_RAM`); its model in
`src/game/view/bosses/lab/windmill_ram_model.py`, its sails in `windmill_ram_sails.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 4.4 L (radius 74.8 px) | `stats.size` |
| hull | from y -24 to 60, 21 then 33 px half wide; deck 10 px high | `HULL_FRONT`, `HULL_BACK`, `HULL_HALF`, `DECK` |
| prow half | (0, -68), (5, -66), (21, -30), (21, -24), (0, -24) (right half), 2 to 13 px high | `PROW`, `PROW_Y` |
| prow swing | about the vertical through (±21, -24), 0° to 55°, mirrored | `PROW_SWING`, `OPEN`; `moving_region` `prow` |
| core | health 1 300, radius 16 | |
| `cheek-left` / `cheek-right` | (∓9, -42), radius 9, health 700, shield, drop 0.5 | on the shut prow |
| `belfry` | (0, 6), radius 12, health 820, shield, drop 0.5 | fighting top 22–24 px |
| cheek turrets | 14 px high; 2 barrels 2.86 px apart, bore 1.1, 7 px long; dome radius 4.5 | `CHEEK_GUN` |
| belfry turret | 25 px high; 3 barrels 2.86 px apart, bore 1.1, 7 px long; dome radius 5 | `BELFRY_GUN` |
| ram gun (core) | (0, -16), 11 px high; 2 barrels, bore 1.2, 8 px long; dome radius 5 | `RAM_GUN` |
| deck rotor (core) | (0, 24), 11.5 px high; 12 barrels, bore 0.8, 3.2 px long | `ROTOR` |
| rotor hatch | octagon of radius 6.5 round (0, 24) | `armour_region` `rotor-hatch` (`mount`) |
| lances | (∓21.5, -39) once open (drawn at (∓9, -33) on the halves), radius 7, health 660, pod 13–16 px; first 1.2 s / 2.0 s | `hidden_weapon` `lance`, ride the halves |
| windmill | tower at (0, 52), 40 px high; hub (0, 47), 48 px high; sails 38 px long, disc leaning 25° forward | `TOWER_AT`, `TOWER_TOP`, `HUB`, `SAIL_REACH`, `SAIL_TILT` |
| sails' spin | 1.3 rad/s shut, 3.4 rad/s open (spinning up through the transformation), half as it dies | `windmill_ram_sails.SPIN` |
| full health | 4 840 (core 1 300, parts 2 220, lances 1 320) | BOSS-54 |
| points | 4 400 | |
| ground speed | ×0.5 | |
| stop height | 0.73 | `stopFraction` |
| sway / bob | 62 px over 7.5 s / 13 px over 2.4 s | the lunge |
| cheek bursts | 3, 0.15 s apart, red 185 px/s, every 2.4 s (first 1.0 s / 2.2 s) | |
| belfry fans | 5, 12° apart, straight down, orange 175 px/s, every 3 s (first 1.6 s) | a sweep |
| core stage 0 | aimed 1, red, every 2.8 s | ram gun |
| core stage 1 | aimed 3, 10° apart, every 2.4 s | ram gun |
| core stage 2 | burst of 4, 0.14 s apart, orange, every 2 s | ram gun |
| core stage 3 | ring of 12 turning 8°, orange, every 1.6 s; aimed 1, red, every 2.4 s | rotor; ram gun |
| weighted fire rate | 4.5 as it comes in, 5.8 after its transformation | BOSS-39 |
| transformation | once both cheek guns are destroyed | `transformParts` |
| neon | amber (1, 0.7, 0), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its health is about that of the 1-4 mini
  boss (Scorpion, 4 760).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Its mechanisms** (round 3 asks each transformation to be a mechanical event): a mirrored
  swing about the vertical (BOSS-45) carrying the lances in (no armour bursts at the transformation),
  with the sails' spin-up as a view rig (`drawing.rig`). The sails are not in the simulation: no
  hit circle or muzzle is on them.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 363 shots and 13
  lasers, every one from a barrel or lens, along it; it dies at about 74 s.
