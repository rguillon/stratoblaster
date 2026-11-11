# Copyright (c) 2026 Renaud Guillon
"""The backdrop of the menus: the ship racing down a neon trench (UI-TITLE-07, D-325).

UI-TITLE-08 for its colours. The balanced ship flies down a trench towards a frontal camera that
flies backwards ahead of it; the trench scrolls away behind the ship, speed streaks rush past
faster still, and the ship sways, banks and floats. Everything is generated in code from a fixed
seed. The ship is hidden on the ship select screen, which shows the ships itself (UI-TITLE-09).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.rng import create_rng
from game.config.title_look import TITLE_LOOK as LOOK
from game.view.balanced_ship import build_balanced_ship
from game.view.trench_geometry import build_streaks, build_trench_chunk
from render.babylon import (
    apply_vertex_data,
    babylon_class,
    color3,
    color3_black,
    color4,
    js_object,
    js_set,
    new_directional_light,
    new_free_camera,
    new_hemispheric_light,
    new_mesh,
    new_standard_material,
    new_transform_node,
    vector3,
    vector3_up,
    vertex_data_of,
)
from render.geometry.gradient_shapes import build_gradient_rect
from render.model_animation import step_model_animations

# isort: split
# __pragma__ ("skip")
from typing import Any

Scene = Any
# __pragma__ ("noskip")

__pragma__("jsmod")


def _self_lit(name: str, scene: Any, fog: bool, intensity: float) -> Any:
    """Return a material that shows its vertex colours times a grey emissive: unlit."""
    mat = new_standard_material(name, scene)
    mat.emissiveColor = color3(intensity, intensity, intensity)
    mat.diffuseColor = color3_black()
    mat.specularColor = color3_black()
    mat.disableLighting = True
    mat.backFaceCulling = False
    mat.fogEnabled = fog
    return mat


def _colored_mesh(name: str, geo: Any, scene: Any, fog: bool, intensity: float = 1) -> Any:
    """Return a mesh of the vertex-coloured geometry `geo`, self-lit."""
    mesh = new_mesh(name, scene)
    data = vertex_data_of(geo.positions, geo.indices, None, geo.colors)
    apply_vertex_data(data, mesh)
    mesh.material = _self_lit(name, scene, fog, intensity)
    return mesh


def _build_sky(scene: Any) -> Any:
    """Return the glow at the far end of the trench, kept out of the glow layer."""
    sky = LOOK.sky
    sky_mesh = _colored_mesh(
        "title-sky",
        build_gradient_rect(sky.width, sky.height, sky.stops),
        scene,
        False,
    )
    sky_mesh.position.set(0, sky.centerY, sky.z)
    return sky_mesh


def _build_trench(scene: Any, random: Any) -> dict[str, Any]:
    """Two stretches of trench end to end, under one node that scrolls away from the camera.

    Each stretch is two merged meshes, the lights at the neon intensity (UI-TITLE-10). The second
    stretch lies one length nearer the camera, so the trench reaches it as the node moves away.
    """
    look = LOOK.trench
    chunk = build_trench_chunk(look, random)
    trench = new_transform_node("title-trench", scene)
    structure = _colored_mesh("title-trench-structure", chunk["structure"], scene, True)
    lights = _colored_mesh("title-trench-lights", chunk["lights"], scene, True, LOOK.neonIntensity)
    structure.parent = trench
    lights.parent = trench
    structure_copy = structure.clone("title-trench-structure-2", trench)
    lights_copy = lights.clone("title-trench-lights-2", trench)
    structure_copy.position.z = look["length"]
    lights_copy.position.z = look["length"]
    trench.position.z = look.startZ
    return {"trench": trench, "structure": [structure, structure_copy]}


def _build_streaks(scene: Any, random: Any) -> Any:
    """Two stretches of speed streaks end to end, under one node; they glow."""
    look = LOOK.streaks
    streaks = new_transform_node("title-streaks", scene)
    mesh = _colored_mesh("title-streak-mesh", build_streaks(look, random), scene, True)
    mesh.parent = streaks
    mesh.clone("title-streak-mesh-2", streaks).position.z = look["length"]
    streaks.position.z = look.startZ
    return streaks


def _set_up_scene(scene: Any) -> None:
    """Horizon colour, linear fog, the camera, and the lights of the title screen."""
    horizon = LOOK.horizon
    scene.clearColor = color4(horizon[0], horizon[1], horizon[2], 1)
    scene.fogMode = babylon_class("Scene").FOGMODE_LINEAR
    scene.fogColor = color3(horizon[0], horizon[1], horizon[2])
    scene.fogStart = LOOK.fog.start
    scene.fogEnd = LOOK.fog.end
    position = LOOK.camera.position
    target = LOOK.camera.target
    camera = new_free_camera("title-camera", vector3(position[0], position[1], position[2]), scene)
    camera.setTarget(vector3(target[0], target[1], target[2]))
    camera.fov = LOOK.camera.fov
    new_hemispheric_light("title-ambient", vector3_up(), scene).intensity = LOOK.lights.ambient
    direction = LOOK.lights.keyDirection
    key = new_directional_light(
        "title-key", vector3(direction[0], direction[1], direction[2]), scene
    )
    key.intensity = LOOK.lights.key


def build_title_backdrop(scene: Any) -> Any:
    """Build the title backdrop in `scene` and return its `MenuBackdrop` handle.

    The handle holds the meshes that must not glow, an `update(dt)` per frame, and
    `showScreen(screen)`.
    """
    _set_up_scene(scene)
    random = create_rng(LOOK.seed)
    sky = _build_sky(scene)
    trench_parts = _build_trench(scene, random)
    trench = trench_parts["trench"]
    streaks = _build_streaks(scene, random)
    pivot = new_transform_node("title-ship", scene)
    ship_position = LOOK.ship.position
    pivot.position.set(ship_position[0], ship_position[1], ship_position[2])
    # The model's nose is towards +Z, where the camera is: the ship flies at it.
    ship = build_balanced_ship(scene)
    ship.parent = pivot
    # Seconds since the backdrop was built.
    clock = [0.0]

    glow_excluded: list[Any] = [sky]
    glow_excluded.extend(trench_parts["structure"])

    def update_frame(dt: float) -> None:
        clock[0] = clock[0] + dt
        t = clock[0]
        tr = LOOK.trench
        st = LOOK.streaks
        s = LOOK.ship
        trench.position.z = tr.startZ - ((t * tr.speed) % tr["length"])
        streaks.position.z = st.startZ - ((t * st.speed) % st["length"])
        sway = 2 * math.pi * s.swayHz * t
        pivot.position.x = s.position[0] + s.swayAmplitude * math.sin(sway)
        pivot.position.y = s.position[1] + s.bobAmplitude * math.sin(2 * math.pi * s.bobHz * t)
        # Banks into the sway, rolled most where it moves sideways fastest: moving to +X, its +X
        # wing dips (a negative roll about Z in Babylon's left-handed frame).
        pivot.rotation.z = -s.bankRad * math.cos(sway)
        step_model_animations(ship, dt)

    def show_screen(screen: str) -> None:
        pivot.setEnabled(screen != "ship-select")

    # The handle is a JavaScript object: `update` is read by the render layer as a property name.
    backdrop = js_object()
    js_set(backdrop, "glowExcludedMeshes", glow_excluded)
    js_set(backdrop, "update", update_frame)
    js_set(backdrop, "showScreen", show_screen)
    return backdrop
