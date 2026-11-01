# Bulwark

> **Area:** Enemies (basic) · **Prefix:** `ENM-BULWARK` · **Related:** [common rules](common.md),
> [shots](../graphics/shots.md)

The Bulwark is the heavy gunship of the basic kinds: an armoured beetle that comes down to the
upper third of the screen, drifts left and right for a while firing spreads of bullets centred on
the player, then leaves downward.

## Requirements

### Look

#### ENM-BULWARK-01 — A heavy armoured beetle · MUST

The Bulwark is a heavy, wide enemy about `size` L wide: a wide, ridged carapace (shell plates with
darker seams between them), mandibles at its front and short legs on its sides.

*Sources: P05-R09, P16-R03.*

#### ENM-BULWARK-02 — A front armour band and a visor slit · MUST

One metal armour band runs across the front of its shell, a chevron, with a neon visor slit above
it; a glowing vein runs along its back.

*Sources: P05-R09, phase 5 review, P16-R03.*

#### ENM-BULWARK-03 — A twin cannon and three reactors · MUST

A twin cannon of dark metal barrels is grafted on its head, over the armour, a charge light at each
tip. It has three reactors: a big one in the middle of its back and one either side.

**Acceptance criteria**
- Unit test: the model has three reactors and two guns.

*Sources: P05-R09, phase 5 review, D-057.*

#### ENM-BULWARK-04 — Green · MUST

The Bulwark's visor, vein, charge lights and reactor flames are bright green (was blue).

*Sources: P05-R09, D-231.*

### Behaviour

#### ENM-BULWARK-05 — It comes down to the upper third · MUST

The Bulwark comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) and slowly moves down at `entrySpeed` to `stopFraction` of the playfield height.

*Sources: P05-R09.*

#### ENM-BULWARK-06 — It drifts, then leaves downward · MUST

There it drifts left and right, `drift` either side of where it came in, one sway every
`driftPeriod`, for `stay`; then it leaves downward at `exitSpeed`.

**Acceptance criteria**
- Given a Bulwark at its stop height, then it drifts for 8 s, then leaves downward.

*Sources: P05-R09.*

#### ENM-BULWARK-07 — A spread centred on the player · MUST

While it is over the playfield (coming in, drifting and leaving), the Bulwark fires every
`fireInterval` (the first half an interval after it comes over the playfield) a spread of
`spreadCount` bullets `spreadSpacing` apart, the middle one aimed at the player, from its twin
cannon.

**Acceptance criteria**
- Given a Bulwark fires, then the middle bullet of its spread is aimed at the player.

*Sources: P05-R09, GD-44.*

#### ENM-BULWARK-08 — Health and points · MUST

The Bulwark has `hp` health and scores `points`. Its hit radius is a little smaller than its width.

*Sources: P05-R09, GD-21.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1.6 L | `src/game/config/enemies.py` `ENEMY_CONFIG["bulwark"]` |
| `hp` / `points` | 200 / 500 | |
| hit radius | 18.5 px | `radius(1.6) × 0.8` |
| `entrySpeed` | 70 px/s | |
| `stopFraction` | 0.74 | of the playfield height |
| `drift` / `driftPeriod` | 70 px / 4 s | |
| `stay` | 8 s | |
| `exitSpeed` | 90 px/s | |
| `fireInterval` | 2 s | first shot after 1 s |
| `spreadCount` / `spreadSpacing` | 5 / 10° | |
| `bullet` | 190 px/s, radius 4, style `blue` | |
| `muzzles` | (±3, −14, 4.2) | the twin cannon's tips |
| `xRange` | 0.3–0.7 | of the ship's reach |
| `neon` | [0.15, 0.4, 1], drawn bright green | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** 1-5, 2-3, 2-4, 2-5, 3-2 to 3-5, 4-1 to 4-5.

The P05 Bulwark was a heavy, wide hull covered with front armour plates and a blue neon visor slit;
the phase 5 review made the plates one band, and its chin gun went (only visible from below).
