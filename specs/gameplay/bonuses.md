# Bonuses

> **Area:** Gameplay · **Prefix:** `GAME-BONUS` · **Related:** [weapons.md](weapons.md), [lives-and-damage.md](lives-and-damage.md), [bombs.md](bombs.md), [scoring.md](scoring.md), [screen.md](screen.md), [../graphics/effects.md](../graphics/effects.md), [../audio/sfx.md](../audio/sfx.md), [../bosses/common.md](../bosses/common.md), [../enemies/common.md](../enemies/common.md)

Some destroyed enemies and boss parts drop a bonus. It falls down the screen and the ship picks it
up by flying over it. There are three kinds: a weapon bonus raises the weapon in use by a level, a
life bonus adds a life, a bomb bonus adds a bomb. This file gives what drops them, how they fall
and are picked up, and what they give. Their look (one shape per kind) is in
[graphics/effects.md](../graphics/effects.md); their sounds in [audio/sfx.md](../audio/sfx.md).

## Requirements

### GAME-BONUS-01 — Three kinds · MUST

There are three kinds of bonus: **weapon**, **life** and **bomb**. Each looks different from the
others by its shape, not only its colour ([graphics/effects.md](../graphics/effects.md)).

*Sources: GD-20, GD-31, D-049, P11-R07.*

### GAME-BONUS-02 — Weapon bonus chance · MUST

A destroyed enemy drops a weapon bonus with a chance that grows with its toughness:
`weapon_chance_per_health` × its full health, kept within [`weapon_chance_min`,
`weapon_chance_max`] (6 % to 20 %): 6 % for the small kinds of up to 40 health (Gnat, Hornet,
Scout, Strafer, Weaver), a Lancer 12 %, a Rocketeer 15 %, a Bulwark or a Carrier 20 %. The chance
does not depend on the weapon used.

**Acceptance criteria**
- Given enemies of 10, 80 and 300 health, then their chances are 6 %, 12 % and 20 % (unit test).

*Sources: D-049, D-059.*

### GAME-BONUS-03 — Life and bomb bonus chances · MUST

A destroyed enemy may drop a life or a bomb bonus instead of a weapon bonus. Its kind is drawn in
this order: life with `life_chance` (1 %), else bomb with `bomb_chance` (3 %), else the weapon
bonus with its chance (GAME-BONUS-02). A destroyed enemy drops at most one bonus. The life and bomb
draws come from a random source of their own, so the weapon bonuses drop exactly as they would
without them.

**Acceptance criteria**
- Given an enemy whose life draw succeeds, then it drops a life bonus and nothing else (unit test).
- Given the same level played with and without life and bomb bonuses, then the weapon draws are the
  same (unit test).

*Sources: P11-R07, D-091, D-092.*

### GAME-BONUS-04 — Bonuses from bosses · MUST

A destroyed boss part drops a weapon bonus with its own chance, set in its boss's data (by default
50 % for a mini boss's parts, 60 % for a final boss's). A final boss's core always drops a weapon
bonus. A mini boss's core always drops a life bonus where it blew up; like any core it may also
drop a weapon bonus, with the toughness chance of GAME-BONUS-02. Boss parts and cores never draw a
life or bomb bonus; the enemies a boss launches do.

**Acceptance criteria**
- Given a part with a drop chance of 1 destroyed, then a weapon bonus appears where the part was;
  with a chance of 0, none (unit test).
- Given a final boss destroyed, then a weapon bonus appears (unit test).
- Given a mini boss destroyed, then a life bonus appears where its core was (unit test).

*Sources: P07-R07, P11-R07.*

### GAME-BONUS-05 — Deterministic drops · MUST

Drops are drawn from the run's seeded random sources, so the same level played the same way drops
the same bonuses of the same kinds, from the same enemies and parts, in the same order. The bonus
draws do not change the enemies' own random choices.

**Acceptance criteria**
- Given the same level played twice with the same enemies and parts destroyed in the same order,
  then the same bonuses drop (unit test).

*Sources: P07-R07, P11-R07, D-049.*

### GAME-BONUS-06 — Every destruction counts · MUST

An enemy drops its bonus however it was destroyed: by a shot, by a bomb, or rammed by the ship.
Enemies that leave the screen or are removed for age drop nothing.

**Acceptance criteria**
- Given an enemy destroyed by a bomb or by ramming, then it draws its bonus as if it had been shot
  (unit test).

*Sources: D-050, P11-R05.*

### GAME-BONUS-07 — Dropping and falling · MUST

A bonus appears where its enemy or part blew up, moved sideways into the ship's reach if it was
outside it ([screen.md](screen.md) GAME-SCREEN-06). It falls straight down the screen at
`fall_speed` (45 px/s, a little slower than the ground scrolls), so there is time to fly over it.
A bonus not picked up goes past the bottom edge and is removed (GAME-SCREEN-07).

**Acceptance criteria**
- Given a bonus dropped at x = 1 200, then it falls at the right end of the ship's reach (unit test).
- Given 2 s, then a bonus has fallen 90 px (unit test).

*Sources: D-049, P07-R07.*

### GAME-BONUS-08 — Picking up · MUST

The ship picks a bonus up when its centre comes within `pickup_radius` (22 px) of the bonus's
centre (more forgiving than the hitbox). Once the game is over, nothing is picked up.

**Acceptance criteria**
- Given the ship 20 px from a bonus, then it picks it up (unit test).
- Given the game is over, when a bonus falls through the ship's last position, then it is not
  picked up (unit test).

*Sources: D-049.*

### GAME-BONUS-09 — What a bonus gives · MUST

- A weapon bonus raises the weapon in use by one level, up to level 5 ([weapons.md](weapons.md)
  GAME-WPN-14).
- A life bonus adds one life ([lives-and-damage.md](lives-and-damage.md)).
- A bomb bonus adds one bomb ([bombs.md](bombs.md)).

Lives and bombs have no maximum, so a life or bomb bonus always adds one.

**Acceptance criteria**
- Given 2 lives, when a life bonus is picked up, then the player has 3 (unit test).
- Given 6 lives, when a life bonus is picked up, then the player has 7 (unit test).

*Sources: GD-20, GD-31, P11-R07, D-049, D-154.*

### GAME-BONUS-10 — Points at the most · MAY

If a game sets a maximum of lives or bombs, a life or bomb bonus picked up at the maximum scores
`overflow_points` instead (life 5 000, bomb 2 000). This game sets no maximum (GAME-BONUS-09), so it
does not happen in play.

**Acceptance criteria**
- Given rules with a maximum of 5 lives and 5 lives held, when a life bonus is picked up, then the
  lives stay 5 and the score rises by 5 000 (unit test).

*Sources: P11-R07, D-154.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| weapon_chance_per_health | 0.0015 per health point | `src/game/config/bonuses.py` `BONUS_RULES["chance"]["perHealth"]` |
| weapon_chance_min / max | 6 % / 20 % | `BONUS_RULES["chance"]["min"]`, `["max"]` |
| life_chance / bomb_chance | 1 % / 3 % | `BONUS_RULES["special"]` |
| part drop chance | 50 % (mini boss parts), 60 % (final boss parts) | `src/game/config/bosses/boss_kit.py` `part` (`dropChance` default 0.5), `final_bosses.py` `fpart` (0.6); per part in each boss's data |
| final boss core drop | 100 % | `coreDrop` 1 in each final boss's data |
| fall_speed | 45 px/s | `BONUS_RULES["fallSpeed"]` |
| pickup_radius | 22 px | `BONUS_RULES["pickupRadius"]` |
| overflow_points | life 5 000, bomb 2 000 | `src/game/config/scoring.py` `SCORING["overflow"]` (unused while there is no maximum) |
| random sources | the run's seed + 1 (weapon draws), + 2 (life and bomb draws) | `src/core/systems/level_run.py` `_player_systems` |

## Notes

- D-092 measured that a player shooting most enemies gets 2–9 life and 8–12 bomb bonuses per World
  1 level, more than the first estimate of about one extra life per level; the chances are
  tunables.
