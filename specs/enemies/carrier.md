# Carrier

> **Area:** Enemies (basic) · **Prefix:** `ENM-CARRIER` · **Related:** [common rules](common.md),
> [Gnat](gnat.md)

The Carrier is the biggest basic kind: a fat, slow brood sac that flies straight down the screen
without ever shooting, releasing Gnats from its side ports. Added at the reviewer's request during
the phase 5 review.

## Requirements

### Look

#### ENM-CARRIER-01 — A fat brood sac · MUST

The Carrier is a fat flying sac about `size` L long, the widest basic kind: a swollen flesh body of
three segments under two bone ribs arched over its back, larvae glowing through its back, and two
neon bands along the middle of its back. Nothing on its back looks like a landing deck.

*Sources: P05-R12, P16-R03.*

#### ENM-CARRIER-02 — Launch ports on its sides, seen from above · MUST

A metal sponson is grafted along each flank. Its outer wall slopes out, so it faces up to the
camera, and holds two launch ports: a dark frame with a mouth that glows as the next launch comes.
The ports are drawn where the Gnats come out (the model and the simulation read the same `ports`).

*Sources: P05-R12.*

#### ENM-CARRIER-03 — Two reactors in flesh sacs · MUST

Two reactors sit at the back, each set in a flesh sac with a glowing vein running from it into the
body.

*Sources: P05-R12, P16-R01.*

#### ENM-CARRIER-04 — Yellow · MUST

The Carrier's lights (bands, larvae, veins, port mouths) and reactor flames are bright yellow (was
amber).

*Sources: P05-R12, D-231.*

### Behaviour

#### ENM-CARRIER-05 — A slow, straight descent · MUST

The Carrier comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) and slowly flies straight down the screen at `speed`, nose down, then leaves at the
bottom.

*Sources: P05-R12.*

#### ENM-CARRIER-06 — It never shoots · MUST

The Carrier never fires.

**Acceptance criteria**
- Given a Carrier, then it never fires a bullet, missile or laser.

*Sources: P05-R12.*

#### ENM-CARRIER-07 — A Gnat from each port · MUST

While it is over the playfield, the Carrier launches every `launchInterval`, the first
`firstLaunch` after it comes over the playfield: one Gnat from each of its four ports (two a side),
the second port of each side `gnat.groupDelay` after the first. Its launches do not follow the
level's fire-rate factor.

**Acceptance criteria**
- Given a Carrier over the playfield, when its launch timer runs out, then a Gnat appears at each
  of its ports.

*Sources: P05-R12, D-036.*

#### ENM-CARRIER-08 — Launched Gnats fly out sideways, then down · MUST

Each launched Gnat is an ordinary [Gnat](gnat.md) (same model, health, points and speed) on its own
path from its port (`launchPath`): out sideways, away from the Carrier, then down past the bottom of
the screen.

**Acceptance criteria**
- Given a Carrier launches, then its Gnats fly away from it, out sideways then down.

*Sources: P05-R12.*

#### ENM-CARRIER-09 — No launch low on the screen · MUST

The Carrier stops launching once it is below `lastLaunchFraction` of the playfield height, too
close to the player.

*Sources: P05-R12.*

#### ENM-CARRIER-10 — Health and points · MUST

The Carrier has `hp` health and scores `points`. Its hit radius is a little smaller than its size.

*Sources: P05-R12, GD-21.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1.8 L | `src/game/config/enemies.py` `ENEMY_CONFIG["carrier"]` |
| `hp` / `points` | 300 / 600 | |
| hit radius | 20.8 px | `radius(1.8) × 0.8` |
| `speed` | 30 px/s | |
| `launchInterval` / `firstLaunch` | 3 s / 1.2 s | |
| `ports` | (±21, 9), (±21, −1) px | from its centre: out to the side, up the screen |
| `launchPath` | (0, 0) → (28, −4) → (55, −30) → (64, −110) → (40, −260) → (20, −800) px | from a right port; mirrored on the left |
| `gnat.groupDelay` | 0.3 s | between the two ports of a side |
| `lastLaunchFraction` | 0.3 | of the playfield height |
| `xRange` | 0.3–0.7 | of the ship's reach |
| `neon` | [1, 0.7, 0.1], drawn bright yellow | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** 1-3, 1-4, 1-5, 2-3, 2-4, 2-5, 3-2 to 3-5, 4-1 to 4-5. Each Carrier launches about
20 Gnats on its way down, which counts in the levels' enemy totals and peaks.

The first Carrier (phase 5 review) had a flight deck, runway lights and an island; at the
reviewer's request they went, replaced by a spine along its back and the side ports. Phase 16 made
it a brood sac (its spine became the ribs and the neon bands along its back).
