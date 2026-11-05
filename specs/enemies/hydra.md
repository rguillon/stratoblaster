# Hydra

> **Area:** enemies · **Prefix:** `ENM-HYDRA` · **Related:** [common.md](common.md), [World 4](../worlds/world-4/world.md)

The Hydra is an elite kind ([common.md](common.md)) with moving parts: a broad, armoured hull with
three long necks swaying in front of it, each ending in a head with a gun on its brow that fires a
burst of bullets along the head, in turn. It is tier 4's **shooter** (World 4, the role of the
[Spinner](spinner.md)); it swapped weapons and roles with the [Juggernaut](juggernaut.md) (owner
request 2026-11-05, D-274). The heads can be shot off one by one; with all three gone the Hydra no
longer fires.

## Requirements

### Look

#### ENM-HYDRA-01 — Shape and size · MUST

The Hydra is a broad hull 1.6 L long, necks and heads included (about 1.5 L across), with three long
necks reaching forward from its front edge, each ending in a head with a glowing eye.

**Acceptance criteria**
- Given the Hydra's model at rest, then it is 1.6 L long (within the size tolerance of
  [common.md](common.md)), and its three necks and heads show from above.

*Sources: P05-R19, P16-R04.*

#### ENM-HYDRA-02 — Cyber-Organic body · MUST

The Hydra's hull is a broad, ridged flesh shell of four segments (teal and graphite shades), a bone
ridge along its back. Metal is grafted on: two armour plates on each shoulder, the front ones
riveted. Heavily plated, with more organs and limbs than any veteran, it reads as an elite
([common.md](common.md)).

**Acceptance criteria**
- Given the Hydra's model, then its shell is flesh with a bone ridge, and its shoulder plates are
  metal.

*Sources: P16-R04.*

#### ENM-HYDRA-03 — Neon lights · MUST

A glowing vein runs along each side of the shell, a line of lights runs along its front edge where
the necks grow out, neon bands ring the necks' collars and each head has a glowing eye, all in the
Hydra's neon colour. That colour is bright green: its configured teal is on the green side of the
two enemy hues ([common.md](common.md)).

**Acceptance criteria**
- Given the Hydra's model, then its veins, front lights, collar bands and eyes are lit in bright
  green.

*Sources: P05-R19, P16-R04, D-231.*

#### ENM-HYDRA-04 — Reactors · MUST

Two reactors sit at the back of its shell, each set in a glowing organ: a teal flesh sac round the
nozzle, a gland on its back and a vein running forward from it.

**Acceptance criteria**
- Given the Hydra's model, then its body has two reactors, each in a flesh sac.

*Sources: P16-R04.*

#### ENM-HYDRA-05 — Necks and heads on their joints · MUST

Each neck is a teal flesh tendril from its joint at the front of the hull to its head, ringed with
two metal collars. Each head is a swollen teal skull with a metal cap on its brow, a bone mandible
either side and a gun on its brow whose tip is where its bullets leave. The model's necks turn on their
joints exactly as the Hydra's do in the game ([common.md](common.md)). A destroyed head disappears
from the model; its neck stays.

**Acceptance criteria**
- Given the Hydra's model, then it draws the three heads of its design, each on its neck joint,
  each with one muzzle at its gun's tip, at the place the game fires from.
- Given a head is destroyed, then it is no longer drawn and its neck still is.

*Sources: P05-R19, P16-R04.*

#### ENM-HYDRA-06 — Triangle budget · MUST

The Hydra's model (hull, necks and heads, reactors included) stays within the elite triangle budget
(1200, [common.md](common.md)). It is about 1160 triangles before the edge trim.

**Acceptance criteria**
- Given the Hydra's model, then its triangle count is at most the elite budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-HYDRA-07 — Entry, stay and exit · MUST

A Hydra comes in alone from just above the top edge, at the wave's entry position or at a random X
between 30 % and 70 % of the width. It flies down at 75 px/s to 74 % of the playfield height (the
upper third), stays there 7 s, then leaves downward at 95 px/s.

**Acceptance criteria**
- Given a Hydra comes in, then it stops at 74 % of the height, stays 7 s, then moves down and off
  the screen.

*Sources: P05-R19.*

#### ENM-HYDRA-08 — Swaying necks · MUST

The three necks are moving parts ([common.md](common.md)) on joints along the hull's front edge
(the left and right ones 8 px out and 5 px ahead of the centre, the middle one 7 px ahead), their
heads at rest 19 px out and 21 px ahead (left and right) and 25 px ahead (middle). Each neck sways
by up to 16° either way every 2.6 s, a third of a period after the one before, so they sway out of
step, all the time.

**Acceptance criteria**
- Given a Hydra, then each head's heading swings by up to 16° either way of its rest heading, the
  three a third of a period apart.

*Sources: P05-R19.*

#### ENM-HYDRA-09 — Heads fire bursts in turn · MUST

While its centre is over the playfield, the Hydra fires one head every `headFireInterval` (0.8 s, the
first 0.5 s after it is over it), in turn (left, middle, right), skipping destroyed heads. Each turn
is a burst of `burstCount` bullets (3, `burstGap` 0.1 s apart, 200 px/s, style `green`) from the tip
of that head's gun, along the head as its neck is turned at that instant (WPN-01); the gun recoils
each time (WPN-03). It launches no missile.

**Acceptance criteria**
- Given a Hydra in place, then its living heads fire their bursts in turn, each bullet from that
  head's gun tip along the head, and no missile.
- Given one head is destroyed, then the other two take turns, still one burst every 0.8 s.

*Sources: P05-R19, tier 4 redesign, owner request 2026-11-05 (D-274).*

#### ENM-HYDRA-10 — The heads as parts · MUST

Each head has its own hit circle (6.5 px, on the head) and its own health (50 HP); shots that hit a
head damage the head, not the hull. A destroyed head blows up as a part does
([common.md](common.md)): no points, no bonus. With every head destroyed the Hydra no longer fires,
but its hull can still be shot and destroyed.

**Acceptance criteria**
- Given every head is destroyed, then the Hydra no longer fires but can still be destroyed.

*Sources: P05-R19.*

#### ENM-HYDRA-11 — Health, points and hit circle · MUST

The Hydra's hull has 220 HP and scores 700 points. Its hit circle is 17 px, at its centre.

**Acceptance criteria**
- Given a Hydra, then its hull takes 220 damage to destroy and scores 700 points, and the heads
  still on it blow up with it.

*Sources: P05-R19.*

#### ENM-HYDRA-12 — Necks and heads from its config, as engine specs · SHOULD

The Hydra's necks and heads are written in its config, and the game hands them to the engine as the
engine's own joint and part specs (`jointed_design`), as it does for the bosses. So the engine reads
the swing the config gives (amplitude, period, phase), in CPython and in the browser alike (no
missing or undefined field).

**Acceptance criteria**
- Given a Hydra is made, then each of its parts is an engine part spec on its neck joint, and each
  neck joint swings 16° every 2.6 s with its configured phase (no NaN angle).

*Sources: D-192.*

#### ENM-HYDRA-13 — Elite kind, World 4 only · MUST

The Hydra is an elite kind: only World 4's waves use it. 4-1 brings it in with the Orbiter, the
first two elite kinds, and every level of World 4 (4-1 to 4-5) uses it.

**Acceptance criteria**
- Given the wave scripts, then no level of Worlds 1 to 3 names the Hydra, and every level of
  World 4 does.

*Sources: P05-R24, D-090.*

#### ENM-HYDRA-14 — Bullets, not missiles · MUST

The Hydra fires bullets only; its old missiles are the Juggernaut's launchers' now
([juggernaut.md](juggernaut.md), ENM-JUGGERNAUT-10).

**Acceptance criteria**
- Given the configs, then the Hydra has a `bullet` and no `missile`.

*Sources: tier 4 redesign, owner request 2026-11-05.*

#### ENM-HYDRA-15 — Guns on the heads · MUST

Each head carries a gun on its brow: a barrel in a housing that recoils when it fires, its tip the
muzzle, with a charge light round its root that glows as the head's turn comes.

**Acceptance criteria**
- Given the Hydra's model, then each head has one muzzle, one recoiling barrel and a charge light.

*Sources: tier 4 redesign, owner request 2026-11-05.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 1.6 L | `src/game/config/enemies_elite.py` `ELITE_CONFIG.hydra.size` |
| health / points | 220 / 700 | `ELITE_CONFIG.hydra.stats` |
| hit radius | 17 px | `ELITE_CONFIG.hydra.stats.radius` |
| xRange | 30 % – 70 % of the width | when the wave gives no entry |
| entrySpeed / stopFraction | 75 px/s / 0.74 | |
| stay / exitSpeed | 7 s / 95 px/s | |
| necks | pivots `[-8, -5]`, `[0, -7]`, `[8, -5]`; heads `[-19, -21]`, `[0, -25]`, `[19, -21]` | `HYDRA_NECKS` |
| neck swing | ±16° every 2.6 s, phases 0, ⅓, ⅔ | `ELITE_CONFIG.hydra.design.joints` |
| head health / radius | 50 / 6.5 px | `HYDRA_HEAD` |
| gun tip (muzzle) | 5 px ahead of the head's centre, 3 px up | `HYDRA_HEAD.eyeAhead`, `eyeHeight` |
| headFireInterval / firstShot | 0.8 s / 0.5 s | in turn; times the level's fire rate factor |
| bursts | 3 bullets 0.1 s apart, 200 px/s, style `green` | `burstCount`, `burstGap`, `bullet` |
| neon | `[0.05, 1, 0.78]`, drawn `[0.05, 1, 0.13]` | `src/game/config/enemy_look_elite.py` `ELITE_NEON.hydra` |
| triangle budget | 1200 (elite) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.elite` |

## Notes

**Appears in** (`src/game/config/world_4/waves.py`): one Hydra in a phrase of its level's cycle in
each of [4-1](../worlds/world-4/4-1-garden-town.md), [4-2](../worlds/world-4/4-2-inner-town.md),
[4-3](../worlds/world-4/4-3-midtown.md), [4-4](../worlds/world-4/4-4-business-district.md) and
[4-5](../worlds/world-4/4-5-downtown.md); the groups grow over each level. It is in no level's
filler.

- D-191 found that the config's joints were read by the engine under the wrong field names (NaN
  angles in the browser); D-192 fixed it with `jointed_design` (ENM-HYDRA-12). The comment in
  `tests/unit/game/sim/enemies/test_hydra.py` that still calls this a bug is stale.
- Known gaps: no unit test checks the model's size or its triangle count since the Python port
  (D-220); with the edge trim the elite models may go over 1200, and whether the budget counts the
  trim is open (D-220).
