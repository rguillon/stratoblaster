# Copyright (c) 2026 Renaud Guillon
"""The game's sound effects (AUD-SFX-01), keyed by the engine's cue (`SoundCue`).

Each one is a recorded sample (CC0, `public/sfx/<name>.ogg` and `.mp3`, credited in `CREDITS.md`,
AUD-ENGINE-01), loaded at start-up and played through the sound effect bus. The sample of a sound
has the sound's name (or, for a sound with variants, that name and `-1` to `-3`). Samples are
normalised to -1 dBFS, so a sound's `gain` is its peak level in the mix. Priorities (AUD-SFX-05):
the player's and the bombs' sounds highest, the enemy shots lowest. The player's gun shots and the
laser hum are mixed quieter than hits and explosions (AUD-SFX-06).

`seconds` is the length of the sample (of the longest, with variants); the voice pool counts it
(AUD-ENGINE-07).
"""

from audio.audio_types import SoundDesign, SoundJitter

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# Priorities (AUD-SFX-05).
PRIORITY = {
    "enemyShot": 0,
    "enemy": 1,
    "hit": 2,
    "weapon": 3,
    "blast": 4,
    "part": 5,
    "player": 6,
    "top": 7,
}


def sound(
    name: str,
    priority: float,
    gain: float,
    seconds: float,
    rest: dict[str, Any],
) -> SoundDesign:
    """Return a sound effect; `rest` holds `samples` (default: the one named `name`).

    And `positional`, `loop` or `jitter`.
    """
    return SoundDesign(
        name,
        rest.get("samples", [name]),
        gain,
        priority,
        seconds,
        rest.get("positional"),
        rest.get("loop"),
        rest.get("jitter"),
    )


# Each blast is varied at random (AUD-SFX-10): a boss dying blows up at a regular pace, and the same
# few recordings at the same pitch would sound like a machine.
BLAST_JITTER = SoundJitter(0.2, 0.3, 0.08)
PART_JITTER = SoundJitter(0.12, 0.2, 0.05)


def _variants(name: str) -> list[str]:
    """Return the names of the three samples of the sound `name`: `name-1`, `name-2`, `name-3`."""
    return [name + "-1", name + "-2", name + "-3"]


PLAYER_WEAPONS = {
    # One burst per volley (AUD-SFX-02), 8 volleys a second: the sample is short.
    "fire:bullet": sound("gun-shot", PRIORITY["weapon"], 0.14, 0.165, {"positional": True}),
    "fire:missile": sound("missile-launch", PRIORITY["weapon"], 0.3, 0.7, {"positional": True}),
    "beam-start:laser": sound("laser-start", PRIORITY["weapon"], 0.3, 0.68, {"positional": True}),
    # Loops while the laser fires (AUD-SFX-03).
    "beam:laser": sound("laser-hum", PRIORITY["weapon"], 0.1, 4.7, {"loop": True}),
    "weapon-switch": sound("weapon-switch", PRIORITY["player"], 0.3, 0.53, {}),
    "weapon-up": sound("weapon-level-up", PRIORITY["player"], 0.35, 0.26, {}),
}

ENEMY_WEAPONS = {
    "enemy-bullet": sound("enemy-shot", PRIORITY["enemyShot"], 0.16, 0.25, {"positional": True}),
    "enemy-missile": sound("enemy-missile", PRIORITY["enemyShot"], 0.22, 0.6, {"positional": True}),
    "laser-warning": sound("laser-warning", PRIORITY["enemy"], 0.2, 0.96, {"positional": True}),
    "laser-fire": sound("enemy-laser", PRIORITY["enemy"], 0.3, 0.72, {"positional": True}),
}

HITS = {
    "hit": sound("hit", PRIORITY["hit"], 0.3, 0.39, {"positional": True}),
    "hit-blocked": sound("hit-shield", PRIORITY["hit"], 0.28, 0.45, {"positional": True}),
    "player-hit": sound("player-hit", PRIORITY["player"], 0.36, 0.78, {"positional": True}),
}

DESTRUCTION = {
    # Three recordings each, one at random every time (AUD-SFX-09).
    "blast-small": sound(
        "explosion-small",
        PRIORITY["blast"],
        0.32,
        0.8,
        {"positional": True, "samples": _variants("explosion-small"), "jitter": BLAST_JITTER},
    ),
    "blast-large": sound(
        "explosion-large",
        PRIORITY["blast"],
        0.42,
        1.5,
        {"positional": True, "samples": _variants("explosion-large"), "jitter": BLAST_JITTER},
    ),
    "part-destroyed": sound(
        "boss-part-destroyed",
        PRIORITY["part"],
        0.55,
        1.55,
        {"positional": True, "jitter": PART_JITTER},
    ),
    "boss-destroyed": sound("boss-destroyed", PRIORITY["top"], 0.5, 2, {}),
}

PLAYER = {
    "life-lost": sound("life-lost", PRIORITY["top"], 0.45, 1, {}),
    "extra-life": sound("extra-life", PRIORITY["top"], 0.4, 0.49, {}),
    "bomb": sound("bomb", PRIORITY["top"], 0.5, 1.98, {}),
    "bonus:bomb": sound("bomb-bonus", PRIORITY["player"], 0.35, 0.69, {}),
    "bonus:weapon": sound("weapon-bonus", PRIORITY["player"], 0.35, 0.38, {}),
    "bonus:life": sound("life-bonus", PRIORITY["player"], 0.35, 0.32, {}),
    # GAME-BONUS-11: the life bonus's chime pitched up, a little softer.
    "bonus:heal": sound("heal-bonus", PRIORITY["player"], 0.28, 0.26, {}),
}

MENUS = {
    "menu-move": sound("menu-move", PRIORITY["top"], 0.18, 0.06, {}),
    "menu-confirm": sound("menu-confirm", PRIORITY["top"], 0.25, 0.04, {}),
    "menu-back": sound("menu-back", PRIORITY["top"], 0.25, 0.06, {}),
    "pause": sound("pause", PRIORITY["top"], 0.3, 0.61, {}),
    "resume": sound("resume", PRIORITY["top"], 0.3, 0.61, {}),
    "slider": sound("slider-step", PRIORITY["top"], 0.4, 0.04, {}),
}


def _all_sounds() -> dict[str, SoundDesign]:
    """Merge the groups into one table (the `...` spread is not available in Transcrypt)."""
    merged: dict[str, SoundDesign] = {}
    for group in [PLAYER_WEAPONS, ENEMY_WEAPONS, HITS, DESTRUCTION, PLAYER, MENUS]:
        merged.update(group)
    return merged


SOUND_DESIGNS = _all_sounds()
