# Copyright (c) 2026 Renaud Guillon
"""Stand-ins for the GLSL materials of `render/scenery/*_material_visual.py` (ENG-47).

Those modules build a Babylon `ShaderMaterial` with `render.babylon.new_glsl_material` and drive its
uniforms through vectors and colours they fill with `set(...)`, which returns the vector (as
Babylon's does). Under CPython the `render.babylon` helpers return None, so `patch_shader_babylon`
gives a module working fakes: a material that keeps each uniform set on it, and vectors and colours
that keep their values. `check_uniforms` then compares what was set with what the shaders declare.
"""

import re
from typing import Any

import pytest

from render import babylon

# The material setter that fills each GLSL uniform type.
SETTER_OF_TYPE = {
    "float": "setFloat",
    "vec2": "setVector2",
    "vec3": ("setVector3", "setColor3"),
    "vec4": "setVector4",
    "sampler2D": "setTexture",
}


class Settable:
    """A Babylon Vector2/3/4 or Color3: `set(...)` keeps the values and returns the object."""

    def __init__(self, *values: float) -> None:
        self.values: tuple[float, ...] = tuple(values)

    def set(self, *values: float) -> "Settable":
        self.values = tuple(values)
        return self

    @property
    def x(self) -> float:
        return self.values[0]

    @x.setter
    def x(self, value: float) -> None:
        self.values = (value, *self.values[1:])


class RecordingMaterial:
    """A `ShaderMaterial` made by `new_glsl_material`: its arguments, and each uniform set on it.

    A vector or a colour is kept as its values when it was set (the material code reuses them).
    """

    def __init__(
        self,
        label: str,
        scene: Any,
        sources: tuple[str, str],
        attributes: list[str],
        uniforms: list[str],
        samplers: list[str] | None,
        need_alpha_blending: bool | None,
    ) -> None:
        self.label = label
        self.scene = scene
        self.vertex = sources[0]
        self.fragment = sources[1]
        self.attributes = attributes
        self.declared = uniforms
        self.samplers = samplers
        self.need_alpha_blending = need_alpha_blending
        self.uniforms: dict[str, Any] = {}
        self.setters: dict[str, str] = {}

    def _keep(self, setter: str, name: str, value: Any) -> None:
        self.uniforms[name] = value.values if isinstance(value, Settable) else value
        self.setters[name] = setter

    def setFloat(self, name: str, value: float) -> None:
        self._keep("setFloat", name, value)

    def setVector2(self, name: str, value: Any) -> None:
        self._keep("setVector2", name, value)

    def setVector3(self, name: str, value: Any) -> None:
        self._keep("setVector3", name, value)

    def setVector4(self, name: str, value: Any) -> None:
        self._keep("setVector4", name, value)

    def setColor3(self, name: str, value: Any) -> None:
        self._keep("setColor3", name, value)

    def setTexture(self, name: str, value: Any) -> None:
        self._keep("setTexture", name, value)


def patch_shader_babylon(monkeypatch: pytest.MonkeyPatch, module: Any) -> list[RecordingMaterial]:
    """Give `module` fakes of the `render.babylon` helpers its material uses.

    Returns the list the materials it makes are added to.
    """
    made: list[RecordingMaterial] = []

    def glsl(
        label: str,
        scene: Any,
        vertex: str,
        fragment: str,
        attributes: list[str],
        uniforms: list[str],
        samplers: list[str] | None,
        need_alpha_blending: bool | None,
    ) -> RecordingMaterial:
        material = RecordingMaterial(
            label, scene, (vertex, fragment), attributes, uniforms, samplers, need_alpha_blending
        )
        made.append(material)
        return material

    fakes: dict[str, Any] = {
        "new_glsl_material": glsl,
        "vector2": Settable,
        "vector3": Settable,
        "vector4": Settable,
        "color3": Settable,
        "babylon_constant": lambda key: key,
    }
    for name, fake in fakes.items():
        if getattr(module, name, None) is getattr(babylon, name):
            monkeypatch.setattr(module, name, fake)
    return made


def shader_uniforms(material: RecordingMaterial) -> dict[str, str]:
    """Return the GLSL type of each uniform its two shaders declare."""
    found = re.findall(r"uniform\s+(\w+)\s+(\w+)\s*;", material.vertex + material.fragment)
    return {name: kind for kind, name in found}


def check_uniforms(material: RecordingMaterial) -> None:
    """Check the uniforms of `material` against its shaders.

    Each uniform of the shaders is declared to Babylon (as a uniform, or a sampler), and each one
    set on the material is in the shaders, set by the setter of its GLSL type.
    """
    in_shaders = shader_uniforms(material)
    samplers = material.samplers if material.samplers is not None else []
    for name, kind in in_shaders.items():
        listed = samplers if kind == "sampler2D" else material.declared
        assert name in listed, name + " is used by the shaders but not declared"
    for name, setter in material.setters.items():
        assert name in in_shaders, name + " is set but not in the shaders"
        expected = SETTER_OF_TYPE[in_shaders[name]]
        allowed = expected if isinstance(expected, tuple) else (expected,)
        assert setter in allowed, name + " is set by " + setter
