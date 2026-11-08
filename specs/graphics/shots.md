# Shots

> **Area:** Graphics · **Prefix:** `GFX-SHOT` · **Related:** [../gameplay/weapons.md](../gameplay/weapons.md), [readability.md](readability.md), [effects.md](effects.md), [art-direction.md](art-direction.md), [player-ships.md](player-ships.md), [../enemies/common.md](../enemies/common.md), [../bosses/common.md](../bosses/common.md)

How the shots look and where they are seen leaving from: the player's minigun tracers, laser and
missiles, and the enemies' bullets, missiles and lasers. What the shots do (streams, damage,
speeds, homing, piercing) is in [GAME-WPN](../gameplay/weapons.md) and the enemy and boss files;
the hits and explosions they cause are in [GFX-FX](effects.md); the colour, size and draw-order
rules they follow are in [GFX-READ](readability.md). Shots are flat, unlit, vertex-coloured meshes
on the playfield; the player's are added on (black is transparent).

## Requirements

### GFX-SHOT-01 — Minigun tracer · MUST

A player bullet is a minigun tracer: a thin streak, white-hot on its centre line at its head,
cooling to cyan then deep blue along its tail and fading out, with a short rounded tip ahead of the
bullet. A new tracer grows out of the muzzle to its full length as it flies, then keeps it; its
width flickers. It is in the player family, never orange or red (the enemy shots' colours).

**Acceptance criteria**
- Given a bullet just fired, then its streak grows from the muzzle; given an old one, it has the
  look's length (unit tests).
- Given the tracer colours, then they are white, cyan and deep blue, in the player family.

*Sources: P03-R01, P14-R02.*

### GFX-SHOT-02 — Bullets leave from inside the ship · MUST

Bullets are seen leaving from under the ship: they start `launchBack` behind the muzzle (16 px below
the nose tip, inside the hull), and their tracers are drawn `bullet.depth` units behind the
playfield plane, so the ship is drawn over them as they leave. The laser does not move: it still
starts at the nose (GFX-SHOT-05).

**Acceptance criteria**
- Given a bullet fired, then it starts `launchBack` behind the muzzle and is drawn under the ship.

*Sources: D-106, P03-R01.*

### GFX-SHOT-03 — Laser beam · MUST

The laser is an intense blue beam: near white on its centre line to deep blue at its edges. It is
drawn as if `widthBonus` px wider than its hit width (so level 1 looks like the first text's level
5), times `glowWidth`, its width flickering; its base and contact glows and its particles use the
same drawn width. Each segment of a piercing beam is its own
bar, thinner at each lower level. Bright blue particles flow up along the beam, spread over its
width, starting again from its base as they reach its end. A glow shows where the beam stops on a
target.

**Acceptance criteria**
- Given a beam of several segments, then one bar is drawn per segment, from its start to its end
  (unit test).
- Given a beam stopped on a target, then a contact glow shows there; given no target, none (unit
  tests).
- Given a beam, then its particles are small discs along it (unit test).

*Sources: P03-R02.*

### GFX-SHOT-04 — Laser base glow · MUST

A pulsing blue glow shows where the beam leaves the ship, bigger at higher levels (its radius grows
with the beam width), stretched along the beam. It is round and smooth: a disc of many sides and
rings with a soft, roughly exponential falloff.

**Acceptance criteria**
- Given a beam, then a glow is drawn at its base; given no beam, none (unit tests).
- Given the base glow, then it has 24 sides and 6 colour rings.

*Sources: P03-R02.*

### GFX-SHOT-05 — The muzzle at each ship's nose · MUST

Each ship's muzzle is `muzzle_inset` below the tip of its nose, measured on the ship's model, not at
a fixed height. The laser and its base glow start there; the bullets start `launchBack` behind it
(GFX-SHOT-02).

**Acceptance criteria**
- Given each ship, then its laser and its base glow start `muzzle_inset` below the highest point of
  its model.

*Sources: P03-R01, P03-R02.*

### GFX-SHOT-06 — Missile model · MUST

A player missile is a small missile: a light grey tube, a glowing cyan nose and two crossed fins at
its tail, with the player ships' blue reactor flame behind it (GFX-SHIP-06), turned along its
heading. It is big enough to see on any ground (about 15 px long).

**Acceptance criteria**
- Given a missile model, then it has a tube, a nose and two crossed fins, its body along its
  heading, nose first (unit tests).

*Sources: P03-R03, P14-R02.*

### GFX-SHOT-07 — Missile flare and trail · MUST

Each missile has a bright, flickering motor flare at its nozzle and a glowing exhaust trail behind
it that grows from the launch point like a tracer, both added on, white to blue, so it shows on any
ground.

**Acceptance criteria**
- Given a flying missile, then a flare is drawn at its nozzle and a trail behind it, the trail no
  longer than its look's length (unit tests).

*Sources: P03-R03.*

### GFX-SHOT-08 — Missiles leave from under the ship's centre · MUST

Missiles launch from the centre of the ship and are drawn `missile.depth` units behind the
playfield plane, so the ship stays on top and covers them as they leave.

**Acceptance criteria**
- Given a missile fired, then it starts at the ship's centre and is drawn under the ship.

*Sources: P03-R03.*

### GFX-SHOT-09 — Enemy shots leave from the barrels, as the camera sees them · MUST

An enemy's or boss's shots start where the player sees its gun's barrel tip. A gun's muzzles are
offsets from the enemy's centre (as seen facing down the screen) plus a height; they are game data
copied from the barrel tips its model marks, and a unit test keeps the two equal. A shot leaves from
the muzzle furthest along its way (side-by-side muzzles take turns), turned with the enemy's
heading, a boss's roll and an orbiting part's spin, then projected along the camera's line of sight
onto the playfield; aimed shots are aimed from that point. A laser projects its emitter the same
way at every step. Launches (hangars, drone bays) start at their part's centre.

**Acceptance criteria**
- Given a raised muzzle, then its shot starts on the playfield where the camera sees the muzzle
  (unit test).
- Given two side-by-side muzzles, then they fire in turn; given an aimed shot, it is aimed from the
  muzzle (unit tests).

*Sources: D-057.*

### GFX-SHOT-10 — Enemy bullets are balls of plasma · MUST

An enemy bullet is a ball of energy, back to front: a faint flickering aura, a deep-coloured body
blended over the ground (so its colour holds over bright snow) whose border fades out, two curled
swirls of brighter plasma spinning opposite ways, a pulsing white-hot core, and the white spark of
GFX-READ-11. It is drawn `bullets.scale` times its hit radius (never under GFX-READ-10's minimum).
Each bullet starts its swirls turned by its heading, so a ring of bullets does not spin as one. The
pulse is a change of size of a small glow, not a flash.

**Acceptance criteria**
- Given a bullet, then its aura flickers and its core pulses round their sizes at their rates, and
  its swirls turn with its heading and age (unit tests).
- Given a bullet over snow, then its colour still shows (manual).

*Sources: D-069, D-074, GD-43.*

### GFX-SHOT-11 — Bullet styles in the warm family · MUST

The enemy bullet styles keep their names (red, magenta, green, orange, blue, purple), which the
enemy specs use, but every one is drawn in the enemy-shot family: a white-hot core round an orange
to amber colour, none yellow.

**Acceptance criteria**
- Given every bullet style, then its colour is in the enemy-shot family (unit test).

*Sources: P14-R02, D-231, GD-43.*

### GFX-SHOT-12 — No dark ring round the enemy bullets · MUST

No dark disc, rim or ring is drawn behind or round an enemy bullet.

**Acceptance criteria**
- Given the layers of an enemy bullet, then none is dark: the aura, body, swirls, core and spark
  only.

*Sources: D-194, P14-R05, P10-R07.*

### GFX-SHOT-13 — Bullets cost a fixed number of draws · SHOULD

Each layer of each bullet colour is one mesh of thin instances, a matrix per bullet, so all the
bullets on screen cost at most one draw per layer and colour (6 layers × 6 colours) however many
fly. A bullet has no node of its own.

**Acceptance criteria**
- Given many bullets of one colour, then each of its layers is drawn by one mesh.

*Sources: D-074.*

### GFX-SHOT-14 — Shells · MUST

A bursting shot (the Mortar's shell; the mine of the removed Minelayer is gone) is drawn as a ball
of plasma of its style, as a bullet, bigger: its hit radius (7 px for the shell, 4 px for a plain
bullet) sets its size. The bullets it bursts into are plain bullets.

**Acceptance criteria**
- Given a shell, then it is drawn as a plasma ball larger than a plain bullet of its
  style.

*Sources: P05-R15, P05-R18, D-074.*

### GFX-SHOT-15 — Enemy missiles · MUST

An enemy missile (one the player can shoot down) is a small dark six-sided body with a self-lit
orange tip, pointing along its heading (and tilted by its pitch while it lofts, WPN-09), the enemy
ships' animated reactor flame (in orange) at its tail, and an orange rim round its body (Babylon's
outline renderer, about 1 px wide), so it shows over blasts and bright ground and is not taken for a
bullet. Missiles keep this rim; the ships' edge trim is not used on shots. Their flames are drawn
over the player's shots and the explosions, under the bullets. It leaves a light grey smoke trail:
small puffs left behind its tail at its height, growing and fading out in about half a second (the
game's seeded particles drawn as thin instances, as the explosions' smoke).

**Acceptance criteria**
- Given an enemy missile, then it has a dark body, an orange tip, a reactor flame and an orange rim,
  turned along its heading.
- Given a flying enemy missile, then puffs of smoke are left behind its tail and fade out.

*Sources: GD-43, P14-R05, D-123, D-220.*

### GFX-SHOT-16 — Enemy laser warning line · MUST

Before a laser fires, a thin warning line shows along where its beam will be, blinking
`warning.blinkHz` times a second between full and half width. It is `warning.width` ×
`contrast.warningWidth` wide, with a white core round the laser's colour (GFX-READ-11). It is drawn
over the models.

**Acceptance criteria**
- Given a warning, then one line is drawn, at full or half width as the blink says (unit tests).
- Given the warning colours, then they go from a white core to the laser colour and dark edges
  (unit test).

*Sources: GD-43, P10-R07, P14-R05.*

### GFX-SHOT-17 — Enemy laser beam · MUST

A firing enemy laser is a beam with a white-hot core, its colour round it, fading out, drawn
`beam.glowWidth` times the beam's width, its width flickering, with a flare at its base like the
player's laser base glow. It is drawn over the models, so it is seen leaving its emitter's lens, not
from under the hull round it.

**Acceptance criteria**
- Given a firing laser, then its beam and base flare are drawn over the models.

*Sources: GD-43, D-072.*

### GFX-SHOT-18 — Enemy laser colours · MUST

A boss's lasers take its neon colour; the other enemies' lasers (the Lancer's) a red. Every laser
colour is then folded into the enemy-shot family (GFX-READ-06), so bosses keep different laser
shades, all orange to amber.

**Acceptance criteria**
- Given a boss's lasers, then their colour is the boss's neon folded into the enemy-shot family;
  given a laser with no boss neon, the laser look's colour folded (unit tests).

*Sources: D-072, P14-R02, D-121.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Tracer width / length | 4.2 / 34 px | `src/game/config/shot_look.py` `SHOT_LOOK["bullet"]` |
| Tracer flicker | ±0.18 at 90 rad/s | `SHOT_LOOK["bullet"]` |
| Tracer depth | 8 units behind the playfield | `SHOT_LOOK["bullet"]["depth"]` |
| `launchBack` (bullet) | 13 px | `src/game/config/player_weapons.py` `BULLET` |
| `muzzle_inset` | 3 px below the nose tip | `src/config/game_play.py` `GAME_PLAY_CONFIG` |
| Laser drawn width / glow width / flicker | hit width + 8 px / 1.8 × drawn width / ±0.12 at 23 Hz | `SHOT_LOOK["laser"]` (owner, 2026-11-08: was 1.8 × hit width) |
| Laser colours | [0.85, 0.95, 1], [0.3, 0.62, 1], [0.06, 0.22, 0.8], black | `SHOT_LOOK["laser"]["colors"]` (owner, 2026-11-08: brighter) |
| Laser particles | 48, 500–900 px/s, radius 1.2–2.6 px, spread 0.9 | `SHOT_LOOK["laser"]["particles"]` |
| Laser contact glow | radius 9 px | `SHOT_LOOK["laser"]["contact"]` |
| Laser base glow | radius 12 × (0.6 + drawn width / 12), stretch 1.3, pulse ±0.15 at 9 and 17 Hz, 24 sides | `SHOT_LOOK["laser"]["muzzle"]` |
| Missile body | length 2.2, radius 0.2, fin span 0.4 model units; body [0.78, 0.8, 0.85], tip [0.3, 0.85, 1] | `SHOT_LOOK["missile"]` |
| Missile flare | radius 7 px, ±0.25 at 70 rad/s | `SHOT_LOOK["missile"]["flare"]` |
| Missile trail | 4 × 46 px | `SHOT_LOOK["missile"]["trail"]` |
| Missile depth | 20 units behind the playfield | `SHOT_LOOK["missile"]["depth"]` |
| `bullets.scale` | 1.6 × hit radius | `src/game/config/enemy_look.py` `ENEMY_LOOK["bullets"]` |
| Bullet aura | 1.45 × radius, ±0.08 at 13 Hz | `ENEMY_LOOK["bullets"]["halo"]` |
| Bullet swirls | 1 × (3 lobes, 6 rad/s) and 0.75 × (2 lobes, −10 rad/s) | `ENEMY_LOOK["bullets"]["swirls"]` |
| Bullet core | 0.35 × radius, ±0.3 at 2.5 Hz | `ENEMY_LOOK["bullets"]["core"]` |
| Bullet body fade | 1, 1, 1, 0.85, 0.4, 0 (centre to edge) | `ENEMY_LOOK["bullets"]["fade"]` |
| Bullet styles | red [1, 0.36, 0.04], magenta [1, 0.55, 0.05], green [1, 0.78, 0.08], orange [1, 0.48, 0.02], blue [1, 0.7, 0.08], purple [1, 0.42, 0.1] | `ENEMY_LOOK["bullets"]["styles"]` |
| White spark | 0.2 × radius | `ENEMY_LOOK["contrast"]["spark"]` |
| Enemy missile | length 11 px, radius 1.8 px, tip [1, 0.5, 0.04], flame 2.6 × 6 px | `ENEMY_LOOK["missile"]` |
| Enemy missile rim | width 0.9 px, intensity 1.2 | `src/game/config/readability.py` `READABILITY["outline"]` |
| Warning line | width 2 px × 1.5, white core 0.85, blink 8 Hz | `ENEMY_LOOK["laser"]["warning"]`, `ENEMY_LOOK["contrast"]` |
| Enemy beam | glow width 2 ×, flicker ±0.12 at 21 Hz | `ENEMY_LOOK["laser"]["beam"]` |
| Enemy beam flare | as the player's base glow | `ENEMY_LOOK["laser"]["flare"]` |
| Lancer laser colour | [1, 0.3, 0.4] (folded when drawn) | `ENEMY_LOOK["laser"]["color"]` |
| Shell hit radius | 7 px | `src/game/config/enemies_veteran.py` |

## Notes

- History of the player's bullet: a neon green blob (phase 3), then a white-hot tracer cooling to
  orange and red (phase 5 review), then recoloured cyan and deep blue (phase 14, the reviewer's
  answer: player shots in the player's colour). The bullet renderer's and the missile model's
  docstrings still say "cooling to red" and "a red nose"; the colours in `SHOT_LOOK` are the cyan
  ones.
- The enemy bullets were glow discs added on (washed out over snow), then blended blobs (D-069), then
  balls of plasma (D-074). A dark backing disc was tried and refused by the reviewer, and the dark
  contrast rim of D-086 was later removed (D-194).
- The enemy shot style per level (D-086) is no longer read: the contrast look is on everywhere
  (GFX-READ-11).
