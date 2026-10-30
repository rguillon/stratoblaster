"""P16-R06, 3-3: the living beast the Sky Temple grew on. Ported from
`view/bosses/world-3/sky-temple-flesh.ts`. Logical pixels, nose +Z, Y up: a huge, swollen body
of moss-skinned flesh carrying the stone tiers on its back like a shell, roots of sinew hanging
from it, veins climbing the stones to the sanctum."""

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.world_3.jungle_flesh import JUNGLE_FLESH, F, gland, sinew, table, vein_to
from game.view.bosses.world_3.sky_temple_parts import SUMMIT, TEMPLE_CYAN, TIERS
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import ROUND_SECTION

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")


def body_stations() -> list[list[float]]:
    """The body under the lowest tier, tail to front (loft stations: z, half width, bottom,
    top)."""
    half = TIERS.halves[0]
    top = TIERS.height + 1
    return [
        [-half - 2, half * 0.55, 2, top - 4],
        [-half * 0.7, half * 0.98, -3, top],
        [0, half * 1.04, -4, top + 1],
        [half * 0.7, half * 0.98, -3, top],
        [half + 2, half * 0.55, 2, top - 4],
    ]


def temple_body(p: EnemyParts) -> None:
    """The body of the beast (P16-R06), in place of the lowest stone tier."""
    p.flesh.loft(ROUND_SECTION, body_stations(), JUNGLE_FLESH)
    half = TIERS.halves[0]
    for s in SIDES:
        for z in [-40, 0, 40]:
            sinew(
                p,
                [[s * half * 0.9, 0, z], [s * (half + 3), -12, z + 6]],
                [s * 2, -2, 0],
                2.4,
            )
    # Veins climbing the tiers along their diagonals up to the sanctum.
    for x in SIDES:
        for z in SIDES:
            start: Vec3 = [x * half * 0.8, TIERS.height + 1.2, z * half * 0.8]
            end: Vec3 = [x * 12, SUMMIT + 0.4, z * 12 - 8]
            vein_to(p, [start, end], [0, 6, 0], TEMPLE_CYAN, 1.6)
            gland(
                p,
                [x * half * 0.8, TIERS.height + 0.4, z * half * 0.8],
                3,
                TEMPLE_CYAN,
            )


def temple_reactors(p: EnemyParts, z: float, nozzles: list[float]) -> None:
    """Its reactors (P16-R01): each in a flesh sac at the back of the beast."""
    for x in nozzles:
        reactor_sac(p, table([x, 0, z]), 4.5, table(TEMPLE_CYAN), F.sinew, None)
