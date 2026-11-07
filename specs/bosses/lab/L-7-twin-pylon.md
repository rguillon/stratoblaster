# Twin Pylon

> **Area:** bosses · **Prefix:** `FB-TWIN-PYLON` · **Related:** [common](../common.md),
> [Bastion Cube](L-7-bastion-cube.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Twin Pylon is the final boss of Lab level L-7: two tall lattice transmission pylons standing
side by side on a long base platform, 5 L across, an energy conduit sagging between their heads and
an arc crackling over it, its core a finned capacitor block in the middle. It fights with
electricity: lasers down the screen from the insulator stacks at the platform's ends and from the
capacitor between the pylons, fast aimed bursts from the coil heads on the pylons' tops, the two
pylons firing in turn, rings of sparks from the transformer at its back. Shared rules are in
[common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's request (2026-11-06, "drop
the animal looking theme") this Lab boss is a machine, not a creature: dark metal lattices, plating,
insulators, cables and neon light lines, no flesh, eyes or veins.

## Requirements

### Look

#### FB-TWIN-PYLON-01 — Silhouette and size · MUST

Seen from above, the Twin Pylon is a long, low platform across the screen, 160 px long and 36 px
deep, its ends chamfered, a short prow on the centre line at its front and an annex at its back; on
it two lattice pylons stand 80 px apart, each a square tower tapering from 22 px at its foot to 9 px
at its head, 36 px high, a cross-arm near its top reaching 17 px either side; between their heads
sags a glowing conduit over the capacitor block in the middle. It is 5 L across.

**Acceptance criteria**
- Manual validation in the boss viewer: two lattice pylons on a long platform, linked at their
  heads, a capacitor between them.

*Sources: Lab boss request (2026-11-06).*

#### FB-TWIN-PYLON-02 — Platform, pylons, conduit and capacitor · MUST

The platform is dark plated steel with lit lines along its long edges, deck plates, vent grilles,
hazard stripes at its ends and three reactors under its back edge. Each pylon has four legs on
footings, a frame at each of four levels, crossed braces on every face, two lit bands round it and a
head block; its cross-arm is a lattice beam (two chords and a zigzag), an insulator string and a
lit tip at each end. The conduit is a glowing cable between two dark ones, clamped along its sag,
with two feeders down to the capacitor. The capacitor (the core) is a stepped block: a lit band
round its step, cooling fins along the flanks of its upper block with lit slits between them, and
two charge bars on its top that brighten as it readies a volley.

**Acceptance criteria**
- Manual validation: one machine of dark metal and neon lines; no creature features.

*Sources: BOSS-49, BOSS-52; departure from BOSS-47 above.*

#### FB-TWIN-PYLON-03 — Its parts and guns · MUST

Every shot and laser leaves one of its gun mounts (BOSS-58):
- **Insulator stacks** (left and right, at the platform's ends): each a tall stack of ribbed discs
  on a lit base, a cable up to its pylon's arm; on its cap a **laser emitter** pointing straight
  down the screen.
- **Coil heads** (left and right, on the pylons' heads): each a glowing toroid round a post wound
  with lit rings, its half of the arc crackling towards the middle; on the post's cap a turret of
  two barrels side by side (its fast aimed bursts).
- **Transformer** (at its back, on the annex): a finned box with lit seams and three insulated
  bushings; on its top a **rotor** of eight barrels (its rings of sparks).
- **Arc laser** (the core's, on the capacitor's top, between the pylons): a laser emitter on a
  turret following the player during its warning line.
- **Front turret** (the core's, on the capacitor's step): three barrels side by side (its aimed
  shots, fans and bursts).
- **Capacitor rotor** (the core's): twelve barrels round a hub on the capacitor's top (its last
  rings). Until it comes into use it lies under an octagonal hatch with a lit seam; the hatch then
  bursts off (BOSS-58), leaving a lit collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws its five parts and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### FB-TWIN-PYLON-04 — Lights · MUST

Its conduit and arcs, the lit bands of its pylons, the edges of its platform, the slits of its
capacitor, its insulators' and coils' rings and the seams of its hatches glow. Its neon colour is
set electric blue (0.3, 0.5, 1); the viewer folds it into the enemy palette (BOSS-50), where it
shows green.

**Acceptance criteria**
- Given its model, then its lights are in its neon colour.

*Sources: BOSS-50.*

#### FB-TWIN-PYLON-05 — Armour regions · MUST

Its armour regions (BOSS-42), each drawn as a piece of its own: the **end cowlings** (a ribbed hood
over each end of the platform, behind the insulator stack, shed at the first transformation), the
**bus covers** (a ribbed plate either side of the capacitor's front) and the **prow plate** (a wedge
over the prow), shed at the second; each leaves a shell frame. The capacitor's hatch is a shed
region of its own (BOSS-58). It does not change shape.

**Acceptance criteria**
- Given its model, then it draws every armour region and it holds together after each
  transformation.

*Sources: BOSS-42, BOSS-44, BOSS-52.*

### Behaviour

#### FB-TWIN-PYLON-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways wide and
slowly and bobs a little. While it is fought the ground scrolls at ×0.6.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.6 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-TWIN-PYLON-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `insulator-left`, `insulator-right`,
`coil-left`, `coil-right` and `transformer`. The core's guns (the arc laser, the front turret and
the capacitor rotor) fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### FB-TWIN-PYLON-08 — Stage patterns · MUST

In every stage while they stand, the insulator stacks fire their lasers straight down the screen,
one end then the other, 3 s apart; the coil heads fire fast bursts of 4 blue bullets at the player,
the two pylons in turn; the transformer's rotor fires rings of 8 purple bullets, turning 11.25° at
each volley. The core's arc laser fires at every stage, more often from one to the next, and:
- stage 0: the arc laser alone;
- stage 1: an aimed magenta bullet;
- stage 2: a fan of 5 straight down, 12° apart, swept;
- stage 3: a burst of 4 at the player;
- stage 4: a ring of 12 blue from the capacitor rotor turning 7.5° at each volley;
- stage 5 and after: a ring of 12 turning -9° at each volley, and an aimed spread of 3, 12° apart.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-TWIN-PYLON-09 — Angry · MUST

After each transformation it is angry (BOSS-27): its newly revealed weapons fire all out,
`boss_rage_rate` times as often, for `boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-TWIN-PYLON-10 — First transformation · MUST

It transforms first when both insulator stacks are destroyed: its end cowlings burst off and an
**orb** rises at each end of the platform, behind where the stacks stood. They shield the core and
fire their rings, in turn.

**Acceptance criteria**
- Given both insulator stacks destroyed, then it transforms and its two orbs are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-40.*

#### FB-TWIN-PYLON-11 — Second transformation · MUST

It transforms again when both coil heads are destroyed: its bus covers and its prow plate burst
off, a **mortar** rises either side of the capacitor's front and a **lance** on the centre line at
its prow, pointing down the screen. They shield the core; the mortars lob their flak in turn, the
lance fires its laser.

**Acceptance criteria**
- Given both coil heads destroyed, then it transforms and its two mortars and its lance are
  revealed.

*Sources: BOSS-35, BOSS-36, BOSS-40.*

#### FB-TWIN-PYLON-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up from one transformation to the next: see Tunable values.

**Acceptance criteria**
- Given its design, then its fire rate as it comes in and after each transformation never goes
  down, and ends higher (unit test).

*Sources: BOSS-39.*

#### FB-TWIN-PYLON-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/twin_pylon.py` (`_TWIN_PYLON`, `TWIN_PYLON`) unless named; its
model in `src/game/view/bosses/lab/twin_pylon_model.py` and `twin_pylon_parts.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (radius 85 px) | `stats.size` |
| platform | x ±80, y ±18, deck 7 px high; prow to y -32, annex to y 38 | `DECK_HALF`, `DECK_TOP`, `PROW`, `ANNEX` |
| pylons | at x ±40; 22 px square at the foot to 9 px at the head, 36 px high; arm at 29 px, 17 px either side | `PYLON_*`, `ARM_*` |
| conduit | from the pylons' heads, sagging to 27 px over the centre | `SAG` |
| capacitor | x ±12, y -20..15; step 13 px, top 21 px (upper block from y -9) | `CAP_*` |
| core | health 2 200, radius 18, drop 1 | |
| `insulator-left`, `insulator-right` | (∓66, -6), radius 11, health 800, shield, drop 0.6 | |
| insulator lasers | 22 px high, fixed, pointing down; base radius 4.5, bore 2.2, 9 px long | `INSULATOR_LASER` |
| `coil-left`, `coil-right` | (∓40, 0), radius 12, health 900, shield, drop 0.6 | on the pylons' heads |
| coil turrets | 38.5 px high; 2 barrels 2.6 px apart, bore 1, 7.5 px long; dome radius 4.6 | `COIL_GUN` |
| `transformer` | (0, 27), radius 13, health 1 000, shield, drop 0.6 | |
| transformer rotor | 14 px high; 8 barrels, bore 0.9, 4 px long; hub radius 5 | `TRANSFORMER_ROTOR` |
| arc laser (core) | (0, -4), 21 px high, on a turret; base radius 5, bore 2.4, 10 px long | `ARC_LASER` |
| front turret (core) | (0, -15), 13 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 5 | `FRONT_GUN` |
| capacitor rotor (core) | (0, 8), 21 px high; 12 barrels, bore 0.85, 3.6 px long; hub radius 4.6 | `CAP_ROTOR` |
| rotor hatch | octagon of radius 6 round (0, 8), the cap 20.6–22.4 px | `armour_region` `rotor-hatch` (`mount`) |
| full health | 9 730 (5 600 without the hidden weapons: core 2 200, parts 4 400; orbs 1 200, mortars 1 280, lance 650) | BOSS-54; the Gull Mothership (1-2) has 9 740 |
| points | 9 000 | |
| ground speed | ×0.6 | |
| stop height | 0.74 | `stopFraction` |
| sway / bob | 35 px over 10 s / 5 px over 4.5 s | |
| insulator lasers | 1.4 s beams every 6 s (first 2 s / 5 s) | |
| coil bursts | 4 blue at 200 px/s, 0.08 s apart, every 2.4 s (first 1 s / 2.2 s) | |
| transformer rings | 8 purple at 185 px/s turning 11.25°, every 2.8 s (first 1.6 s) | |
| arc laser | 1.5 s beams every 7, 6.5, 6, 5.5 s; 1.6 s beams every 5, 4.6 s (stages 0 to 5) | core |
| core stage 1 | aimed 1, magenta 190 px/s, every 2.6 s | front turret |
| core stage 2 | fan of 5, 12° apart, every 2.6 s | front turret, a sweep |
| core stage 3 | burst of 4, 0.1 s apart, every 2.2 s | front turret |
| core stage 4 | ring of 12 blue turning 7.5°, every 2.2 s | capacitor rotor |
| core stage 5+ | ring of 12 turning -9°, every 1.8 s; aimed 3, 12° apart, every 2.4 s | rotor; front turret |
| weighted fire rate | 10.0 as it comes in, 17.1 after its first transformation, 19.3 after its second | BOSS-39 |
| transformations | `insulator-left` and `insulator-right`, then `coil-left` and `coil-right` destroyed | `transformParts` |
| end cowlings | x 60..80, y 1..18 (mirrored), 6–12 px; form 1; shell frame | `armour_region` `end-cowls` |
| bus covers | x 13..30, y -19..-1 (mirrored), 6–11 px; form 2; shell frame | `bus-covers` |
| prow plate | x ±12, y -32..-19, 6–11 px; form 2; shell frame | `prow-plate` |
| orbs | (∓70, 10), radius 9, health 600, pod 8.5 px, blue; first 1.2 s / 2.4 s | form 1 |
| mortars | (∓21, -10), radius 8.5, health 640, pod 9 px, purple; first 1.2 s / 2.6 s | form 2 |
| lance | (0, -27), radius 8, health 650, pod 9 px; first 1.8 s | form 2, the centre line |
| neon | electric blue (0.3, 0.5, 1) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is that of the 1-2 final
  boss (Gull Mothership, 9 740).
- **Not a creature** (see the departure from BOSS-47 above).
- **Heights.** Its coil heads' turrets stand 38.5 px high, higher than most bosses' mounts (the
  World 1 bosses' stand under 28 px): seen from the game's tilted camera they show a little ahead of
  their hit circles.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 302 bullets and 42
  lasers, every one from a mount, bullets along their barrels; it dies at about 134 s.
