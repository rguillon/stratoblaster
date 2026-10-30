"""The in-game HUD, ported from `ui/game-hud.ts`: one bar along the bottom of the playfield, the
level's progress along its top edge, the ship's health, lives and bombs, the score and the weapon.
"""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from ui.boss_bar import BossBar, BossBarFrame  # noqa: E402
from ui.screens.elements import element  # noqa: E402

# Under this share of its health the bar turns red.
LOW_HEALTH = 0.3


class HudTexts:
    """Texts of the in-game HUD, provided by the game. Each is a function of the values it shows."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        health: str,
        weapon: Any,
        lives: Any,
        bombs: Any,
        score: Any,
        high_score: Any,
        bomb: Any,
    ) -> None:
        # Label of the health bar.
        self.health = health
        # The weapon and its level, e.g. `Bullet · Lv 1/5`: (name, level, levels).
        self.weapon = weapon
        # The lives left (GD-20).
        self.lives = lives
        # The bombs left (P11-R05).
        self.bombs = bombs
        # The score, and the high score line under it (P11-R02).
        self.score = score
        self.high_score = high_score
        # Label of the touch bomb button, with the bombs left (P11-R06).
        self.bomb = bomb


class HudFrame:
    """What the HUD shows on one frame."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
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
        # The weapon fired (it can be switched) and its level, out of `weapon_levels`.
        self.weapon = weapon
        self.weapon_level = weapon_level
        self.weapon_levels = weapon_levels
        # Share of the level flown, 0..1.
        self.progress = progress
        # The score, and the best of it and the saved high score (P11-R02).
        self.score = score
        self.high_score = high_score
        # The bombs left (P11-R05); no bombs shown when None.
        self.bombs = bombs
        # The boss being fought, for its health bar (P07-R02); none when None.
        self.boss = boss


class HudSetup:
    """The fixed parts of a HUD: the ship and the texts."""

    def __init__(self, ship: str, texts: HudTexts, on_bomb: Any = None) -> None:
        self.ship = ship
        self.texts = texts
        # The touch bomb button was pressed (P11-R06). No button when None.
        self.on_bomb = on_bomb


def _percent(share: float) -> str:
    clamped = window.Math.min(1, window.Math.max(0, share))
    return str(window.Math.round(clamped * 1000) / 10) + "%"


def _bomb_press(on_bomb: Any) -> Any:
    """A pointer-down listener of the touch bomb button: stops the event, then bombs."""

    def handler(event: Any) -> None:
        event.stopPropagation()
        on_bomb()

    return handler


class GameHud:
    """The in-game HUD. Laid out at the logical resolution over the playfield; it takes no clicks
    or taps but on its touch bomb button (P11-R06). Text and bars change only when their value
    does.
    """

    def __init__(self, doc: Any, parent: Any, setup: HudSetup) -> None:
        self._setup = setup
        self.root = element(doc, "div", "game-hud")
        self.root.setAttribute("aria-hidden", "true")
        panel = element(doc, "div", "hud-panel")
        progress = element(doc, "div", "hud-progress")
        self._progress_bar = element(doc, "div", "hud-progress-fill")
        progress.append(self._progress_bar)
        self._lives = element(doc, "div", "hud-lives")
        self._bombs = element(doc, "div", "hud-bombs")
        name = element(doc, "div", "hud-name")
        name.append(element(doc, "div", "hud-ship", setup.ship), self._lives, self._bombs)
        bar = element(doc, "div", "hud-bar")
        self._health_bar = element(doc, "div", "hud-bar-fill")
        bar.append(self._health_bar)
        self._health_text = element(doc, "div", "hud-health-text")
        meter = element(doc, "div", "hud-meter")
        meter.append(bar, self._health_text)
        health = element(doc, "div", "hud-health")
        health.append(name, meter)
        score = element(doc, "div", "hud-score")
        self._score = element(doc, "div", "hud-score-value")
        self._high_score = element(doc, "div", "hud-high-score")
        score.append(self._score, self._high_score)
        self._weapon = element(doc, "div", "hud-weapon")
        panel.append(progress, health, score, self._weapon)
        self.root.append(panel)
        self._bomb_button = (
            self._new_bomb_button(doc, setup.on_bomb) if setup.on_bomb is not None else None
        )
        self._boss = BossBar(doc, self.root)
        parent.append(self.root)
        self._shown = ""
        self._shown_score = ""

    def _new_bomb_button(self, doc: Any, on_bomb: Any) -> Any:
        """The touch bomb button (P11-R06): the only part of the HUD that takes taps."""
        button = element(doc, "div", "hud-bomb-button")
        button.setAttribute("role", "button")
        button.addEventListener("pointerdown", _bomb_press(on_bomb))
        self.root.append(button)
        return button

    def update(self, frame: HudFrame) -> None:
        """Shows `frame`, touching the page only when something visible changed."""
        self._boss.update(frame.boss)
        self._update_score(frame)
        texts = self._setup.texts
        health = (
            texts.health + " " + str(window.Math.ceil(frame.health)) + " / " + str(frame.max_health)
        )
        low = "low" if frame.health < LOW_HEALTH * frame.max_health else ""
        shown = [
            health,
            _percent(frame.health / frame.max_health),
            texts.weapon(frame.weapon, frame.weapon_level, frame.weapon_levels),
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
        self._health_text.textContent = shown[0]
        self._health_bar.style.width = shown[1]
        self._weapon.textContent = shown[2]
        self._progress_bar.style.width = shown[3]

    def _update_score(self, frame: HudFrame) -> None:
        """The score, the high score, and the bombs left, by the lives and on the touch button."""
        bombs_key = "undefined" if frame.bombs is None else str(frame.bombs)
        key = str(frame.score) + "|" + str(frame.high_score) + "|" + bombs_key
        if key == self._shown_score:
            return
        self._shown_score = key
        texts = self._setup.texts
        self._score.textContent = texts.score(frame.score)
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
        self.root.remove()
