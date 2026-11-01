# Hornet

> **Area:** Enemies (basic) · **Prefix:** `ENM-HORNET` · **Related:** [common rules](common.md),
> [Splitter](splitter.md), [bosses](../bosses/common.md)

The Hornet is a diver: it comes down from the top, brakes to a stop, turns its nose to the player,
then dives straight at where the player was and leaves the screen. It never shoots; it is
dangerous by ramming. A Splitter's pods behave as small Hornets, and some bosses launch Hornets.

## Requirements

### Look

#### ENM-HORNET-01 — A stinger diver · MUST

The Hornet is a wasp-like diver about `size` L long: a body of three swollen flesh segments, a
metal stinger grafted on its nose under a single neon eye, and a glowing vein along its back.

*Sources: P05-R02, P16-R03.*

#### ENM-HORNET-02 — Swept membrane wings that flutter · MUST

Two sharply swept wings, a membrane stretched on bone struts out to their tips, each with a vein
along its leading strut, flutter about their roots.

**Acceptance criteria**
- Unit test: the model has two wings and no gun.

*Sources: P05-R02, P16-R03, P16-R07.*

#### ENM-HORNET-03 — Yellow, one reactor in a flesh sac · MUST

The Hornet's eye, veins and reactor flame are bright yellow (was red). Its one reactor, at the
back, is set in a flesh sac.

*Sources: P05-R02, phase 5 review, D-231.*

### Behaviour

#### ENM-HORNET-04 — It brakes into its stop · MUST

The Hornet comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) and flies straight down at `entrySpeed` until its braking distance, then slows down
at a constant `entryBrake` to rest at `stopFraction` of the playfield height: no sudden halt.

**Acceptance criteria**
- Given a Hornet coming in, then it reaches its stop height at rest, and its speed never changes by
  more than its braking allows in one step.

*Sources: P05-R02, phase 5 review.*

#### ENM-HORNET-05 — It turns its nose to the player · MUST

At its stop, the Hornet stays `pause` seconds while it turns its nose to the player. The turn
starts as it brakes and eases in as the nose gets there (fast enough to turn all the way round
during the pause).

*Sources: P05-R02, phase 5 review.*

#### ENM-HORNET-06 — It dives at where the player was · MUST

At the end of its pause, the Hornet dives in a straight line towards where the player was at that
moment, starting from rest and gathering speed at `diveAcceleration` up to `diveMaxSpeed`, until it
leaves the screen. It does not steer during the dive.

**Acceptance criteria**
- Given a Hornet has finished its pause, then it dives towards the player position recorded at the
  end of the pause.

*Sources: P05-R02, phase 5 review.*

#### ENM-HORNET-07 — It does not shoot · MUST

The Hornet never fires.

*Sources: P05-R02.*

#### ENM-HORNET-08 — Launched Hornets start with their pause · MUST

A Hornet sent out by another enemy (a boss's drone bay) comes out where it is launched, side by side
with the others of its launch, and starts with its pause: it turns to the player, then dives.

*Sources: P05-R02, P05-R10.*

#### ENM-HORNET-09 — Health and points · MUST

The Hornet has `hp` health and scores `points`.

*Sources: P05-R02.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 0.7 L | `src/game/config/enemies.py` `ENEMY_CONFIG["hornet"]` |
| `hp` / `points` | 20 / 100 | |
| hit radius | 10.1 px | `radius(0.7)` |
| `entrySpeed` | 220 px/s | |
| `entryBrake` | 440 px/s² | about 0.5 s and 55 px of braking |
| `stopFraction` | 0.72 | of the playfield height, from the bottom |
| `pause` | 0.5 s | |
| `diveAcceleration` / `diveMaxSpeed` | 1000 px/s² / 620 px/s | |
| `xRange` | 0.15–0.85 | of the ship's reach |
| launch spacing | 14 px | side by side, `src/game/sim/bosses/boss_launches.py` |
| `neon` | [1, 0.08, 0.1], drawn bright yellow | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** every level, 1-1 to 4-5. Bosses' drone bays and hangars launch Hornets too
(Sentinel, Aurora Station, Dam Breaker, Geyser Rig; see their files), and every
[Splitter](splitter.md) breaks into small Hornets.

The P05 Hornet was an arrow head with sharply swept wings and a single red neon eye; the phase 5
review smoothed its stop and its dive (it used to halt at once and jump to its dive speed).
