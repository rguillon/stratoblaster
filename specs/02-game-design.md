# 02 — Game design (global)

> Rules that hold for the **whole game**, across phases. Phase files may refine them but not contradict them.
> Requirement IDs: `GD-xx`. Leave sections empty if not decided yet — fill them before the phase that needs them.
> Values in tables are *tunable*: the agent should put them in a single config file, not hard-code them.

## 1. Screen & camera
| ID | Requirement |
|----|-------------|
| GD-01 | Vertical scrolling, ground speed vary per level |
| GD-02 | Logical resolution: 480×640, scaled to fit window |
| GD-03 | Aspect ratio handling:  responsive  |

## 2. Controls
| Action | Keyboard | Gamepad | Touch |
|--------|----------|---------|-------|
| Move | arrows / WASD (key position based so it also works on AZERTY keyboards)| left stick | drag  |
| Shoot |  space  | button | button |
| Special / bomb | E | button | button|
| Pause |  Esc / P | button | button |

- GD-10 Input feel: the player ship shall have little acceleration but quickly reach it's maximal speed

## 3. Player
- GD-20 Lives / health model: Start with 3 lives, more lives can be collected as dropped bonnuses and a 100% health bar.
- GD-21 Hitbox: small hitbnox for the player, visual equivalent hotbox for the enemies
- GD-22 Invincibility after hit: the player becomes invicible for 2 seconds after getting hit. The ship blinkswhen invisible.

## 4. Weapons & power-ups (global rules)
- GD-30 The player shall have 3 main weapons: guns, laser, missiles.
- GD-31 Each weapon shall be upgradable up to level 5
- GD-32 The player shall have secondary bombs, one bomb cause damage to every enemy on the screen. Enough damage to kill most of the low level enemies.


## 5. Enemies (global rules)
- GD-40 Enemies shall be spaw (alone or in waves) based on how far the player advance in the level.
- GD-41 Each level shall have one mini boss and one final boss.
- GD-42 The mini boss shall act as a checkpoint
- GD-43 Enemies can shoot colorfull bullets, missiles that the player can shoot, or laser (with a 1s warning line before  shooting the actual lazer)
- GD-44 Enemies can shoot at preset direction or pointing ar the player
- GD-45 Each enemy kind has a present movement kind: it can be a prefefined path, or diving right at the player.
- GD-46 The minibosses and final bosses shall have destructible parts, every time one part is destroyed, the attack pattern change.

## 6. Scoring
- GD-50 Enemy killed shall provide points accoding to their difficulty.
- GD-51 High score persistence shall be based on a cookie.

## 7. Game flow & screens
<!-- TODO: list screens and transitions, e.g. Title → Game → Game Over → Title; Pause overlay -->
```
itle ──start──▶ Select Ship t──▶ Select level ──▶Game ──lives=0──▶ Game Over ──any key──▶ Title
                                                    │ ▲
                                                  pause│ │resume
                                                    ▼ │
                                                  Pause
```

## 8. Visual style
- GD-60 Art direction: All the models shall be generated from code, the style shall be Cyber
punk/synthwave
- GD-61 Palette: The player ship shall be shiny grey/blue. The enemies shall be dark metalic with neon lights. The background shall be more pastel.
- GD-62 Effects: Particle effect shall be emitted every time a projectil hits a ship. Explosions shall be generated when a ship isdestroyed.
## 9. Audio
- GD-70 Music: Music shall be code generated. One music per level, a more  stressfull music when fighting a boss.
- GD-71 SFX: SFXshall be software generated.

## Glossary
| Term | Meaning |
|------|---------|
| <!-- e.g. Wave --> | <!-- a group of enemies spawned together --> |
