# Splitter

> **Area:** Enemies (basic) · **Prefix:** `ENM-SPLITTER` · **Related:** [common rules](common.md),
> [Hornet](hornet.md), [shots](../graphics/shots.md)

The Splitter is tier 4's **diver** (World 4, the role of the [Hornet](hornet.md)): it comes in from
the top, brakes, turns its nose to the player and dives at where the player was. It never shoots.
Bigger and tougher than a Hornet, it breaks into its three pods when destroyed, and each pod dives at
the player like a small Hornet: killing it is not the end of it. The [Hive](hive.md) launches them.

## Requirements

### Look

#### ENM-SPLITTER-01 — A body made of the three pods it splits into · MUST

The Splitter is about `size` L across: three pods fitted around a small flesh heart with a neon
ring, so its body is visibly made of the parts it splits into. Each pod is a curled flesh grub, a
wedge fitted around the heart, with a metal plate grafted on its back, a neon seam along its inner
side (between it and the heart) and a glowing vein across it.

*Sources: P05-R10, P16-R03.*

#### ENM-SPLITTER-02 — An eye that charges, one reactor · MUST

An eye on top of its heart is a charge light that brightens through the pause before the dive. It
has one reactor at the back and no gun (it never shoots, ENM-SPLITTER-06).

**Acceptance criteria**
- Unit test: the model has one reactor and no gun.

*Sources: P05-R10, phase 5 review, D-057.*

#### ENM-SPLITTER-03 — The pod alone · MUST

A broken-off pod is the same grub wedge, about `splitterPod.size` L across, alone, with a reactor
on its inner side; it dives outer side first. It has no gun.

**Acceptance criteria**
- Unit test: the pod's model has a reactor and no gun, and is its own model.

*Sources: P05-R10, P16-R03.*

#### ENM-SPLITTER-04 — Yellow · MUST

The Splitter's lights (ring, seams, veins, eye) and reactor flames, and its pods', are bright
yellow (was purple).

*Sources: P05-R10, D-231.*

### Behaviour

#### ENM-SPLITTER-05 — Tier 4's diver, coming in from the top · MUST

The Splitter comes in from just above the top edge, at the wave's entry position or at a random X in
`xRange`, flying down at `entrySpeed` and braking (`entryBrake`) into its stop height, `stopFraction`
of the playfield height (the upper half). Built mid-screen (as the Hive launches it,
ENM-HIVE-09) at `Splitter(x, y, stop_y)`, with `stop_y` at or below where it starts, it starts with
the pause. If it reaches the bottom of the screen undestroyed it just leaves: no pods.

**Acceptance criteria**
- Given the kind spawns, then one Splitter comes in above the top edge and stops at `stopFraction`.
- Given a Splitter that reaches the bottom of the screen, then it leaves and spawns no pod.

*Sources: P05-R10, tier 4 redesign.*

#### ENM-SPLITTER-06 — It turns to the player and dives, never shooting · MUST

Stopped, the Splitter stays `pause` turning its nose to the player (its eye charging), then dives in
a straight line towards where the player was at the end of the pause, from rest at
`diveAcceleration` up to `diveMaxSpeed`, as a Hornet does ([ENM-HORNET-05, -06](hornet.md)), until it
leaves the screen. It never fires a bullet, missile or laser.

**Acceptance criteria**
- Given a Splitter in place, then it aims, then dives at the player.
- Given a Splitter over a long run, then it fires nothing.

*Sources: tier 4 redesign (replaces the aimed bullets of P05-R10, GD-44).*

#### ENM-SPLITTER-07 — It splits when destroyed · MUST

When it is destroyed, the Splitter's three pods break off at its position, 120° apart around where
its heart was, `podOffset` out from it, each facing outwards.

**Acceptance criteria**
- Given a Splitter is destroyed, then 3 pods appear around its position, 120° apart.

*Sources: P05-R10.*

#### ENM-SPLITTER-08 — Each pod dives like a small Hornet · MUST

Each pod behaves as a small Hornet that starts with its pause: it stays `splitterPod.pause` turning
its nose to the player, then dives in a straight line towards where the player was, from rest at
`splitterPod.diveAcceleration` up to `splitterPod.diveMaxSpeed`, until it leaves the screen. A pod
does not shoot.

**Acceptance criteria**
- Given a Splitter is destroyed, then its 3 pods dive towards the player.

*Sources: P05-R10, P05-R02.*

#### ENM-SPLITTER-09 — Health and points · MUST

The Splitter has `hp` health and scores `points`; each pod has `splitterPod.hp` health and scores
`splitterPod.points`.

*Sources: P05-R10.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1 L | `src/game/config/enemies.py` `ENEMY_CONFIG["splitter"]` |
| `hp` / `points` | 200 / 450 | tier 4 diver (450: GAME-SCORE-03 against the Phantom) |
| hit radius | 14.5 px | `radius(1)` |
| `entrySpeed` / `entryBrake` | 150 px/s / 300 px/s² | |
| `stopFraction` | 0.7 | |
| `xRange` | 20 % – 80 % of the width | when the wave gives no entry |
| `pause` | 0.7 s | |
| `diveAcceleration` / `diveMaxSpeed` | 800 px/s² / 480 px/s | |
| `podOffset` | 12.9 px | the pods' distance from the centre |
| `splitterPod.size` | 0.4 L | `ENEMY_CONFIG["splitterPod"]` |
| `splitterPod.hp` / `points` | 10 / 50 | hit radius 5.8 px |
| `splitterPod.pause` | 0.35 s | |
| `splitterPod.diveAcceleration` / `diveMaxSpeed` | 950 px/s² / 560 px/s | |
| `neon` | [0.65, 0.2, 1], drawn bright yellow | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** the wave plans, and launched by the [Hive](hive.md) (ENM-HIVE-09).
Its model is one of the child models (`CHILD_MODELS`) so the Hive can launch it without building one in play.

The P05 Splitter was a hexagonal core with three small pods attached around it and purple neon
seams between them. Its violet neon (hue 274°) is nearer the yellow than the green, so it is drawn
yellow.
