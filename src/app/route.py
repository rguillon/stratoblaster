"""The pages the app can start on, ported from `app/route.ts`: picked from the URL path, so it
works under any deployment sub-path.
"""

from org.transcrypt.stubs.browser import __pragma__

# (pattern, route) pairs, tried in order. The patterns are JavaScript regular expression sources.
# `bosses/` or `boss/` (phase 7 review); `props/` (reviewer, 2026-10-28).
ROUTE_PATTERNS = [
    ["/player_ship(/(index\\.html)?)?$", "player-ship-viewer"],
    ["/player_shots(/(index\\.html)?)?$", "player-shots-viewer"],
    ["/enemies(/(index\\.html)?)?$", "enemy-viewer"],
    ["/boss(es)?(/(index\\.html)?)?$", "boss-viewer"],
    ["/props(/(index\\.html)?)?$", "prop-viewer"],
]


def _matches(source: str, text: str) -> bool:
    __pragma__("js", "{}", "return new RegExp(source).test(text);")
    return False


def resolve_route(pathname: str) -> str:
    """Picks the page to start from the URL path."""
    for pattern, route in ROUTE_PATTERNS:
        if _matches(pattern, pathname):
            return route
    return "game"


def redirect_of(pathname: str) -> str | None:
    """Where to send the browser instead of `pathname`, if anywhere: a viewer's path without its
    trailing slash (`/props`) gets the game's page from the dev server, so it goes to `/props/`.
    """
    if resolve_route(pathname) == "game" or _matches("(/|\\.html)$", pathname):
        return None
    return pathname + "/"
