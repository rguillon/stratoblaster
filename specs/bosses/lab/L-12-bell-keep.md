# Bell Keep

> **Area:** bosses · **Prefix:** `MB-BELL-KEEP` · **Related:** [common](../common.md),
> [Cloud Dreadnought](L-12-cloud-dreadnought.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Bell Keep is the mini boss of Lab level L-12: a floating castle. A round stone keep stands on a
chunk of rock that tapers to a point beneath it, chains and glowing crystals hanging off it: a
curtain wall with its merlons, a gatehouse with two drawbridges across its front, a crenellated
drum tower either side of the gates, a square bell tower at its back and a round donjon in its
courtyard under a slate spire. It tolls: slow rings of heavy bullets from its bell tower, aimed
pairs from its towers. Once both towers have fallen its drawbridges come down, its portcullises
rise and a cannon rolls out of each gate onto its bridge: heavy aimed fire. Shared rules are in
[common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme", then "flying fortress theme"): it is
architecture of dressed stone, timber, iron and rock, with gold light lines, no flesh, eyes or
limbs.

## Requirements

### Look

#### MB-BELL-KEEP-01 — Silhouette and size · MUST

Seen from above it is a round castle 54 px across its curtain wall on a ragged disc of rock about 90
px across (the rock showing all round the wall), a ledge of rock jutting out in front of its gates.
Seen from the side, the rock tapers to a point 30 px under its top. Four chains hang off the
rock's rim, each ending in a lit weight; clusters of gold crystals jut from the rock's top round the
wall and from its flanks beneath (what keeps it aloft).

**Acceptance criteria**
- Manual validation in the boss viewer: a castle on a floating rock, unlike any other boss.

*Sources: Lab boss request (2026-11-06).*

#### MB-BELL-KEEP-02 — Walls, gatehouse and donjon · MUST

Its curtain wall is a stone ring 4 px thick and 12 px high round a flagstone courtyard, merlons
along its top, a darker course round its foot, lit arrow slits. The gatehouse across its front has
a middle pier and two gates, a lit arch over each, merlons along its front and a winch housing
over each gate. The donjon (its core) is a round stone tower in the courtyard, corbelled and
crenellated, a lit band under its corbels and lit windows (its charge lights) round it, the seat of
its turret on its roof's front and its slate spire behind. Two lit tracks run from the courtyard to
the gates.

**Acceptance criteria**
- Manual validation: one castle, its walls, gates and donjon readable from above.

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-BELL-KEEP-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Front towers** (`tower-left`, `tower-right`): stone drums either side of the gates, corbelled,
  crenellated, lit slits, a pennant streaming from each; a twin-barrelled turret on top (its aimed
  pairs).
- **Bell tower** (`belfry`): a square stone tower at its back, merlons at its corners, pennants; a
  bell rotor of ten barrels on its front half (its tolling rings), its bell's timber frame over its
  back half.
- **Donjon turret** (the core's, on the donjon's roof): three barrels side by side (its aimed shots
  and bursts).
- **Donjon rotor** (the core's, behind the turret): fourteen barrels round a hub (its last spiral).
  Until its last stage it lies under the slate spire, a hatch (BOSS-58): as the rotor comes into use
  the spire bursts off, leaving an iron collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws its three parts and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### MB-BELL-KEEP-04 — Lights and its bell · MUST

Its arrow slits, windows, arches, crystals, bands and the pennants' stripes glow. Its neon colour,
set warm gold, shows bright yellow (BOSS-50). Its bell (a bronze bell with two lit bands, on a
timber yoke) swings in the bell tower's frame from its axle, tolling at each end of its swing: slow
and gentle as it comes in, wider and twice as fast once it has transformed; it is gone with the bell
tower. The bell is on a rig of the model's own (D-228): it is not hit and fires nothing.

**Acceptance criteria**
- Given its model, then its lights are bright yellow.
- Manual validation: the bell swings, faster after the transformation, and is gone with the tower.

*Sources: BOSS-50, user request (2026-11-06: "get creative on how the boss transforms").*

#### MB-BELL-KEEP-05 — Its drawbridges and portcullises · MUST

Its two drawbridges are moving pieces (BOSS-45): timber planking on iron bands, lit along their
sides, an iron shoe at their tips, ribbed underneath so that raised they show their planks to the
front. Each is drawn lowered (its top level with the gate's sill) and rests raised, swung 90° up
about its hinge (across the boss, at the gate's sill); the left one is the right one's mirror image.
At its transformation they swing down to lie on the ledge and stay there; they leave no frame.
Behind each gate an iron portcullis rises out of the gate as its bridge comes down, and chains pay
out from the winches over the gates to the bridges' tips (the model's rig, MB-BELL-KEEP-04).

**Acceptance criteria**
- Given its design, then its transformation moves its two bridges, mirrored (unit tests on the
  moving regions).
- Given its model, then it draws each bridge, and it holds together at rest and once they are
  down.

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### MB-BELL-KEEP-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then drifts on its
rock: a slow sway, a deep bob. While it is fought the ground scrolls at ×0.4.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.4 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-BELL-KEEP-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `tower-left`, `tower-right` and
`belfry`. The core's guns (the donjon's turret and rotor) fire the core's volleys and are the last
the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### MB-BELL-KEEP-08 — Stage patterns: it tolls · MUST

In every stage while they stand: the bell rotor tolls a ring of 10 heavy, slow orange bullets every
3 s, each ring turned half a step (18°) from the last; each front tower sweeps an aimed pair of red
bullets 6° apart, the two in turn. The core fires:
- stage 0: an aimed magenta bullet;
- stage 1: a burst of 3 at the player;
- stage 2: an aimed spread of 3, 10° apart;
- stage 3 (all three parts gone): the donjon rotor's ring of 14 turning half a step at each volley
  (a spiral), and an aimed spread of 3, 8° apart.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-BELL-KEEP-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two cannons fire all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given the transformation is over, then it is angry and fires only its cannons.

*Sources: BOSS-27.*

#### MB-BELL-KEEP-10 — Its transformation: the drawbridges come down · MUST

It transforms when both front towers are destroyed (named, BOSS-36): its drawbridges swing down
(MB-BELL-KEEP-05), its portcullises rise, and a **cannon** rolls straight out of each gate, from
the courtyard behind it along its lit track onto the middle of its bridge (it slides out of the
body, BOSS-43, rather than unfolding), then raises its turret: three heavy barrels sweeping aimed
spreads of big red shells. They shield the core. The fight turns from dodging slow rings to
weaving through heavy aimed fire.

**Acceptance criteria**
- Given both front towers destroyed, then it transforms, its bridges come down and its two cannons
  are revealed on them.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### MB-BELL-KEEP-11 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at its transformation.

**Acceptance criteria**
- Given its design, then its weighted fire rate after its transformation is above the one as it
  comes in (unit test).

*Sources: BOSS-39.*

#### MB-BELL-KEEP-12 — Death, drops and points · MUST

Its parts drop a weapon bonus half the time, its cannons 30 % (BOSS-57). It scores the points of
Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/bell_keep.py` (`_BELL_KEEP`, `BELL_KEEP`); its model in
`src/game/view/bosses/lab/bell_keep_model.py`, `bell_keep_parts.py` and `bell_keep_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.4 L (radius 57.8 px) | `stats.size` |
| rock | radius 46 at its rim, top 4 px, point 30 px beneath; ledge 38 × 22 px round (0, -40) | `ROCK_TOP`, `ROCK_PROFILE`, `LEDGE` |
| curtain wall | radius 27 out, 23 in, 4–16 px, merlons 3 px | `WALL_OUT`, `WALL_IN`, `WALL_TOP`, `MERLON` |
| gatehouse | x ±18, y -30..-21, 19 px high; gates x ±(3.5..14.5), 14 px high | `GATE_*` |
| courtyard floor | 6 px (the gates' sills) | `FLOOR` |
| front towers | (±25, -14), radius 7.5, 26 px high | `TOWER_AT`, `TOWER_RADIUS`, `TOWER_TOP` |
| bell tower | (0, 26), 20 px square, 22 px high; bell frame to 34 px, bell at (0, 30) | `BELFRY_*`, `BELL_*` |
| donjon | (0, 3), radius 12, 24 px high | `DONJON_*` |
| core | health 1 000, radius 13 | |
| `tower-left`, `tower-right` | (∓25, -14), radius 10, health 600, shield, drop 0.5 | |
| `belfry` | (0, 26), radius 11, health 760, shield, drop 0.5 | |
| tower turrets | 26 px high; 2 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 4.6 | `TOWER_GUN` |
| bell rotor | (0, 19.5), 22 px high; 10 barrels, bore 1, 3.2 px long; hub radius 4.6 | `BELL_ROTOR` |
| donjon turret (core) | (0, -3.5), 24 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long | `KEEP_GUN` |
| donjon rotor (core) | (0, 8), 24 px high; 14 barrels, bore 0.8, 3.2 px long; hub radius 4.4 | `KEEP_ROTOR` |
| spire (hatch) | octagon of radius 6 round (0, 8); cone to 36 px | `armour_region` `spire` (`mount`) |
| drawbridges (moving regions) | x 3.5..14.5 (mirrored), from the gate (y -30) 12 px out, 2 px thick; swing `across` about (0, -30, 6) from -90° (raised) to 0 (lowered, as drawn); no frame | `moving_region` `bridge` |
| cannons | (∓9, -38) on the bridges, radius 8, health 610 (0.8 of the bell tower's), pod 6–8.5 px, red; roll out from (∓9, -15); first 1.2 s / 2.0 s | `out_of` |
| bell | swings ±0.45 rad over 6 s; ±0.8 rad over 3 s once transformed | `bell_keep_rig` `SWING`, `PERIOD` |
| portcullises | rise 9 px as the bridges come down | `bell_keep_rig` `RISE` |
| full health | 4 180 (core 1 000, parts 1 960, cannons 1 220) | BOSS-54 |
| points | 3 500 | |
| ground speed | ×0.4 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 50 px over 8.5 s / 6 px over 4.2 s | |
| bell rotor's tolls | ring of 10 turning 18°, orange 105 px/s radius 6, every 3 s (first 1 s) | |
| towers' pairs | aimed 2, 6° apart, red 185 px/s, every 2.2 s (first 1.4 s / 2.5 s) | sweeps |
| core stage 0 | aimed 1, magenta 175 px/s, every 3 s | donjon turret |
| core stage 1 | burst of 3, 0.15 s apart, every 2.6 s | donjon turret |
| core stage 2 | aimed 3, 10° apart, every 2.6 s | donjon turret |
| core stage 3 | ring of 14 turning 12.9°, orange 165 px/s, every 1.5 s; aimed 3, 8° apart, every 2.4 s | rotor; turret |
| cannons' fire | aimed spreads of 3 shells, 12° apart, 150 px/s radius 7, every 2.4 s | BOSS-40 |
| weighted fire rate | 5.5 as it comes in, 7.0 after its transformation | BOSS-39 |
| transformation | `tower-left` and `tower-right` | `transformParts` |
| neon | warm gold (1, 0.85, 0.4), shown yellow | `BOSS_LOOK.neon` |
| triangles | about 3 340 drawn (core, parts, armour) and 560 on its rig: 3 900, within 4 000 | BOSS-53 (scratch count) |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is near the Lab's other
  mini bosses' (the Bastion Cube's 4 040).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Drawn lowered.** The bridges are drawn as they end up, lowered, so that the cannons' pods lie
  within their outlines (BOSS-42); the models drop the faces turned down, so the bridges' undersides
  are ribbed (each face 40° off flat) to still show once raised.
- **Rolling out.** The cannons roll out of the gates (`out_of`: they slide straight out of the
  body, BOSS-43) rather than riding the bridges down; they are on the bridges once these are down.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 634 shots, every one
  from a barrel, along it; it dies at about 74 s.
