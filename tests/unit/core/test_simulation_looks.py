# Copyright (c) 2026 Renaud Guillon
"""The simulation does not read the look.

Weather (GFX-WEATHER-05) and lava (GFX-TERRAIN-18) are only looks. Checked over the import
statements of `src/core/`: the simulation modules import none of the sky, weather, terrain, lava or
lightning looks.
"""

import ast
from pathlib import Path

import core

CORE_DIR = Path(core.__file__).resolve().parent

# The modules that are the look itself (the sky, the lightning and the atmosphere, pure, in core):
# they may import the weather and time-of-day configs, the simulation may not import them.
LOOK_MODULES = {"core.scenery.sky_look", "core.scenery.lightning", "core.scenery.atmosphere"}

# A module name containing one of these words is a look (sky, weather, terrain, lava) or the
# configs of one (time of day, lightning).
LOOK_WORDS = ("sky", "weather", "terrain", "lava", "lightning", "atmosphere", "time_of_day")


def _module_name(path: Path) -> str:
    relative = path.relative_to(CORE_DIR.parent).with_suffix("")
    return ".".join(relative.parts)


def _imports(path: Path) -> list[str]:
    """Return the absolute modules a file imports, in its import statements.

    Those under a `__pragma__` skip block are included too: they are still imports.
    """
    names: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.append(node.module)
    return names


def _is_look(module: str) -> bool:
    return any(word in part for part in module.split(".") for word in LOOK_WORDS)


def _simulation_files() -> list[Path]:
    return sorted(
        path
        for path in CORE_DIR.rglob("*.py")
        if _module_name(path) not in LOOK_MODULES and "__pycache__" not in path.parts
    )


def test_gfx_weather_05_the_simulation_does_not_import_the_weather_or_the_sky() -> None:
    """Also GFX-TERRAIN-18: lava is not an input of the simulation either."""
    files = _simulation_files()
    assert len(files) > 50
    offending = [
        (_module_name(path), name) for path in files for name in _imports(path) if _is_look(name)
    ]
    assert offending == []


def test_gfx_weather_05_the_scan_sees_the_look_imports_it_is_meant_to_forbid() -> None:
    """The check is not blind: the look modules themselves do import the weather and sky configs."""
    sky_look = CORE_DIR / "scenery" / "sky_look.py"
    assert "config.weather" in _imports(sky_look)
    assert any(_is_look(name) for name in _imports(sky_look))
