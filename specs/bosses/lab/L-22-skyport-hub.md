# Skyport Hub

> **Area:** bosses · **Prefix:** `FB-SKYPORT-HUB` · **Related:** [common](../common.md),
> [Iron Lighthouse](L-22-iron-lighthouse.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Skyport Hub is the final boss of Lab level L-22: a gigantic flying airport seen from above. An
X of four runways radiates from an octagonal apron round a domed terminal, a control tower behind
it; a pier juts out at its front (the concourse), at its back (the radar's) and either side (a fuel
depot's); a ducted lift fan spins under each runway's end. It comes in with three guns: a fixed
battery at the end of each front runway, firing along it, and the control tower's turret. Its fuel
depots and radar carry no gun, but every part it loses brings a new gun up out of a hatch. Once
both depots are gone its rear runways swing forward round the terminal into their place, a sweeper
riding each; once its radar is gone its terminal's roof splits and its halves slide apart on rails,
a missile rack riding each, and a hangar rises between them, launching Hornets. Shared rules are in
[common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06: "drop the animal looking theme", then "10 more gigantic flying
fortress, add non rotating guns too, don't add too many start guns, 3 max, then more appear when
they are destroyed"): it is a machine of metal decks, tarmac and glass with aqua light lines, no
flesh, eyes or limbs.

## Requirements

### Look

#### FB-SKYPORT-HUB-01 — Silhouette and size · MUST

Seen from above it is a great X about 150 px across: four runways 16 px wide running out along the
diagonals from 14 px to 82 px off its centre, a lift fan's duct past each end, round an octagonal
apron 60 px across with its four piers (front to 54 px, back to 62 px, sides to 62 px). Seen from
the side, its decks are 4 px thick over dark girder keels and a keel cone under the apron.

**Acceptance criteria**
- Manual validation in the boss viewer: a flying airport, unlike any other boss.

*Sources: Lab boss request (2026-11-06).*

#### FB-SKYPORT-HUB-02 — Runways, terminal and tower · MUST

Each runway is dark tarmac on a metal deck, a dashed pale centre line, four threshold stripes and a
number block at its end, lit edge lights down both sides, a raised kerb along its edges. The
terminal (the core) is an octagonal hall 32 px across, glazed walls with a lit band, two jet bridges
out of its front; its roof (two halves, FB-SKYPORT-HUB-11) has skylights lit along it. Rails on
posts run out either side of it, under its roof's edges. The control tower behind it is a tapering
shaft, a glazed cab with a lit sill, its turret on the cab's roof and an antenna with a beacon. The
front pier carries the concourse, a long low building with lit windows; the apron has a lit hold
line round the terminal and seams along the diagonals.

**Acceptance criteria**
- Manual validation: one airport, its runways, terminal and tower readable from above.

*Sources: BOSS-49, user request (2026-11-06).*

#### FB-SKYPORT-HUB-03 — Its parts · MUST

- **Runway-end batteries** (`gun-left`, `gun-right`): an armoured crescent blast wall at the end
  of each front runway, open outwards, ammunition lockers, a lit band; its fixed gun on a plinth in
  it (the plinth stays, with the stump, once it is destroyed).
- **Fuel depots** (`depot-left`, `depot-right`, no gun): three pale round tanks with domed tops and
  lit bands in a bunded yard on each side pier, a pipe rack to the apron.
- **Radar** (`radar`, no gun): a braced lattice mast on a plinth on the back pier, a platform with a
  lit rail and a beacon; its dish turns on top (the model's rig) and is gone with it.

**Acceptance criteria**
- Given its model, then it draws its five parts and every gun mount.

*Sources: BOSS-48, BOSS-58, lab-brief round 5 (gunless parts).*

#### FB-SKYPORT-HUB-04 — Lights · MUST

Its edge lights, hold line, skylights, windows, seams, fan lips and beacons glow. Its neon colour,
aqua `[0.3, 1, 0.8]`, shows bright green (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: BOSS-50.*

#### FB-SKYPORT-HUB-05 — Its rear runways · MUST

The two rear runways (heading 45° and 135° from config +X, with their lift fans) are moving pieces
(BOSS-45). Drawn at rest, at its first transformation each swings 27° forward about the vertical
through its root (`(±9.9, 9.9)`), clockwise for the right one seen from above, the left one its
mirror image, into the space the fuel depots held. They leave no frame (the space they leave is
open sky between the piers).

**Acceptance criteria**
- Given its design, then its first transformation moves its two rear runways, mirrored (unit tests
  on the moving regions); no part it can hit stands on them as they move.

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### FB-SKYPORT-HUB-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then drifts: a slow
sway, a gentle bob. While it is fought the ground scrolls at ×0.8. Its four lift fans spin in their
ducts (the model's rig), the rear ones riding their runways as they swing and spinning up as they
move; its radar's dish turns until the radar is destroyed.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.8 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-SKYPORT-HUB-07 — Gun mounts · MUST

Every shot leaves one of its gun mounts (BOSS-58). Fixed mounts (no turret) fire along their
barrels only:
- **Runway-end batteries** (on `gun-left` / `gun-right`, fixed): three barrels side by side,
  pointing out along their runway (45° off straight down).
- **Tower turret** (the core's): three barrels side by side on the control tower's cab roof.
- **Runway turrets** (the core's, on the front runways, 34 px out): two barrels side by side.
- **Lance** (the core's, fixed, at the front pier's tip): a laser pointing straight down.
- **Silos** (the core's, on the side piers, 36 px out): a block of two missile ports each.
- **Runway casemates** (the core's, fixed, on the front runways, 51 px out): three barrels side by
  side pointing out along their runway.
- **Hub rotor** (the core's, on the back pier): sixteen barrels round a hub.

Every core gun but the tower turret lies under an armoured octagonal lid (a hatch, BOSS-58) that
bursts off as it first comes into use, the gun rising out of the dark well under it.

**Acceptance criteria**
- Given its model, then every mount is drawn from its config numbers; given a fight in the
  simulation, then every shot leaves a barrel along it.

*Sources: BOSS-29, BOSS-58, user request (2026-11-06: "add non rotating guns too").*

#### FB-SKYPORT-HUB-08 — Stage patterns: guns rise as parts fall · MUST

Parts' volleys, while they stand: each runway-end battery fires a row of three orange bullets along
its runway every 2.4 s; the depots and the radar fire nothing. The core fires, a new gun joining at
every stage (the earlier ones keep firing):
- stage 0: the tower turret, an aimed magenta bullet every 2.2 s. **Guns out: 3** (2 fixed).
- stage 1: the tower a burst of 3; the runway turrets rise, aimed pairs 8° apart. Guns out: 4 (a
  battery lost first) or 5.
- stage 2: the tower an aimed spread of 3; the lance rises (a laser every 7 s, 1.4 s beam). Guns
  out: 4 to 8 (8 with the sweepers, if both depots are the parts lost).
- stage 3: the tower a burst of 4 red; the silos rise, two homing missiles each every 6.5 s. Guns
  out: 6 to 12.
- stage 4: the tower an aimed red pair; the runway casemates rise, rows of three red along their
  runways every 2.6 s. Guns out: 10 to 13.
- stage 5 (all five parts gone): the hub rotor rises: a ring of 16 turning 11.25° at each volley (a
  spiral) every 1.4 s; the tower a burst of 3. Guns out: 13 (with the revealed weapons standing).

Every lost part brings at least one new gun out; every stage's pattern differs from the last.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and its new mounts rise; each shot
  leaves a barrel (a fight in the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58, user request (2026-11-06: "then more appear when they are
destroyed").*

#### FB-SKYPORT-HUB-09 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons it has just revealed fire all out for
`boss_rage_seconds` (the sweepers, then the racks and the hangar). It has no angry pattern of its
own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-SKYPORT-HUB-10 — First transformation: the runways swing · MUST

It transforms the first time when both fuel depots are destroyed (named, BOSS-36): its rear runways
strain, then swing forward round the terminal (FB-SKYPORT-HUB-05), their lift fans spinning up, and
a **sweeper** unfolds on each, 40 px out along it (at about `(±47.5, 23.6)`): a laser on a turret
whose beam sweeps after the player. They shield the core. The fight turns from fixed rows along the
front runways to beams sweeping in from its flanks.

**Acceptance criteria**
- Given both depots destroyed, then it transforms, its rear runways swing and its two sweepers ride
  them.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### FB-SKYPORT-HUB-11 — Second transformation: the terminal opens · MUST

It transforms the second time when its radar is destroyed (named, BOSS-36; after the first): the
terminal's roof, two halves drawn closed, strains, then its halves slide apart on their rails, 13 px
each way (a mirrored slide, BOSS-45), each carrying a **rack** (a block of four missile ports,
pairs of homing missiles) on its top; the terminal's open hall (a dark floor, girders, a lit edge)
shows between them, and a **hangar** rises in it on the centre line, its doors sliding apart to
launch Hornets. They shield the core. The fight turns from bullets and beams to homing missiles and
launched enemies chasing the player.

**Acceptance criteria**
- Given the radar destroyed after the first transformation, then it transforms again, its roof
  halves slide apart carrying its racks and its hangar is revealed between them.

*Sources: BOSS-35, BOSS-36, BOSS-41, BOSS-45.*

#### FB-SKYPORT-HUB-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at each transformation (about 3.0 as it comes in, 7.5
after the first, 10.7 after the second).

**Acceptance criteria**
- Given its design, then its weighted fire rate never goes down and ends higher (unit test).

*Sources: BOSS-39.*

#### FB-SKYPORT-HUB-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its revealed weapons 30 %, its core always
(BOSS-57). It scores the points of Tunable values. Its full health is in line with the 1-2 final
boss's (Gull Mothership, 9740).

**Acceptance criteria**
- Given its design, then its drop chances and its points are those of Tunable values.

*Sources: BOSS-54, BOSS-56, BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/skyport_hub.py` (`_SKYPORT_HUB`, `SKYPORT_HUB`); its model in
`src/game/view/bosses/lab/skyport_hub_model.py`, `skyport_hub_parts.py` and `skyport_hub_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5.2 L (radius 88.4 px) | `stats.size` |
| decks | 2 → 6 px; apron 30 px to its flats | `DECK_LOW`, `DECK`, `APRON` |
| runways | half width 8, from 14 to 78 (+4 tip) px out, at ±45° and ±135° | `RUNWAY_*`, `FRONT_DEG`, `REAR_DEG` |
| lift fans | 84 px out, radius 9 | `FAN_OUT`, `FAN_R` |
| terminal | 16 px to its flats, walls 12 px, roof 12 → 15.5 px, slide 13 px | `TERMINAL`, `ROOF`, `ROOF_SLIDE` |
| control tower | (0, 24), cab 27 → 32 px | `TOWER_AT`, `CAB_*` |
| rear runway swing | -27° about (±9.9, 9.9) | `REAR_SWING` |
| core health | 2200 | `coreHealth` |
| batteries | 66 px out on the front runways, radius 9, health 800 | rows of 3 orange 170 px/s, 2.4 s |
| fuel depots | (±49, -3), radius 11, health 750, no gun | |
| radar | (0, 52), radius 10, health 900, no gun | |
| sweepers, racks, hangar | radius 8 / 7 / 9, health 720 each | 0.8 of the sturdiest part |
| full health | 9800 | core + parts + revealed weapons (BOSS-54) |
| points | 9500 | `points` |
| motion | stop 0.72, sway 36 px / 11 s, bob 4 px / 5 s, ground ×0.8 | |
| tower turret | aimed 1 / burst 3 / spread 3 9° / burst 4 / pair 6° / burst 3 | magenta then red |
| runway turrets | aimed pairs 8°, every 2.8 s | `RUNWAY_GUNS` |
| lance | laser every 7 s, 1.4 s beam | `LANCE_BEAM` |
| silos | 2 missiles each, every 6.5 s | `SILOS` |
| runway casemates | rows of 3 red, every 2.6 s | `CASEMATES` |
| hub rotor | ring of 16, 11.25° turn, every 1.4 s | |

## Implementation report

- Config, model (core, parts and armour drawings, rig), registration at the `# LAB L-22` markers.
- Simulated fight (a part broken every 12 s): every shot leaves a barrel (0 off), it dies at about
  134 s.
- Guns out per stage checked in the simulation (guns first: 3, 4, 4, 6, 10, 13; depots first: 3, 5,
  8, 12, 13, 13).
