# Hive Carrier

> **Area:** bosses · **Prefix:** `FB-HIVE-CARRIER` · **Related:** [common](../common.md),
> [Twin Hammerhead](L-2-twin-hammerhead.md), [Hornet](../../enemies/hornet.md)

The Hive Carrier is the final boss of the Lab's level L-2. **Lab boss: in the dev viewer only**; no
level brings it in. It is a fat hexagonal hive-ship, 4 L across: a honeycomb of wax cells over a
waxy shell held by dark metal ribs, a domed queen chamber in its middle (its core), a cell-bay at
each of its four slanted corners and a bony ram with a queen gland at its front. It fights by area
denial and swarms rather than precise aim: its front bays launch Hornets, its rear bays lob big
spores that burst into rings, its ram fans bullets straight down. It sheds its side combs for a pair
of mortars, then its front and rear combs for a pair of sweepers and a hangar on its centre line.
Shared rules are in [common](../common.md).

## Requirements

### Look

#### FB-HIVE-CARRIER-01 — Silhouette and size · MUST

Seen from above, the Hive Carrier is a broad hexagon with no wings, 4 L across: its side corners at
(±66, 0), its others at (±36, ±54); a raised cell-bay over each slanted corner, a wedge-shaped ram
jutting from its front edge (down the screen), and a hexagonal domed chamber in its middle.

**Acceptance criteria**
- Manual validation in the boss viewer: a hexagonal honeycomb hive, unlike any other boss.

*Sources: user request (2026-11-05, the Lab bosses).*

#### FB-HIVE-CARRIER-02 — Body · MUST

Its shell is a bevelled hexagonal slab of sinew-shaded wax up to 6 px, its deck dark between the
cells. Wax cells (hexagonal prisms on a hexagonal grid, bone and sinew shades, some a little taller,
a few with a lit larva on top) cover the deck, clear of the chamber, the bays, the ram and the metal
ribs. Dark metal is grafted on: a band round its rim, clamps on its side corners with a running
light each, and six radial ribs from the chamber out to the bays' collars and towards the side
corners, a vein along each. The queen chamber is a waxy hexagonal dome to 18.8 px with a dark metal
collar round its foot, a vein ring, veins down its six edges, glands on its flanks and the crown
turret's pedestal on its front slope. Two reactors in sacs and bone barbs at its stern.

**Acceptance criteria**
- Manual validation: a living hive of wax and metal.

*Sources: BOSS-47, BOSS-49.*

#### FB-HIVE-CARRIER-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Front bays** (`bay-front-left`, `bay-front-right`): a metal hexagonal collar with a neon ring,
  six big wax cells round a lit hive mouth; they launch Hornets (BOSS-25) and have no gun.
- **Rear bays** (`bay-rear-left`, `bay-rear-right`): the same collar and cells round a pedestal
  under a spore cannon, one fat barrel on a turret (their spores).
- **Ram**: a bony wedge with bone mandibles either side, a queen gland on it with a vein ring and a
  grafted plate under a turret of five barrels side by side (its fans).
- **Crown turret** (the core's): five barrels side by side on the chamber's front slope (its aimed
  shots, bursts and fans).
- **Hive rotor** (the core's): fourteen barrels on the chamber's top (its last ring). Until then it
  lies under a hexagonal wax hatch with a metal rim and a seam of light, which bursts off as the
  rotor comes into use, leaving a collar; the rotor rises out of it.

**Acceptance criteria**
- Given its model, then it draws its four bays, its ram and every gun mount.

*Sources: BOSS-25, BOSS-48, BOSS-58.*

#### FB-HIVE-CARRIER-04 — Lights · MUST

Its veins, larvae, glands, hive mouths and running lights glow in its neon colour, set amber,
shown bright yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50.*

#### FB-HIVE-CARRIER-05 — Its combs (armour) · MUST

The cells over three areas are the armour it sheds (BOSS-42), each drawn as a piece of its own:
- `side-combs` (first transformation): the cells over its side corners, x 38..65, y -16..16
  (mirrored), a vein across each to a gland; the mortars lie folded under them;
- `front-combs` (second): the cells either side of the chamber's front, x 5..22, y -42..-21, its
  outer back corner cut along the rib (mirrored), a vein across each; the sweepers lie under them;
- `rear-comb` (second): the cells behind the chamber, x -12..12, y 19..42 (not mirrored), a vein
  and a gland on it; the hangar lies under it.

Each bursts into plates cracked from its outline and leaves a `shell` lattice frame.

**Acceptance criteria**
- Given its design, then each transformation sheds its regions and each hidden weapon lies in one.
- Given its model, then it draws each region's armour.

*Sources: BOSS-42, BOSS-43, BOSS-44.*

### Behaviour

#### FB-HIVE-CARRIER-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways and
bobs. While it is fought the ground scrolls at ×0.4.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.4 of the level's speed.

*Sources: BOSS-03, BOSS-10.*

#### FB-HIVE-CARRIER-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: its four bays and its ram. The core's
guns (the crown turret and the hive rotor) fire the core's volleys and are the last the player
destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### FB-HIVE-CARRIER-08 — Stage patterns · MUST

Area denial and swarms. Its parts fire in every stage while they stand:
- each front bay launches 2 Hornets side by side, which dive at the player, the two bays in turn;
- each rear bay's spore cannon sweeps a fan of 2 big, slow spores straight down, 24° apart, each
  bursting into a ring of 6 after 1.3 s, the two bays in turn;
- the ram sweeps a fan of 5 red bullets straight down, 15° apart.

The core fires:
- stage 0: 1 aimed orange bullet;
- stage 1: an aimed spread of 3, 12° apart, a sweep;
- stage 2: a burst of 4;
- stage 3: a fan of 5 straight down, 12° apart, a sweep;
- stage 4: a fan of 7 and 1 aimed red bullet;
- stage 5 (all five parts gone): a ring of 14 from the hive rotor turning 9° at each volley (a
  spiral), and a burst of 3 red from the crown turret.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys.

*Sources: BOSS-20, BOSS-21, BOSS-23, BOSS-25.*

#### FB-HIVE-CARRIER-09 — Angry · MUST

It is angry after each transformation (BOSS-27): the weapons that transformation revealed (the
mortars; then the sweepers and the hangar's Hornets) fire all out, alone, for `boss_rage_seconds`.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only what it revealed.

*Sources: BOSS-27.*

#### FB-HIVE-CARRIER-10 — First transformation: mortars · MUST

Once two of its parts are destroyed, its side combs burst off, baring a dark metal lattice, and two
**mortars** unfold on its side corners. They shield the core and lob flak shells at the player that
burst into rings.

**Acceptance criteria**
- Given two parts destroyed, then it transforms and its two mortars are revealed.

*Sources: BOSS-36, BOSS-38, BOSS-40.*

#### FB-HIVE-CARRIER-11 — Second transformation: sweepers and a hangar · MUST

Once four of its parts are destroyed, its front combs and its rear comb burst off: two **sweepers**
unfold either side of the chamber's front, firing lasers that sweep after the player, and a
**hangar** opens on its centre line behind the chamber, launching Hornets.

**Acceptance criteria**
- Given four parts destroyed, then it transforms a second time and reveals its sweepers and hangar.

*Sources: BOSS-36, BOSS-38, BOSS-40, BOSS-41.*

#### FB-HIVE-CARRIER-12 — Laser colour · MUST

Its sweepers' lasers are drawn in its own colour (BOSS-32).

**Acceptance criteria**
- Given its lasers, then their colour is its neon folded into the enemy shots' family.

*Sources: BOSS-32.*

#### FB-HIVE-CARRIER-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always
(BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/hive_carrier.py` (`_HIVE_CARRIER`, `HIVE_CARRIER`) unless named;
the model in `src/game/view/bosses/lab/hive_carrier_model.py` and `hive_carrier_comb.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 4 L (radius 68 px) | |
| core | health 1 900, radius 22, drop 1 | |
| bays | (∓36, ∓42), radius 14, health 720, shield, drop 0.6 | `BAY_X`, `BAY_Y` |
| spore cannons (rear bays) | 15 px high; 1 barrel, bore 2.6, 6 px long; dome radius 5.5 | `SPORE_GUN` |
| `ram` | (0, -60), radius 13, health 880, shield, drop 0.6; turret 11 px high, 5 barrels 2.6 px apart, bore 1, 7 px long, dome 6 | |
| crown turret (core) | (0, -13), 17 px high; 5 barrels 2.6 px apart, bore 1, 8 px long; dome radius 6 | `mounts` `crown` |
| hive rotor (core) | (0, 6), 19.6 px high; 14 barrels, bore 0.7, 3.4 px long; hub radius 5 | `mounts` `hive-rotor` |
| rotor hatch | hexagon of radius 6.5 round (0, 6), 17.8–20.8 px | `rotor-hatch` |
| full health | 9 700 (5 660 without the hidden weapons) | BOSS-54; the Gull Mothership's is 9 740 |
| points | 9 000; 900 a part | |
| ground speed | ×0.4 | |
| stop height | 0.74 | |
| sway / bob | 35 px over 10 s / 6 px over 5 s | |
| Hornets | 2 a front bay every 6.5 s (first 2.5 s left, 5.75 s right) | `launches` |
| spores | fan of 2, 24° apart, straight down, radius 8, 95 px/s, bursting after 1.3 s into 6 at 150 px/s; every 4 s (first 2 s / 4 s) | `SPORE` |
| ram fan | 5, 15° apart, red 185 px/s, every 2.6 s (first 1.2 s) | a sweep |
| core stage 0 | 1 aimed, orange 175 px/s, every 2.8 s | crown turret |
| core stage 1 | aimed 3, 12° apart, every 2.6 s | crown turret |
| core stage 2 | burst of 4, 0.14 s apart, every 2.4 s | crown turret |
| core stage 3 | fan of 5, 12° apart, every 2.4 s | crown turret |
| core stage 4 | fan of 7 every 2.2 s; 1 aimed red every 2.6 s | crown turret |
| core stage 5 | ring of 14 turning 9° every 1.3 s; burst of 3 red every 2.8 s | hive rotor; crown turret (named) |
| transformations | 2 and 4 parts destroyed | default thresholds |
| side combs (shed first) | x 38..65, y -16..16, `shell`, mirrored; cells 6–10.3 px | `SIDE_COMB` |
| front combs (shed second) | x 5..22, y -42..-21, corner cut from (22, -33) to (15, -21), `shell`, mirrored | `FRONT_COMB` |
| rear comb (shed second) | x -12..12, y 19..42, `shell`, not mirrored | `REAR_COMB` |
| mortars | (∓48, 0), radius 10, health 700, pod 10 px, orange; first 1.2 s / 2.0 s | |
| sweepers | (∓13, -32), radius 7, health 880, pod 10 px; first 1.4 s / 4.4 s | |
| hangar | (0, 30), radius 10, health 880, pod 10 px; first 2.2 s | the Lab's only hangar |
| cells | grid 6 px, cells 5.2 px round, 3.5–4.3 px high | `hive_carrier_comb` |
| neon | amber (1, 0.8, 0.05), shown yellow | `BOSS_LOOK.neon` |
