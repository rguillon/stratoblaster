# Credits

Third-party assets used by the game (ENG-122, ENG-133). All models are generated from code (ENG-126,
GFX-ART-01, ENG-121), and so is the music (AUD-MUSIC-01). The sound effects are samples from two CC0
packs (AUD-ENGINE-01, AUD-SFX-08).

## Sound effects

Both packs are by [Kenney](https://www.kenney.nl) and released under
[Creative Commons Zero (CC0 1.0)](https://creativecommons.org/publicdomain/zero/1.0/): public domain,
free for any use without attribution, which is compatible with this project's MIT license. They are
credited anyway.

- **Sci-Fi Sounds** 1.0, Kenney, <https://opengameart.org/content/sci-fi-sounds> (also on
  <https://kenney.nl/assets/sci-fi-sounds>)
- **Interface Sounds** 1.0, Kenney, <https://opengameart.org/content/interface-sounds> (also on
  <https://kenney.nl/assets/interface-sounds>)

Each game sound (`public/sfx/<sound>.ogg` and `.mp3`) is one file of a pack, made mono, 44.1 kHz, cut
where noted (20 ms fade-out), normalised to a −1 dBFS peak and encoded with ffmpeg (Ogg Vorbis
quality 3, MP3 quality 5).

| Sound | Author | Source pack | Source file | License | Changes |
| ----- | ------ | ----------- | ----------- | ------- | ------- |
| `gun-shot` | Kenney | Sci-Fi Sounds 1.0 | `laserSmall_000.ogg` | CC0 1.0 | trimmed to 0.16 s |
| `missile-launch` | Kenney | Sci-Fi Sounds 1.0 | `thrusterFire_000.ogg` | CC0 1.0 | trimmed to 0.7 s |
| `laser-start` | Kenney | Sci-Fi Sounds 1.0 | `laserLarge_000.ogg` | CC0 1.0 | – |
| `laser-hum` | Kenney | Sci-Fi Sounds 1.0 | `engineCircular_000.ogg` | CC0 1.0 | tail cross-faded into the head for a seamless loop (4.7 s) |
| `weapon-switch` | Kenney | Sci-Fi Sounds 1.0 | `doorClose_001.ogg` | CC0 1.0 | – |
| `weapon-level-up` | Kenney | Interface Sounds 1.0 | `maximize_002.ogg` | CC0 1.0 | – |
| `enemy-shot` | Kenney | Sci-Fi Sounds 1.0 | `laserSmall_003.ogg` | CC0 1.0 | trimmed to 0.25 s |
| `enemy-missile` | Kenney | Sci-Fi Sounds 1.0 | `thrusterFire_002.ogg` | CC0 1.0 | trimmed to 0.6 s |
| `laser-warning` | Kenney | Sci-Fi Sounds 1.0 | `forceField_002.ogg` | CC0 1.0 | – |
| `enemy-laser` | Kenney | Sci-Fi Sounds 1.0 | `laserLarge_003.ogg` | CC0 1.0 | – |
| `hit` | Kenney | Sci-Fi Sounds 1.0 | `impactMetal_004.ogg` | CC0 1.0 | – |
| `hit-shield` | Kenney | Sci-Fi Sounds 1.0 | `impactMetal_001.ogg` | CC0 1.0 | trimmed to 0.45 s |
| `player-hit` | Kenney | Sci-Fi Sounds 1.0 | `impactMetal_003.ogg` | CC0 1.0 | – |
| `explosion-small` | Kenney | Sci-Fi Sounds 1.0 | `explosionCrunch_000.ogg` | CC0 1.0 | – |
| `explosion-large` | Kenney | Sci-Fi Sounds 1.0 | `explosionCrunch_002.ogg` | CC0 1.0 | – |
| `boss-part-destroyed` | Kenney | Sci-Fi Sounds 1.0 | `explosionCrunch_003.ogg` | CC0 1.0 | – |
| `boss-destroyed` | Kenney | Sci-Fi Sounds 1.0 | `lowFrequency_explosion_000.ogg` | CC0 1.0 | – |
| `life-lost` | Kenney | Sci-Fi Sounds 1.0 | `lowFrequency_explosion_001.ogg` | CC0 1.0 | – |
| `extra-life` | Kenney | Interface Sounds 1.0 | `confirmation_004.ogg` | CC0 1.0 | – |
| `bomb` | Kenney | Sci-Fi Sounds 1.0 | `explosionCrunch_004.ogg` | CC0 1.0 | – |
| `bomb-bonus` | Kenney | Interface Sounds 1.0 | `glass_004.ogg` | CC0 1.0 | – |
| `weapon-bonus` | Kenney | Interface Sounds 1.0 | `select_003.ogg` | CC0 1.0 | – |
| `life-bonus` | Kenney | Interface Sounds 1.0 | `confirmation_003.ogg` | CC0 1.0 | – |
| `menu-move` | Kenney | Interface Sounds 1.0 | `tick_004.ogg` | CC0 1.0 | – |
| `menu-confirm` | Kenney | Interface Sounds 1.0 | `select_001.ogg` | CC0 1.0 | – |
| `menu-back` | Kenney | Interface Sounds 1.0 | `back_001.ogg` | CC0 1.0 | – |
| `pause` | Kenney | Interface Sounds 1.0 | `switch_001.ogg` | CC0 1.0 | – |
| `resume` | Kenney | Interface Sounds 1.0 | `switch_002.ogg` | CC0 1.0 | – |
| `slider-step` | Kenney | Interface Sounds 1.0 | `tick_001.ogg` | CC0 1.0 | – |

## Other assets

| Asset | Author | Source | License |
| ----- | ------ | ------ | ------- |
| Babylon.js (vendored, `public/vendor/babylon.js`) | Babylon.js contributors | https://www.babylonjs.com | Apache-2.0 |
