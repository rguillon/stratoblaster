"""The shots and explosions of the enemies page, ported from `app/enemy-viewer-shots.ts`.

Everything is drawn on the playfield layer: the player's shots (one renderer per weapon, as on
`player_shots/`, hits included), the enemies' shots and the explosions (GD-62).
"""

from org.transcrypt.stubs.browser import __pragma__

from render.game_view import EnemyShotFrame, ShotFrame

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class ShotsToDraw:
    """What `EnemyViewerShots.sync` draws: the `enemies` and the `shots` (their worlds), the new
    `blasts` and `impacts`, and the `dt` seconds of the frame."""

    def __init__(self, enemies: Any, shots: Any, blasts: Any, impacts: Any, dt: float) -> None:
        self.enemies = enemies
        self.shots = shots
        self.blasts = blasts
        self.impacts = impacts
        self.dt = dt


class EnemyViewerShots:
    """The shots and explosions of the enemies page, all drawn on the playfield layer."""

    def __init__(self, game: Any, playfield: Any, shot_style: str | None = None) -> None:
        """`shot_style`: the level's style for the enemy shots (phase 10, P10-R07), if any."""
        self.playfield = playfield
        scene = playfield.root.getScene()

        def build() -> list[Any]:
            player: dict[str, Any] = {}
            for weapon in game.player_weapons:
                factory = game.view.player_shot_renderers.get(weapon.id)
                if factory is None:
                    raise ValueError('No shot renderer for weapon "' + weapon.id + '"')
                player[weapon.id] = factory(scene)
            enemy = game.view.enemies.shots(scene, shot_style)
            return [player, enemy, game.view.enemies.blasts(scene)]

        built = playfield.run(build)
        self._player: dict[str, Any] = built[0]
        self._enemy: Any = built[1]
        self._blasts: Any = built[2]

    def sync(self, to_draw: ShotsToDraw) -> None:
        """Draws the frame described by `to_draw`."""
        enemies = to_draw.enemies
        shots = to_draw.shots
        impacts = to_draw.impacts
        dt = to_draw.dt

        def draw() -> None:
            flying = [p for p in shots.projectiles if p.alive]
            for weapon_id, renderer in self._player.items():
                beam = shots.beam if shots.weapon.id == weapon_id else []
                renderer.sync(
                    ShotFrame(
                        [p for p in flying if p.weapon.id == weapon_id],
                        beam,
                        [impact for impact in impacts if impact.weapon_id == weapon_id],
                        dt,
                    )
                )
            s = enemies.shots
            self._enemy.sync(
                EnemyShotFrame(
                    [b for b in s.bullets if b.alive],
                    [m for m in s.missiles if m.alive],
                    s.lasers,
                    dt,
                )
            )
            self._blasts.sync(to_draw.blasts, dt)

        self.playfield.run(draw)

    def dispose(self) -> None:
        for renderer in self._player.values():
            renderer.dispose()
        self._enemy.dispose()
        self._blasts.dispose()
