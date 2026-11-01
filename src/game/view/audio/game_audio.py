"""The game's generated music and sound effects (AUD-MUSIC-01, AUD-SFX-01): the track for each
music request (composed once, then kept), and the
`AudioBindings` the engine takes.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from audio.audio_bindings import MusicRequest  # noqa: E402 (after the Transcrypt skip block, ENG-153)

__pragma__("noskip")

from audio.audio_bindings import AudioBindings, AudioMix  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from audio.audio_types import MusicEffects, Track  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from game.view.audio.compose_track import TrackRequest, compose_track, seed_of  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from game.view.audio.instruments import INSTRUMENTS  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from game.view.audio.jingles import JINGLES  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from game.view.audio.music_styles import MENU_STYLE, WORLD_STYLES, MusicStyle  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from game.view.audio.sound_designs import SOUND_DESIGNS  # noqa: E402 (after the Transcrypt skip block, ENG-153)

# Explosions of enemies at least this big (hit radius, logical pixels) sound large.
LARGE_BLAST_RADIUS = 18

# Levels of the music and sound effect buses at full volume (AUD-ENGINE-02): the loudest sound
# effects stay within `loudest_sfx` (+6 dB) of the music at equal volume settings (AUD-SFX-06).
MIX = AudioMix(0.8, 1)

# The synthwave echo (a dotted eighth) and reverb the instruments send to (AUD-ENGINE-06).
EFFECTS = MusicEffects(0.75, 0.35, 2.2)

# The made tracks, by id: a track is a few thousand notes.
made = {}  # type: dict[str, Track]


def world_of(level_id: str) -> int:
    """The world of a level id such as `2-3` (`Number.parseInt(levelId, 10)`)."""
    __pragma__("js", "{}", "return parseInt(level_id, 10);")
    return 0


def style_of(level_id: str) -> MusicStyle | None:
    """The style of a level's world, if the world exists."""
    return WORLD_STYLES.get(world_of(level_id))


def cached(track_id: str, style: MusicStyle | None, boss: bool) -> Track | None:
    """Composes a track once, then keeps it (AUD-MUSIC-01)."""
    if not style:
        return None
    track = made.get(track_id)
    if not track:
        track = compose_track(TrackRequest(track_id, style, seed_of(track_id), boss))
        made[track_id] = track
    return track


def game_music(request: MusicRequest) -> Track | None:
    """The track for a request: each level its own, from its id (AUD-MUSIC-02); one boss track
    per world (AUD-MUSIC-07); the menu theme (AUD-MUSIC-11); the jingles (AUD-MUSIC-10)."""
    if request.kind == "menu":
        return cached("menu", MENU_STYLE, False)
    level = request.level_id or ""
    if request.kind == "level":
        return cached("level-" + level, style_of(level), False)
    if request.kind == "boss":
        world = world_of(level)
        return cached("boss-" + str(world), WORLD_STYLES.get(world), True)
    if request.kind == "jingle":
        return JINGLES.get(request.jingle or "")
    return None


# The game's generated music and sound effects, the data the game-agnostic engine plays
# (AUD-ENGINE-13).
GAME_AUDIO = AudioBindings(
    game_music,
    INSTRUMENTS,
    SOUND_DESIGNS,
    LARGE_BLAST_RADIUS,
    MIX,
    EFFECTS,
)
