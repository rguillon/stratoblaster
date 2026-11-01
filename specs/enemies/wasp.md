# Wasp

> **Area:** enemies · **Prefix:** `ENM-WASP` · **Related:** [common.md](common.md), [hornet.md](hornet.md), [hive.md](hive.md), [World 3](../worlds/world-3/world.md), [World 4](../worlds/world-4/world.md)

The Wasp is a veteran kind ([common.md](common.md)): a small armed diver that comes in groups of
three. Each Wasp stops, turns its nose to the player, fires one aimed fan of three bullets, then
dives at where the player was, like a [Hornet](hornet.md) that shoots. The [Hive](hive.md) launches
Wasps too. It has no moving parts.

## Requirements

### Look

#### ENM-WASP-01 — Shape and size · MUST

The Wasp is a small, wasp-like insect 0.6 L long: a narrow, swollen, striped abdomen at the back, a
plated thorax and a small head at the front, two pairs of thin swept wings and a sting out of its
tail. Seen from above it reads as an insect, not as a ship.

**Acceptance criteria**
- Given the Wasp's model, then it is 0.6 L long (within the size tolerance of
  [common.md](common.md)), and its abdomen, four wings and sting show from above.

*Sources: P05-R14, P16-R04.*

#### ENM-WASP-02 — Cyber-Organic body · MUST

The Wasp is Cyber-Organic ([common.md](common.md)). Its abdomen is three swollen flesh segments
(sinew shade), its thorax a ridged carapace (slate and membrane shades), its head a flesh bulb
between its eyes. Metal is grafted on: a plate on the head's brow and a short gun barrel set in its
jaws, between two bone mandibles hooking forward. It has more grafts and limbs than the basic kinds,
so it reads as a veteran.

**Acceptance criteria**
- Given the Wasp's model, then its abdomen, thorax and head are flesh, the brow plate and the gun
  are metal, and the mandibles are bone.

*Sources: P16-R04.*

#### ENM-WASP-03 — Neon lights · MUST

Three neon bands stripe the back of the abdomen, the sting is neon, and two small eyes glow on the
head, all in the Wasp's neon colour. That colour is bright yellow: its configured yellow is on the
yellow side of the two enemy hues ([common.md](common.md)).

**Acceptance criteria**
- Given the Wasp's model, then its bands, sting and eyes are lit in bright yellow.

*Sources: P05-R14, P16-R04, D-231.*

#### ENM-WASP-04 — Charge light · SHOULD

A charge light at the mouth of the gun in its jaws brightens through the pause and is at full
brightness when the fan leaves ([common.md](common.md)).

**Acceptance criteria**
- Given a Wasp halfway through its pause, then its charge is about one half; at the end of the pause
  it is full.

*Sources: P05-R14, P16-R04.*

#### ENM-WASP-05 — Wings and reactors · MUST

Its two pairs of wings are membranes (a membrane skin on a bone strut along the leading edge), the
front pair the bigger. Each wing flutters on its root (living motion, [common.md](common.md)). Two
small plain reactors (no flesh sac, to save triangles) sit under its wings.

**Acceptance criteria**
- Given the Wasp's model, then it has four fluttering wings, two reactors and one gun muzzle.

*Sources: P16-R04.*

#### ENM-WASP-06 — Triangle budget · MUST

The Wasp's model, reactors included, stays within the veteran triangle budget (700,
[common.md](common.md)). It is about 490 triangles before the edge trim.

**Acceptance criteria**
- Given the Wasp's model, then its triangle count is at most the veteran budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-WASP-07 — Groups of three · MUST

A Wasp group is three Wasps side by side, 42 px apart, coming in from just above the top edge
(60 px). The middle Wasp is at the wave's entry position, or at a random X between 25 % and 75 % of
the width; the whole group is kept inside the range that enemies coming from the top keep to.

**Acceptance criteria**
- Given a Wasp group spawns, then 3 Wasps come in side by side, 42 px apart, just above the top
  edge.

*Sources: P05-R14.*

#### ENM-WASP-08 — Entry and pause · MUST

Each Wasp flies straight down at 240 px/s, then brakes at a constant 480 px/s² to rest at 72 % of
the playfield height (it slows into its stop, it does not halt at once). Its nose starts turning to
the player while it brakes. It then stays still for 0.4 s, turning its nose to the player, easing
in as it gets there. A Wasp that starts at or below its stop height starts with the pause.

**Acceptance criteria**
- Given a Wasp comes in, then it stops at 72 % of the height, and its speed never changes by more
  than the braking allows in one step.
- Given its pause, then it lasts 0.4 s and its nose ends on the player.

*Sources: P05-R14.*

#### ENM-WASP-09 — Aimed fan · MUST

When its pause ends, the Wasp fires once a fan of 3 bullets 12° apart, the middle one aimed at the
player (so ±12°), from the gun in its jaws. It fires only if its centre is over the playfield.

**Acceptance criteria**
- Given a Wasp ends its pause over the playfield, then it fires its aimed fan of 3 once, the middle
  bullet towards the player.
- Given a Wasp ends its pause outside the playfield, then it fires nothing.

*Sources: P05-R14.*

#### ENM-WASP-10 — Dive · MUST

After the fan, the Wasp dives in a straight line towards the player's position recorded at the end
of its pause, as a [Hornet](hornet.md) does: from rest, accelerating at 1000 px/s² up to 600 px/s,
until it leaves the screen.

**Acceptance criteria**
- Given a Wasp ends its pause, then it dives towards the player position recorded at that moment,
  not towards where the player moves afterwards.

*Sources: P05-R14.*

#### ENM-WASP-11 — Health, points and hit circle · MUST

A Wasp has 30 HP and scores 150 points. Its hit circle is 0.85 of half its size (8.7 px), at its
centre.

**Acceptance criteria**
- Given a Wasp, then it takes 30 damage to destroy and scores 150 points.

*Sources: P05-R14.*

#### ENM-WASP-12 — Veteran kind, from World 3 · MUST

The Wasp is a veteran kind. No wave of World 1 or World 2 uses it. It is the first veteran kind
World 3 brings in, at 3-1, and the waves of every later level (3-2 to 4-5) use it too.

**Acceptance criteria**
- Given the wave scripts, then no level of Worlds 1 and 2 names the Wasp, and every level from 3-1
  to 4-5 does.

*Sources: P05-R24, D-090.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 0.6 L | `src/game/config/enemies_veteran.py` `VETERAN_CONFIG.wasp.size` |
| health / points | 30 / 150 | `VETERAN_CONFIG.wasp.stats` |
| hit radius | 8.7 px | `radius(0.6)`: 0.6 × 34 × 0.85 / 2 |
| groupSize / groupSpacing | 3 / 42 px | |
| xRange | 25 % – 75 % of the width | the group's middle Wasp, when the wave gives no entry |
| entrySpeed / entryBrake | 240 px/s / 480 px/s² | |
| stopFraction | 0.72 | of the playfield height |
| pause | 0.4 s | |
| fanCount / fanSpacing | 3 / 12° | |
| bullet | style `orange`, 220 px/s, radius 4 | |
| diveAcceleration / diveMaxSpeed | 1000 px/s² / 600 px/s | |
| muzzles | `[0, -10.4, 0.8]` | the gun in its jaws |
| neon | `[1, 0.85, 0.05]`, drawn `[1, 1, 0.05]` | `VETERAN_NEON.wasp` |
| triangle budget | 700 (veteran) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.veteran` |

## Notes

**Appears in** (`src/game/config/world_3/waves.py`, `world_4/waves.py`): one phrase of its level's
cycle in each of [3-1](../worlds/world-3/3-1-canal-works.md),
[3-2](../worlds/world-3/3-2-docklands.md), [3-3](../worlds/world-3/3-3-workers-quarter.md),
[3-4](../worlds/world-3/3-4-suburbs.md), [3-5](../worlds/world-3/3-5-garden-villages.md),
[4-1](../worlds/world-4/4-1-garden-town.md), [4-2](../worlds/world-4/4-2-inner-town.md),
[4-3](../worlds/world-4/4-3-midtown.md) and [4-4](../worlds/world-4/4-4-business-district.md)
(2 groups, 1.6 s apart), and in [4-5](../worlds/world-4/4-5-downtown.md) (3 groups, 1.4 s apart);
the groups grow over each level. The Hives of 4-3, 4-4 and 4-5 launch more ([hive.md](hive.md)). It
is in no level's filler and no boss sends it out.

- The Wasp's code is the Hornet's (`Wasp` extends `Hornet`), with its own numbers and the fan.
- The veteran models were slimmed under a cap of 550 triangles in phase 16 (a TypeScript test of
  phase 5, not carried over to Python); the budget of the tier is 700.
- Known gaps: no unit test checks the model's size or its triangle count since the Python port
  (D-220).
