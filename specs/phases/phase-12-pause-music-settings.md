# Phase 12 — Pause, Music and Settings

> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.
> Drafted by the agent at the reviewer's request (2026-10-26) from GD §2, GD §7, GD-70, GD-71, ENG-54, ENG-110 and ENG-112. Unspecified choices use agent defaults (D-095); the reviewer may change any of them before setting the status to `Ready`.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 11

---

## 🧑 Goal
The player can pause a level at any time, resume it, open the settings or go back to the main menu from the pause menu. The game pauses itself when the tab is hidden. Every level has its own code-generated music, boss fights switch to a more intense track, and every action has a software-generated sound. A settings screen, reachable from the title screen and the pause menu, sets the music and sound effect volumes, which are saved.

## 🧑 Requirements

> ID format `P12-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> Builds on the game flow of GD §7, the menus and their unified input (P01-R09..R12), the level flow (P06-R02, P06-R03), the bosses and checkpoint (P07) and the high score save (P11-R03). Numbers are listed in **Tunable values**.
> Pause, the audio engine (synthesis, sequencer, mixer) and the settings store are game-agnostic engine features (`src/app/`, `src/audio/`, `src/ui/`); the songs, sound designs, key bindings and texts are game data in `src/game/` (`01-engineering.md` §2.3). Audio only reacts to core state and events and never changes them (ENG-11).

### P12-R01 — Pause and resume  · MUST

During a level, the player can pause the game:
- keyboard: `Escape` and `KeyP` (by key position, so QWERTY and AZERTY work), as in GD §2;
- gamepad (standard mapping): Start (button 9) and Select / View (button 8);
- touch: an on-screen pause button (`❚❚`) in the top-right corner of the playfield, at least 44×44 CSS px, that never covers the score, health bar or boss bar.

While paused, nothing in the level advances: no scrolling, no spawns, no movement, no shots, no timers (invincibility, bomb, laser warnings, checkpoint, level end). The last frame stays visible, dimmed, under the pause menu (P12-R02). Resuming continues from exactly the same state: no time is skipped and the fixed-step clock does not catch up the paused time.

In the game screen, `Escape`, `Backspace` and gamepad B no longer leave the level directly (P01-R09, P06-R02, D-041 are superseded for the game screen only; they stay `back` in the menus). Leaving a level goes through the pause menu (P12-R02).

The "Level complete" and "Game over" panels cannot be paused (they are already stopped).

**Acceptance criteria**
- [ ] Given a level, when `Escape`, `KeyP`, gamepad Start or Select, or the touch pause button is pressed, then the game is paused and the pause menu shows (unit test on the controls, e2e by key and touch).
- [ ] Given a paused level for 10 s, when it is resumed, then the level's scroll position, the enemies, shots and timers are exactly as when it was paused (unit test over the simulation state).
- [ ] Given the game screen, when `Backspace` or gamepad B is pressed, then the level does not leave and does not pause.
- [ ] Given the pause button on a 390×844 and an 800×600 screen, then it is fully visible, at least 44×44 CSS px, and overlaps no other HUD element (e2e screenshot check).

### P12-R02 — Pause menu  · MUST

The pause menu is a panel over the dimmed playfield, in the menu look (P01-R13), titled `Paused`, with three entries, navigated with the menu actions (P01-R12):
1. **Resume** (selected when the menu opens): closes the menu and resumes the level.
2. **Settings**: opens the settings screen (P12-R04). Back from the settings screen returns to the pause menu, with the level still paused.
3. **Main menu**: asks `Leave the level?` with **No** (selected by default) and **Yes**. Yes ends the attempt as leaving does today: the high score is saved (P11-R03) and the title screen shows. No returns to the pause menu.

In the pause menu, `back` (`Escape`, `Backspace`, gamepad B) and the pause controls (`KeyP`, gamepad Start) resume the level. Pressing `Escape` twice therefore pauses and resumes.

**Acceptance criteria**
- [ ] Given the pause menu, when Resume is confirmed, then the level resumes (unit test and e2e).
- [ ] Given the pause menu, when `Escape` or gamepad B is pressed, then the level resumes.
- [ ] Given the pause menu, when Main menu then Yes is confirmed with a score of 3 000 and a saved high score of 1 000, then the title screen shows and the high score is 3 000 (e2e).
- [ ] Given the `Leave the level?` question, when No or `back` is chosen, then the pause menu shows again and the level is still paused.
- [ ] Given the pause menu, when Settings is opened and closed, then the pause menu shows again with the level still paused (e2e).
- [ ] The whole pause menu can be used with the keyboard only, the gamepad only and taps only.

### P12-R03 — Automatic pause  · MUST

The level pauses by itself, with the pause menu showing, when:
- the page becomes hidden (`visibilitychange` to `hidden`: tab switched, window minimised, phone locked) (ENG-110);
- the gamepad that was in use is disconnected.

It never resumes by itself: the player resumes from the pause menu. In the menus, a hidden page only silences the audio (P12-R11) until it is visible again.

**Acceptance criteria**
- [ ] Given a level, when the page becomes hidden, then the level is paused and, when the page is visible again, the pause menu shows (e2e with a faked `visibilitychange`).
- [ ] Given a level played with a gamepad, when the gamepad is disconnected, then the level is paused (unit test with a fake gamepad).
- [ ] Given a paused level, when the page is hidden and shown again, then it is still paused.

### P12-R04 — Settings screen  · MUST

A **Settings** screen, in the menu look (P01-R13) and navigated with the menu actions (P01-R12, on-screen Back button P01-R11), reachable:
- from the title screen, as a new **Settings** entry under **Start** (Start stays selected by default);
- from the pause menu (P12-R02).

It has two settings, each a slider of `volume_steps` steps (0 to 10) shown as a bar with its number:
- **Music**: the music volume;
- **Sound effects**: the sound effect volume.

Left / right (keys, D-pad, stick) change the selected slider by one step; tapping or dragging on a slider sets it. A change is heard at once: the music volume changes the music that is playing, and a sound effect slider change plays a short sample sound at the new volume. At 0 the bus is silent.

The values are saved in cookies (D-010, `<gameId>_music_volume`, `<gameId>_sfx_volume`) on every change and read at start. A missing or invalid value reads as the default. Back leaves the screen to where it was opened from.

**Acceptance criteria**
- [ ] Given no settings cookie, then Music shows `music_volume_default` and Sound effects shows `sfx_volume_default`.
- [ ] Given Music is set to 3, when the page is reloaded, then Music shows 3 and the music plays at that volume (unit test on the gain, e2e on the value).
- [ ] Given a cookie value of `banana` or `42`, then the default is used and no error is thrown (unit test).
- [ ] Given Sound effects is set to 0, then no sound effect is heard (the SFX bus gain is 0; unit test).
- [ ] Given the settings opened from the title, when Back is pressed, then the title shows; opened from the pause menu, the pause menu shows.
- [ ] The settings screen can be used with the keyboard only, the gamepad only and taps only, with touch targets of at least 44×44 CSS px.

### P12-R05 — Audio engine  · MUST

All music and sound effects are generated in the browser by code with the Web Audio API (oscillators, noise, filters, envelopes, effects): no audio file is loaded (GD-70, GD-71; ENG-120's audio formats do not apply). The engine has:
- a **music** bus and a **sound effect** bus, each with its own volume (P12-R04), into a master limiter so the output never clips;
- a sequencer that schedules notes ahead on the audio clock, so the music keeps time when frames are slow;
- an unlock step: browsers only start audio after a user gesture, so the audio context starts on the first key press, tap, click or gamepad button (the loading or title screen). Nothing is heard before, and nothing breaks.

If Web Audio is missing or fails, the game runs silently without errors. Generating the audio does not lower the frame rate below the 60 fps pillar on the reference machine.

**Acceptance criteria**
- [ ] Given a production build, then it contains no audio file and fetches none (build test).
- [ ] Given the page has just loaded with no user input, then the audio context is not running and no console warning about autoplay is shown; after the first key press it runs (e2e).
- [ ] Given a browser without `AudioContext`, then every screen works and no error is thrown (unit test with the API removed).
- [ ] Given the busiest level of World 4 with music and effects, then the frame rate stays at 60 fps on the reference machine (manual check, recorded in the report).

### P12-R06 — Level music  · MUST

Every level (`1-1` to `4-5`) has its own music (GD-70), generated from that level's data:
- each world has a style that matches its look, in the cyberpunk / synthwave direction (GD-60): World 1 (desert and sea) bright and driving, World 2 (Frozen North) cold and airy, World 3 (Jungle) percussive, World 4 (Volcanic Lands) dark and heavy;
- the five levels of a world share the world's style (instruments, tempo range) but differ in melody, chords and rhythm, so no two levels sound the same;
- the same level always plays the same music (deterministic from the level's id, never from `Math.random`);
- a track lasts at least `music_loop_min` before it repeats, and loops without a gap or a click.

The music starts with the level and fades out in `music_fade` when the level ends, is left, or is over.

**Acceptance criteria**
- [ ] Given the 20 levels, then their generated note sequences are pairwise different (unit test on the sequencer data).
- [ ] Given level `2-3` generated twice, then both note sequences are identical (unit test).
- [ ] Given any level track, then its loop is at least `music_loop_min` long (unit test).
- [ ] Given each world, then the reviewer can tell the four world styles apart by ear (manual check).

### P12-R07 — Boss music and jingles  · MUST

- When a mini boss or final boss fight starts (its boss bar shows), the level music cross-fades in `music_crossfade` to that world's **boss track**: faster and more intense than its level tracks (GD-70). When the mini boss is destroyed, it cross-fades back to the level track, from its start. After the final boss, the boss track stops with the level end.
- Short jingles, generated like the music, play once: **level complete** (with the "Level complete" panel), **game over** (with the "Game over" panel) and **checkpoint reached** (when the mini boss is destroyed, over the music).
- Continue (P11-R04) restarts the level track.

**Acceptance criteria**
- [ ] Given a level reaches its mini boss, then the boss track is playing within `music_crossfade` and the level track has stopped (unit test on the music state driven by the boss events).
- [ ] Given the mini boss is destroyed, then the level track plays again from its start.
- [ ] Given the 4 worlds, then there are 4 boss tracks, each faster (higher tempo) than every level track of its world (unit test).
- [ ] Given a level completed and a game over, then the matching jingle plays once (unit test on the audio events).

### P12-R08 — Menu music  · MUST

The menus (title, ship select, level select, settings opened from the title) play one calm **menu theme**, generated like the level music, looping. It keeps playing (it does not restart) when moving between these screens, and fades out when a level starts.

**Acceptance criteria**
- [ ] Given the title, when the player goes to ship select and level select, then the menu theme keeps playing without restarting (unit test on the music state).
- [ ] Given a level is confirmed, then the menu theme fades out and the level track starts.

### P12-R09 — Sound effects  · MUST

Every event below plays its own generated sound (GD-71), designed so the player can tell them apart:

| Group | Events |
|-------|--------|
| Player weapons | gun shot, laser start and laser hum while firing, missile launch, weapon switch, weapon level up |
| Enemy weapons | enemy bullet shot, enemy missile launch, laser warning line, enemy laser fire |
| Hits | player shot hits an enemy, player shot hits a shielded or armoured part, player ship is hit |
| Destruction | small enemy explosion, large enemy explosion, boss part destroyed, boss destroyed |
| Player | life lost, extra life, bomb, bomb bonus picked up, weapon bonus picked up, life bonus picked up |
| Menus | move selection, confirm, back, pause, resume, settings slider step |

Sounds that follow a position (shots, hits, explosions) are panned left or right with the x position on the playfield, by at most `sfx_pan_max`.

**Acceptance criteria**
- [ ] Given each event of the table, then the audio layer plays its sound when the core or menu event happens (unit test with a fake audio context, one case per event).
- [ ] Given an explosion at the left edge of the playfield, then its pan is `-sfx_pan_max`; at the centre, 0 (unit test).
- [ ] Given each sound, then the reviewer finds it fits the cyberpunk look and is not unpleasant for a child (manual check).

### P12-R10 — Mixing limits  · MUST

So that busy screens stay pleasant:
- at most `sfx_voices_max` sound effects play at once; when full, a new sound replaces the oldest playing sound of lower or equal priority (player sounds and bombs have the highest priority, enemy shots the lowest);
- the same sound started again within `sfx_retrigger_min` is not played twice (it may be made a bit louder instead);
- the player's gun shots and the laser hum are mixed quieter than hits and explosions, so holding the fire button is not tiring;
- the master limiter keeps the output under `master_peak` and short flashes of sound (bombs, big explosions) are not louder than `loudest_sfx` relative to the music.

**Acceptance criteria**
- [ ] Given 40 explosions in one frame, then at most `sfx_voices_max` sounds play (unit test).
- [ ] Given the same hit sound requested twice 10 ms apart, then it plays once (unit test).
- [ ] Given a player sound requested while all voices are taken by enemy shots, then it plays (unit test).

### P12-R11 — Audio follows pause and the page  · MUST

- When the game pauses (P12-R01, P12-R03), the level or boss music pauses at its position and every playing sound effect stops. Resuming continues the music from the same position. The menu sounds of the pause menu and the settings screen still play.
- When the page is hidden, all audio is silenced (the audio context is suspended) and resumes when the page is visible again.
- Leaving a level from the pause menu fades the music out and starts the menu theme on the title.

**Acceptance criteria**
- [ ] Given a level track 30 s in, when the game is paused for 10 s and resumed, then the track continues from about 30 s, not 40 s (unit test on the sequencer position).
- [ ] Given the page is hidden, then the audio context is suspended; visible again, it runs (e2e with a faked `visibilitychange`).
- [ ] Given the pause menu, when the selection moves, then the menu move sound plays.

### P12-R12 — Test API  · MUST

In e2e builds, `getState()` also gives `paused` (true / false), the current screen including `pause` and `settings`, the music and sound effect volumes, the playing music track id (for example `level-2-3`, `boss-2`, `menu`) and the last sound effects played (event names, most recent last); `sendAction` accepts `pause` and `resume`. The existing test-only `pause()` (ENG-52) stays separate from the game's pause. None of it ships in the production bundle.

**Acceptance criteria**
- [ ] Given an e2e build, when `sendAction('pause')` is sent in a level, then `getState().paused` is true and the screen is `pause`.
- [ ] Given a level 2-3 is playing, then `getState()` reports the track `level-2-3`; during its mini boss fight, `boss-2`.
- [ ] Given a gun shot, then `getState()` lists the gun shot sound among the last sound effects.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| pause keys / buttons | `Escape`, `KeyP`; gamepad 9, 8; touch `❚❚` button | P12-R01 (GD §2) |
| pause_dim | 50 % black over the playfield | P12-R01 |
| volume_steps | 0 … 10 | P12-R04 |
| music_volume_default | 6 | P12-R04 |
| sfx_volume_default | 8 | P12-R04 |
| volume curve | gain = (step / 10)², 0 = silent | P12-R04; perceived loudness is closer to linear |
| music_loop_min | 60 s | P12-R06 |
| music_fade | 1 s | P12-R06, P12-R08 |
| music_crossfade | 1 s | P12-R07 |
| level tempo range | World 1: 120–132 BPM; World 2: 100–112; World 3: 112–124; World 4: 90–104 | P12-R06; boss tracks 20–30 BPM faster than their world |
| sfx_pan_max | 0.6 | P12-R09 |
| sfx_voices_max | 16 | P12-R10 |
| sfx_retrigger_min | 30 ms | P12-R10 |
| master_peak | −1 dBFS | P12-R10 |
| loudest_sfx | +6 dB over the music at equal volume settings | P12-R10 |
| scheduler lookahead | 100 ms, checked every 25 ms | P12-R05 |

## 🧑 Out of scope for this phase
- Any graphics setting.
- Key and button remapping, a "reduce flashes & screen shake" option, colour-blind bullet colours (ENG-112): a later phase.
- A master volume slider, a mute shortcut key, and a separate volume for the menu sounds.
- Audio files, recorded samples, voices, and music that changes with the score or the player's health.
- A countdown before resuming, and pausing the "Level complete" and "Game over" panels.
- Rebinding `Escape` in the menus: it stays `back` there (P01-R09).

## 🧑 Engineering additions for this phase
- `src/audio/` holds the game-agnostic engine (context and unlock, buses and limiter, voices and priorities, sequencer, synth building blocks); `src/game/view/audio/` (or `src/game/config/audio/`) holds the songs, sound designs and their tunables (ENG-141, ENG-142). The level → track and event → sound mappings are game data.
- Unit tests run against a fake `AudioContext` (no real audio in Node). Music generation is a pure function of the level data and a seeded RNG (`src/core/math/rng.ts`), so it is unit tested without audio.
- The ENG-54 smoke suite gains its pause / resume step (`sendAction('pause')`, then `resume`), and a hidden-page auto-pause check.
- e2e runs with audio unlocked by a key press and asserts no console error or warning from audio on every page.
- `docs/architecture.md` describes the audio layer and the pause state (ENG-131).

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] `Escape`, `P`, gamepad Start and the touch `❚❚` button pause; Resume, `Escape` and gamepad B resume; nothing moves while paused
- [ ] Main menu → Yes leaves the level and keeps a new high score; No stays paused
- [ ] Switching tab during a level pauses it and silences the game
- [ ] Each world's music has its own mood, levels of a world sound different, and the music loops without a click
- [ ] The boss track kicks in with the boss bar and goes back to the level track after the mini boss
- [ ] Every action has a sound; holding fire with the guns or laser is not tiring; a full World 4 screen is not too loud
- [ ] The Music and Sound effects sliders change the volume at once and are kept after a reload; 0 is silent
- [ ] Still 60 fps in the busiest World 4 level with sound on

## 🧑 Notes, references, sketches
- GD §2 binds Pause to `Esc / P`, while P01-R09, P06-R02 and D-041 made `Esc` leave the level. This phase follows GD §2 in the game screen and keeps `Esc` as Back in the menus. The reviewer may update P06-R02 and D-041's wording.
- The GD §7 flow becomes: `Game ──pause──▶ Pause ──resume──▶ Game`, `Pause ──settings──▶ Settings ──back──▶ Pause`, `Pause ──main menu, yes──▶ Title`, and `Title ──settings──▶ Settings ──back──▶ Title`.
- ENG-07 / ENG-120 mention `localStorage` and OGG / MP3 audio files; settings use cookies (D-010) and audio is generated (GD-70, GD-71), so neither applies.
- Pause menu sketch (480×640 logical):
```
            ┌──────────────────┐
            │      PAUSED      │
            │                  │
            │   ▶ Resume       │
            │     Settings     │
            │     Main menu    │
            └──────────────────┘
```
- Settings sketch:
```
   SETTINGS

   ▶ Music          ██████░░░░  6
     Sound effects  ████████░░  8

   [ Back ]
```

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 12"**.
> The agent ticks each item when fixed.

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
<!-- Ambiguities found before implementing. If non-empty, agent stops and waits. -->

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Menu actions `pause`, `resume`, `cancel` (Escape) and a slider `set` command; P / Escape / Start / Select bindings; `Backspace` and B do nothing in a level; gamepad-in-use disconnect detection in `GameControls` | P12-R01, P12-R03 |
| `MenuFlow`: `pause` and `settings` screens (`core/menu/menu-screen.ts`), pause menu (Resume / Settings / Main menu + `Leave the level?`), Settings entry on the title, volumes in the flow state; the level kept alive and frozen while paused (`GameSession`, `start-app` frame ticker) | P12-R01, P12-R02, P12-R04 |
| Settings saved in cookies (`app/saved-settings.ts`), read at start, invalid values → defaults | P12-R04 |
| Views and screens: pause panel over a 50 % dim, `❚❚` button, settings screen with two sliders (keys, taps, drag), CSS | P12-R01, P12-R02, P12-R04 |
| Auto pause on `visibilitychange` and on the gamepad in use disconnecting; audio context suspended while hidden | P12-R03, P12-R11 |
| `src/audio/`: output (lazy context, unlock on first gesture, music / SFX buses, master limiter, silent fallback), volume curve, lookahead sequencer, synth voices, voice pool (limits, priorities, retrigger), music player (cross-fades, fades, pause at position), level cue extraction from core state | P12-R05, P12-R07, P12-R09, P12-R10, P12-R11 |
| Core: `ShotImpact.blocked` (a hit that did no damage, e.g. on a shielded core) | P12-R09 |
| `src/game/view/audio/`: per-world styles, seeded level / boss / menu composers, jingles, instruments, sound designs, cue → sound map | P12-R06, P12-R07, P12-R08, P12-R09, P12-R10 |
| Music director in `app/`: menu theme across menus, level / boss tracks from the boss bar, jingles, fades on leave / complete / over, Continue restarts the level track | P12-R06, P12-R07, P12-R08, P12-R11 |
| Test API: `paused`, screens, volumes, music track id, last sounds; `pause` / `resume` actions; build check for audio files | P12-R12, P12-R05 |
| Unit tests (fake `AudioContext`, pure composers / sequencer / pool), e2e (pause, settings, audio unlock, hidden page), existing e2e moved from `back` to the pause menu; docs | all |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P12-R01 | | | | |

### Gate results
```
make check output summary: lint ✔ / typecheck ✔ / tests N passed / coverage xx% / build ✔
```

### How to test manually
<!-- Steps, keys, debug toggles, URL. -->

### Deviations from spec
<!-- Anything done differently and why. Also logged in DECISIONS.md. -->

### Known limitations
-

### Suggestions for future phases
-
