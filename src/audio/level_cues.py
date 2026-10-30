"""The engine's sound cues (P12-R09), ported from `audio/level-cues.ts`: what happened in a level
step that a game may give a sound. `fire:<weaponId>` (a volley of a projectile weapon),
`beam-start:<weaponId>` (a beam starts; `beam:<weaponId>` names its looping hum), `weapon-switch`,
`weapon-up`, `enemy-bullet`, `enemy-missile`, `laser-warning`, `laser-fire`, `hit`, `hit-blocked`,
`player-hit`, `blast-small`, `blast-large`, `part-destroyed`, `boss-destroyed`, `life-lost`,
`extra-life`, `bomb`, `bonus:<kind>`; and on the menus `menu-move`, `menu-confirm`, `menu-back`,
`pause`, `resume`, `slider`.

Audio only reads the core's state, it never changes it (ENG-11). The TypeScript Sets and Maps of
bullets and lasers are lists compared by identity (`is`), as Transcrypt has no object-keyed
collections.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.systems.level_run import LevelRun

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class SoundCue:
    """A sound cue: `cue`, and where it happened on the playfield (`x`, None when not panned)."""

    def __init__(self, cue: str, x: float | None = None) -> None:
        self.cue = cue
        self.x = x


class _PlayerSnapshot:
    """What the player's weapons, hull and bombs were at the last step."""

    def __init__(
        self, weapon: str, level: float, lives: float, bombs: float, bosses: float
    ) -> None:
        self.weapon = weapon
        self.level = level
        self.lives = lives
        self.bombs = bombs
        self.bosses = bosses


def _contains(items: list[Any], item: Any) -> bool:
    """Whether `item` is one of `items` (by identity: `in` on a Transcrypt list is `indexOf`)."""
    return item in items


class LevelCues:
    """Turns the state of a `LevelRun` after each step into sound cues (P12-R09), by comparing it
    with the step before: new shots, impacts, blasts, hits, bonuses picked up. One cue of a kind
    per step: a volley of shots is one sound.
    """

    def __init__(self, large_blast_radius: float) -> None:
        self._large_blast_radius = large_blast_radius
        self._started = False
        # The player's volleys counted at the last step.
        self._volleys = 0
        self._bullets: list[Any] = []
        # The lasers and their phase at the last step: parallel lists.
        self._laser_keys: list[Any] = []
        self._laser_phases: list[str] = []
        self._missile_id = 0
        self._snapshot = _PlayerSnapshot("", 0, 0, 0, 0)
        # The beam weapon firing at the last step, if any.
        self.beam: str | None = None

    def observe(self, run: LevelRun) -> list[SoundCue]:
        """The cues of the step just run. The first call only takes the starting state."""
        cues: list[SoundCue] = []
        self._player_shots(run, cues)
        self._enemy_shots(run, cues)
        self._laser_cues(run, cues)
        self._impacts(run, cues)
        self._hits(run, cues)
        self._player(run, cues)
        if not self._started:
            self._started = True
            return []
        return cues

    def _player_shots(self, run: LevelRun, cues: list[SoundCue]) -> None:
        """A volley's first shot sounds it (its streams fire one after the other)."""
        shots = run.shots
        if shots.volleys != self._volleys:
            _add(cues, "fire:" + shots.weapon.id, run.ship.x)
        self._volleys = shots.volleys
        beam = shots.weapon.id if len(shots.beam) > 0 else None
        if beam is not None and beam != self.beam:
            _add(cues, "beam-start:" + beam, run.ship.x)
        self.beam = beam

    def _enemy_shots(self, run: LevelRun, cues: list[SoundCue]) -> None:
        shots = run.enemies.shots
        alive: list[Any] = []
        for bullet in shots.bullets:
            if not bullet.alive:
                continue
            alive.append(bullet)
            if not _contains(self._bullets, bullet):
                _add(cues, "enemy-bullet", bullet.x)
        self._bullets = alive
        for missile in shots.missiles:
            if missile.alive and missile.id > self._missile_id:
                _add(cues, "enemy-missile", missile.x)
            self._missile_id = max(self._missile_id, missile.id)

    def _laser_cues(self, run: LevelRun, cues: list[SoundCue]) -> None:
        """A laser's warning line, then its beam."""
        keys: list[Any] = []
        phases: list[str] = []
        for laser in run.enemies.shots.lasers:
            before = self._phase_before(laser)
            if before is None:
                _add(cues, "laser-warning", laser.x)
            if laser.phase == "firing" and before != "firing":
                _add(cues, "laser-fire", laser.x)
            keys.append(laser)
            phases.append(laser.phase)
        self._laser_keys = keys
        self._laser_phases = phases

    def _phase_before(self, laser: Any) -> str | None:
        for i in range(len(self._laser_keys)):
            if self._laser_keys[i] is laser:
                return self._laser_phases[i]
        return None

    def _impacts(self, run: LevelRun, cues: list[SoundCue]) -> None:
        for impact in run.impacts:
            _add(cues, "hit-blocked" if impact.blocked else "hit", impact.x)
        for blast in run.blasts:
            large = blast.kind == "enemy" and blast.radius >= self._large_blast_radius
            _add(cues, "blast-large" if large else "blast-small", blast.x)
        for part in run.enemies.broken_parts:
            _add(cues, "part-destroyed", part.x)

    def _hits(self, run: LevelRun, cues: list[SoundCue]) -> None:
        """Hits on the player, and bonuses picked up."""
        for hit in run.hits:
            if hit.event == "hit":
                _add(cues, "player-hit", hit.x)
            elif hit.event != "ignored":
                _add(cues, "life-lost", hit.x)
        picked = run.bonuses.picked if run.bonuses is not None else []
        for bonus in picked:
            _add(cues, "bonus:" + bonus.kind, bonus.x)

    def _player(self, run: LevelRun, cues: list[SoundCue]) -> None:
        now = _PlayerSnapshot(
            run.shots.weapon.id,
            run.shots.level,
            run.hull.lives if run.hull is not None else 0,
            run.bombs.fired if run.bombs is not None else 0,
            len(run.fights.defeated),
        )
        before = self._snapshot
        if now.weapon != before.weapon:
            _add(cues, "weapon-switch", None)
        elif now.level > before.level:
            _add(cues, "weapon-up", None)
        if now.lives > before.lives:
            _add(cues, "extra-life", None)
        if now.bombs > before.bombs:
            _add(cues, "bomb", run.ship.x)
        if now.bosses > before.bosses:
            _add(cues, "boss-destroyed", None)
        self._snapshot = now


def _add(cues: list[SoundCue], cue: str, x: float | None) -> None:
    """Adds a cue unless one of the same kind is already in this step (one cue per kind)."""
    for existing in cues:
        if existing.cue == cue:
            return
    cues.append(SoundCue(cue, x))
