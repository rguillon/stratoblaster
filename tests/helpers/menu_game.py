"""A small game definition for the menu tests: the texts the menus read, two ships and a level
catalog of three levels (the second and third locked)."""

from types import SimpleNamespace

from core.content.level_catalog import LevelCatalog, LevelEntry
from core.entities.player_ship import PlayerShipDefinition, PlayerShipRoster


def make_texts() -> SimpleNamespace:
    return SimpleNamespace(
        loading="Loading",
        highScore="High score",
        start="Start",
        settings="Settings",
        startHint="Arrows",
        chooseShip="Choose a ship",
        chooseShipHint="Pick",
        back="Back",
        chooseLevel="Choose a level",
        chooseLevelHint="Pick a level",
        locked="Locked",
        paused="Paused",
        resume="Resume",
        mainMenu="Main menu",
        pauseHint="P resumes",
        leaveLevel="Leave the level?",
        no="No",
        yes="Yes",
        musicVolume="Music",
        sfxVolume="Effects",
        settingsHint="Drag",
        gameOver="Game over",
        levelComplete="Level complete",
        continueFromCheckpoint="Continue",
        toLevelSelect="Level select",
        continueHint="Tap to go on",
        newHighScore="New high score!",
        fire="FIRE",
        pauseButton="II",
        enemiesDestroyed=lambda destroyed, spawned: f"{destroyed}/{spawned}",
        finalScore=lambda score: f"Score {score}",
        gameLevel=lambda label: f"Level {label}",
        title="STRATO",
    )


def make_game() -> SimpleNamespace:
    ships = PlayerShipRoster(
        100,
        [PlayerShipDefinition("alpha", "Alpha", 1, 5), PlayerShipDefinition("beta", "Beta", 2, 3)],
    )
    levels = LevelCatalog(
        2,
        [
            LevelEntry("1-1", "1-1", 1, 1, True),
            LevelEntry("1-2", "1-2", 1, 2, False),
            LevelEntry("1-3", "1-3", 1, 3, False),
        ],
    )
    return SimpleNamespace(
        id="stratoblaster",
        title="STRATOBLASTER",
        texts=make_texts(),
        player_ships=ships,
        levels=levels,
    )
