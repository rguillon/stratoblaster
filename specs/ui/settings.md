# Settings

> **Area:** UI · **Prefix:** `UI-SET` · **Related:** [screen-flow.md](screen-flow.md), [title-screen.md](title-screen.md), [pause-menu.md](pause-menu.md), [menu-input.md](menu-input.md), [../audio/engine.md](../audio/engine.md), [../audio/sfx.md](../audio/sfx.md)

A small settings screen with two volume sliders, Music and Sound effects, reached from the title
and from the pause menu. The values are kept in cookies. How the volumes drive the audio (gain
curve, buses) is in [audio/engine.md](../audio/engine.md).

## Requirements

### UI-SET-01 — Where the settings open from · MUST

The settings screen opens from:
- the title screen, through its **Settings** entry under **Start** (Start stays selected by default);
- the pause menu ([pause-menu.md](pause-menu.md)).

Back (the key, gamepad B, `Escape` or the on-screen Back button) returns to the screen it was opened
from.

**Acceptance criteria**
- Given the settings opened from the title, when Back is pressed, then the title shows; opened from the pause menu, the pause menu shows.

*Sources: P12-R04.*

### UI-SET-02 — Two sliders, nothing else · MUST

The screen has exactly two settings, each a slider of `volume_steps` steps (0 to 10) shown as a bar
of 10 cells, lit up to its value, with the value's number next to it:
- **Music**: the music volume;
- **Sound effects**: the sound effect volume.

There is no master volume, key remapping or graphics setting.

**Acceptance criteria**
- Given the settings screen, then it shows the Music and Sound effects sliders and nothing else to set.

*Sources: P12-R04, D-095.*

### UI-SET-03 — Changing a slider · MUST

The screen opens with Music selected. Up and Down pick a slider (no wrap). Left and Right change the
selected slider by one step, stopping at 0 and 10. Tapping or dragging on a slider's bar selects it
and sets it to the step under the finger.

**Acceptance criteria**
- Given Music at 6, when Right is pressed, then Music is 7; at 10, Right leaves it at 10.
- Given the Sound effects bar, when it is tapped at its left end, then Sound effects is 0 and is the selected slider (e2e).

*Sources: P12-R04.*

### UI-SET-04 — A change is heard at once · MUST

A change is heard at once: the music volume changes the music that is playing, and a slider change
plays a short sample sound (`slider-step`) at the new volume. At 0 the music or the sound effects
are silent ([audio/engine.md](../audio/engine.md)).

**Acceptance criteria**
- Given Sound effects is set to 0, then no sound effect is heard (the SFX bus gain is 0; unit test).
- Given Music is set to 3, then the music bus plays at the gain of step 3 (unit test).

*Sources: P12-R04.*

### UI-SET-05 — Default volumes · MUST

With nothing saved, Music is `music_volume_default` and Sound effects `sfx_volume_default`.

**Acceptance criteria**
- Given no settings cookie, then Music shows 6 and Sound effects shows 8.

*Sources: P12-R04, D-095.*

### UI-SET-06 — The volumes are saved · MUST

The two values are saved in cookies (`<gameId>_music_volume`, `<gameId>_sfx_volume`) on every
change, and read at start. A missing value, or anything but a whole number from 0 to 10, reads as
the default, without error.

**Acceptance criteria**
- Given Music is set to 3, when the page is reloaded, then Music shows 3 and the music plays at that volume.
- Given a cookie value of `banana` or `42`, then the default is used and no error is thrown.

*Sources: P12-R04, D-010, D-095.*

### UI-SET-07 — Over a paused level · MUST

Opened from the pause menu, the settings screen is drawn over the paused level, which shows dimmed
(50 % black) behind it and stays paused while the volumes change.

**Acceptance criteria**
- Given the settings opened from the pause menu, then the last frame of the level shows dimmed behind them and the level does not advance.

*Sources: P12-R02, P12-R04.*

### UI-SET-08 — The screen's look and devices · MUST

The heading "Settings" is at the top, the Back button at the top left and the hint "▲ ▼ to pick ·
◀ ▶ or tap to set" under the sliders. Each slider is a row (label, bar, number) at least 64 px tall;
the selected row is the light cyan block of the menus, its lit cells black. Every target is at
least 44 × 44 CSS px. The screen can be used with the keyboard only, the gamepad only and taps only.

**Acceptance criteria**
- Given the settings at 390 × 844, then every slider and the Back button are at least 44 × 44 CSS px (e2e).

*Sources: P12-R04.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `volume_steps` | 0 … 10 | `src/config/audio.py` `AUDIO_CONFIG.volume_steps` |
| `music_volume_default` | 6 | `AUDIO_CONFIG.default_volumes.music` |
| `sfx_volume_default` | 8 | `AUDIO_CONFIG.default_volumes.sfx` |
| Cookies | `stratoblaster_music_volume`, `stratoblaster_sfx_volume` | `src/app/saved_settings.py` `saved_setting_keys`; kept 365 days (`MENU_CONFIG.cookie_max_age_days`) |
| Slider row | 64 px tall; label 130 px, number 34 px | `index.html` `.settings-slider` |
| Texts | "Settings", "Music", "Sound effects", the hint | `src/game/config/menu_texts.py` `MENU_TEXTS` |
