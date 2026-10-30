"""The game's sound effects (P12-R09, GD-71), all
synthesised, keyed by the engine's cue (`SoundCue`). Priorities (P12-R10): the player's and the
bombs' sounds highest, the enemy shots lowest. The player's gun shots and the laser hum are mixed
quieter than hits and explosions.

`sound(...)` takes its optional fields (`positional`, `loop`, `hold`) as a dict, as the
The layers take a partial object.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from audio.audio_types import FilterSpec, SoundDesign  # noqa: E402
from game.view.audio.sound_recipes import (  # noqa: E402
    MINIGUN,
    ExplosionSize,
    chime,
    env,
    explosion,
    flatten_layers,
    minigun,
    tone,
)

# Priorities (P12-R10).
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
    layers: list[Any],
    rest: dict[str, Any],
) -> SoundDesign:
    """A sound effect; `rest` holds `positional`, `loop` or `hold` (default 0)."""
    return SoundDesign(
        name,
        flatten_layers(layers),
        gain,
        priority,
        rest.get("hold", 0),
        rest.get("positional"),
        rest.get("loop"),
    )


PLAYER_WEAPONS = {
    "fire:bullet": sound(
        "gun-shot", PRIORITY["weapon"], 0.14, minigun(MINIGUN), {"positional": True}
    ),
    "fire:missile": sound(
        "missile-launch",
        PRIORITY["weapon"],
        0.3,
        [
            tone(
                "noise",
                1,
                0.8,
                env(0.01, 0.3, 0, 0.08),
                {"filter": FilterSpec("bandpass", 2600, 2, 500, 0.3)},
            ),
            tone("sawtooth", 220, 0.3, env(0.005, 0.2), {"glide_to": 90, "glide_seconds": 0.2}),
        ],
        {"positional": True},
    ),
    "beam-start:laser": sound(
        "laser-start",
        PRIORITY["weapon"],
        0.3,
        [
            tone(
                "sawtooth",
                300,
                0.6,
                env(0.005, 0.18, 0, 0.05),
                {
                    "glide_to": 1300,
                    "glide_seconds": 0.15,
                    "filter": FilterSpec("lowpass", 3000, None, None, None),
                },
            ),
        ],
        {"positional": True},
    ),
    "beam:laser": sound(
        "laser-hum",
        PRIORITY["weapon"],
        0.1,
        [
            tone(
                "sawtooth",
                110,
                0.6,
                env(0.05, 0.1, 0.8, 0.12),
                {"filter": FilterSpec("lowpass", 900, 3, None, None)},
            ),
            tone(
                "square",
                220,
                0.3,
                env(0.05, 0.1, 0.8, 0.12),
                {
                    "detune_cents": 9,
                    "filter": FilterSpec("lowpass", 1400, None, None, None),
                },
            ),
        ],
        {"loop": True},
    ),
    "weapon-switch": sound(
        "weapon-switch",
        PRIORITY["player"],
        0.3,
        chime("square", [660, 990], 0.06, 0.5),
        {},
    ),
    "weapon-up": sound(
        "weapon-level-up",
        PRIORITY["player"],
        0.35,
        chime("triangle", [523, 659, 784, 1047], 0.07, 0.6),
        {},
    ),
}

ENEMY_WEAPONS = {
    "enemy-bullet": sound(
        "enemy-shot",
        PRIORITY["enemyShot"],
        0.14,
        [
            tone(
                "triangle",
                760,
                0.7,
                env(0.001, 0.08),
                {"glide_to": 340, "glide_seconds": 0.08},
            )
        ],
        {"positional": True},
    ),
    "enemy-missile": sound(
        "enemy-missile",
        PRIORITY["enemyShot"],
        0.22,
        [
            tone(
                "noise",
                1,
                0.7,
                env(0.02, 0.35, 0, 0.06),
                {"filter": FilterSpec("bandpass", 900, 3, 300, 0.35)},
            ),
        ],
        {"positional": True},
    ),
    "laser-warning": sound(
        "laser-warning",
        PRIORITY["enemy"],
        0.2,
        [
            tone("square", 880, 0.5, env(0.002, 0.07, 0, 0.02), {}),
            tone("square", 880, 0.5, env(0.002, 0.07, 0, 0.02), {"delay": 0.16}),
        ],
        {"positional": True},
    ),
    "laser-fire": sound(
        "enemy-laser",
        PRIORITY["enemy"],
        0.3,
        [
            tone(
                "sawtooth",
                170,
                0.6,
                env(0.01, 0.4, 0.3, 0.15),
                {
                    "glide_to": 90,
                    "glide_seconds": 0.5,
                    "filter": FilterSpec("lowpass", 1800, None, None, None),
                },
            ),
            tone(
                "noise",
                1,
                0.3,
                env(0.01, 0.4, 0.2, 0.15),
                {"filter": FilterSpec("bandpass", 1200, None, None, None)},
            ),
        ],
        {"positional": True, "hold": 0.3},
    ),
}

HITS = {
    "hit": sound(
        "hit",
        PRIORITY["hit"],
        0.3,
        [
            tone(
                "noise",
                1,
                0.6,
                env(0.001, 0.05),
                {"filter": FilterSpec("highpass", 1800, None, None, None)},
            ),
            tone("square", 320, 0.4, env(0.001, 0.06), {"glide_to": 140, "glide_seconds": 0.06}),
        ],
        {"positional": True},
    ),
    "hit-blocked": sound(
        "hit-shield",
        PRIORITY["hit"],
        0.28,
        [
            tone(
                "square",
                1480,
                0.4,
                env(0.001, 0.12, 0, 0.06),
                {"filter": FilterSpec("bandpass", 2400, 6, None, None)},
            ),
            tone("triangle", 2210, 0.3, env(0.001, 0.15, 0, 0.08), {}),
        ],
        {"positional": True},
    ),
    "player-hit": sound(
        "player-hit",
        PRIORITY["player"],
        0.5,
        [
            tone(
                "sawtooth",
                240,
                0.6,
                env(0.002, 0.25, 0, 0.06),
                {"glide_to": 70, "glide_seconds": 0.25},
            ),
            tone(
                "noise",
                1,
                0.5,
                env(0.001, 0.15),
                {"filter": FilterSpec("lowpass", 2500, None, None, None)},
            ),
        ],
        {"positional": True},
    ),
}

# Explosion sizes (D-108): enemies small and large, boss parts and the player, the bomb and bosses.
BLAST_SMALL = ExplosionSize(0.3, 2600, 120, 0, 3)
BLAST_LARGE = ExplosionSize(0.6, 3000, 90, 0.9, 5)
BLAST_HUGE = ExplosionSize(1.1, 3400, 70, 2, 8)

DESTRUCTION = {
    "blast-small": sound(
        "explosion-small",
        PRIORITY["blast"],
        0.32,
        explosion(BLAST_SMALL, 0),
        {"positional": True},
    ),
    "blast-large": sound(
        "explosion-large",
        PRIORITY["blast"],
        0.42,
        explosion(BLAST_LARGE, 0),
        {"positional": True},
    ),
    "part-destroyed": sound(
        "boss-part-destroyed",
        PRIORITY["part"],
        0.55,
        [
            explosion(BLAST_LARGE, 0),
            tone(
                "square",
                1200,
                0.25,
                env(0.001, 0.4, 0, 0.1),
                {"glide_to": 300, "glide_seconds": 0.4},
            ),
        ],
        {"positional": True},
    ),
    # A chain: the core goes, then two more blasts inside the hull.
    "boss-destroyed": sound(
        "boss-destroyed",
        PRIORITY["top"],
        0.55,
        [
            explosion(BLAST_HUGE, 0),
            explosion(BLAST_LARGE, 0.35),
            explosion(BLAST_LARGE, 0.8),
            tone(
                "sawtooth",
                400,
                0.3,
                env(0.01, 1.4, 0, 0.2),
                {
                    "glide_to": 40,
                    "glide_seconds": 1.4,
                    "filter": FilterSpec("lowpass", 900, None, None, None),
                },
            ),
        ],
        {},
    ),
}

PLAYER = {
    "life-lost": sound(
        "life-lost",
        PRIORITY["top"],
        0.45,
        [
            tone(
                "square",
                660,
                0.5,
                env(0.005, 0.6, 0, 0.1),
                {
                    "glide_to": 110,
                    "glide_seconds": 0.6,
                    "filter": FilterSpec("lowpass", 2000, None, None, None),
                },
            ),
            explosion(BLAST_LARGE, 0),
        ],
        {},
    ),
    "extra-life": sound(
        "extra-life",
        PRIORITY["top"],
        0.4,
        chime("triangle", [784, 988, 1175, 1568], 0.08, 0.7),
        {},
    ),
    "bomb": sound(
        "bomb",
        PRIORITY["top"],
        0.5,
        [
            explosion(BLAST_HUGE, 0),
            tone(
                "sawtooth",
                800,
                0.25,
                env(0.005, 0.8, 0, 0.1),
                {
                    "glide_to": 60,
                    "glide_seconds": 0.8,
                    "filter": FilterSpec("lowpass", 1500, None, None, None),
                },
            ),
        ],
        {},
    ),
    "bonus:bomb": sound(
        "bomb-bonus",
        PRIORITY["player"],
        0.35,
        chime("square", [523, 784], 0.07, 0.45),
        {},
    ),
    "bonus:weapon": sound(
        "weapon-bonus",
        PRIORITY["player"],
        0.35,
        [
            tone(
                "triangle",
                440,
                0.7,
                env(0.003, 0.16, 0.2, 0.1),
                {"glide_to": 1320, "glide_seconds": 0.14},
            ),
            tone("sine", 1760, 0.3, env(0.003, 0.1, 0, 0.1), {"delay": 0.1}),
        ],
        {},
    ),
    "bonus:life": sound(
        "life-bonus",
        PRIORITY["player"],
        0.35,
        chime("sine", [784, 1175, 1568], 0.06, 0.7),
        {},
    ),
}

MENUS = {
    "menu-move": sound(
        "menu-move",
        PRIORITY["top"],
        0.18,
        [tone("square", 1200, 0.5, env(0.001, 0.03), {})],
        {},
    ),
    "menu-confirm": sound(
        "menu-confirm",
        PRIORITY["top"],
        0.25,
        chime("square", [660, 990], 0.05, 0.5),
        {},
    ),
    "menu-back": sound(
        "menu-back",
        PRIORITY["top"],
        0.25,
        chime("square", [660, 440], 0.05, 0.5),
        {},
    ),
    "pause": sound(
        "pause",
        PRIORITY["top"],
        0.3,
        [
            tone(
                "sine",
                880,
                0.7,
                env(0.003, 0.15, 0, 0.05),
                {"glide_to": 440, "glide_seconds": 0.15},
            ),
        ],
        {},
    ),
    "resume": sound(
        "resume",
        PRIORITY["top"],
        0.3,
        [
            tone(
                "sine",
                440,
                0.7,
                env(0.003, 0.15, 0, 0.05),
                {"glide_to": 880, "glide_seconds": 0.15},
            ),
        ],
        {},
    ),
    "slider": sound(
        "slider-step",
        PRIORITY["top"],
        0.4,
        [tone("triangle", 1000, 0.6, env(0.002, 0.07), {})],
        {},
    ),
}


def _all_sounds() -> dict[str, SoundDesign]:
    sounds: dict[str, SoundDesign] = {}
    for group in [PLAYER_WEAPONS, ENEMY_WEAPONS, HITS, DESTRUCTION, PLAYER, MENUS]:
        for key, value in group.items():
            sounds[key] = value
    return sounds


# Every sound effect, by cue.
SOUND_DESIGNS = _all_sounds()
