"""The darksynth backdrop of the menus (P01-R05, D-103): a night
street between dark towers with lit windows, neon signs and roof trims, scrolling towards the
camera, a distant skyline, haze, rain, and the balanced ship floating and turning above the
street. Everything is generated in code from a fixed seed. The ship is hidden on the ship select
screen, which shows the ships itself.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.rng import create_rng
from game.config.title_look import TITLE_LOOK as LOOK
from game.view.balanced_ship import build_balanced_ship
from game.view.city_geometry import build_city_chunk, build_rain, build_skyline
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

__pragma__("jsmod")

__pragma__("skip")
from typing import Any  # noqa: E402

Scene = Any
__pragma__("noskip")


def _self_lit(name: str, scene: Any, fog: bool, intensity: float) -> Any:
    """A material that shows its vertex colours times a grey emissive: unlit."""
    mat = new_standard_material(name, scene)
    mat.emissiveColor = color3(intensity, intensity, intensity)
    mat.diffuseColor = color3_black()
    mat.specularColor = color3_black()
    mat.disableLighting = True
    mat.backFaceCulling = False
    mat.fogEnabled = fog
    return mat


def _colored_mesh(name: str, geo: Any, scene: Any, fog: bool, intensity: float = 1) -> Any:
    """A mesh of the vertex-coloured geometry `geo`, self-lit."""
    mesh = new_mesh(name, scene)
    data = vertex_data_of(geo.positions, geo.indices, None, geo.colors)
    apply_vertex_data(data, mesh)
    mesh.material = _self_lit(name, scene, fog, intensity)
    return mesh


def _build_sky(scene: Any, random: Any) -> list[Any]:
    """The sky and the distant skyline; returns the meshes that must not glow."""
    sky = LOOK.sky
    sky_mesh = _colored_mesh(
        "title-sky",
        build_gradient_rect(sky.width, sky.height, sky.stops),
        scene,
        False,
    )
    sky_mesh.position.set(0, sky.centerY, sky.z)
    skyline_look = LOOK.skyline
    towers = build_skyline(skyline_look, random)
    skyline_mesh = _colored_mesh("title-skyline", towers["structure"], scene, False)
    skyline_lights = _colored_mesh(
        "title-skyline-lights",
        towers["lights"],
        scene,
        False,
        LOOK.neonIntensity,
    )
    for mesh in [skyline_mesh, skyline_lights]:
        mesh.position.set(0, skyline_look.y, skyline_look.z)
    return [sky_mesh, skyline_mesh]


def _build_city(scene: Any, random: Any) -> dict[str, Any]:
    """Two copies of a city chunk, end to end, under one node that scrolls towards the camera."""
    chunk = build_city_chunk(LOOK.city, random)
    city = new_transform_node("title-city", scene)
    structure = _colored_mesh("title-city-structure", chunk["structure"], scene, True)
    lights = _colored_mesh("title-city-lights", chunk["lights"], scene, True, LOOK.neonIntensity)
    structure.parent = city
    lights.parent = city
    structure_copy = structure.clone("title-city-structure-2", city)
    lights_copy = lights.clone("title-city-lights-2", city)
    structure_copy.position.z = LOOK.city["length"]
    lights_copy.position.z = LOOK.city["length"]
    return {"city": city, "structure": [structure, structure_copy]}


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
    """Builds the title backdrop in `scene` and returns its `MenuBackdrop` handle: the meshes that
    must not glow, an `update(dt)` per frame, and `showScreen(screen)`."""
    _set_up_scene(scene)
    random = create_rng(LOOK.seed)
    sky = _build_sky(scene, random)
    city_parts = _build_city(scene, random)
    city = city_parts["city"]
    structure = city_parts["structure"]
    rain = _colored_mesh("title-rain", build_rain(LOOK.rain, random), scene, True)
    rain.position.y = LOOK.rain.y
    pivot = new_transform_node("title-ship", scene)
    ship_position = LOOK.ship.position
    pivot.position.set(ship_position[0], ship_position[1], ship_position[2])
    ship = build_balanced_ship(scene)
    ship.parent = pivot
    # Seconds since the backdrop was built.
    clock = [0.0]

    glow_excluded: list[Any] = []
    glow_excluded.extend(sky)
    glow_excluded.extend(structure)
    glow_excluded.append(rain)

    def update_frame(dt: float) -> None:
        clock[0] = clock[0] + dt
        t = clock[0]
        c = LOOK.city
        r = LOOK.rain
        s = LOOK.ship
        city.position.z = -((t * c.scrollSpeed) % c["length"])
        rain.position.y = r.y - ((t * r.speed) % r.height)
        pivot.rotation.y += s.rotationSpeedRadPerSec * dt
        pivot.position.y = s.position[1] + s.bobAmplitude * math.sin(2 * math.pi * s.bobHz * t)
        step_model_animations(ship, dt)

    def show_screen(screen: str) -> None:
        pivot.setEnabled(screen != "ship-select")

    # The handle is a JavaScript object: `update` is read by the render layer as a property name.
    backdrop = js_object()
    js_set(backdrop, "glowExcludedMeshes", glow_excluded)
    js_set(backdrop, "update", update_frame)
    js_set(backdrop, "showScreen", show_screen)
    return backdrop
