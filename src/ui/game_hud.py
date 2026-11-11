# Copyright (c) 2026 Renaud Guillon
"""The in-game HUD: light readouts in the corners of the playfield window (UI-HUD-01, D-317).

No panels and no backgrounds: outlined text and slim gauges over the level. The score at the top
left, the lives and bombs at the top right, the boss gauge between them during a fight, the level's
progress as a rail up the right edge, the health at the bottom left and the weapon at the bottom
right. The side columns outside the window are left empty (the touch buttons sit in the right one).
"""

from org.transcrypt.stubs.browser import window

from ui.boss_bar import BossBar, BossBarFrame
from ui.screens.elements import element, replace_children

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# Under this share of its health the bar turns red (UI-HUD-04).
LOW_HEALTH = 0.3


class HudTexts:
    """Texts of the in-game HUD, provided by the game. Each is a function of the values it shows."""

    def __init__(
        self,
        health: str,
        lives: Any,
        bombs: Any,
        score: Any,
        high_score: Any,
        bomb: Any,
    ) -> None:
        # Label of the health readout.
        self.health = health
        # The lives left (UI-HUD-03).
        self.lives = lives
        # The bombs left (UI-HUD-03).
        self.bombs = bombs
        # The score, and the high score line under it (UI-HUD-05).
        self.score = score
        self.high_score = high_score
        # Label of the touch bomb button, with the bombs left (UI-HUD-10).
        self.bomb = bomb


class HudFrame:
    """What the HUD shows on one frame."""

    def __init__(
        self,
        health: float,
        max_health: float,
        lives: int,
        weapon: str,
        weapon_level: int,
        weapon_levels: int,
        progress: float,
        score: int,
        high_score: int,
        bombs: int | None = None,
        boss: BossBarFrame | None = None,
    ) -> None:
        self.health = health
        self.max_health = max_health
        self.lives = lives
        # The weapon fired (it can be switched) and its level, out of `weapon_levels` (UI-HUD-06).
        self.weapon = weapon
        self.weapon_level = weapon_level
        self.weapon_levels = weapon_levels
        # Share of the level flown, 0..1 (UI-HUD-02).
        self.progress = progress
        # The score, and the best of it and the saved high score (GAME-SCORE-07, UI-HUD-05).
        self.score = score
        self.high_score = high_score
        # The bombs left (UI-HUD-03); no bombs shown when None.
        self.bombs = bombs
        # The boss being fought, for its health bar (UI-HUD-12); none when None.
        self.boss = boss


class HudSetup:
    """The fixed parts of a HUD: the ship and the texts."""

    def __init__(self, ship: str, texts: HudTexts, on_bomb: Any = None) -> None:
        self.ship = ship
        self.texts = texts
        # The touch bomb button was pressed (UI-HUD-10). No button when None.
        self.on_bomb = on_bomb


def _percent(share: float) -> str:
    clamped = window.Math.min(1, window.Math.max(0, share))
    return str(window.Math.round(clamped * 1000) / 10) + "%"


def split_lead(score: str) -> list[str]:
    """Split a padded score into its padding zeros and its digits (UI-HUD-05).

    The zeros are drawn dim; the last digit is always a digit, so a score of 0 shows one bright 0.
    """
    lead = 0
    while lead < len(score) - 1 and score[lead] == "0":
        lead += 1
    return [score[:lead], score[lead:]]


def _bomb_press(on_bomb: Any) -> Any:
    """Return a pointer-down listener of the touch bomb button: stops the event, then bombs."""

    def handler(event: Any) -> None:
        event.stopPropagation()
        on_bomb()

    return handler


class GameHud:
    """The in-game HUD.

    Laid out at the logical resolution over the playfield window; it takes no clicks or taps but on
    its touch bomb button. Text and gauges change only when their value does (UI-HUD-11).
    """

    def __init__(self, doc: Any, parent: Any, setup: HudSetup) -> None:
        self._doc = doc
        self._setup = setup
        self.root = element(doc, "div", "game-hud")
        self.root.setAttribute("aria-hidden", "true")
        self.root.append(
            self._new_score(doc),
            self._new_stock(doc),
            self._new_progress(doc),
            self._new_health(doc, setup.ship),
            self._new_weapon(doc),
        )
        self._bomb_button = (
            self._new_bomb_button(doc, setup.on_bomb) if setup.on_bomb is not None else None
        )
        self._boss = BossBar(doc, self.root)
        parent.append(self.root)
        self._shown = ""
        self._shown_score = ""
        self._shown_pips = ""

    def _new_score(self, doc: Any) -> Any:
        """Return the top left: the score, its padding zeros dim, and the high score (UI-HUD-05)."""
        score = element(doc, "div", "hud-score")
        self._score = element(doc, "div", "hud-score-value")
        self._score_lead = element(doc, "span", "hud-score-lead")
        self._score_digits = element(doc, "span", "hud-score-digits")
        self._score.append(self._score_lead, self._score_digits)
        self._high_score = element(doc, "div", "hud-high-score")
        score.append(self._score, self._high_score)
        return score

    def _new_stock(self, doc: Any) -> Any:
        """Return the top right: the lives and the bombs left (UI-HUD-03)."""
        stock = element(doc, "div", "hud-stock")
        self._lives = element(doc, "div", "hud-lives")
        self._bombs = element(doc, "div", "hud-bombs")
        stock.append(self._lives, self._bombs)
        return stock

    def _new_progress(self, doc: Any) -> Any:
        """Return the level's progress: a rail up the right edge, filled from below (UI-HUD-02)."""
        progress = element(doc, "div", "hud-progress")
        self._progress_bar = element(doc, "div", "hud-progress-fill")
        progress.append(self._progress_bar)
        return progress

    def _new_health(self, doc: Any, ship: str) -> Any:
        """Return the bottom left: the callsign and health over a segmented bar (UI-HUD-04)."""
        health = element(doc, "div", "hud-health")
        label = element(doc, "div", "hud-health-label")
        self._health_text = element(doc, "span", "hud-health-text")
        label.append(element(doc, "span", "hud-ship", ship), self._health_text)
        bar = element(doc, "div", "hud-bar")
        self._health_bar = element(doc, "div", "hud-bar-fill")
        bar.append(self._health_bar)
        health.append(label, bar)
        return health

    def _new_weapon(self, doc: Any) -> Any:
        """Return the bottom right: the weapon's name and a pip per level, lit to it (UI-HUD-06)."""
        weapon = element(doc, "div", "hud-weapon")
        self._weapon = element(doc, "div", "hud-weapon-name")
        self._pips = element(doc, "div", "hud-weapon-pips")
        weapon.append(self._weapon, self._pips)
        return weapon

    def _new_bomb_button(self, doc: Any, on_bomb: Any) -> Any:
        """Return the touch bomb button (UI-HUD-10): the only part of the HUD that takes taps."""
        button = element(doc, "div", "hud-bomb-button")
        button.setAttribute("role", "button")
        button.addEventListener("pointerdown", _bomb_press(on_bomb))
        self.root.append(button)
        return button

    def update(self, frame: HudFrame) -> None:
        """Show `frame`, touching the page only when something visible changed."""
        self._boss.update(frame.boss)
        self._update_score(frame)
        self._update_pips(frame.weapon_level, frame.weapon_levels)
        texts = self._setup.texts
        health = (
            texts.health + " " + str(window.Math.ceil(frame.health)) + " / " + str(frame.max_health)
        )
        low = "low" if frame.health < LOW_HEALTH * frame.max_health else ""
        shown = [
            health,
            _percent(frame.health / frame.max_health),
            frame.weapon,
            _percent(frame.progress),
            texts.lives(frame.lives),
            low,
        ]
        key = "|".join(shown)
        if key == self._shown:
            return
        self._shown = key
        self._lives.textContent = shown[4]
        self._health_bar.classList.toggle("low", shown[5] == "low")
        self.root.classList.toggle("hud-low", shown[5] == "low")
        self._health_text.textContent = shown[0]
        self._health_bar.style.width = shown[1]
        self._weapon.textContent = shown[2]
        self._progress_bar.style.height = shown[3]

    def _update_pips(self, level: int, levels: int) -> None:
        """One pip per weapon level, the first `level` lit (UI-HUD-06)."""
        key = str(level) + "/" + str(levels)
        if key == self._shown_pips:
            return
        self._shown_pips = key
        pips = [
            element(self._doc, "i", "hud-pip on" if i < level else "hud-pip") for i in range(levels)
        ]
        replace_children(self._pips, pips)

    def _update_score(self, frame: HudFrame) -> None:
        """Show the score, the high score, and the bombs left (also on the touch button)."""
        bombs_key = "undefined" if frame.bombs is None else str(frame.bombs)
        key = str(frame.score) + "|" + str(frame.high_score) + "|" + bombs_key
        if key == self._shown_score:
            return
        self._shown_score = key
        texts = self._setup.texts
        parts = split_lead(texts.score(frame.score))
        self._score_lead.textContent = parts[0]
        self._score_digits.textContent = parts[1]
        self._high_score.textContent = texts.high_score(
            window.Math.max(frame.score, frame.high_score)
        )
        self._bombs.textContent = "" if frame.bombs is None else texts.bombs(frame.bombs)
        button = self._bomb_button
        if button is None:
            return
        bombs = 0 if frame.bombs is None else frame.bombs
        button.textContent = texts.bomb(bombs)
        button.classList.toggle("empty", bombs <= 0)

    def dispose(self) -> None:
        """Dispose."""
        self.root.remove()
