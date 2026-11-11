# Lives and damage

> **Area:** Gameplay · **Prefix:** `GAME-LIFE` · **Related:** [player-ship.md](player-ship.md), [bombs.md](bombs.md), [bonuses.md](bonuses.md), [level-flow.md](level-flow.md), [scoring.md](scoring.md), [../ui/hud.md](../ui/hud.md), [../ui/continue-and-game-over.md](../ui/continue-and-game-over.md), [../graphics/effects.md](../graphics/effects.md), [../enemies/common.md](../enemies/common.md)

The player has a health bar and lives. Enemy shots and enemies touching the ship's small hitbox
take health; each hit gives a short invincibility; when the health runs out a life is lost, and
with no life left the game is over. After the mini boss, a game over can be continued from the
checkpoint. Lives (and bombs) carry over from a completed level to the next. This file gives those
rules and numbers. The HUD that shows them is in [ui/hud.md](../ui/hud.md); the "Game over" panel
and its choices in [ui/continue-and-game-over.md](../ui/continue-and-game-over.md).

## Requirements

### GAME-LIFE-01 — Health bar · MUST

Each life is a full health bar: the ship's health ([player-ship.md](player-ship.md)), 100 for the
Balanced ship, the game's one ship. A level starts with the health bar full. Damage never takes the
health below 0.

**Acceptance criteria**
- Given the ship at the start of a level, then its health is 100 of 100 (unit test).

*Sources: GD-20, P02-R01, D-050, D-326.*

### GAME-LIFE-02 — Lives · MUST

The player starts with `lives_start` (3) lives: in the first level played, and after a Continue.
Other levels start with the lives kept from the level completed before (GAME-LIFE-12). More lives
are only collected from life bonuses ([bonuses.md](bonuses.md)), never from the score.

**Acceptance criteria**
- Given a fresh start (nothing kept), then a level starts with 3 lives (unit test).

*Sources: GD-20, D-091, D-154.*

### GAME-LIFE-03 — What hurts, and how much · MUST

| What touches the hitbox | Damage |
|-------------------------|--------|
| an enemy bullet | 10 |
| an enemy missile | 20 |
| an enemy laser beam, while it fires (once per beam; its warning line does not hurt) | 25 |
| an enemy, or a boss's core or any of its parts (collision) | 30 |

**Acceptance criteria**
- Given each kind of hit on a ship that is not invincible, then it loses the damage of the table
  (unit test).
- Given a laser's warning line across the ship, then it loses nothing (unit test).

*Sources: D-050, P07-R06.*

### GAME-LIFE-04 — Touching the hitbox · MUST

Only the ship's hitbox counts ([player-ship.md](player-ship.md) GAME-SHIP-06). A bullet or missile
touches it when their centres are at most `hit_radius` + its radius apart. A firing laser touches
it when the beam, along its length, passes within `hit_radius` + half its width of the ship's
centre. An enemy touches it when its hitbox (for a boss: its core or any part still standing)
overlaps the ship's.

**Acceptance criteria**
- Given a laser beam whose end stops short of the ship, then it does not touch it, even if the
  beam's line would (unit test).
- Given a boss part that is already destroyed over the ship, then it is no collision (unit test).

*Sources: GD-21, D-050, P07-R06.*

### GAME-LIFE-05 — What a hit does to what hit · MUST

When a hit lands: the enemy bullet is gone, the enemy missile blows up, the laser beam hurts the
ship no more, and a rammed enemy takes `ram_damage` (40): enemies with up to 40 health (Hornet,
Scout, Wasp, Strafer, Splitter pods) blow up, tougher ones are hurt. A boss and its parts
take no ramming damage. An enemy destroyed by ramming counts as destroyed: it scores and may drop a
bonus.

**Acceptance criteria**
- Given the ship rams a Hornet (20 health), then the Hornet is destroyed, scores its points and the
  ship takes 30 (unit test).
- Given the ship touches a boss part, then the ship takes the collision damage and the part loses
  no health (unit test).

*Sources: D-050, P07-R06, P11-R01.*

### GAME-LIFE-06 — One hit at a time · MUST

In each simulation step at most one hit lands: the most damaging of everything touching the
hitbox. It then makes the ship invincible (GAME-LIFE-07), so several hits never land together.

**Acceptance criteria**
- Given a bullet and an enemy touching the ship in the same step, then only the collision (30)
  lands, and the bullet is not used up (unit test).

*Sources: D-050.*

### GAME-LIFE-07 — Invincibility after a hit · MUST

After a hit, the ship is invincible for `invincible_time` (2 s) and blinks `blink_rate` (10) times
a second meanwhile. While it is invincible, enemy shots and enemies go through it: nothing hurts
it, and nothing is used up by touching it.

**Acceptance criteria**
- Given a hit, then for 2 s no hit lands (unit test), and the ship is shown and hidden every
  0.05 s.
- Given the 2 s are over, then the next hit lands (unit test).

*Sources: GD-22, D-050.*

### GAME-LIFE-08 — Losing a life · MUST

When the health reaches 0, a life is lost. If the player has lives left, the ship comes back at
once, where it is, with full health, and stays invincible for the rest of its 2 s; the bombs are
topped up ([bombs.md](bombs.md)). A hit shows a small spark where it landed, a lost life a blast on
the ship ([graphics/effects.md](../graphics/effects.md)).

**Acceptance criteria**
- Given 3 lives and 10 health, when a bullet lands, then the player has 2 lives and full health
  (unit test).

*Sources: GD-20, D-050, P11-R05.*

### GAME-LIFE-09 — Game over · MUST

When the last life is lost, the game is over: the ship blows up and is gone (it no longer moves,
shoots, sets bombs off or picks bonuses up), no new wave comes, and the enemies on screen go on.
The "Game over" panel shows `game_over_delay` (2 s) later
([ui/continue-and-game-over.md](../ui/continue-and-game-over.md)).

**Acceptance criteria**
- Given the last life is lost, then the ship cannot move or shoot, and no wave starts (unit test).
- Given the game is over, then the "Game over" panel shows 2 s later.

*Sources: GD-20, D-050.*

### GAME-LIFE-10 — When the ship cannot be hurt · MUST

Besides its invincibility after a hit, the ship cannot be hurt while a bomb is going off
([bombs.md](bombs.md)), nor while it rises into the level or flies off it at the end
([level-flow.md](level-flow.md)). It does not blink then.

**Acceptance criteria**
- Given a bomb going off, when a bullet reaches the ship, then it loses no health (unit test).
- Given the ship rising in at the start of a level, then no hit lands (unit test).

*Sources: P11-R05, D-092.*

### GAME-LIFE-11 — Continue from the checkpoint · MUST

When the game is over after the level's mini boss was destroyed, the player may Continue
([ui/continue-and-game-over.md](../ui/continue-and-game-over.md)). Continue starts the level again
(the scene is built again) from its checkpoint ([level-flow.md](level-flow.md)): just after the
mini boss, the waves before it skipped and the mini boss not coming again, with 3 full lives, 3
bombs, and the weapons and score saved at the checkpoint. Without a checkpoint there is no
Continue. The checkpoint is forgotten when the level is left.

**Acceptance criteria**
- Given the mini boss of 1-2 destroyed, then the game over, when Continue is chosen, then 1-2
  starts again just after its mini boss with 3 lives, 3 bombs and the weapon levels the player had
  when the mini boss was destroyed, and the mini boss does not come again (unit test).
- Given a game over before the mini boss, then there is no Continue.

*Sources: GD-42, P07-R08, D-056, P11-R04, D-154.*

### GAME-LIFE-12 — Lives and bombs kept between levels · MUST

When a level is completed, the lives and bombs the player has left are kept, and the next level
started, whichever it is, starts with them ([level-flow.md](level-flow.md)). A game over keeps
nothing (what was kept before stays). A Continue starts with the starting 3 lives and 3 bombs.
There is no maximum: lives and bombs can pile up from level to level. Kept values that cannot be
read (not a whole number of at least 1 life and 0 bombs) count as none: the starting values.

**Acceptance criteria**
- Given 1-1 completed with 5 lives and 7 bombs, when any level starts, then it has 5 lives and 7
  bombs (unit test on the saved supplies, e2e).
- Given an unreadable saved value, then the level starts with 3 lives and 3 bombs (unit test).

*Sources: D-154.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| lives_start | 3 | `src/game/config/hull.py` `HULL_RULES["lives"]` |
| invincible_time | 2 s | `HULL_RULES["invincibleSeconds"]` |
| hit_radius | 5 px | `HULL_RULES["hitRadius"]` |
| damage | bullet 10, missile 20, laser 25, collision 30 | `HULL_RULES["damage"]` |
| ram_damage | 40 | `HULL_RULES["ramDamage"]` |
| lives maximum | none | `HULL_RULES` sets no `maxLives` (D-154; was 5, P11-R07) |
| blink_rate | 10 per second | `src/config/game_play.py` `GAME_PLAY_CONFIG.damage.blink_hz` |
| hit spark / ship blast | radius 6 / 16 px | `GAME_PLAY_CONFIG.damage.hit_spark`, `.ship_blast` |
| game_over_delay | 2 s | `GAME_PLAY_CONFIG.damage.game_over_delay` |
| saved supplies key | `<game id>_supplies` (cookie) | `src/app/saved_supplies.py` |

## Notes

- D-050 measured (seed 606, Balanced ship, standing still in the middle) that the 3 lives last
  about 60–85 s in World 1; a bot that only weaves and fires finishes 1-1 to 1-3.
