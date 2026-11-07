# Leviathan Spine

> **Area:** bosses · **Prefix:** `FB-LEVIATHAN-SPINE` · **Related:** [common](../common.md),
> [Moth Lantern](L-3-moth-lantern.md)

**Lab boss: in the dev viewer only.** It is listed after the 40 game bosses in the dev viewer's
Bosses list, and no level brings it in.

The Leviathan Spine is the final boss of Lab level L-3: a very long, narrow sea-serpent lying along
the screen, 5.5 L from snout to tail, its head down the screen and its segmented back armoured. Its
pectoral fins fire laser beams slanting across under it, three gun nodes along its spine fire lines
of aimed bursts, a tracking laser and walls of bullets, and its tail fluke fires homing missiles. It
sheds the plating of its back twice: a gatling pair, then a cannon pair and a lance horn on its
crown. Shared rules are in [common](../common.md).

## Requirements

### Look

#### FB-LEVIATHAN-SPINE-01 — Silhouette and size · MUST

Seen from above, the Leviathan Spine is a sea-serpent lying along the screen's vertical: a wedge
skull at its front (down the screen), a long body of nine swollen segments, full from its neck to
its middle and tapering to its tail, a crescent fluke at its tail, and a broad pectoral fin either
side behind its head. It is about 190 px long and 30 px across (70 px across its fins).

**Acceptance criteria**
- Manual validation in the boss viewer: a long serpent, head down the screen, narrow beside its
  length, unlike any other boss.

*Sources: Lab boss request (2026-11-05).*

#### FB-LEVIATHAN-SPINE-02 — Body · MUST

Its body is a graphite belly under a segmented carapace (slate plates, graphite seams), bone spikes
along its ridge with a glowing vein down its spine, a glowing lateral line down each flank and metal
bands grafted round it, riveted plates on two of them. Its skull is a slate wedge with a bone brow
ridge and snout plate, glowing eyes on its sides, fangs at its snout, a horn either side at its
back and three gill slits of light down each side of its neck; a metal collar at the back of its
skull carries its crest turret.

**Acceptance criteria**
- Manual validation: one serpent creature with grafted metal, its shell segmented.

*Sources: BOSS-47, BOSS-49.*

#### FB-LEVIATHAN-SPINE-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Fins** (left and right, behind its head): each a membrane on bone rays, a vein of light along
  its leading edge, and at its tip a fixed laser emitter slanting 24° across the centre line (the
  left fin's to the screen's right), so that their beams cross under it.
- **Front node** (on its spine behind the head): an armoured growth ringed with bone spikes, a twin
  gun on it (its bursts).
- **Middle node**: the same growth, a laser emitter on a turret on it, following the player through
  its warning line.
- **Rear node**: the same growth, a five-barrel fan turret on it (its walls of bullets).
- **Tail fluke**: a crescent of membrane on bone rays, a block of four missile ports grafted on its
  root.
- **Crest turret** (the core's, at the back of its skull): five barrels side by side (its aimed
  shots, bursts and fans).
- **Tail rotor** (the core's): fourteen barrels round a hub near its tail (its last ring), under an
  armoured hatch until its last stage; the hatch bursts off as the rotor comes into use (BOSS-58).

**Acceptance criteria**
- Given its model, then it draws its fins, its three nodes, its fluke and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### FB-LEVIATHAN-SPINE-04 — Lights · MUST

Its spine vein, lateral lines, gill slits, eyes, fin edges and fluke veins glow. Its neon colour,
set deep blue, shows bright green (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: BOSS-50.*

#### FB-LEVIATHAN-SPINE-05 — What it sheds · MUST

Its armour is three lengths of its own carapace, drawn as pieces of their own (D-254), the core
drawing the rest of its shell: `flanks`, its shell from y -16 to 2 (behind its fins), with its
spine vein, a spike and two grafted plates; `back`, its shell from y 20 to 38 (behind its middle
node), the same; and `crown`, the horned bone plate over its skull from y -88 to -70. Each bursts
into plates cracked from its outline and leaves a `shell` lattice frame; none is mirrored. The tail
hatch over its rotor is a region of its own (BOSS-58).

**Acceptance criteria**
- Given its design, then its first transformation sheds the flanks, its second the back and the
  crown, and each hidden weapon lies in a region its transformation sheds.
- Given its model, then it draws each region's armour, and it holds together with and without it.

*Sources: BOSS-42, BOSS-44, BOSS-52.*

### Behaviour

#### FB-LEVIATHAN-SPINE-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then weaves from
side to side and bobs. While it is fought the ground scrolls at ×1.2: it swims with the player.

**Acceptance criteria**
- Given the fight, then the ground eases to ×1.2 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-LEVIATHAN-SPINE-07 — Parts and core · MUST

It has six parts as it comes in, all shielding its core: `fin-left`, `fin-right`, `node-front`,
`node-rear`, `node-mid` and `tail-fluke`. The core's guns (the crest turret and the tail rotor) fire
the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its six parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### FB-LEVIATHAN-SPINE-08 — Stage patterns · MUST

In every stage while they stand: each fin fires its slanting laser, the two in turn, so their beams
cut across the screen under it; the front node fires lines of 5 aimed blue bullets 0.1 s apart; the
middle node's laser tracks the player through its warning line, then fires; the rear node sweeps a
wall of 7 orange bullets straight down, 9° apart; the fluke fires pairs of homing missiles. The core
fires:
- stage 0: an aimed red bullet;
- stage 1: an aimed fan of 3, 10° apart, swept;
- stage 2: a burst of 4 at the player;
- stage 3: a fan of 5 straight down, 12° apart, swept;
- stage 4: a fan of 7, 12° apart;
- stage 5: a burst of 6, and an aimed fan of 3 blue bullets;
- stage 6 (all six parts gone): a ring of 14 from the tail rotor, turning a little at each volley
  (a spiral), and a fan of 5 blue bullets.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-LEVIATHAN-SPINE-09 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons that transformation revealed fire all
out for `boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-LEVIATHAN-SPINE-10 — First transformation: its flanks · MUST

Once both fins are destroyed, the plating of its flanks bursts off, baring a dark metal lattice, and
a **gatling** pair unfolds there, either side of its spine. They shield the core and fire bursts of
4 at the player, in turn.

**Acceptance criteria**
- Given both fins destroyed, then it transforms and its two gatlings are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-40.*

#### FB-LEVIATHAN-SPINE-11 — Second transformation: its back and crown · MUST

Once its front and rear nodes are destroyed, the plating of its back bursts off for a **cannon**
pair, either side of its spine, and the crown of its skull for a **lance** on its centre line, a
horn of light pointing down the screen over its snout. They shield the core; the cannons sweep
aimed spreads of 3 big shells, the lance fires its laser.

**Acceptance criteria**
- Given its front and rear nodes destroyed, then it transforms a second time and its cannons and
  lance are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-40, BOSS-41.*

#### FB-LEVIATHAN-SPINE-12 — Laser colour · MUST

Its lasers (its fins', its middle node's and its lance's) are drawn in its own neon colour folded
into the enemy shots' family (BOSS-32).

**Acceptance criteria**
- Given its lasers, then their style is its kind id.

*Sources: BOSS-32.*

#### FB-LEVIATHAN-SPINE-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/leviathan_spine.py` (`_LEVIATHAN_SPINE`, `LEVIATHAN_SPINE`)
unless named; its model in `src/game/view/bosses/lab/leviathan_spine_model.py` and
`leviathan_spine_body.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5.5 L (radius 93.5 px); about 190 px long, snout y -96, tail tip y 96 | `stats.size` |
| core | health 3 000, radius 18, drop 1 | |
| `fin-left`, `fin-right` | (∓28, -24), radius 12, health 950, shield, drop 0.6 | |
| fin lasers | (∓31, -28), 6 px high, fixed, slanting ∓24°; barrel bore 1.8, 9 px long; base radius 3.6 | `FIN_LASER`, `FIN_SLANT` |
| `node-front` | (0, -42), radius 11, health 1 100, shield, drop 0.6 | |
| front node's twin gun | 17 px high; 2 barrels 2.9 px apart, bore 1.1, 8 px long; dome radius 5 | `FRONT_GUN` |
| `node-mid` | (0, 11), radius 11, health 1 200, shield, drop 0.6 | |
| middle node's laser | 17.5 px high, on a turret; bore 2.1, 10 px long; dome radius 5 | `mounts` `node-mid` |
| `node-rear` | (0, 47), radius 11, health 1 100, shield, drop 0.6 | |
| rear node's fan turret | 15.5 px high; 5 barrels 2.3 px apart, bore 0.9, 7 px long; dome radius 6.1 | `REAR_GUN` |
| `tail-fluke` | (0, 81), radius 13, health 1 200, shield, drop 0.6 | |
| fluke's missile block | (0, 81), 7 px high; 4 ports | `mounts` `tail-fluke` |
| crest turret (core) | (0, -63), 11 px high; 5 barrels 2.3 px apart, bore 0.9, 7 px long; dome radius 6.1 | `mounts` `crest` |
| tail rotor (core) | (0, 64), 10.6 px high; 14 barrels, bore 0.7, 3 px long; hub radius 4.4 | `mounts` `tail-rotor` |
| rotor hatch | octagon of radius 6 round (0, 64), the cap 10–12.6 px | `armour_region` `rotor-hatch` (`mount`) |
| full health | 15 020 (core 3 000, parts 6 500, hidden weapons 5 520) | BOSS-54; the Mesa Fortress (1-3) has 15 000 |
| points | 10 000; 1 000 a part | |
| ground speed | ×1.2 | |
| stop height | 0.7 | `stopFraction` |
| sway / bob | 70 px over 7 s / 8 px over 3.5 s | |
| fin lasers | 1.5 s beams every 6 s (first 2 s / 5 s) | |
| front node | bursts of 5, 0.1 s apart, blue 190 px/s, every 2.6 s (first 1 s) | |
| middle node | laser 1.6 s every 6.5 s (first 3.5 s) | |
| rear node | fans of 7, 9° apart, straight down, orange 175 px/s, every 2.6 s (first 1.6 s) | a sweep |
| fluke | 2 homing missiles, 30° apart, every 6 s (first 4 s) | |
| core stages 0–6 | aimed 1 (every 3 s); aimed 3, 10° (2.6 s); burst of 4 (2.4 s); fan of 5, 12° (2.4 s); fan of 7, 12° (2.2 s); burst of 6 and aimed 3 blue (2.2 s, 2.8 s); ring of 14 turning 9° (1.4 s) and fan of 5 blue (2.6 s) | red 185 px/s; crest turret, the ring from the tail rotor |
| weighted fire rate | 9.5 as it comes in, 11.8 after the first transformation, 12.3 after the second | BOSS-39 |
| transformation 1 | `fin-left` and `fin-right` destroyed | `transformParts` |
| flanks region (shed) | x ±14.4, y -16..2, `shell`, not mirrored | |
| gatlings | (∓8, -7), radius 7, health 960, pod 11.5 px, blue; first 1.2 s / 2.0 s | |
| transformation 2 | `node-front` and `node-rear` destroyed | |
| back region (shed) | x ±13.6 at y 20 to ±12.6 at y 38, `shell`, not mirrored | |
| crown region (shed) | x ±10 at y -88 to ±12 at y -70, `shell`, not mirrored | |
| cannons | (∓8, 29), radius 7.5, health 1 200, pod 11 px, orange; first 1.4 s / 2.6 s | |
| lance | (0, -78), radius 8, health 1 200, pod 9.6 px, on the centre line; first 2 s | |
| neon | deep blue (0.05, 0.6, 1), shown green | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is that of the 1-3 final
  boss (Mesa Fortress).
- **Sweeping lasers.** BOSS-31 lets only a sweeper's beam turn while it fires: its middle node's
  laser tracks the player during its warning line and then holds, and its fins' beams slant across
  the screen instead.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-05): 1 488 bullets and
  missiles, every one from a barrel or port, and 25 lasers; it dies at about 146 s.
