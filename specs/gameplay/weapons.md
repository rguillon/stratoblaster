# Player weapons

> **Area:** Gameplay · **Prefix:** `GAME-WPN` · **Related:** [player-ship.md](player-ship.md), [controls.md](controls.md), [bonuses.md](bonuses.md), [bombs.md](bombs.md), [level-flow.md](level-flow.md), [../graphics/shots.md](../graphics/shots.md), [../audio/sfx.md](../audio/sfx.md), [../bosses/common.md](../bosses/common.md), [../ui/hud.md](../ui/hud.md)

The player's ship has three main weapons, the guns, the laser and the missiles, each with five
levels. One is in use at a time; the player switches between them, and weapon bonuses raise the
one in use. This file gives how each weapon fires and hits at each level, its damage and rate, the
balance rule between them, switching, levelling up, and keeping the levels from one level to the
next. What the shots look like is in [graphics/shots.md](../graphics/shots.md); their sounds in
[audio/sfx.md](../audio/sfx.md). The bombs are a separate, secondary weapon ([bombs.md](bombs.md)).

## Requirements

### GAME-WPN-01 — Three main weapons · MUST

The player has three main weapons: the **guns** (id `bullet`, shown "Bullet"), the **laser**
(`laser`) and the **missiles** (`missile`), in that order. Every ship fires all three. One weapon
is in use at a time.

**Acceptance criteria**
- Given the game data, then there are three weapons in the order `bullet`, `laser`, `missile`; the
  guns and the missiles fire projectiles, the laser is a beam (unit test).

*Sources: GD-30, D-015.*

### GAME-WPN-02 — Five levels · MUST

Each weapon has five levels, 1 to 5. A weapon used for the first time starts at level 1. A level
asked outside 1–5 is kept within it.

**Acceptance criteria**
- Given a weapon selected at level 7, then it fires at level 5; at level 0, at level 1 (unit test).

*Sources: GD-31.*

### GAME-WPN-03 — Guns: streams by level · MUST

The guns fire straight streams of minigun bullets:

| Level | Streams |
|-------|---------|
| 1 | one forward stream |
| 2 | two forward streams, `dual_spacing` (12 px) apart |
| 3 | one forward stream and two diagonal streams at ±10° |
| 4 | two forward streams and two diagonal streams at ±10° |
| 5 | one forward stream and four diagonal streams at ±10° and ±20° |

Diagonal streams come in mirrored pairs, left and right.

**Acceptance criteria**
- Given each level of the guns, then its streams are those of the table (unit test on the data).

*Sources: P03-R01.*

### GAME-WPN-04 — Guns: bullets · MUST

A gun bullet flies at a constant velocity of 600 px/s along its stream. Each stream fires 8
bullets a second. A bullet deals 10 damage to the first target it touches (hit radius 4 px), then
is gone. Bullets leave from inside the ship, under it: `bullet_launch_back` (13 px) behind the
ship's muzzle, so they start 16 px below the tip of its nose.

**Acceptance criteria**
- Given the guns at level 1 held for 1 s, then 8 bullets are fired (unit test).
- Given a bullet touching a target of 30 health, then the target has 20 left and the bullet is gone
  (unit test).

*Sources: P03-R01, D-015, D-106.*

### GAME-WPN-05 — The muzzle · MUST

The ship's muzzle (where the guns and the laser leave from) is `muzzle_inset` (3 px) below the tip
of the ship's nose, measured on each ship's own model, so the shots of every ship start at its
nose. The missiles leave from the ship's centre instead.

**Acceptance criteria**
- Given each of the three ships, then the laser starts 3 px below the tip of its nose.

*Sources: P03-R01, P03-R03.*

### GAME-WPN-06 — Laser: a continuous beam · MUST

The laser is a continuous beam fired straight ahead (up the screen) from the muzzle for as long as
fire is held. It is instant and never misses: it damages what it touches, every step, by its
level's damage per second:

| Level | Damage per second | Width |
|-------|-------------------|-------|
| 1 | 100 | 4 px |
| 2 | 200 | 6 px |
| 3 | 300 | 8 px |
| 4 | 400 | 10 px |
| 5 | 500 | 12 px |

A target is touched when its centre is above the beam's start and its distance across from the beam
is at most its radius plus half the beam's width. With nothing in its way, the beam runs to the top
of the screen.

**Acceptance criteria**
- Given the laser at level 3 on a target for 1 s, then the target loses 300 health (unit test).
- Given a target beside the beam by more than its radius plus half the width, then it is not
  touched (unit test).

*Sources: P03-R02, D-015, D-059, D-281.*

### GAME-WPN-07 — Laser: piercing · MUST

At level 1 the beam stops at the first target it touches (the lowest one). Above level 1, it goes
through that target and goes on from it one level lower (thinner, less damage per second), so a
level-N beam touches at most N targets, each at the level of the piece of beam that reaches it. A
target is touched once per step.

**Acceptance criteria**
- Given a column of three targets and the laser at level 2, then the lowest takes the level 2
  damage, the second the level 1 damage and the third none (unit test).

*Sources: P03-R02.*

### GAME-WPN-08 — Missiles: flight and homing · MUST

A missile leaves the ship's centre at 150 px/s along its stream and speeds up at 600 px/s², up to
700 px/s. It homes on the living target closest to the missile within `homing_range` (320 px,
about half the screen's height), turning towards it at up to 180° a second; the target is chosen
again every step. With no target in range it flies straight on. Farther enemies are not pursued.

**Acceptance criteria**
- Given a target 200 px away, then a missile turns towards it (unit test).
- Given the only target 400 px away, then the missile flies straight (unit test).
- Given a missile after 1 s of flight, then its speed is 700 px/s (unit test).

*Sources: P03-R03, D-015.*

### GAME-WPN-09 — Missiles: area damage · MUST

A missile that touches a target (missile radius 3 px) blows up there and deals 8 damage to every
target whose hitbox is within `missile_blast` (10 px) of the impact, the one touched included. The
damage is the same at every level. Each missile stream fires 4 missiles a second.

**Acceptance criteria**
- Given two targets next to each other within the blast, when a missile hits one, then both lose
  8 health (unit test).

*Sources: P03-R03, D-059, D-281.*

### GAME-WPN-10 — Missiles: streams by level · MUST

| Level | Streams |
|-------|---------|
| 1 | one forward stream |
| 2 | two diagonal streams at ±25° |
| 3 | one forward stream and two diagonal streams at ±25° |
| 4 | four diagonal streams at ±25° and ±45° |
| 5 | one forward stream and four diagonal streams at ±25° and ±45° |

The diagonal missiles fan out wide before they home.

**Acceptance criteria**
- Given each level of the missiles and no target, then the missiles fly along the angles of the
  table (unit test on the data).

*Sources: P03-R03.*

### GAME-WPN-11 — Streams fire in turn · MUST

When a level of the guns or the missiles has several streams, they do not fire all at once: they
fire one after the other, in their listed order (the forward stream first, then the left / right
pairs from the inside out), evenly spaced: one shot every 1 / (rate × streams) seconds. Each stream
still fires its own rate (bullets 8 a second, missiles 4 a second), so a level fires as many shots
a second, and deals as much damage, as if they all fired together. When fire is pressed, or the
weapon or its level changes, the first stream fires at once.

**Acceptance criteria**
- Given a two-stream level held for one volley period, then each stream fired once, never both in
  the same instant, and over a second each stream fired its rate (unit test).
- Given fire pressed, then the first shot leaves on that step (unit test).

*Sources: P03-R11, D-102.*

### GAME-WPN-12 — Weapon balance · MUST

The weapons are balanced against the guns, which are the reference (the bosses were tuned with
them): at every level the laser deals 125 % of the guns' damage per second and the missiles 40 %
of it (every stream counted), so the laser is above the guns and the guns are above the missiles.
Each weapon pays for its strength: the guns spread widest (up to 5 streams, which reach wide waves),
so the laser, the most focused (one column, never misses, pierces, but the ship must sit under its
target), deals more; the missiles need no aiming at all (they home) and so deal the least. The aim is that each weapon is the best pick for about a
third of the waves. With the current numbers:

| Level | Guns | Laser | Missiles |
|-------|------|-------|----------|
| 1 | 80 /s | 100 /s (125 %) | 32 /s (40 %) |
| 2 | 160 /s | 200 /s (125 %) | 64 /s (40 %) |
| 3 | 240 /s | 300 /s (125 %) | 96 /s (40 %) |
| 4 | 320 /s | 400 /s (125 %) | 128 /s (40 %) |
| 5 | 400 /s | 500 /s (125 %) | 160 /s (40 %) |

**Acceptance criteria**
- Given the weapon data, then at every level the laser's damage per second is 125 % of the guns'
  and the missiles' is 40 % of it (unit test on the data).

*Sources: GD-33, D-059, D-281.*

### GAME-WPN-13 — Switching weapon · MUST

Each press of the switch control ([controls.md](controls.md)) changes the weapon in use to the next
one, in order: guns → laser → missiles → guns. Each weapon keeps its own level: switching back
gets a weapon back at the level it had. Shots already in flight keep flying. The ship can switch
only while the player flies it (not while it rises in or flies off, nor once the game is over).

**Acceptance criteria**
- Given the guns at level 3 and the laser never used, when the switch is pressed, then the laser is
  in use at level 1; pressed twice more, the guns are back at level 3 (unit test).

*Sources: D-043, D-049.*

### GAME-WPN-14 — Levelling up · MUST

A weapon bonus picked up ([bonuses.md](bonuses.md)) raises the weapon in use by one level, up to
level 5; the new level fires at once. A weapon bonus picked up at level 5 gives nothing. The other
weapons keep their levels.

**Acceptance criteria**
- Given the missiles at level 2 in use, when a weapon bonus is picked up, then the missiles are at
  level 3 and the guns' level is unchanged (unit test).
- Given the weapon in use at level 5, when a weapon bonus is picked up, then it stays at level 5.

*Sources: GD-31, D-049.*

### GAME-WPN-15 — Weapon levels kept between levels · MUST

The very first level played starts with the guns at level 1. When a level is completed, the weapon
in use and the level of each weapon used so far are kept, and the next level started, whichever it
is, starts with them ([level-flow.md](level-flow.md)). A game over keeps nothing. A Continue starts
from the weapons saved at the checkpoint ([lives-and-damage.md](lives-and-damage.md)). Kept weapons
that cannot be read count as none (guns at level 1).

**Acceptance criteria**
- Given 1-2 completed with the laser in use at level 4 and the guns at level 3, when 1-3 (or any
  level) starts, then the laser is in use at level 4, and switching to the guns gives level 3
  (unit test on the saved weapons, e2e).
- Given a game over, then the weapons kept before the level are unchanged.
- Given an unreadable saved value, then the level starts with the guns at level 1 (unit test).

*Sources: D-071, P06-R02, P07-R08.*

### GAME-WPN-16 — Only what is on screen can be hit · MUST

The player's shots, laser, homing missiles (and bombs) can only hit targets whose centre is on
screen ([screen.md](screen.md) GAME-SCREEN-04): enemies, boss parts and cores, and enemy missiles,
which the player can shoot down. An enemy takes no damage before it comes into view, so no enemy
blows up out of sight.

**Acceptance criteria**
- Given an enemy just above the top edge in the line of fire, then it takes no damage; once it is
  on screen, it does (unit test).
- Given an enemy missile on screen, when a bullet touches it, then it is shot down.

*Sources: D-042, GD-43.*

### GAME-WPN-17 — Blocked hits · MUST

A shot that hits something that takes no damage (a boss core shielded by its parts,
[bosses/common.md](../bosses/common.md)) does no damage and is reported as a blocked hit, so it can
sound different ([audio/sfx.md](../audio/sfx.md)). Damage dealt is never more than the health the
target had.

**Acceptance criteria**
- Given a bullet hitting a shielded core, then the core's health is unchanged and the impact is
  marked blocked (unit test).

*Sources: D-097.*

### GAME-WPN-18 — Firing only while flying · MUST

The ship fires only while the player flies it: not while it rises into the level or flies off it
([level-flow.md](level-flow.md)), and not once the game is over. Releasing fire stops the next
shots; shots in flight keep flying.

**Acceptance criteria**
- Given the ship rising in at the start of a level, when fire is held, then nothing is fired (unit
  test).

*Sources: D-050, D-015.*

### GAME-WPN-19 — Weapons are data · SHOULD

The weapons are data in the game config (streams per level, rates, speeds, damage, homing, beam
levels), read by a game-agnostic, pure and deterministic shot simulation in the engine. Changing a
number needs no code change. The engine refuses weapon data with a duplicate id, no level, a level
without streams, or impossible numbers (a rate, speed, radius or damage that is not positive, a
negative acceleration, homing or blast, a speed cap under the launch speed).

**Discrepancy:** the engine has no check: nothing refuses weapon data at run time. The game's own
weapons are checked by a unit test (`tests/unit/game/sim/test_player_build.py`); the engine's check,
which nothing ran, was removed with the code only tests called (D-237).

*Sources: D-015.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| guns | 600 px/s, 8 shots/s per stream, 10 damage, radius 4 px | `src/game/config/player_weapons.py` `BULLET` |
| dual_spacing | 12 px | `DUAL_SPACING` |
| guns diagonals | ±10°, ±20° | `BULLET["levels"]` |
| bullet_launch_back | 13 px | `BULLET["launchBack"]` (D-106) |
| muzzle_inset | 3 px below the nose tip | `src/config/game_play.py` `GAME_PLAY_CONFIG.muzzle_inset` |
| laser damage per second | 100 / 200 / 300 / 400 / 500 | `LASER["levels"]` (D-281; was 80 / 140 / 200 / 260 / 320, D-059) |
| laser width | 4 / 6 / 8 / 10 / 12 px | `LASER["levels"]` |
| missiles | 150 → 700 px/s at 600 px/s², 4 shots/s per stream, radius 3 px | `MISSILE` |
| homing | 180°/s, `homing_range` 320 px | `MISSILE["homingTurnRateDeg"]`, `["homingRange"]` |
| missile damage | 8 to everything within `missile_blast` 10 px | `MISSILE["damage"]`, `["blastRadius"]` (D-281; was 14, D-059) |
| missile diagonals | ±25°, ±45° | `MISSILE_ANGLES` (phase 3 review; the first text said ±10°, ±20°) |
| saved weapons key | `<game id>_weapons` (cookie) | `src/app/saved_weapons.py` |

## Notes

- The guns' diagonals miss small or far targets, so on a single boss their real damage is closer to
  their forward streams': the laser is the best boss weapon, the guns the best against wide waves,
  the missiles the safest but the weakest (D-281).
- There is no way to start again from level 1 weapons but clearing the cookies (D-071).
