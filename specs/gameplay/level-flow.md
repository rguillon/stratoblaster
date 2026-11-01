# Level flow

> **Area:** Gameplay · **Prefix:** `GAME-LEVEL` · **Related:** [screen.md](screen.md), [weapons.md](weapons.md), [lives-and-damage.md](lives-and-damage.md), [scoring.md](scoring.md), [../bosses/common.md](../bosses/common.md), [../enemies/common.md](../enemies/common.md), [../worlds/world-1/world.md](../worlds/world-1/world.md), [../ui/continue-and-game-over.md](../ui/continue-and-game-over.md), [../audio/music.md](../audio/music.md), [../dev/debug-options.md](../dev/debug-options.md)

How a level runs, the same for every level: the ship rises in, the ground scrolls at the level's
speed, waves of enemies come in by distance, a mini boss in the middle saves a checkpoint, a final
boss ends the level, and the ship flies off the top before the "Level complete" panel. This file
gives those rules. What each level holds (its scenery, ground speed, length, waves, bosses and
difficulty) is in its file under [worlds/](../worlds/world-1/world.md); how a boss fights in
[bosses/](../bosses/common.md).

## Requirements

### GAME-LEVEL-01 — Waves by distance · MUST

Each level has a wave script: a list of waves, each triggered by how far the level has got (its
progress), never by time. A wave gives the enemy kind, how many groups come (`count`), where they
come in (a side and a position across it, 0 to 1, optionally shifted for each group by `spread`)
and the delay between groups (`interval`). When the level passes a wave's distance, its groups are
queued one `interval` apart and come in on time, so several waves can be on screen at once. The
waves of each level are written in seconds at its ground speed in its file
([worlds/](../worlds/world-1/world.md)) and turned into distances. The engine runs wave scripts
knowing the enemy kinds only by their ids, and refuses a wave of an unknown kind or with impossible
numbers.

**Acceptance criteria**
- Given a wave at a distance, when the level passes it, then its enemies come in, and not before
  (unit test).
- Given the same level played twice, then the waves come at the same distances (unit test).

*Sources: GD-40, P06-R02, P06-R07, D-036.*

### GAME-LEVEL-02 — Ground speed per level · MUST

Each level has its own ground speed (from 55 to 70 px/s today; the first level of each world is
the fastest), given in its file. Outside the boss fights (GAME-LEVEL-07), the ground scrolls at that speed for the whole
level.

**Acceptance criteria**
- Given a level of ground speed 65 px/s, when 10 s pass without a fight, then the ground and the
  level's progress have moved 650 px (unit test).

*Sources: GD-01, P06-R04.*

### GAME-LEVEL-03 — Level length · MUST

A level's length is set as a scroll time at its ground speed (240 s in World 1, 300 s in Worlds 2
to 4, in the world files). The boss fights add to the time played: the scroll time does not count
them.

**Acceptance criteria**
- Given each level, then its length divided by its ground speed is its world's scroll time (unit
  test, in the world tests).

*Sources: P06-R04, P07-R06.*

### GAME-LEVEL-04 — A mini boss and a final boss · MUST

Each level has one mini boss and one final boss. The mini boss arrives when the level's progress
reaches `mini_boss_at` (half its length); the final boss when it reaches the end.

**Acceptance criteria**
- Given a level, when its progress reaches half its length, then its mini boss arrives; at its
  end, its final boss (unit test).

*Sources: GD-41, P07-R06.*

### GAME-LEVEL-05 — A quiet stretch before each boss · MUST

No new wave starts in the `quiet_before_boss` (10 s, at the level's ground speed) before each boss,
so the screen clears before it arrives.

**Acceptance criteria**
- Given each level's wave script, then no wave is triggered in the 10 s before either boss (unit
  test).

*Sources: P07-R06.*

### GAME-LEVEL-06 — No waves during a fight · MUST

From a boss's arrival until it is destroyed (its death blasts included), the level's progress
waits and no new wave starts. The enemies already on screen carry on, and the enemies the boss
launches come. After the fight, the level goes on from where the boss came, so no wave is skipped
or squeezed by a fight.

**Acceptance criteria**
- Given a boss is alive, then no new wave starts (unit test).
- Given a fight that lasts 60 s, then the waves after the boss come at the same progress as without
  the fight (unit test).

*Sources: P07-R03, P07-R06, D-054.*

### GAME-LEVEL-07 — Ground speed during a fight · MUST

When a boss arrives, the ground speed eases over `boss_speed_ease` (2 s, smoothly) from the
level's speed to the boss's fight ground speed: a factor of the level's speed, from ×0 (stopped)
to ×1.5 (a chase), set per boss ([bosses/](../bosses/common.md)). It stays so for as long as the
boss is alive, however long that is, and eases back to the level's speed over 2 s once the boss is
destroyed. The ground (scenery) and the level's progress (waves, bosses, end, the HUD's progress)
are kept apart: during a fight the ground moves on while the progress waits.

**Acceptance criteria**
- Given a boss with a factor of 0.5 arriving in a level scrolling at 60 px/s, then 2 s later the
  ground scrolls at 30 px/s, and stays so until the boss is destroyed (unit test).
- Given the boss destroyed, then the ground is back to 60 px/s 2 s later (unit test).

**Discrepancy:** after the final boss the ground does not ease back: the level's progress is at its
end and no longer held, so the ground stops at once when the final boss is gone, while the ship
flies its free seconds and leaves (`ScrollTrack.step` caps the run at the end unless held).

*Sources: P07-R03, D-054.*

### GAME-LEVEL-08 — The ground never runs out · MUST

However long a fight lasts, the scenery goes on with no gap or edge, also past the level's end
during the final fight: each level draws `runout` seconds (at its speed) of its last section's
ground past its end, sized for a long fight; past that, the terrain still goes on, without props.
Because the ground moves on during fights while the progress waits, the scenery gets ahead of the
level by about each fight's time × its factor.

**Acceptance criteria**
- Given a final boss fight that lasts 5 minutes (the boss not shot), then the ground keeps
  scrolling at the fight speed with no gap or edge in the scenery.

*Sources: P07-R03, D-054.*

### GAME-LEVEL-09 — The checkpoint · MUST

Destroying the level's mini boss saves a checkpoint: the level's progress at the mini boss, the
bosses passed, the player's weapons and their levels, and the score at that moment. A game over
after it can be continued from there ([lives-and-damage.md](lives-and-damage.md) GAME-LIFE-11).
The checkpoint is forgotten when the level is left; a new attempt from the level select has none.
A "checkpoint reached" jingle plays ([audio/music.md](../audio/music.md)).

**Acceptance criteria**
- Given the mini boss destroyed, then the checkpoint holds its progress, one boss passed, the
  weapons and the score (unit test).
- Given the level left and started again from the level select, then it has no checkpoint.

*Sources: GD-42, P07-R08, D-056, P11-R04.*

### GAME-LEVEL-10 — Level end · MUST

A level with a final boss ends when that boss is destroyed (after its death blasts); a level
without one ends when its scroll reaches its length. From then on no group of enemies comes in,
not even the rest of a wave already started. The bosses, and the enemies they and other enemies
launch, count among the enemies spawned and destroyed.

**Acceptance criteria**
- Given the final boss destroyed, then the level is cleared, and not before (unit test).
- Given a level without a boss whose scroll ends, then no enemy spawns after that point (unit
  test).

*Sources: P06-R03, P07-R06.*

### GAME-LEVEL-11 — The ship rises into the level · MUST

At the start of a level, the ship rises from `journey_below` (160 px) under the bottom of its
flight area to its start position ([player-ship.md](player-ship.md) GAME-SHIP-07) in
`journey_arrive` (1.6 s), slowing down as it arrives. Meanwhile the game flies it: the player
cannot move it, shoot, switch weapon or set a bomb off, and it cannot be hurt. A level started at a
given time or boss (debug options), or seeking in it, puts the ship at its start at once.

**Acceptance criteria**
- Given a level starts, then the ship is below the screen, reaches its start after 1.6 s, and only
  then answers the controls (unit test).

*Sources: reviewer request 2026-10-28 (no old ID; commit 98a3bf9).*

### GAME-LEVEL-12 — The ship flies off the top · MUST

Once the level is cleared (GAME-LEVEL-10), the player keeps the ship for `journey_free` (3 s): it
still flies, shoots and can be hit. Then, once the enemies left are gone or `level_end_wait`
(10 s) after the level was cleared, the game flies it off the top of the screen: from
`journey_leave_speed` (120 px/s, or the ship's own speed up if faster), speeding up at 900 px/s²,
its sideways drift dying out, and it cannot be hurt. The level is complete once the ship is
`journey_above` (120 px) past the top; the "Level complete" panel then shows
([ui/continue-and-game-over.md](../ui/continue-and-game-over.md)).

**Acceptance criteria**
- Given the final boss destroyed with no enemy left, then the ship flies off the top 3 s later and
  the level completes once it is gone (unit test).
- Given enemies still on screen, then the ship waits for them to go, at most 10 s from the level's
  clearing (unit test).

*Sources: P06-R03, P07-R06, reviewer request 2026-10-28 (no old ID; commit 98a3bf9).*

### GAME-LEVEL-13 — What a level ends with · MUST

A level ends either complete or over (the game is over, [lives-and-damage.md](lives-and-damage.md)).
Its result gives the level, the enemies destroyed out of those spawned, the outcome, the score,
and, for a game over after the mini boss, the checkpoint. The end-of-level panels show it
([ui/continue-and-game-over.md](../ui/continue-and-game-over.md)).

**Acceptance criteria**
- Given level 1-2 completed, then its result names `1-2`, its destroyed / spawned counts and its
  score (unit test).

*Sources: P06-R03, D-050, D-056.*

### GAME-LEVEL-14 — What carries over to the next level · MUST

When a level is completed, the player's weapons and their levels ([weapons.md](weapons.md)
GAME-WPN-15) and their lives and bombs ([lives-and-damage.md](lives-and-damage.md) GAME-LIFE-12)
are kept, in cookies, and the next level started from the level select, whichever it is, starts
with them. A game over, or leaving a level, keeps nothing new. The score and the checkpoint never
carry over: each attempt scores on its own ([scoring.md](scoring.md)).

**Acceptance criteria**
- Given 1-1 completed, when 1-4 is started, then it starts with the weapons, lives and bombs 1-1
  ended with (e2e).
- Given a game over in 1-2, when 1-2 is started again, then it starts with what 1-1 ended with.

*Sources: D-071, D-154, D-091.*

### GAME-LEVEL-15 — A run is deterministic · MUST

A level run is pure and deterministic: it depends only on its data, its seed (`run_seed`, the same
for every level) and the controls of each step, so the same level played the same way plays the
same, whatever the frame rate. It is stepped at a fixed rate (`step_rate`, 60 Hz, ENG-100), at most
`max_steps` steps a frame, with frame times capped at 0.1 s so a stall does not jump the game; the
drawing interpolates between steps.

**Acceptance criteria**
- Given the same level run twice with the same controls, then the enemies, shots and score are the
  same at every step (unit test).

*Sources: D-036, P06-R07.*

### GAME-LEVEL-16 — Levels are data · SHOULD

A playable level is data assembled by the game (its scenery, wave script, difficulty factors,
bosses and their distances, runout); the engine's level run knows neither the enemy kinds nor the
bosses by name (`01-engineering.md` §2.3).

*Sources: D-036.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground speed | per level, 55–70 px/s | each level's scenery data (`scrollSpeed`), see [worlds/](../worlds/world-1/world.md) |
| scroll time | 240 s (World 1), 300 s (Worlds 2–4) | each level's scenery sections |
| mini_boss_at | 50 % of the level's length | `src/game/config/world_1/bosses.py` `MINI_BOSS_AT` (used by every world, `src/game/sim/assemble_level.py`) |
| quiet_before_boss | 10 s | `src/game/config/world_1/bosses.py` `QUIET_BEFORE_BOSS` |
| boss_speed_ease | 2 s | `src/game/config/boss_fights.py` `BOSS_FIGHT_RULES["speedEaseSeconds"]` |
| fight ground speed | ×0 to ×1.5, per boss | each boss's `groundSpeed` |
| runout | per level, 30–160 s | `src/game/config/world_*/bosses.py` `runout` |
| journey_arrive / journey_below | 1.6 s / 160 px | `src/config/game_play.py` `GAME_PLAY_CONFIG.journey` |
| journey_free | 3 s | same |
| journey_leave_speed / acceleration / journey_above | 120 px/s / 900 px/s² / 120 px | same |
| level_end_wait | 10 s | `GAME_PLAY_CONFIG.end_wait` |
| run_seed | 606 | `GAME_PLAY_CONFIG.seed` |
| step_rate / max_steps | 60 Hz / 25 steps a frame | `GAME_PLAY_CONFIG.step_hz`, `.max_steps_per_frame` |
| frame time cap | 0.1 s | `src/config/menu.py` `MENU_CONFIG.max_frame_seconds` |

## Notes

- The ship's arrival and departure were added at the reviewer's request on 2026-10-28 (phase 15
  work) without a requirement or a decision; GAME-LEVEL-11 and GAME-LEVEL-12 record them.
- Before the bosses (phase 7), a level ended at the end of its scroll, once the last enemies were
  gone or after 10 s (P06-R03); GAME-LEVEL-10 keeps that rule for a level without a final boss.
