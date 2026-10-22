# 02 — Game design (global)

> Rules that hold for the **whole game**, across phases. Phase files may refine them but not contradict them.
> Requirement IDs: `GD-xx`. Leave sections empty if not decided yet — fill them before the phase that needs them.
> Values in tables are *tunable*: the agent should put them in a single config file, not hard-code them.

## 1. Screen & camera
| ID | Requirement |
|----|-------------|
| GD-01 | Orientation / scrolling direction: <!-- TODO: vertical up / horizontal right / fixed arena --> |
| GD-02 | Logical resolution: <!-- TODO: e.g. 480×640, scaled to fit window, integer scaling? --> |
| GD-03 | Aspect ratio handling: <!-- TODO: letterbox / stretch / responsive --> |

## 2. Controls
| Action | Keyboard | Gamepad | Touch |
|--------|----------|---------|-------|
| Move | <!-- arrows / WASD --> | <!-- left stick --> | <!-- drag --> |
| Shoot | <!-- space / auto-fire --> | | |
| Special / bomb | | | |
| Pause | <!-- Esc / P --> | | |
| <!-- other --> | | | |

- GD-10 Input feel: <!-- TODO: e.g. instant, no acceleration; focus/slow mode while holding Shift -->

## 3. Player
- GD-20 Lives / health model: <!-- TODO: 3 lives one-hit / HP bar / shields -->
- GD-21 Hitbox: <!-- TODO: small core hitbox smaller than sprite? -->
- GD-22 Invincibility after hit: <!-- TODO: duration -->
- GD-23 Movement speed: <!-- TODO -->

## 4. Weapons & power-ups (global rules)
- GD-30 <!-- TODO: power levels, how they are gained/lost -->

## 5. Enemies (global rules)
- GD-40 <!-- TODO: behaviour families, spawn rules, difficulty scaling -->

## 6. Scoring
- GD-50 <!-- TODO: points per kill, combo/multiplier, extra life thresholds -->
- GD-51 High score persistence: <!-- TODO: localStorage / none -->

## 7. Game flow & screens
<!-- TODO: list screens and transitions, e.g. Title → Game → Game Over → Title; Pause overlay -->
```
Title ──start──▶ Game ──lives=0──▶ Game Over ──any key──▶ Title
                  │ ▲
                pause│ │resume
                  ▼ │
                 Pause
```

## 8. Visual style
- GD-60 Art direction: <!-- TODO: pixel art / vector neon / geometric shapes only -->
- GD-61 Palette: <!-- TODO -->
- GD-62 Effects: <!-- TODO: particles, screen shake, hit flash -->
- GD-63 Font / UI style: <!-- TODO -->

## 9. Audio
- GD-70 Music: <!-- TODO: none / chiptune / generated with WebAudio -->
- GD-71 SFX: <!-- TODO: list key events -->
- GD-72 Mute / volume control: <!-- TODO -->

## 10. Difficulty & balance
- GD-80 <!-- TODO: difficulty modes? target run length? -->

## Glossary
| Term | Meaning |
|------|---------|
| <!-- e.g. Wave --> | <!-- a group of enemies spawned together --> |
