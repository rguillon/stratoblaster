"""Kinds of prop drawn as imposters (D-211, D-212): their pictures baked into one atlas, their quads
drawn by an `ImposterField`; only their lights (if any) stay real geometry, drawn by a `PropField`
from the lights-only factories of `models`.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery.imposter_field import ImposterField
from render.scenery.prop_field import prop_geometry
from render.scenery.scenery_look import PropGeometry

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from core.scenery.ground_boxes import PropPlacement  # noqa: E402

__pragma__("noskip")


def lights_only(factory: Any) -> Any:  # noqa: ANN401
    """A model factory making only the lights of what `factory` makes, and its shadow's stand-in
    (D-212)."""

    def make() -> PropGeometry:
        geometry = prop_geometry(factory)
        return PropGeometry(ColoredGeometry(), geometry.lights, None, None, geometry.shadow)

    return make


class ImposterKinds:
    """The kinds of `kinds` (all of them in `models`: `imposter_kinds` checks), drawn as imposters
    with `atlas` (an `ImposterAtlas`) as the camera tilted by `tilt` sees them. `models`: the
    factories to give a `PropField` (those kinds making only their lights). Their pictures are
    baked by `bake_once`, which must run outside the ground's adoption (the bake's mesh must
    not hang from it)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        scene: Any,  # noqa: ANN401
        models: dict[str, Any],
        kinds: list[str],
        atlas: Any,  # noqa: ANN401
        tilt: float,
    ) -> None:
        self.kinds = kinds
        self.field = ImposterField(scene, kinds, atlas.look, tilt, atlas.material)
        self.models: dict[str, Any] = {}
        for k, factory in models.items():
            self.models[k] = lights_only(factory) if k in kinds else factory
        bodies = [prop_geometry(models[k]).structure for k in kinds]

        def bake() -> None:
            atlas.bake(bodies, tilt)

        self._bake: Any = bake

    @property
    def meshes(self) -> list[Any]:
        """The quads' meshes."""
        return self.field.meshes

    def bake_once(self) -> None:
        """Bakes the pictures, the first time only."""
        if self._bake is not None:
            self._bake()
            self._bake = None

    def place(self, placements: list[PropPlacement]) -> None:
        """Draws the imposters of `placements` (those of other kinds are left out)."""
        self.field.place(placements)


def imposter_kinds(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    scene: Any,  # noqa: ANN401
    models: dict[str, Any],
    kinds: list[str],
    atlas_of: Any,  # noqa: ANN401
    tilt: float,
) -> ImposterKinds | None:
    """The `ImposterKinds` of `kinds`, if `models` has any of them and `atlas_of(count)` gives an
    atlas for them (not None)."""
    names = [k for k in kinds if k in models]
    if len(names) == 0 or atlas_of is None:
        return None
    atlas = atlas_of(len(names))
    if atlas is None:
        return None
    return ImposterKinds(scene, models, names, atlas, tilt)
