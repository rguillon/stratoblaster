# Dev menu and viewers

> **Area:** Dev · **Prefix:** `DEV-MENU` · **Related:** [debug-options.md](debug-options.md), [perf-tools.md](perf-tools.md), [../ui/title-screen.md](../ui/title-screen.md), [../ui/screen-flow.md](../ui/screen-flow.md), [../ui/menu-input.md](../ui/menu-input.md), [../graphics/player-ships.md](../graphics/player-ships.md), [../graphics/props.md](../graphics/props.md), [../graphics/traffic.md](../graphics/traffic.md), [../enemies/common.md](../enemies/common.md), [../bosses/common.md](../bosses/common.md)

With `?dev` in the URL, the title screen gets a Dev entry. It opens a menu of viewers, which show the
game's models and levels drawn as in game, one at a time: the player ships, the enemies, the bosses,
the props (with the cars) and the levels, and two audio viewers that play the game's sounds and
music on demand (DEV-MENU-19, DEV-MENU-20). They are for checking the look and the sound by hand.
The viewers are screens of the game page, reached through the menus; they replace the separate
debug pages of the earlier phases (`player_ship/`, `player_shots/`, `enemies/`, `bosses/`, `props/`,
`level_zero/`). There is no viewer of the player shots. The URL options that start a level straight
away are in [debug-options.md](debug-options.md).

## Requirements

### DEV-MENU-01 — A Dev entry with `?dev` · MUST

With `dev` in the URL query (`?dev`, with or without a value), the title screen has a last entry,
`Dev`, after Settings. Confirming it opens the dev menu (DEV-MENU-03). Without `dev` there is no Dev
entry and no viewer. It works in every build, the deployed one included, so the models can be
checked on the live site.

**Acceptance criteria**
- Given the game opened without `?dev`, then the title screen has no Dev entry.
- Given `?dev`, then the title screen's last entry is `Dev`, and confirming it shows the dev menu.

*Sources: D-199, D-004.*

### DEV-MENU-02 — The viewers are part of the game page · MUST

The viewers live inside the game page and its menus. There are no separate debug pages, routes or
page entries: only the game page is built. A viewer is built when it is opened and dropped when it is
left.

**Acceptance criteria**
- Given the build output, then it has one page (`index.html`) and no viewer page.
- Given a viewer left with Back, then its scene is disposed of.

*Sources: D-187, D-199.*

### DEV-MENU-03 — The dev menu · MUST

The dev menu has the heading `Dev tools`, one entry per viewer in this order: `Player ships`,
`Enemies`, `Bosses`, `Props`, `Levels`, `Sounds`, `Music`, the hint `▲ ▼ to pick · Enter or tap to
open`, and the Back button. ▲ ▼ move the selection, Confirm or a tap opens the viewer selected, and
Back returns to the title screen with the Dev entry selected. It takes the menus' usual input
(keyboard, gamepad, mouse and touch, [../ui/menu-input.md](../ui/menu-input.md)).

**Acceptance criteria**
- Given the dev menu, when Enemies is confirmed, then the enemies viewer opens on its first item.
- Given the dev menu, when Back is pressed, then the title screen shows with Dev selected.

*Sources: D-199.*

### DEV-MENU-04 — Developer texts · SHOULD

The dev menu and the viewers are a developer tool: their texts are in English only and live with
the viewers' tunables, not with the game's translated menu texts.

*Sources: D-199.*

### DEV-MENU-05 — A viewer's screen · MUST

A viewer draws its 3D view over the whole screen and shows over it:
- the Back button and the viewer's name as its heading;
- a caption with the item's name, its place in the list (`3 / 11`; in a grouped list its group and
  its place in the group, `Tiles: docks · 1 / 5`) and a status line;
- the scrolling menu of its items down the left side (DEV-MENU-07);
- the hint at the bottom, which lists the viewer's controls.

The status line says `Building…` while the viewer's scene is being built; the levels viewer shows
the time and the level's length (`1:24 / 4:05`); the props viewer shows `1 square = 1 block`. Until
its scene is built, the menu backdrop shows behind it.

**Acceptance criteria**
- Given the enemies viewer, then its caption names the enemy shown and its place in the list.
- Given a viewer whose scene is not built yet, then its status line reads `Building…`.

*Sources: D-199, D-202, D-205, D-206.*

### DEV-MENU-06 — Moving through a viewer · MUST

In a viewer:
- ◀ ▶ show the item before or after, round the list; ▲ ▼ do the same, except in a grouped list,
  where they jump to the first item of the group before or after, round the list;
- Confirm flips the viewer's toggle: close-up or game size in the model viewers (DEV-MENU-09), play
  or stop in the levels viewer (DEV-MENU-18);
- Back (or Esc) returns to the dev menu.

A list of one item does not move. Each viewer keeps its item and its toggle while the page is open,
so it opens again where it was left. The model viewers start in close-up, the levels viewer stopped.

**Acceptance criteria**
- Given the enemies viewer on its last enemy, when ▶ is pressed, then it shows the first one.
- Given the props viewer, when ▼ is pressed, then it shows the first prop of the next group.
- Given a viewer left and opened again, then it shows the same item.

*Sources: D-199, D-202, P05-R11.*

### DEV-MENU-07 — The scrolling menu · MUST

Every viewer shows a menu that scrolls up and down, in a panel down the left side of the screen. It
lists the viewer's items; in a grouped list (the props) each group's heading comes before its items,
with the group's number of items (`Tiles: docks (5)`). A tap on an item shows it; a tap on a heading
shows its group's first item. The item shown is filled, and its group's heading outlined. Each time
the item changes, the menu is scrolled so the item shown is in its middle. The wheel over the menu
scrolls it, and a touch drag pans it; a drag that starts on the menu does not turn the model. Long
names are cut with an ellipsis.

**Acceptance criteria**
- Given the props viewer, when a group heading is tapped, then the group's first prop is shown.
- Given the item changes, then the menu is scrolled so the item shown is in its middle.
- Given the wheel turned over the menu, then the menu scrolls and the model does not zoom.

*Sources: D-204, D-206, D-208.*

### DEV-MENU-08 — Drawn as in game · MUST

The viewers show the models as the game draws them: the game's own models, materials, lights,
environment, glow and edge trim, with the game's camera. The ships and levels viewers build a
level's scene as a level is built, after its ground is ready (it comes from the ground worker); the
enemies and bosses viewers use a level's light without its ground (DEV-MENU-13); the props viewer has
its own stage (DEV-MENU-16).

**Acceptance criteria**
- Given a ship, an enemy or a boss in a viewer, then it has the same materials, lights and edge trim
  as in a level.

*Sources: D-199, D-222.*

### DEV-MENU-09 — Close-up or game size · MUST

In the model viewers, Confirm switches between the **close-up**, where the model fills
`close_up_fill` of the screen's height, and **game size**, where it is as big as in game. Over a
level's scene (ships, enemies, bosses) the close-up narrows the camera's field of view, so the
ground is magnified with the model and nothing else changes; the props viewer brings its camera
closer instead (DEV-MENU-17).

**Acceptance criteria**
- Given a ship in close-up, then it fills about 35 % of the screen's height; given game size, then
  it is drawn as in a level.

*Sources: D-199.*

### DEV-MENU-10 — Dragging turns the model · MUST

A mouse or finger drag over a model viewer turns the model by `turn_per_pixel` per pixel. A ship, an
enemy or a boss turns round its nose (horizontal drag) and nose up or down (vertical drag), on top of
the heading and bank the game gives it; a prop's camera turns round the prop (DEV-MENU-17). The
turn is kept from one item to the next, so models compare at the same angle, and is reset when the
viewer is opened again. A drag that starts on the Back button or the menu does not turn the model.

**Acceptance criteria**
- Given a ship turned by a drag, when the next ship is shown, then it is at the same angle.

*Sources: D-199.*

### DEV-MENU-11 — The wheel zooms · MUST

In the model viewers (ships, enemies, bosses, props), the mouse wheel zooms: turning it up zooms
in, down zooms out, by e^(`zoom_per_pixel`) per pixel of wheel, within `zoom_range` of the view
without zoom. The zoom is kept from one model to the next, like the turn, and reset when the viewer
is opened again. Over a level's scene it narrows the field of view on top of the close-up's; in the
props viewer it brings the camera closer, keeping the field of view. The wheel never changes the
model: ◀ ▶, ▲ ▼ and the menu do. Over the menu the wheel scrolls the menu (DEV-MENU-07).

**Acceptance criteria**
- Given a model viewer, when the wheel turns up, then the model looks bigger; it never grows past 8
  times nor shrinks under a quarter of its size without zoom.

*Sources: D-208.*

### DEV-MENU-12 — The ships viewer · MUST

The ships viewer shows each player ship (in the game's order: Balanced, Heavy, Light) at the middle
of the view, on the playfield of the first level (1-1), over its ground, with its animations (its
reactor flames).

**Acceptance criteria**
- Given the ships viewer, when the ground of 1-1 is ready, then the first ship shows at the middle
  of the view in close-up.

*Sources: D-199, D-004.*

### DEV-MENU-13 — The enemies viewer · MUST

The enemies viewer shows each enemy kind, in the game's order, one at a time, living its own life
as in a level, pinned at the middle of the view:
- it is spawned where its kind brings it in, with fixed random numbers (`model_seed`), and stepped
  at the game's rate in a world that has the playfield and the player at the bottom middle;
- its moves turn it, its turrets aim, its joints, limbs and rings move and its lights charge, but it
  is drawn at the middle of the view, with its own heading;
- what it fires or sends out is not kept or shown;
- once it is gone, has left the playfield after entering it, or is older than the game lets an enemy
  get (`max_enemy_age`), a new one is spawned.

The scene has no ground: no terrain, roads, props, sea or clouds, and nothing waits for the ground
worker. It has the light of the first level (its atmosphere at the start) and its sky reflections,
the game's playfield camera and the playfield layer, over a plain dark backdrop.

**Acceptance criteria**
- Given the enemies viewer, then the first enemy shows at once, moving as in game, at the middle of
  the view.
- Given an enemy that leaves the playfield, then a new one of its kind comes in.

*Sources: D-199, D-222, P05-R11, P16-R10.*

### DEV-MENU-14 — The bosses viewer · MUST

The bosses viewer shows each boss, in the game's order, as the enemies viewer shows the enemies
(DEV-MENU-13): with no ground, living its own life pinned at the middle of the view. A boss comes in
and runs its first-stage patterns; it does not expire. K (`break_key`) breaks its next part, as K does
in a level in debug mode ([debug-options.md](debug-options.md) DEV-OPT-09): the part's blast, the
transformations and, once only the core is left, the boss's death, drawn with the game's explosions
where the boss is shown. A new boss then comes in. The bosses viewer's hint names K. K does nothing in
the other viewers.

**Acceptance criteria**
- Given the bosses viewer, when K is pressed, then the boss's next part blows up where the boss is
  shown.
- Given K pressed until the boss dies, then a new boss of the same kind comes in.

*Sources: D-199, D-222, P07-R09, P16-R10.*

### DEV-MENU-15 — What the props viewer lists · MUST

The props viewer lists every prop that a level stands on its ground (the building groups and trees
its sections allow, its floating props, lines, podiums and set pieces), and every kind of car a level
drives on its roads. Each is listed once, shown with the materials of the first level that has it
(its world's tone). The props are listed in the order of the game's prop groups (the tile groups,
`Buildings`, `Cars`...), the cars last under `Cars`, and the props in no group after them under
`Other`. Groups with no such prop (the road kit) are left out.

**Acceptance criteria**
- Given the props viewer, then every prop placed in a level and every car kind is in its menu, under
  its group.
- Given the props viewer, then the road kit pieces are not listed.

*Sources: D-199, D-202, D-209.*

### DEV-MENU-16 — The props stage · MUST

The props viewer loads no level's ground. One scene, built once when the viewer opens, shows the
prop picked alone, standing on a dark floor ruled with a line on every block's edge (the game's tile,
`block` ground units); the status line says `1 square = 1 block`. The prop's footprint covers whole
squares: centred on a line for an even number of blocks, in a square for an odd one. The floor
reaches `grid_reach` blocks beyond the footprint each way. The prop is lit by studio lights: a
hemispheric light, a key light and a fill light from the other side, plus the image-based lighting
and the glow (its windows glow). A car is drawn at the scale the levels draw the cars (`car_scale`),
so it reads true against the grid at game size; the close-up still fits it to the screen.

**Acceptance criteria**
- Given a prop 3 blocks across and 4 along, then it covers exactly 3 × 4 squares of the grid.
- Given a car at game size, then it is as big against the grid as it is in a level.

*Sources: D-205, D-209.*

### DEV-MENU-17 — The props camera · MUST

The props camera orbits the prop. A drag across turns it round the prop, a drag up or down raises
or lowers it, kept within `pitch_range` from straight up. At game size it is at the game camera's
distance from the ground (in ground units), with the game's field of view, so the prop is as big as
in game; the close-up comes closer, until the prop fills `close_up_fill` of the screen's height; the
wheel's zoom then brings it closer still. The prop is drawn right of the middle, by `view_shift` of
half the view's width, so the menu on the left does not hide it.

**Acceptance criteria**
- Given a drag up, then the camera rises, and never past `pitch_range`.
- Given game size, then the prop is drawn at the size the game draws it.

*Sources: D-203, D-205, D-206, D-208.*

### DEV-MENU-18 — The levels viewer · MUST

The levels viewer flies over a level's scenery only (no enemies, no ship, no HUD), in the order of
the level select (1-1 to 4-5). The arrows change the level. The wheel scrubs the level's time back
and forth: `scrub_seconds` per `wheel_step` pixels of wheel, within the level's length, and the view
eases to the time asked (`scrub_ease` per second). Confirm plays or stops the level: playing, its
time goes on at the level's pace. The status line shows the time and the level's length (`m:ss /
m:ss`). The viewer waits for the level's ground before it builds its scene.

**Acceptance criteria**
- Given the levels viewer, when the wheel turns down, then the view moves on along the level and the
  time shown grows; it never goes past the level's length.
- Given Confirm, then the level scrolls on at its own pace; Confirm again stops it.

*Sources: D-199.*

### DEV-MENU-19 — The sounds viewer · MUST

The sounds viewer lists every sound effect of the game, one button per cue (`fire:bullet`,
`enemy-bullet`, `menu-move`...; [../audio/sfx.md](../audio/sfx.md)), in the game's order, in a grid
of three a row that fills the screen and scrolls, under the heading `Sounds`. It draws no scene:
the menu backdrop shows behind it, and the menu theme goes on. The sound picked plays as in game,
unpanned, at the settings' volume: the arrows pick the sound before or after (round the list) and
play it, a press on a button picks and plays it at once (on the press, not the release), Confirm
(or a press on the button picked) plays it again, and a button held plays its sound again after
`hold_delay`, then every `hold_interval`, until the pointer is let go or leaves the screen.
Opening the viewer plays nothing. The item picked gives no menu sound (its feedback is
`played`, not `moved`), so nothing covers the sound. A looping sound (the laser hum) plays until
another sound is picked or the viewer is left. The status line under the heading says
`Playing: <name>` with the name of the sound played. The hint reads `Arrows or tap: play a sound ·
Hold a button: repeat it · Enter: play it again · Esc: back`.

**Acceptance criteria**
- Given the sounds viewer, then it has one button per sound cue, the first `fire:bullet`.
- Given ▶ pressed on `fire:bullet`, then `missile-launch` is the last sound played and the status
  says `Playing: missile-launch`; no `menu-move` plays.
- Given a tap on a button, then its sound plays; given Enter, then it plays again.
- Given a button held for a second, then its sound plays at least twice more; let go, it plays
  no more.

*Sources: D-238.*

### DEV-MENU-20 — The music viewer · MUST

The music viewer lists every track the game plays, each once, labelled by its id, under the
heading `Music`, in the groups `Menu` (the menu theme), `Levels` (one track per level, in the level
select's order), `Bosses` (each boss track once: several levels share one) and `Jingles`
(`complete`, `over`, `checkpoint`; [../audio/music.md](../audio/music.md)), in the sounds viewer's
grid. The tracks are composed when the dev menu is set up (so each boss track is listed once), and
kept, as in game. The track picked plays from its start as in game: ◀ ▶ pick the track before or
after and play it, ▲ ▼ jump to the group before or after, a tap on a button picks and plays it,
Confirm plays it again. A level or boss track replaces the music playing (cross-faded); a jingle
plays once over it. Opening the viewer plays nothing: the menu theme goes on until a track is
picked, and the menus leave the music to the viewer while it is open. Back to the dev menu, the
menu theme returns. The status line says `Playing: <track id> · m:ss` with the track playing and
the time into it. The hint reads `◀ ▶ or tap: play a track · ▲ ▼: group · Enter: play it again ·
Esc: back`.

**Acceptance criteria**
- Given the music viewer, then its buttons start with `menu`, `level-1-1`, each boss track is
  listed once under `Bosses`, and `jingle-complete` is under `Jingles`.
- Given ▶ pressed on `menu`, then the music playing is `level-1-1`; given `jingle-complete`
  tapped, then the music playing is still `level-1-1`.
- Given Back, then the music playing is `menu` again.

*Sources: D-238.*

## Tunable values

All in `src/config/dev_viewer.py` `DEV_VIEWER_CONFIG` unless said otherwise.

| Name | Value | Notes |
|------|-------|-------|
| viewers | ships, enemies, bosses, props, levels, sounds, music | `DEV_VIEWERS`, in menu order; `DEV_AUDIO_VIEWERS`: sounds, music |
| `close_up_fill` | 0.35 | Share of the screen height the model fills in close-up |
| `turn_per_pixel` | 0.01 rad | Per pixel dragged |
| `zoom_per_pixel` | 0.0015 | The wheel zooms by e^(this) per pixel |
| `zoom_range` | 0.25 to 8 | Times the view without zoom |
| `wheel_step`, `scrub_seconds` | 100 px, 4 s | Levels viewer: time scrubbed per wheel step |
| `scrub_ease` | 10 per s | How fast the levels viewer catches up with the wheel |
| `model_seed` | 7 | Random numbers the enemies and bosses are spawned with |
| `break_key` | `KeyK` | Bosses viewer |
| `hold_delay`, `hold_interval` | 0.4 s, 0.25 s | Sounds viewer: a button held repeats its sound after `hold_delay`, then every `hold_interval` |
| `max_enemy_age` | 40 s | `src/config/game_play.py` `GAME_PLAY_CONFIG.max_enemy_age`; with `cull_margin` 80 px for leaving the playfield |
| player position | bottom middle, y = 90 px | `GAME_PLAY_CONFIG.ship_start_y` |
| `block` | 10 ground units | The game's tile (`propTiles.tile.size`); 10 when the game names none (`src/app/dev_prop_stage.py` `DEFAULT_BLOCK`) |
| `grid_reach` | 8 blocks | `DEV_VIEWER_CONFIG.props.grid_reach` |
| `car_scale` | 0.6 | The levels' `props.cars.scale` |
| floor, grid colours | (0.07, 0.07, 0.1), (0.2, 0.75, 0.9) | `props.floor_color`, `props.grid_color`; grid 0.3 above the floor (`grid_lift`) |
| background | (0.12, 0.1, 0.18) | `props.clear_color` |
| studio lights | ambient 1, key 1.9, fill 0.9, environment 1.2, glow 0.6 (blur 32) | `props.*_intensity`, `props.glow` |
| `pitch`, `pitch_range` | 1.0 rad, 0.15 to 1.45 rad | Props camera, from straight up |
| `view_shift` | 0.34 | Share of half the view's width the prop is drawn right of the middle |

## Notes

- The old debug pages had more tools: a wireframe view with hit circles, a player ship that could
  fly and shoot and could not die, toggles for the living motion and the hitbox, the FPS / polygons
  tile, the boss's stage shown, and the props page's road kit with its sample layout and footprint
  labels. They went with the pages (D-187) and are not in the Dev menu.
- The bosses viewer lists the bosses in the game's order, with no world headings, and shows every
  boss with the first level's light, not over its own level (D-222).
- The first props viewer's `SceneryStage` methods (`solo_props`, `find_prop`, `shift_ground`, D-199,
  replaced by D-205) are gone: nothing called them (D-237).
