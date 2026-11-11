# Ship select

> **Area:** UI · **Prefix:** `UI-SHIP` · **Related:** [screen-flow.md](screen-flow.md), [menu-input.md](menu-input.md), [title-screen.md](title-screen.md), [level-select.md](level-select.md), [../gameplay/player-ship.md](../gameplay/player-ship.md), [../graphics/player-ships.md](../graphics/player-ships.md), [../performance.md](../performance.md)

The screen where the player picks one of the three player ships. The ships turn side by side over
the menu backdrop, each above a card with its name and stats; the highlighted one is bigger, lit and
on a neon ring. What the ships are and how they fly is in
[gameplay/player-ship.md](../gameplay/player-ship.md); their models are in
[graphics/player-ships.md](../graphics/player-ships.md).

## Requirements

### UI-SHIP-01 — The ships, side by side · MUST

The screen shows every player ship of the game's roster, side by side in roster order (Balanced,
Heavy, Light), each turning on itself at `ship_select_rotation_speed`. The ships are a 3D stage
drawn over the menu backdrop, whose own ship is hidden on this screen
([title-screen.md](title-screen.md)).

**Acceptance criteria**
- Given the ship select screen, then the 3 ships are shown, rotating, Balanced on the left and Light on the right.

*Sources: P01-R06, D-008.*

### UI-SHIP-02 — A card under each ship · MUST

Under each ship, a card gives its name and its stats in plain words: its speed, from its factor of
the base speed (`Speed: slow` under 1, `Speed: normal` at 1, `Speed: fast` over 1), and its health
(e.g. `HP 100`). The row of cards
is as wide as the row of ships on screen, so each card sits under its ship. Above the cards: the
heading "Choose your ship"; under them, the hint "◀ ▶ to pick · Enter or tap to go"; at the
top left, the Back button ([menu-input.md](menu-input.md)).

**Acceptance criteria**
- Given the ship select screen, then each card shows its ship's name, speed and HP, under its ship.

*Sources: P01-R06, P01-R11.*

### UI-SHIP-03 — The highlighted ship stands out · MUST

Exactly one ship is highlighted. It is scaled up (`highlight_scale`, the others at `dim_scale`;
the scales ease from one to the other), it is the only ship lit by a key light (the others get only
the ambient light, so they look dimmed), and it stands on a glowing neon ring. Its card shows the
`▲` mark, at full opacity; the other cards are faded.

**Acceptance criteria**
- Given a ship is highlighted, then it is bigger and lit, the ring is under it, and its card has the `▲` mark; the others are smaller, darker and their cards faded.

The ring is the menus' cyan (`#00e8ff`, D-198, D-324).

*Sources: P01-R06, D-008.*

### UI-SHIP-04 — Changing the highlight · MUST

Left and Right move the highlight to the next ship; it wraps around at the ends. Up and Down do
nothing. Tapping another card highlights its ship; tapping the highlighted card confirms it.

**Acceptance criteria**
- Given the balanced ship is highlighted, when Right is pressed, then the next ship is highlighted; at the last ship, Right highlights the first one.

*Sources: P01-R06, P01-R11.*

### UI-SHIP-05 — Balanced first · MUST

The first time the screen opens (no ship saved, UI-SHIP-07), the first ship of the roster is
highlighted: Balanced.

**Acceptance criteria**
- Given `ship-select` is opened for the first time, then the balanced ship is highlighted.

*Sources: P01-R06, D-008.*

### UI-SHIP-06 — Confirm and Back · MUST

Confirm stores the highlighted ship as the chosen ship and opens the level select screen. Back opens
the title. The highlight is kept while the game runs: coming back from the level select screen, or
from the title, the same ship is highlighted.

**Acceptance criteria**
- When Confirm is pressed, then the highlighted ship is stored as the chosen ship and the screen is `level-select`.
- Given `level-select` after choosing Heavy, when Back is pressed, then Heavy is highlighted.

*Sources: P01-R06, P01-R01.*

### UI-SHIP-07 — The last ship is remembered · MAY

The chosen ship is saved in a cookie (`<gameId>_last_ship`, kept `cookie_max_age`) when it is
confirmed, and it is highlighted first the next time the game starts. An unknown saved ship is
ignored (Balanced is highlighted).

**Acceptance criteria**
- Given the player chose the light ship and reloads the page, when `ship-select` opens, then the light ship is highlighted.
- Given the cookie names a ship that does not exist, then the balanced ship is highlighted.

*Sources: P01-R14, D-010, D-016.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `ship_select_rotation_speed` | 0.5 rad/s | `src/config/menu.py` `MENU_CONFIG.ship_select.rotation_speed_rad_per_sec` |
| Ship spacing | 6 units (7 until D-319) | `MENU_CONFIG.ship_select.spacing` |
| `highlight_scale` / `dim_scale` | 1.2 / 0.7 | `MENU_CONFIG.ship_select`; eased at 10 /s (`scale_ease_per_sec`) |
| Lights | ambient 0.25, key 2.6, rim 0.8 | `MENU_CONFIG.ship_select.lights` |
| Ring | 6.4 units across, 0.12 thick, colour `(1, 0.92, 0.05)` | `MENU_CONFIG.ship_select.ring` |
| Camera | framing margin 1.2, horizontal FOV 1.0, target height 0.6 (1.05 and −1.2 until D-319) | `MENU_CONFIG.ship_select.camera`; the cards' row width is 100 / 1.2 % |
| Faded cards | 60 % opacity | `index.html` `.ship-card` |
| `cookie_max_age` | 365 days | `MENU_CONFIG.cookie_max_age_days` |

## Notes

- Moving the highlight must not stall the screen: each ship has its own key light, turned on and
  off, and each ship is drawn highlighted once while the menus load (D-116, D-118). See
  [performance.md](../performance.md) for the "instant feedback" rule.
- The ship stats are shown as plain words (`Speed: fast`) since D-323; they were
  `Speed ×1 (225 px/s)` before. Bars or stars were suggested in phase 1 and never asked for.
