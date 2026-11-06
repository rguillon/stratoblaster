# Rocket Interceptor

> **Area:** bosses · **Prefix:** `MB-ROCKET-INTERCEPTOR` · **Related:** [common](../common.md),
> [Aerial Ark](L-20-aerial-ark.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Rocket Interceptor is the mini boss of Lab level L-20: a gigantic rocket-plane strapped to
boosters, about 3.6 L across: a slim core plane with stubby delta wings riding between two big
strap-on booster rockets, held to its wingtips by pylons. Strapped in, it fills the sky with salvos
of homing missiles from the blocks on its boosters' backs and lobs flak from its tail turret. Once
both boosters are wrecked it jettisons them and unfolds: its stub wings telescope out into the room
the boosters left, and the doors at each new wingtip open on a lance. The fight turns from missiles
to shoot down and flak to dodge into precise, straight laser lances either side and fast bursts.
Shared rules are in [common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "10 more gigantic airplanes but be really creative on the
transformation") this Lab boss is an aircraft, not a creature: dark metal plating, glass, rocket
casings, pylons and neon light lines, no flesh, eyes or veins.

## Requirements

### Look

#### MB-ROCKET-INTERCEPTOR-01 — Silhouette and size · MUST

Seen from above, its nose down the screen, it is a long needle-nosed fuselage (y -52 to 36) with a
short delta wing either side (out to x ±22), a big booster rocket either side of it (axes at x ±33,
nose cones down to y -48, nozzles back to y 39), each joined to a wingtip by two pylons. About
3.6 L across with its boosters on; once they are gone and its wings are out, a slim plane with long
straight wings about 3 L across.

**Acceptance criteria**
- Manual validation in the boss viewer: a rocket-plane between two boosters at rest; a slim
  long-winged plane, a lance at each wingtip, once it has transformed.

*Sources: Lab boss request (2026-11-06, "gigantic airplanes").*

#### MB-ROCKET-INTERCEPTOR-02 — Body · MUST

Its fuselage is a faceted hull of dark plating: a smoked glass canopy behind its nose, a light down
each shoulder, seams and a vent on its back, the chin gun's seat ahead of the canopy, the spine
rotor's hatch amidships; two canted fins and two small tailplanes at its tail, and its main rocket's
bell nozzle out of the tail, burning. Its stub wings are thick swept plates, lit along their leading
edges, a slot in each tip (where the wing's sections come out) between the pylons' sockets. Each
booster casing is a long cylinder of dark plating with pale bands and a lit ring, a stringer down its
back and a light down each flank, a flat armoured saddle on its back for its missile block, a bell
nozzle at its back with its flame, a dark bulkhead at its front under its nose cone, and two pylons
to the wingtip, their bolts lit.

**Acceptance criteria**
- Manual validation: one aircraft of metal, glass and neon lines; no creature features.

*Sources: BOSS-49, BOSS-52; departure from BOSS-47 above.*

#### MB-ROCKET-INTERCEPTOR-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Boosters** (left and right): each booster's nose cone (a long ogive with a pale band, a lit ring
  and strakes) is the part; a block of four missile ports stands on the saddle on its casing's back.
  Destroyed, the nose cone is gone and the bulkhead shows; the casing stays, the stump on its saddle.
- **Flak turret** (at its tail, between the fins): an armoured drum lit round its foot, splinter
  plates round it, carrying the **flak mortar** (a fat barrel in a cradle on a turntable).
- **Chin gun** (the core's, on the nose ahead of the canopy): two barrels side by side (its aimed
  shots, spreads and bursts).
- **Spine rotor** (the core's): ten barrels round a hub on the fuselage's back (its last rings).
  Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes into use
  the hatch bursts off (BOSS-58), leaving a lit collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws both nose cones, the flak turret and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### MB-ROCKET-INTERCEPTOR-04 — Lights · MUST

Its wings' leading edges and tip lamps, the fuselage's shoulder lines, the fins' tips, the nose
lamp, the boosters' rings, flank lines and pylon bolts, the wing sections' edges and the wingtip
doors' edges, the turret's ring and the hatch's seam glow. Its neon colour is set flame orange
(1, 0.45, 0.2); the viewer folds it into the enemy palette (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are in its neon colour.

*Sources: BOSS-50.*

#### MB-ROCKET-INTERCEPTOR-05 — Its boosters fall away and its wings unfold · MUST

Its transformation is a staged morph of 2 s (the reveal timeline, BOSS-43, BOSS-45):
1. **Bolts** (to 0.15): it strains, its boosters shudder on their pylons.
2. **Jettison** (0.12 to the end): each booster casing, pylons and all, rolls outward off the
   wingtip (up to 72°), swings its nose out and falls away behind and below the plane, still burning,
   until it is out of sight (it is gone once the transformation is over). The boosters (parts) have
   left the fight as it starts (they retire, BOSS-46).
3. **Telescoping** (0.15 to 0.6, eased): out of the slot in each stub wing's tip slides the wing's
   middle section (to x 36), and out of it the outer section (to x 51), twice as far: the wing comes
   out in two stages into the room the boosters left. The outer section is a moving piece (BOSS-45,
   a slide of 29 px), the middle section the view rig's (half its slide).
4. **The tip opens** (0.36 to 0.56): the two doors over the outer section's end open fore and aft
   like a clamshell, folding right over (150°) to lie either side of the tip, and the lance under them swings up and slides its barrel out (0.4 to
   1.0), the open doors lying either side of it like rails.

**Acceptance criteria**
- Given its design, then its transformation slides both outer sections out, mirrored, and its
  lances ride them (unit tests on the moving regions); its boosters retire.
- Given its model, then it holds together at rest (boosters on) and once its wings are out.
- Manual validation: the boosters peel away and the wings telescope out, the tips opening on the
  lances.

*Sources: BOSS-43, BOSS-45, BOSS-46, BOSS-52.*

### Behaviour

#### MB-ROCKET-INTERCEPTOR-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways wide and
quick and bobs. While it is fought the ground scrolls at ×1.3 (an interceptor at full burn).

**Acceptance criteria**
- Given the fight, then the ground eases to ×1.3 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-ROCKET-INTERCEPTOR-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `booster-left`, `booster-right` and
`flak`. The core's guns (the chin gun and the spine rotor) fire the core's volleys and are the last
the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-ROCKET-INTERCEPTOR-08 — Stage patterns · MUST

In every stage while they stand, each booster fires a pair of homing missiles 24° apart every
5.5 s, the two boosters in turn; the flak turret lobs a flak shell at the player, a big, slow orange
bullet that bursts into a ring of 8 red ones after 1.2 s. The core fires:
- stage 0: an aimed orange bullet;
- stage 1: an aimed spread of 3, 10° apart;
- stage 2: fast bursts of 5 red bullets at the player, 0.1 s apart;
- stage 3 and after: a ring of 10 from the spine rotor, one bullet a barrel, turning 9° at each
  volley (a spiral), and bursts of 3.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-ROCKET-INTERCEPTOR-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two lances fire all out, as often as their
warning, beam and gap allow, for `boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two lances.

*Sources: BOSS-27.*

#### MB-ROCKET-INTERCEPTOR-10 — Transformation: jettison and unfold · MUST

It transforms once, when both boosters are destroyed (named; they retire at it, so their stumps go
with their casings). As an event: the wrecked boosters are jettisoned and fall away, the wings
telescope out to x ±51 and a **lance** comes out at each new wingtip (on the outer section, under
its doors). The lances shield the core and fire straight down the screen either side of it. The
fight changes character: no more missiles to shoot down and flak to dodge from two wide boosters,
but two walls of laser either side, the flak and the core's fast bursts between them.

**Acceptance criteria**
- Given both boosters destroyed, then it transforms, its boosters retire, its wings slide out and
  its two lances are revealed on them.

*Sources: BOSS-35, BOSS-36, BOSS-45, BOSS-46.*

#### MB-ROCKET-INTERCEPTOR-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its lances 30 %; it drops a life bonus as a mini
boss (BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/rocket_interceptor.py` (`_ROCKET_INTERCEPTOR`,
`ROCKET_INTERCEPTOR`) unless named; its model in `src/game/view/bosses/lab/rocket_interceptor_model.py`
and `rocket_interceptor_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.6 L (radius 61 px) | `stats.size` |
| fuselage | y -52 to 36, 14 px wide, back 12 px high | `NOSE`, `TAIL`, `SPINE_TOP`; loft `FUSELAGE` |
| stub wing (right) | (7, -10) (22, 8) (22, 26) (7, 28); 2.5 to 6.5 px high | `WING`, `WING_Y` |
| boosters | axes at x ±33, 10.5 px high, radius 9.5; nose tip y -48, casing y -30 to 30, nozzle exit y 39; saddle top 20.5 | `BOOSTER_*` |
| wing middle section (rig) | x 20–36, y 9.5–24.5, out from 15 px in | `MID`, `MID_IN` |
| wing outer section (moving region) | (34, 10.5) (47, 10.5) (51, 14) (51, 20) (47, 23.5) (34, 23.5), 2.8 to 5.2 px high; slides from 29 px in (mirrored); no frame | `EXTENSION`, `EXT_Y`, `EXT_IN`; `moving_region` `wing-ext` |
| wingtip doors (rig) | x 38–49.5, hinged at y 11 and 23, open 150° over 0.36–0.56 | `rocket_interceptor_rig.DOOR_*`, `OPEN` |
| jettison (rig) | over 0.12–1.0: roll 72° outward, 45 px out, 80 px back, 110 px down | `FALL`, `ROLL`, `DRIFT` |
| core | health 1 620, radius 13 | |
| `booster-left`, `booster-right` | (∓33, -24), radius 13, health 750, shield, drop 0.5, retire at 1 | nose cones |
| missile blocks | (∓33, -14), 4 ports, block top 23.5 | `missile_mount` |
| `flak` | (0, 30), radius 9, health 800, shield, drop 0.5 | |
| flak mortar | (0, 31), 11.5 px high; 1 barrel, bore 3, 4.4 px long, mortar cradle | `FLAK_MORTAR` |
| chin gun (core) | (0, -40), 8 px high; 2 barrels 2.6 px apart, bore 1, 7 px long | `CHIN_GUN` |
| spine rotor (core) | (0, 4), 12 px high; 10 barrels, bore 0.8, 3.2 px long; hub radius 4.4 | `ROTOR` |
| rotor hatch | octagon of radius 6 round (0, 4) | `armour_region` `rotor-hatch` (`mount`) |
| full health | 5 200 (core 1 620, parts 2 300, lances 1 280) | BOSS-54; about the 1-5 mini boss's (Sentinel, 5 150) |
| points | 5 200 | |
| ground speed | ×1.3 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 62 px over 6.4 s / 6 px over 3 s | |
| booster missiles | 2 homing, 24° apart, every 5.5 s (first 1.2 s / 3.9 s) | `volley.missiles` |
| flak | 1 orange shell at 100 px/s, radius 7, bursting after 1.2 s into 8 red at 155 px/s, aimed, every 3 s (first 2.2 s) | `FLAK` |
| core stage 0 | aimed 1 orange at 185 px/s, every 2.8 s | chin gun |
| core stage 1 | aimed 3, 10° apart, every 2.4 s | chin gun |
| core stage 2 | burst of 5 red at 205 px/s, 0.1 s apart, every 1.6 s | chin gun |
| core stage 3+ | ring of 10 orange turning 9°, every 1.5 s; burst of 3 red, every 2 s | rotor; chin gun |
| weighted fire rate | 2.15 as it comes in, 5.59 after its transformation | BOSS-39 |
| transformation | `booster-left` and `booster-right` destroyed | `transformParts` |
| lances | (∓44, 17) on the outer sections, radius 7, health 640, pod from 5.2 to 8.7 px; first 1.2 s / 3.6 s | ride the sections; `lance` kind (a laser 1.4 s every 7.5 s, straight down) |
| neon | flame orange (1, 0.45, 0.2) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about that of the 1-5
  mini boss (Sentinel).
- **Not a creature** (see the departure from BOSS-47 above).
- **Retiring destroyed parts.** Its boosters are both named for its transformation and retire at it:
  they are always destroyed by then, and retiring hides their stumps, which would otherwise hang in
  the air where the casings were once these have fallen away. Their casings are the view rig's, not
  parts: the player shoots their nose cones.
- **The jettison is only looks.** The falling boosters are the rig's (no hit circle, no muzzle); they
  are hidden once the transformation is over. The wholeness check (BOSS-52) sees them on at rest and
  gone after.
- **Silhouette.** No other boss is a plane between two strap-on rockets; the Twin Hammerhead (L-2)
  and the Twin Pylon (L-7) are twin hulls without a plane between them.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 329 shots and 11
  lasers, every shot from a barrel, along it; it dies at about 74 s.
