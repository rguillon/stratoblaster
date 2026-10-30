"""One play of a level (P06-R02, R03, R07), ported from `core/systems/level-run.ts`.

The ground scrolls, the wave script brings the enemies in by distance, the player flies and shoots
them. When the scroll reaches the end no more enemies come; once the last ones are gone (or after
`end_wait`) the level is complete. With bosses (P07-R06), no wave comes while one is fought, and a
level with a final boss ends once that boss is destroyed instead. Pure and deterministic: everything
depends on the `dt` and controls given to `step`.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import EnemyEntry, EnemySpawnArea
from core.entities.shot_target import damage_target
from core.math.rng import create_rng
from core.scenery.scenery_level import level_length
from core.scenery.scroll_track import ScrollTrack
from core.systems.bonus_world import BonusWorld
from core.systems.boss_fights import BossFightHooks, BossFightRules, BossFights
from core.systems.enemy_world import EnemyBlast, EnemyDifficulty, EnemyWorld, EnemyWorldOptions
from core.systems.level_run_types import (
    LandedHit,
    LevelCheckpoint,
    LevelControls,
    LevelResult,
    LevelRunOptions,
    Supplies,
)
from core.systems.player_bombs import PlayerBombs
from core.systems.player_flight import PlayerFlight
from core.systems.player_hits import find_player_hits
from core.systems.player_hull import PlayerHull
from core.systems.run_arsenal import RunArsenal
from core.systems.ship_journey import ShipJourney, flight_of
from core.systems.shot_world import ShotImpact, ShotWorld, ShotWorldOptions
from core.systems.wave_runner import WaveRunner, validate_wave_script

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

from core.entities.enemy import DropSource  # noqa: E402
from core.entities.shot_target import ShotTarget  # noqa: E402
from core.math.rng import Random  # noqa: E402
from core.systems.enemy_shots import EnemyLaser  # noqa: E402

__pragma__("noskip")

# Fight timings when the run is given none (only matters for levels with bosses).
NO_BOSS_RULES = BossFightRules(0, 1)


def _default_in_view(width: float, height: float) -> Callable[[float, float], bool]:
    """Whether a point is in the playfield's rectangle (the default `in_view`)."""

    def in_view(x: float, y: float) -> bool:
        return x >= 0 and x <= width and y >= 0 and y <= height

    return in_view


def _player_systems(
    options: LevelRunOptions,
    reach: tuple[float, float],
) -> tuple[BonusWorld | None, PlayerHull | None, PlayerBombs | None]:
    """The bonuses, hull and bombs of a run, each only when its rules are given. The life and bomb
    bonuses draw from a source of their own (P11-R07), so the weapon bonuses drop as before.
    """
    seed = options.seed
    supplies = options.start_supplies
    bonuses: BonusWorld | None = None
    if options.bonuses is not None:
        bonuses = BonusWorld(
            options.bonuses,
            create_rng(seed + 1),
            reach,
            options.cull_margin,
            create_rng(seed + 2),
        )
    hull: PlayerHull | None = None
    if options.hull is not None:
        max_health = options.ship.max_health if options.ship.max_health is not None else 100
        lives = supplies.lives if supplies is not None else None
        hull = PlayerHull(options.hull, max_health, lives)
    bombs: PlayerBombs | None = None
    if options.bombs is not None:
        bomb_count = supplies.bombs if supplies is not None else None
        bombs = PlayerBombs(options.bombs, bomb_count)
    return bonuses, hull, bombs


class LevelRun:
    """One play of a level. `track` is the ground's scroll, `enemies` the enemies and their shots,
    `shots` the player's shots, `ship` the player's ship; `blasts`, `impacts` and `hits` are what
    the last step produced.
    last step produced.
    """

    def __init__(self, options: LevelRunOptions) -> None:
        self._options = options
        self.blasts: list[EnemyBlast] = []
        self.impacts: list[ShotImpact] = []
        self.hits: list[LandedHit] = []
        self._phase: str = "playing"
        self._clearing_for = 0.0
        # What the player's shots can hit: the enemies and missiles on screen.
        self._targets: list[ShotTarget] = []
        # Saved when the mini boss is destroyed (P07-R08).
        self._checkpoint: LevelCheckpoint | None = None
        # Laser beams that already hit the player (a beam hits once).
        self._lasers_hit: set[EnemyLaser] = set()

        screen = options.screen
        level = options.level
        kinds = options.kinds
        cull_margin = options.cull_margin
        max_enemy_age = options.max_enemy_age
        kind_ids: list[str] = []
        for kind in kinds:
            kind_ids.append(kind.id)
        validate_wave_script(level.waves, kind_ids)
        self.track = ScrollTrack(level.scenery.scroll_speed, level_length(level.scenery))
        random = create_rng(options.seed)
        area = ShotWorldOptions(screen.width, screen.height, cull_margin)
        world = EnemyWorldOptions(
            screen.width, screen.height, cull_margin, max_enemy_age, options.eye
        )
        difficulty: EnemyDifficulty = level.difficulty
        self.enemies = EnemyWorld(world, random, difficulty)
        self.shots = ShotWorld(area, options.weapon)
        self.shots.select(options.weapon, options.weapon_level)
        self.shots.targets = self._targets
        bounds = options.bounds
        half = bounds.half_width_at(bounds.min_y)
        self._reach = (bounds.center_x - half, bounds.center_x + half)
        self.bonuses, self.hull, self.bombs = _player_systems(options, self._reach)
        flight = flight_of(options)
        self.ship: PlayerFlight = flight.ship
        self.journey: ShipJourney | None = flight.journey
        self.waves = WaveRunner(level.waves, lambda kind, entry: self._spawn(kind, entry, random))
        weapons = options.weapons if options.weapons is not None else [options.weapon]
        self.arsenal = RunArsenal(self.shots, weapons, options.weapon_level)
        bosses = level.bosses if level.bosses is not None else []
        boss_kinds = options.boss_kinds if options.boss_kinds is not None else []
        boss_rules = options.boss_rules if options.boss_rules is not None else NO_BOSS_RULES
        reach = self._reach
        hooks = BossFightHooks(
            lambda: EnemySpawnArea(screen.width, screen.height, random, None, reach),
            lambda boss: self.enemies.add(boss),  # noqa: PLW0108 (a method reference loses `self`)
        )
        self.fights = BossFights(bosses, boss_kinds, boss_rules, hooks)
        if options.start_weapons is not None:
            self.arsenal.restore(options.start_weapons)
        if options.checkpoint is not None:
            self._resume(options.checkpoint)
        self._aim_shots()

    @property
    def phase(self) -> str:
        return self._phase

    @property
    def result(self) -> LevelResult:
        over = self._phase == "over"
        checkpoint = self._checkpoint if over and self._checkpoint is not None else None
        return LevelResult(
            self._options.level.id,
            self.enemies.kills,
            self.enemies.spawned,
            "over" if over else "complete",
            self.score,
            None,
            checkpoint,
        )

    @property
    def score(self) -> float:
        """Points scored so far in this attempt (P11-R01), from the checkpoint's after a
        Continue."""
        return self.enemies.score

    @property
    def supplies(self) -> Supplies | None:
        """The lives and bombs left, kept for the next level (reviewer, 2026-10-28); none without a
        hull.
        """
        if self.hull is None:
            return None
        bomb_count = self.bombs.count if self.bombs is not None else 0
        return Supplies(self.hull.lives, bomb_count)

    @property
    def checkpoint(self) -> LevelCheckpoint | None:
        """The checkpoint saved so far (P07-R08), if any."""
        return self._checkpoint

    def step(self, dt: float, controls: LevelControls) -> None:
        """Advances the run by `dt` seconds with the player's `controls`."""
        self.blasts = []
        self.impacts = []
        self.hits = []
        if self._phase == "complete":
            return
        flying = self._fly(dt, controls)
        self._aim_shots()
        self.shots.firing = flying and bool(controls.fire)
        self.track.step(dt)
        if self._phase == "playing":
            self._step_level(dt)
        self.enemies.player_x = self.ship.x
        self.enemies.player_y = self.ship.y
        self.enemies.step(dt)
        self._aim_at_visible()
        self._step_bomb(dt, flying and controls.bomb is True)
        self.shots.step(dt)
        self.blasts = self.enemies.blasts
        self.impacts = self.shots.impacts
        self._step_hull(dt)
        self._step_bonuses(dt)
        if self._phase == "clearing":
            self._clear(dt)

    def seek(self, time: float) -> None:
        """Starts again at `time` seconds into the level (P06-R09): the enemies and shots on screen
        go, the waves before that point are skipped and the later ones come as usual.
        """
        if self._phase == "over":
            return
        self.track.seek(time)
        if self.journey:
            self.journey.skip_arrival(self.ship)
        self._restart_at(None)

    def _resume(self, checkpoint: LevelCheckpoint) -> None:
        """From the checkpoint (P07-R08): its progress, its bosses passed and its weapons."""
        self.track.seek(checkpoint.progress / self.track.speed)
        self._restart_at(checkpoint.bosses_passed)
        self.arsenal.restore(checkpoint.weapons)
        self.enemies.score = checkpoint.score
        self._checkpoint = checkpoint

    def _restart_at(self, bosses_passed: int | None) -> None:
        """Clears the playfield and goes on from the track's progress, as if the level began
        there."""
        self.enemies.clear()
        if self.bonuses:
            self.bonuses.clear()
        for shot in self.shots.projectiles:
            shot.alive = False
        self.waves.skip_to(self.track.progress)
        self.fights.skip_to(self.track, bosses_passed)
        self._phase = "playing"
        self._clearing_for = 0.0

    def _step_level(self, dt: float) -> None:
        """The level goes on: bosses come and go, the waves come while no boss is fought (P07-R06),
        and the level ends with its final boss, or at the end of its scroll without one.
        """
        fights = self.fights
        track = self.track
        fights.step(dt, track)
        if not fights.active:
            self.waves.step(dt, track.progress)
        defeated = fights.just_defeated
        if defeated is not None and defeated.rank == "mini":
            self._checkpoint = LevelCheckpoint(
                # Where the mini boss is (the fight may start a hair before it).
                max(track.progress, defeated.at),
                fights.passed,
                self.arsenal.snapshot(),
                self.score,
            )
        finished = fights.final_defeated if fights.has_final else track.ended
        if finished:
            self.waves.stop()
            self._phase = "clearing"
            if self.journey:
                self.journey.clear()

    def break_boss_part(self) -> None:
        """A debug key (P07-R09): destroys the next intact part of the boss fought, or its core."""
        boss = self.fights.boss
        if boss is not None:
            boss.break_next()

    def _step_bomb(self, dt: float, pressed: bool) -> None:
        """A bomb (P11-R05): when one goes off, every enemy and boss piece on screen takes its
        damage once (a shielded core takes none); while it lasts, the enemy shots are cleared.
        """
        bombs = self.bombs
        if bombs is None:
            return
        bombs.step(dt)
        if pressed and bombs.fire(self.ship.x, self.ship.y):
            for target in self._targets:
                damage_target(target, bombs.rules.damage)
        if bombs.active is not None:
            self.enemies.shots.clear()

    def _step_hull(self, dt: float) -> None:
        """The most damaging enemy shot or enemy touching the ship lands, unless the ship is
        invincible (GD-21, GD-22) or a bomb is going off (P11-R05); with no life left the game is
        over (GD-20). A lost life tops the bombs back up (P11-R05).
        """
        hull = self.hull
        rules = self._options.hull
        if hull is None or rules is None or self._phase == "over":
            return
        hull.step(dt)
        if hull.invincible > 0:
            return
        if self.bombs is not None and self.bombs.active is not None:
            return
        if self.journey is not None and self.journey.scripted:
            return
        hits = find_player_hits(self.ship, rules, self.enemies, self._lasers_hit)
        if len(hits) == 0:
            return
        hit = hits[0]
        hit.land()
        self._landed(LandedHit(hit.kind, hit.x, hit.y, hull.hit(hit.damage)))

    def _landed(self, hit: LandedHit) -> None:
        """A hit landed: a lost life tops the bombs up, the last one ends the game."""
        self.hits = [hit]
        if hit.event == "lifeLost" and self.bombs is not None:
            self.bombs.refill()
        if hit.event != "gameOver":
            return
        self._phase = "over"
        self.waves.stop()

    def _step_bonuses(self, dt: float) -> None:
        """Drops bonuses where enemies blew up (a life bonus where a mini boss did, P11-R07), moves
        them, and gives what each one picked up gives.
        """
        bonuses = self.bonuses
        if bonuses is None:
            return
        destroyed = self.enemies.destroyed
        broken = self.enemies.broken_parts
        boss = self.fights.boss
        rank = self.fights.rank
        drops: list[DropSource] = []
        drops.extend(destroyed)
        drops.extend(broken)
        bonuses.drop(
            drops,
            lambda t: (t is not boss) and (t in destroyed),
        )
        if boss is not None and rank == "mini" and boss in destroyed:
            bonuses.place("life", boss)
        bonuses.step(dt, None if self._phase == "over" else self.ship)
        for bonus in bonuses.picked:
            self._collect(bonus.kind)

    def _collect(self, kind: str) -> None:
        """A weapon bonus raises the weapon in use by a level, up to its last (the new level fires
        at once); a life or a bomb bonus adds one, or scores its points at the most (P11-R07).
        """
        if kind == "weapon":
            self.arsenal.level_up(1)
            return
        if kind == "life":
            added = self.hull.add_life() if self.hull is not None else None
        else:
            added = self.bombs.add() if self.bombs is not None else None
        if added is not True:
            overflow = (
                self._options.bonuses.overflow_points if self._options.bonuses is not None else None
            )
            points: float = 0
            if overflow is not None:
                points = overflow.life if kind == "life" else overflow.bomb
            self.enemies.score += points

    def _aim_at_visible(self) -> None:
        """Only what is on screen can be hit (see `LevelRunOptions.in_view`)."""
        given = self._options.in_view
        if given is not None:
            in_view = given
        else:
            in_view = _default_in_view(self._options.screen.width, self._options.screen.height)
        self._targets.clear()
        for target in self.enemies.targets:
            if in_view(target.x, target.y):
                self._targets.append(target)

    def _clear(self, dt: float) -> None:
        """Completes the level once the last enemies are gone, or after the longest wait, and with a
        journey once the ship has flown off the top of the screen.
        """
        self._clearing_for += dt
        done = self.journey.stage == "gone" if self.journey is not None else self._cleared
        if done:
            self._phase = "complete"

    @property
    def _cleared(self) -> bool:
        return len(self.enemies.enemies) == 0 or self._clearing_for >= self._options.end_wait

    def _fly(self, dt: float, controls: LevelControls) -> bool:
        """The player flies the ship; whether they do: once the game is over the ship is gone (the
        enemies go on until the overlay shows), and while it arrives or leaves the journey flies it.
        """
        if self._phase == "over":
            return False
        scripted = self.journey.scripted if self.journey is not None else False
        flying = not scripted
        if flying and controls.switch_weapon:
            self.arsenal.switch_weapon()
        if flying:
            self.ship.step(dt, controls.move, self._options.bounds)
        ready = self._phase == "clearing" and self._cleared
        if self.journey is not None:
            self.journey.step(dt, self.ship, self._options.bounds, ready)
        return flying

    def _spawn(self, kind_id: str, entry: EnemyEntry, random: Random) -> None:
        kind = None
        for candidate in self._options.kinds:
            if candidate.id == kind_id:
                kind = candidate
                break
        if kind is None:
            return
        screen = self._options.screen
        # Phase 6 review: from the top, only where the ship can reach at the bottom of the screen.
        area = EnemySpawnArea(screen.width, screen.height, random, entry, self._reach)
        self.enemies.add(*kind.spawn(area))

    def _aim_shots(self) -> None:
        """Shots leave from the ship's nose (muzzle) and centre."""
        x = self.ship.x
        y = self.ship.y
        self.shots.muzzle_x = x
        self.shots.center_x = x
        self.shots.center_y = y
        self.shots.muzzle_y = y + self._options.ship.muzzle_offset
