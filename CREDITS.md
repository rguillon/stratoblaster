# Credits

Third-party assets used by the game (ENG-122, ENG-133). All models are generated from code (ENG-126,
GFX-ART-01, ENG-121), and so is the music (AUD-MUSIC-01). The sound effects are samples from two CC0
packs (AUD-ENGINE-01, AUD-SFX-08).

## Sound effects

The packs and files below, two of them by [Kenney](https://www.kenney.nl), are released under
[Creative Commons Zero (CC0 1.0)](https://creativecommons.org/publicdomain/zero/1.0/): public domain,
free for any use without attribution, which is compatible with this project's MIT license. They are
credited anyway.

- **Sci-Fi Sounds** 1.0, Kenney, <https://opengameart.org/content/sci-fi-sounds> (also on
  <https://kenney.nl/assets/sci-fi-sounds>)
- **The Free Firearm Sound Library**, Ben Jaszczak, et al., <https://opengameart.org/content/the-free-firearm-sound-library>
  (CC0): only for the player gun
- **Explosion**, **Chunky Explosion**, **Muffled Distant Explosion** (Nenad Simic), **Explosion somewhere far**
  and **Battle at sea**, all CC0 recordings on OpenGameArt (<https://opengameart.org/content/explosion-0>,
  `/content/chunky-explosion`, `/content/muffled-distant-explosion`, `/content/explosion-somewhere-far`,
  `/content/battle-at-sea`)
- **Interface Sounds** 1.0, Kenney, <https://opengameart.org/content/interface-sounds> (also on
  <https://kenney.nl/assets/interface-sounds>)

Each game sound (`public/sfx/<sound>.ogg` and `.mp3`) is one file of a pack, made mono, 44.1 kHz, cut
where noted (20 ms fade-out), normalised to a −1 dBFS peak and encoded with ffmpeg (Ogg Vorbis
quality 3, MP3 quality 5).

| Sound | Author | Source pack | Source file | License | Changes |
| ----- | ------ | ----------- | ----------- | ------- | ------- |
| `gun-shot` | Ben Jaszczak, et al. | The Free Firearm Sound Library | `ak47.ogg` | CC0 | six single AK-47 shots (five different ones) cut out and laid 21 ms apart, every other one quieter, into one 0.165 s minigun burst |
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
| `explosion-small-1` | (author not named) | Explosion | `explosion.wav` | CC0 | leading silence removed, cut to 0.78 s |
| `explosion-small-2` | (author not named) | Chunky Explosion | `Chunky Explosion.mp3` | CC0 | leading silence removed, cut to 0.8 s |
| `explosion-small-3` | (author not named) | Battle at sea | `cannon_hit_ship_short.ogg` | CC0 | cut to 0.8 s |
| `explosion-large-1` | Nenad Simic | Muffled Distant Explosion | `NenadSimic - Muffled Distant Explosion.wav` | CC0 | cut to 1.25 s |
| `explosion-large-2` | (author not named) | Explosion somewhere far | `explosion_somewhere_far.mp3` | CC0 | cut to 1.5 s |
| `explosion-large-3` | (author not named) | Chunky Explosion | `Chunky Explosion.mp3` | CC0 | cut to 1.5 s |
| `boss-part-destroyed` | Nenad Simic | Muffled Distant Explosion | `NenadSimic - Muffled Distant Explosion.wav` | CC0 | cut to 1.55 s |
| `boss-destroyed` | (author not named) | Chunky Explosion | `Chunky Explosion.mp3` | CC0 | cut to 2 s |
| `life-lost` | (author not named) | Explosion | `explosion.wav` | CC0 | leading silence removed, cut to 0.98 s |
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
