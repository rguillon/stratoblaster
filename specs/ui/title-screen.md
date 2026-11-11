# Title screen

> **Area:** UI · **Prefix:** `UI-TITLE` · **Related:** [screen-flow.md](screen-flow.md), [look-and-layout.md](look-and-layout.md), [settings.md](settings.md), [ship-select.md](ship-select.md), [../dev/dev-menu.md](../dev/dev-menu.md), [../gameplay/scoring.md](../gameplay/scoring.md), [../01-engineering.md](../01-engineering.md)

The first screen after loading: the high score, the game's name as a chrome logo, the Start and
Settings entries, a short controls hint and the build's version, over a 3D neon trench generated in
code, the balanced ship racing down it towards the camera, speed streaks rushing past. The same 3D
backdrop stays behind the other menu screens.

## Requirements

### UI-TITLE-01 — What the title shows · MUST

From top to bottom, the title screen shows:
1. the **high score**: a small label ("High score") over its value (UI-TITLE-03);
2. the **logo**: the game's name ([look-and-layout.md](look-and-layout.md), UI-TITLE-02);
3. **Start**, selected by default;
4. **Settings** ([settings.md](settings.md));
5. **Full screen**, only where the browser allows full screen (UI-TITLE-11);
6. **Dev**, only with `?dev` in the URL ([dev/dev-menu.md](../dev/dev-menu.md));
7. a short controls hint (UI-TITLE-05);
8. the version and short commit hash, small, in the bottom right corner (UI-TITLE-04).

It has no Back button.

**Acceptance criteria**
- Given the title screen, then it shows the high score, the logo, Start (selected), Settings, the hint and the version, and no Back button.
- Given no `?dev` in the URL, then there is no Dev entry.

*Sources: P01-R04, P12-R04.*

### UI-TITLE-02 — The game's name · MUST

The game is called **Stratoblaster**. The name comes from the game's data (`GAME_CONFIG.title`), is
shown as the logo, and is also the page's title.

**Acceptance criteria**
- Given the title screen, then the logo reads "Stratoblaster" and the browser tab's title is "Stratoblaster".

*Sources: P01-R04, D-016.*

### UI-TITLE-03 — The high score · MUST

The high score is read from its cookie (`<gameId>_high_score`, i.e. `stratoblaster_high_score`).
It is `0` when there is no cookie yet. A value that is not a plain non-negative whole number reads
as `0`, without error. When a level attempt beats it, the new high score is saved
([gameplay/scoring.md](../gameplay/scoring.md)) and the title shows it from then on, also after a
reload.

**Acceptance criteria**
- Given no high-score cookie, then the title screen shows a high score of `0`.
- Given a high-score cookie with value `12345`, then the title screen shows `12345`.
- Given a corrupted cookie value (`not-a-score`), then the title screen shows `0` and no error is thrown.
- Given a saved high score of 1 000, when a level is left from the pause menu with 3 000 points, then the title shows `3000`, also after a reload (e2e).

*Sources: P01-R04, GD-51, P11-R03, D-010, D-016.*

### UI-TITLE-04 — Version and commit · MUST

The bottom right corner shows `v<version>` over the short commit hash, in small monospace green
text. Both are written into the build from git (ENG-83): the version is the latest release tag,
the commit the short hash of the built commit; either reads `unknown` when git cannot tell.

**Acceptance criteria**
- Given a build, then the title shows `v` and the version of the build, and a short hash of 7 or more hex digits (or `unknown`) (e2e).
- At 800 × 600, 1920 × 1080 and 390 × 844, the version is fully inside the window.

*Sources: P01-R04, ENG-83.*

### UI-TITLE-05 — The controls hint · MUST

A short hint near the bottom tells how to start: "Press Space / Enter or tap to start" (game texts,
`startHint`). It is in the secondary text colour and does not move
([look-and-layout.md](look-and-layout.md)).

**Acceptance criteria**
- Given the title screen, then the hint contains "Space / Enter".

*Sources: P01-R04.*

### UI-TITLE-06 — Moving on the title · MUST

Up and down move between Start, Settings (and Full screen, and Dev); the selection does not wrap.
Confirming Start opens the ship select screen; Settings opens the settings screen; Full screen
toggles the page's full screen and stays on the title (UI-TITLE-11); Dev opens the dev menu. Back
does nothing. Coming back from the settings screen or the dev menu, the entry that opened it is
still selected; coming back from anywhere else (the ship select screen, or leaving a level), Start
is selected.

**Acceptance criteria**
- Given the title with Start selected, when Down then Confirm are pressed, then the screen is `settings`; when Back is pressed there, then the title shows with Settings selected.
- Given the title with Settings selected, when Down is pressed without a Dev entry, then Settings stays selected.

*Sources: P01-R04, P12-R04, P01-R01.*

### UI-TITLE-07 — The ship racing down a neon trench · SHOULD

Behind the menu, a 3D scene generated in code (owner, 2026-11-11, D-325; a night city street
before): the balanced player ship races down a deep trench, seen from the front, its nose towards
the camera. The camera flies backwards ahead of it, a little above, looking down the trench behind
it. The trench has a dark floor and two tall walls of panels of uneven depth, with lit slots, a
neon strip along the foot of each wall, lit ribs across the floor and a dashed guide line down its
middle; it scrolls away behind the ship at `title_trench_speed` and loops forever, its far end lost
in haze in front of a glowing sky. Fast speed streaks (`title_streaks`) rush past the ship and the
camera, faster than the trench, so the ship reads as flying fast. The ship sways from side to side,
banking into each turn, and floats gently up and down (`title_ship_sway`, `title_ship_float`). The
trench and the streaks come from a fixed seed, so they are the same on every run. No model or
texture is downloaded.

**Acceptance criteria**
- The background is animated and generated in code (no downloaded model or texture).
- Two builds of the trench and of the streaks give the same geometry (unit test with the seed).
- Unit test: each frame scrolls the trench and the streaks away from the camera, the streaks faster,
  and both loop; the ship faces the camera, sways, banks into the sway and floats.

*Sources: P01-R05, D-014, D-104, D-325.*

### UI-TITLE-08 — Dark, in neon blue and green · MUST

The backdrop is dark and follows the menus' cyan scheme
([look-and-layout.md](look-and-layout.md)): a deep blue glow low in the sky through teal to black
higher up, a deep blue-black haze, near-black trench floor and blue-grey walls, cyan, green and
blue slots, strips, ribs and guide line, cyan and white streaks (D-198, D-325; the synthwave dusk
of D-323 was undone by D-324).

**Acceptance criteria**
- Unit test: the sky, haze, floor and wall colours stay dark; the neon and streak colours stay bright.
- Manual check: no magenta, violet or red in the backdrop.

*Sources: P01-R05, D-012, D-198, D-324.*

### UI-TITLE-09 — The backdrop stays behind the menus · MUST

The backdrop is drawn behind every menu screen: the title, the ship select screen (where its own
ship is hidden, as that screen shows the ships itself, [ship-select.md](ship-select.md)), the level
select screen, and the settings screen opened from the title. It is not drawn while a level is
played or paused, nor during the boot loading screen.

**Acceptance criteria**
- Given the ship select screen, then the backdrop's ship is hidden; back on the title, it shows again.

*Sources: D-008.*

### UI-TITLE-10 — The backdrop keeps 60 FPS · SHOULD

The title screen keeps 60 FPS on the reference hardware (ENG-101). The trench is drawn in a handful
of draw calls (each stretch of trench is two merged, vertex-coloured meshes: its dark structure,
kept out of the glow, and its lights, which glow; the streaks are one merged mesh per stretch). The
neon is drawn at `title_neon_intensity`, so the glow and the tone mapping do not wash the lights
into white blobs.

**Acceptance criteria**
- Manual check with the FPS tile or the browser performance tools: 60 FPS on the title.

*Sources: P01-R05, D-014.*

### UI-TITLE-11 — Full screen · MUST

Where the browser allows the page to go full screen (`document.fullscreenEnabled`), the title has
a **Full screen** entry between Settings and Dev. Confirming it asks the browser for full screen
(the whole page, `documentElement`); in full screen it reads **Exit full screen** and confirming
it leaves. The entry follows the page: when the browser leaves full screen by itself (Escape), the
entry reads Full screen again. A refused request (no user gesture, a browser's policy) changes
nothing and throws nothing. The flow reports the confirmation as `fullscreen` feedback and stays
on the title; the app toggles the page (`app/page_fullscreen.py`). Where the browser allows no
full screen (an iPhone's Safari), there is no entry.

**Acceptance criteria**
- Given a browser that allows full screen, then the title shows the Full screen entry after
  Settings and before Dev; given one that does not, then it shows none (unit tests).
- Given the Full screen entry confirmed, then the page's full screen is toggled and the title
  stays, with the entry selected; once the page is full screen, the entry reads "Exit full screen"
  (unit tests).
- e2e: on the title, Down, Down selects `fullscreen`; Enter keeps the title and raises no console
  error.

*Sources: owner request, D-248.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `title_trench_speed` | 60 units/s | `src/game/config/title_look.py` `TITLE_LOOK["trench"]["speed"]` |
| Trench stretch | 160 units long, 10 wide, walls 16 high | `TITLE_LOOK["trench"]`; two stretches end to end |
| `title_streaks` | 220 streaks, 2 to 7 units long, 160 units/s | `TITLE_LOOK["streaks"]`; two stretches of 60 units |
| `title_ship_sway` | 0.8 units at 0.18 Hz, banking up to 0.35 rad | `TITLE_LOOK["ship"]` `swayAmplitude`, `swayHz`, `bankRad` |
| `title_ship_float` | 0.2 units at 0.5 Hz | `TITLE_LOOK["ship"]` `bobAmplitude`, `bobHz` |
| Camera | at (0, 2.4, 10), looking at (0, 0, -30) | `TITLE_LOOK["camera"]`; ahead of the ship, facing it |
| Trench seed | 2077 | `TITLE_LOOK["seed"]` |
| Fog | 20 to 140 units | `TITLE_LOOK["fog"]` |
| `title_neon_intensity` | 0.45 | `TITLE_LOOK["neonIntensity"]` |
| Colours | see UI-TITLE-08 | `TITLE_LOOK` (`horizon`, `sky.stops`, `trench.colors`, `NEON`, `WINDOW_COLORS`, `streaks.colors`) |
| `cookie_max_age` | 365 days | `src/config/menu.py` `MENU_CONFIG.cookie_max_age_days` |

## Notes

- For a short time the reviewer had the menu ship replaced by a wireframe, then anime-styled fighter
  pilot; it was reverted to the balanced ship and the pilot code deleted (D-104). The striped sun of
  the synthwave and darksynth looks is gone too.
- The night city street with its towers, signs, skyline and rain (D-012, D-014) was replaced by the
  trench (D-325, owner: "I want the ship to move like it is in a trench with a frontal facing
  camera, no more city background, put fast moving particles making it look like the ship flies
  fast").
