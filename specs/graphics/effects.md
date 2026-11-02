# Effects

> **Area:** Graphics · **Prefix:** `GFX-FX` · **Related:** [shots.md](shots.md), [readability.md](readability.md), [art-direction.md](art-direction.md), [../gameplay/bombs.md](../gameplay/bombs.md), [../gameplay/bonuses.md](../gameplay/bonuses.md), [../gameplay/lives-and-damage.md](../gameplay/lives-and-damage.md), [../bosses/common.md](../bosses/common.md), [../audio/sfx.md](../audio/sfx.md)

The visual effects of the playfield: the sparks and glows where shots hit, the explosions where
ships blow up (fireballs, smoke, burning debris, embers), the bomb's shockwave and the bonuses'
look. They are generated in code, short and capped so they never hide the ship or the enemy
bullets for long ([GFX-READ](readability.md)). What a bomb or a bonus does is in
[GAME-BOMB](../gameplay/bombs.md) and [GAME-BONUS](../gameplay/bonuses.md); a boss part's hit flash
and smoke are in [BOSS](../bosses/common.md); the sounds in [AUD-SFX](../audio/sfx.md).

## Requirements

### GFX-FX-01 — Every hit on a ship shows · MUST

Every time a projectile hits a ship, a particle effect shows where it hit: a burst of metal sparks
for a player bullet (GFX-FX-02), a cyan blast for a player missile (GFX-FX-03), a glow where the
laser touches (GFX-SHOT-03), and a small spark for an enemy shot hitting the player (GFX-FX-04).

**Acceptance criteria**
- Given a player bullet hitting an enemy, then sparks fly where it hit (unit test).
- Given an enemy bullet hitting the player, then a spark shows where it landed (unit test).

*Sources: GD-62, P03-R01, P03-R03.*

### GFX-FX-02 — Bullet hits throw metal sparks · MUST

A bullet hit throws a burst of sparkling metal sparks back from the hit and to the sides: thin
streaks along their motion, white-hot to ice blue, that slow down with drag, twinkle and shrink away
within their life. Each spark is a diamond of few triangles.

**Acceptance criteria**
- Given a hit, then `count` sparks start there and fly back within `spreadDeg` of straight back
  (unit tests).
- Given a spark over its life, then it slows, fades and shrinks, and is removed after it (unit
  tests).
- Given the spark colours, then they are in the player family (no gold or orange).

*Sources: P03-R01, P14-R02.*

### GFX-FX-03 — Missile impact blast · MUST

Where a player missile hits, a cyan glowing disc of `radiusFactor` times the missile's blast radius
swells and fades over `duration`, in the player family.

**Acceptance criteria**
- Given a missile impact, then a disc grows there and is gone after `duration` (unit tests).

*Sources: P03-R03, P14-R02.*

### GFX-FX-04 — Hits on the player · MUST

When an enemy shot or an enemy reaches the player ship, a small spark blast shows where it landed
(a missile-sized blast of radius `hit_spark`); when the hit costs a life, a blast of radius
`ship_blast` shows on the ship instead.

**Acceptance criteria**
- Given a hit that landed, then one small blast shows where it landed; given a hit that cost a
  life, one blast shows on the ship (unit tests).

*Sources: GD-62, D-050.*

### GFX-FX-05 — Ships explode in layers · MUST

When an enemy, a boss part, a boss or an enemy missile is destroyed, it explodes where it was: a
thin shock ring that races out and fades; fireballs, the first at the centre at once and the others
round it a little later, swelling as they cool from white-hot through yellow, orange and deep red to
brown, laid over the ground (not added on, which turns flat white over bright ground), opaque at
first, then fading; dark smoke left behind each fireball, lit by the fire at first, then grey;
burning debris thrown out, slowing down, trailing embers and smoke wisps while it is hot; and
embers that cool fast.

**Acceptance criteria**
- Given an enemy blast, then it throws a ring, fireballs, debris and embers (unit test).
- Given a fireball over its life, then it cools from white-hot to deep red and fades after its
  opaque share (unit tests).
- Given burning debris, then it drops embers while hot and nothing once burnt out (unit tests).

*Sources: GD-62.*

### GFX-FX-06 — Explosion size follows what blew up · MUST

An explosion is sized from the hit radius of what blew up: a big ship makes a big blast, a tiny one
a small blast with fewer fireballs, pieces and embers, and smaller pieces under `fullRadius`. A
missile blows up smaller (`missileScale`) with fewer particles. No blast is drawn bigger than for a
hit radius of `maxRadius`, so one covers at most the screen share of GFX-READ-15.

**Acceptance criteria**
- Given a missile blast, then it is smaller and throws fewer pieces than an enemy blast (unit
  test).
- Given a blast bigger than `maxRadius`, then it is drawn as one of `maxRadius` (unit test).

*Sources: GD-62, P14-R07, D-124.*

### GFX-FX-07 — No flash in the explosions · MUST

Explosions start with no white flash. Their shock ring is laid over the ground rather than added to
it, so a blast does not light up the ground under it.

**Acceptance criteria**
- Given the explosion layers, then they are smoke, rings, fireballs, debris and embers, with no
  flash layer (unit test); the ring layer is blended, not added on.

*Sources: D-133.*

### GFX-FX-08 — Explosions are over fast · MUST

Every particle of an explosion, smoke and embers included, is gone within `effectMaxDuration` of the
blast.

**Acceptance criteria**
- Given the longest-lived blast, when it is simulated, then no particle is left after
  `effectMaxDuration`.

**Gap:** this duration is not checked by a unit test since the Python port (the particle lives in
the config add up to about 0.58 s).

*Sources: P14-R07, D-124.*

### GFX-FX-09 — Particles drawn as thin instances · SHOULD

Each explosion layer is one mesh of thin instances with a matrix and a colour per particle, so any
number of explosions costs one draw per layer. The buffers grow by powers of two and are refilled
each frame, the instance count set before the upload (so new particles never show for a frame where
old ones were). Each layer holds at most `cap` particles; new ones are dropped beyond. The layers
are never culled; smoke is drawn under the fire. The particle simulation is plain, seeded and
unit-tested, apart from the drawing. An effect drawn this way is either added on or kept out of the
glow layer.

**Acceptance criteria**
- Given a layer at its cap, when a particle is added, then it is dropped (unit test).
- Given the same blasts and seed, then the particles are the same.

*Sources: D-034.*

### GFX-FX-10 — The bomb's shockwave · MUST

A bomb going off shows a cyan shockwave ring growing from where the ship was, fast then slowing,
until it covers the whole playfield at the end of the bomb, fading as it goes, and a short, dim warm
flash at the ship that fades within `flash.seconds`. There is one flash per bomb (never 3 flashes a
second). Both are drawn in front of the ships and the explosions, under the enemy shots, and the
flash is dim enough that the ship and the surviving enemy bullets stay visible through it.

**Acceptance criteria**
- Given a bomb, then its ring grows from where the ship was, fast then slowing, and fades as the
  bomb ages; its flash is full at once and gone after `flash.seconds` (unit tests).
- Given no bomb, then neither the ring nor the flash shows (unit test).

*Sources: P11-R05, P14-R07, D-124.*

### GFX-FX-11 — How a bonus looks · MUST

A bonus is a badge, `size` px in radius, that swings about its upright axis from side to side (never
a whole spin, which would show it edge-on half the time) over a pulsing halo. It is unlit and drawn
in its own colours, so it glows; it is drawn in front of the ships and the explosions. Every bonus is
in the pickup family, a blue violet that does not read pink.

**Acceptance criteria**
- Given a bonus, then its badge swings and its halo pulses as the bonus ages (unit test).
- Given every saturated bonus colour, then it is in the pickup family (unit test).

*Sources: P11-R07, D-049, D-231.*

### GFX-FX-12 — One shape per bonus kind · MUST

The kinds are told apart by shape, not colour: a weapon bonus is a hexagon badge with a violet
frame, a dark face and two light violet chevrons pointing up (a level up); a life bonus is a heart
in a violet rim; a bomb bonus is a violet ball with a highlight, marked `B`.

**Acceptance criteria**
- Given the three kinds, then each is drawn with its own badge and halo (unit tests).

*Sources: P11-R07, D-049, D-231.*

### GFX-FX-13 — Pickup flash · MUST

Where the ship picks a bonus up, a violet ring flashes out, growing to `flash.size` times the badge
and fading over `flash.life`.

**Acceptance criteria**
- Given a pickup, then a ring starts there, grows and fades, and is gone after `flash.life` (unit
  tests).

*Sources: D-049, D-231.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Bullet sparks | 14 sparks, 120–380 px/s, ±80°, drag 7/s, life 0.18–0.4 s, 8–16 × 2.4 px, twinkle ±0.45 at 18–34 Hz, 4 sides | `src/game/config/shot_look.py` `SHOT_LOOK["impact"]["bullet"]` |
| Missile impact | 1.6 × blast radius, 0.3 s | `SHOT_LOOK["impact"]["missile"]` |
| `hit_spark` / `ship_blast` | 6 / 16 px | `src/config/game_play.py` `ShipDamage(10, 6, 16, 2)` |
| `missileScale` | 0.6 | `src/game/config/enemy_look.py` `ENEMY_LOOK["blasts"]` |
| `maxRadius` | 22 px | `ENEMY_LOOK["blasts"]` |
| `fullRadius` | 16 px | `ENEMY_LOOK["blasts"]` |
| Fire colours | [1, 0.97, 0.88] → [1, 0.8, 0.4] → [1, 0.45, 0.1] → [0.65, 0.14, 0.03] | `ENEMY_LOOK["blasts"]["heat"]` |
| Shock ring | 4 × radius, 0.35 s | `ENEMY_LOOK["blasts"]["ring"]` |
| Fireballs | 2–14, size 1.2–2 × radius, growth 1.5, life 0.3–0.45 s, delay ≤ 0.12 s, opaque 0.45 of life | `ENEMY_LOOK["blasts"]["fireball"]` |
| Smoke | size 1–1.6 × radius, life 0.2–0.3 s, alpha 0.55 | `ENEMY_LOOK["blasts"]["smoke"]` |
| Debris | 4–36 pieces, 80–240 px/s, 2.6–5 px, life 0.3–0.4 s; an ember every 0.025 s, a wisp every 0.09 s | `ENEMY_LOOK["blasts"]["debris"]` |
| Embers | 5–40, 60–220 px/s, 1–2 px, life 0.12–0.25 s | `ENEMY_LOOK["blasts"]["embers"]` |
| `cap` | 1200 particles per layer | `ENEMY_LOOK["blasts"]` |
| Bomb wave | radius 900 px (820 until D-249 and from D-252 to D-253, 1 000 on the whole 16:9 screen between), cyan rim, 48 sides | `src/game/config/bomb_look.py` `BOMB_LOOK["wave"]` |
| Bomb flash | radius 320 px, 0.3 s, heart [0.4, 0.34, 0.22] | `BOMB_LOOK["flash"]` |
| Bomb duration | 1 s | `src/game/config/bombs.py` |
| Bonus `size` | 11 px | `src/game/config/bonus_look.py` `BONUS_LOOK` |
| Bonus swing | ±0.9 rad at 0.7 Hz | `BONUS_LOOK["swing"]` |
| Bonus halo | 1.7 × size, ±0.2 at 2.5 Hz | `BONUS_LOOK["halo"]` |
| Bonus colours | frame [0.55, 0.3, 1], face [0.06, 0.04, 0.1], chevrons [0.75, 0.6, 1]; heart, bomb ball | `BONUS_LOOK` |
| Pickup flash | 4 × size, 0.35 s, [0.7, 0.5, 1] | `BONUS_LOOK["flash"]` |

## Notes

- History of the explosions: one orange disc (phase 5), then six layers with a white flash, bigger
  and with burning debris (phase 5 review), no minimum size for tiny ships (phase 5 review), capped
  and shortened (phase 14, D-124), and the flash removed (D-133).
- History of the bonus colours: acid yellow badge with cyan chevrons, pink heart, orange ball (phase
  6 and P11-R07), all green (phase 14), all violet (D-231).
