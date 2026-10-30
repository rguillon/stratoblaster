"""The in-game HUD of a level (P07-R02, P11-R02, R06).

The HUD's frame is computed from the level run; the widgets are `ui/` classes.
"""

from org.transcrypt.stubs.browser import __pragma__

from config.game_play import GAME_PLAY_CONFIG as CFG
from ui.boss_bar import BossBarFrame
from ui.game_hud import GameHud, HudFrame, HudSetup, HudTexts
from ui.stats_tile import StatsTile

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def boss_bar_frame(run: Any, texts: Any) -> BossBarFrame | None:
    """The boss health bar of `run`'s fight (P07-R02), if a boss is being fought."""
    bar = run.fights.bar
    if bar is None:
        return None
    rank = texts.hudMiniBoss if bar.rank == "mini" else texts.hudBoss
    return BossBarFrame(bar.name, rank, bar.share, bar.notches)


def hud_frame(
    run: Any,
    max_health: float,
    texts: Any,
    high_score: int = 0,
) -> HudFrame:
    """What the HUD shows of `run` (phase 6 review, P07-R02, P11-R02); `max_health` stands for no
    hull, `high_score` is the saved one.
    """
    shots = run.shots
    track = run.track
    hull = run.hull
    bombs = run.bombs
    health = hull.health if hull is not None else max_health
    lives = hull.lives if hull is not None else 0
    progress = track.progress / track.length_ if track.length_ > 0 else 1
    return HudFrame(
        health,
        max_health,
        lives,
        shots.weapon.name,
        shots.level,
        len(shots.weapon.levels),
        progress,
        run.score,
        max(high_score, run.score),
        bombs.count if bombs is not None else None,
        boss_bar_frame(run, texts),
    )


def create_hud(
    doc: Any,
    parent: Any,
    ship: str,
    texts: Any,
    on_bomb: Any,
) -> GameHud:
    """The in-game HUD in `parent`, for the ship named `ship`, with the game's `texts`; `on_bomb`
    is the touch bomb button's.
    """
    hud_texts = HudTexts(
        texts.hudHealth,
        texts.hudWeapon,
        texts.hudLives,
        texts.hudBombs,
        texts.hudScore,
        texts.hudHighScore,
        texts.hudBomb,
    )
    return GameHud(doc, parent, HudSetup(ship, hud_texts, on_bomb))


class LevelOverlaysOptions:
    """Where a level's HUD and debug tile go, and what they show: `doc`, `debug` (the debug tile
    is shown only in debug mode), `stats_parent` and `hud_parent` (None: no tile, no HUD)."""

    def __init__(
        self,
        doc: Any,
        debug: bool,
        stats_parent: Any,
        hud_parent: Any,
    ) -> None:
        self.doc = doc
        self.debug = debug
        self.stats_parent = stats_parent
        self.hud_parent = hud_parent


def create_level_overlays(
    options: LevelOverlaysOptions,
    ship: str,
    texts: Any,
    on_bomb: Any,
) -> tuple[GameHud | None, StatsTile | None]:
    """The level's HUD (with a parent) and debug tile (in debug mode, with a parent)."""
    stats: StatsTile | None = None
    if options.debug and options.stats_parent is not None:
        stats = StatsTile(options.doc, options.stats_parent, CFG.stats.refresh)
    hud: GameHud | None = None
    if options.hud_parent is not None:
        hud = create_hud(options.doc, options.hud_parent, ship, texts, on_bomb)
    return hud, stats
