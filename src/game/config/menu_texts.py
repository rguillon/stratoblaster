"""Menu texts (short words, readable by kids)"""

from game.config.record import record

# Digits the score shows, zero-padded (P11-R02).
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
        "startHint": "Press Space / Enter or tap to start",
        "chooseShip": "Choose your ship",
        "chooseShipHint": "◀ ▶ to pick · Enter or tap again to go",
        "chooseLevel": "Choose a level",
        "chooseLevelHint": "Arrows to pick · Enter or tap again to go",
        "back": "Back",
        "locked": "Locked!",
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
        "hudHealth": "HP",
        "hudLives": lambda lives: "♥ " + str(lives),
        "hudWeapon": lambda weapon, level, levels: (
            weapon + " · Lv " + str(level) + "/" + str(levels)
        ),
        "hudBombs": lambda bombs: "● " + str(bombs),
        "hudScore": padded,
        "hudHighScore": lambda score: "HI " + padded(score),
        "hudBomb": lambda bombs: "Bomb " + str(bombs),
        "hudMiniBoss": "Mini boss",
        "hudBoss": "Boss",
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
