# Strafer

> **Area:** Enemies (basic) · **Prefix:** `ENM-STRAFER` · **Related:** [common rules](common.md),
> [shots](../graphics/shots.md)

The Strafer is a fan shooter that crosses the top of the screen sideways, dropping fans of three
bullets straight down whatever the player does. It is the only basic kind that comes in from a
side.

## Requirements

### Look

#### ENM-STRAFER-01 — A wide flying wing · MUST

The Strafer is a wide flying wing about `size` L wide and about half as long: a wide pair of
membrane wings on bone struts out of a squat flesh body with two eyes. Its wings flutter about
their roots.

*Sources: P05-R04, P16-R03, P16-R07.*

#### ENM-STRAFER-02 — A row of neon glands along the leading edges · MUST

A row of three steady neon glands runs along each wing's leading edge.

*Sources: P05-R04.*

#### ENM-STRAFER-03 — Four reactors and three guns on each flank · MUST

Four reactors sit along the trailing edge. Three metal gun barrels on each flank of the body, one
above the other along it, point out sideways fanned 15° apart (one towards the nose, one straight
out, one towards the tail), a charge light at each tip: as the Strafer flies across the screen, the
three of one side face down it. Each is a barrel that recoils (WPN-03, WPN-04).

**Acceptance criteria**
- Unit test: the model has four reactors, six guns (each a sliding barrel) and two wings.

*Sources: P05-R04, phase 5 review, D-057, D-268.*

#### ENM-STRAFER-04 — Yellow · MUST

The Strafer's lights, charge lights and reactor flames are bright yellow (was magenta).

*Sources: P05-R04, D-231.*

### Behaviour

#### ENM-STRAFER-05 — A side pass across the top third · MUST

The Strafer comes in from the left or the right side, in the top third of the screen (at the wave
entry's side and height, or at random from either side at `heightFraction` of the playfield
height), crosses the whole width horizontally at `speed`, its nose along its way, and leaves on the
other side.

**Acceptance criteria**
- Given a Strafer from the left, then it crosses to the right and leaves; from the right, the
  other way.

**Discrepancy:** in 1-1 and 1-2, three Strafer groups added by the wave density's spread (D-044:
−0.15 of the height per extra group of a side beat) cross at 60–65 % of the height, just below the
top third.

*Sources: P05-R04, D-048.*

#### ENM-STRAFER-06 — A fan of three straight down · MUST

While it is over the playfield, the Strafer fires a fan of `fanCount` bullets every `fireInterval`
(the first half an interval after it comes over the playfield), in preset directions:
−`fanSpacing`, 0 and +`fanSpacing` from straight down, whatever the player's position. Each leaves
from its own barrel of the flank facing down the screen, at its tip and along the barrel (WPN-01).

**Acceptance criteria**
- Given a Strafer fires, then its 3 bullets leave at −15°, 0° and +15° from straight down, whatever
  the player's position, each from the tip of a different barrel, along it.

*Sources: P05-R04, GD-44, D-268.*

#### ENM-STRAFER-07 — Health and points · MUST

The Strafer has `hp` health and scores `points`. Its hit radius is smaller than its width (a circle
inside a wide wing).

*Sources: P05-R04, GD-21.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1.2 L | width; `src/game/config/enemies.py` `ENEMY_CONFIG["strafer"]` |
| `hp` / `points` | 40 / 150 | |
| hit radius | 13.0 px | `radius(1.2) × 0.75` |
| `speed` | 150 px/s | |
| `heightFraction` | 0.8 | of the playfield height, without a wave entry |
| `fireInterval` | 1 s | first shot after 0.5 s |
| `fanCount` / `fanSpacing` | 3 / 15° | |
| `bullet` | 200 px/s, radius 4, style `magenta` | |
| `muzzles` | (±9, −1.5, 1.5) | the flank guns' tips |
| `neon` | [1, 0.1, 0.85], drawn bright yellow | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** every level, 1-1 to 4-5, always from a side (wave heights 0.75 to 0.82 of the
playfield).

The P05 Strafer was a wide, flat flying wing with a row of magenta neon lights along its leading
edge.
