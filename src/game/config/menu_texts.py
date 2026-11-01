"""Menu texts (short words, readable by kids: UI-LOOK-09; every text of the UI: UI-LOOK-10)"""

from game.config.record import record

# Digits the score shows, zero-padded (UI-HUD-05).
SCORE_DIGITS = 7


def padded(score: int) -> str:
    """The score as `SCORE_DIGITS` digits, zero-padded on the left (JS `padStart`)."""
    text = str(score)
    while len(text) < SCORE_DIGITS:
        text = "0" + text
    return text


MENU_TEXTS = record(
    {
        "loading": "Loading…",
        "highScore": "High score",
        "start": "Start",
        # The title's controls hint (UI-TITLE-05).
        "startHint": "Press Space / Enter or tap to start",
        "chooseShip": "Choose your ship",
        "chooseShipHint": "◀ ▶ to pick · Enter or tap again to go",
        # The level select's heading and hint (UI-LEVEL-09).
        "chooseLevel": "Choose a level",
        "chooseLevelHint": "Arrows to pick · Enter or tap again to go",
        "back": "Back",
        "locked": "Locked!",
        # The level played, under the HUD's weapon (UI-HUD-06).
        "gameLevel": lambda level: "Level " + str(level),
        "fire": "Fire",
        "levelComplete": "Level complete!",
        "gameOver": "Game over",
        "enemiesDestroyed": lambda destroyed, spawned: (
            "Enemies destroyed: " + str(destroyed) + " / " + str(spawned)
        ),
        "finalScore": lambda score: "Score: " + str(score),
        "newHighScore": "New high score!",
        "continueHint": "Press Space / Enter or tap to go on",
        "continueFromCheckpoint": "Continue",
        "toLevelSelect": "Level select",
        # The HUD's health (UI-HUD-04), lives and bombs (UI-HUD-03), weapon (UI-HUD-06).
        "hudHealth": "HP",
        "hudLives": lambda lives: "♥ " + str(lives),
        "hudWeapon": lambda weapon, level, levels: (
            weapon + " · Lv " + str(level) + "/" + str(levels)
        ),
        "hudBombs": lambda bombs: "● " + str(bombs),
        "hudScore": padded,
        "hudHighScore": lambda score: "HI " + padded(score),
        "hudBomb": lambda bombs: "Bomb " + str(bombs),
        # The boss gauge's kind (UI-HUD-16).
        "hudMiniBoss": "Mini boss",
        "hudBoss": "Boss",
        # The "not supported" message (UI-LOAD-02).
        "unsupported": "Sorry! This game cannot run in this browser or on this device. "
        + "Please try a recent version of Chrome, Edge, Firefox or Safari on a computer.",
        "settings": "Settings",
        "settingsHint": "▲ ▼ to pick · ◀ ▶ or tap to set",
        "musicVolume": "Music",
        "sfxVolume": "Sound effects",
        "pauseButton": "❚❚",
        "paused": "Paused",
        "resume": "Resume",
        "mainMenu": "Main menu",
        "pauseHint": "Esc / P to resume",
        "leaveLevel": "Leave the level?",
        "no": "No",
        "yes": "Yes",
    }
)
