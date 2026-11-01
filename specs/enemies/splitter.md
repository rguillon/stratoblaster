# Splitter

> **Area:** Enemies (basic) · **Prefix:** `ENM-SPLITTER` · **Related:** [common rules](common.md),
> [Hornet](hornet.md), [shots](../graphics/shots.md)

The Splitter flies down a curved path, firing aimed bullets. Destroyed, it breaks into its three
pods, which each dive at the player like a small Hornet: killing it is not the end of it.

## Requirements

### Look

#### ENM-SPLITTER-01 — A body made of the three pods it splits into · MUST

The Splitter is about `size` L across: three pods fitted around a small flesh heart with a neon
ring, so its body is visibly made of the parts it splits into. Each pod is a curled flesh grub, a
wedge fitted around the heart, with a metal plate grafted on its back, a neon seam along its inner
side (between it and the heart) and a glowing vein across it.

*Sources: P05-R10, P16-R03.*

#### ENM-SPLITTER-02 — An eye that charges, one reactor · MUST

An eye on top of its heart is its gun: a charge light that brightens before it fires. It has one
reactor at the back.

**Acceptance criteria**
- Unit test: the model has one reactor and one gun.

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

#### ENM-SPLITTER-05 — A curved path down the screen · MUST

The Splitter flies down a predefined curved path (`path`) from above the top of the screen to below
the bottom, at `speed`, its nose along the path, mirrored towards the wave's entry or at random.

*Sources: P05-R10.*

#### ENM-SPLITTER-06 — One aimed bullet at a steady beat · MUST

While it is over the playfield, the Splitter fires one bullet aimed at the player every
`fireInterval`, the first `firstShot` after it comes over the playfield, from its eye.

*Sources: P05-R10, GD-44.*

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
| `hp` / `points` | 50 / 200 | |
| hit radius | 14.5 px | `radius(1)` |
| `speed` | 95 px/s | |
| `path` | (0.2, 1.1) → (0.3, 0.7) → (0.65, 0.45) → (0.8, −0.15) | fractions of the playfield (x across the ship's reach) |
| `fireInterval` / `firstShot` | 2.5 s / 0.8 s | |
| `bullet` | 200 px/s, radius 4, style `purple` | |
| `muzzles` | (0, 0, 5.4) | the eye on top of its heart |
| `podOffset` | 12.9 px | the pods' distance from the centre |
| `splitterPod.size` | 0.4 L | `ENEMY_CONFIG["splitterPod"]` |
| `splitterPod.hp` / `points` | 10 / 50 | hit radius 5.8 px |
| `splitterPod.pause` | 0.35 s | |
| `splitterPod.diveAcceleration` / `diveMaxSpeed` | 950 px/s² / 560 px/s | |
| `neon` | [0.65, 0.2, 1], drawn bright yellow | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** 1-2 to 1-5, 2-2 to 2-5, 3-1 to 3-5, 4-1 to 4-5 (every level but 1-1 and 2-1).

The P05 Splitter was a hexagonal core with three small pods attached around it and purple neon
seams between them. Its violet neon (hue 274°) is nearer the yellow than the green, so it is drawn
yellow.
