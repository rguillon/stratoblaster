# Copyright (c) 2026 Renaud Guillon
"""Apply a graphics quality level to a scene, and time the GPU's frames (D-410).

The share of pixels drawn is set by the page (its fit, ENG-110); here, what a level changes in a
scene: the sun's shadows' filtering, and its glow layers' blur, kept the same size on screen when
fewer pixels are drawn (their images follow the canvas's size).
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import new_weak_map

# isort: split
# __pragma__ ("skip")
from typing import Any

from render.handles import WeakMap

# __pragma__ ("noskip")


# Each glow layer's blur, as made (in pixels of its image at the full pixel count).
_GLOW_KERNELS: WeakMap[float] = new_weak_map()


def apply_quality(scene: Any, render_scale: float, shadow_filter: str) -> None:
    """Set the shadows' filtering (`"medium"` or `"low"`) and the glows' blur of `scene`.

    `render_scale`: the share of the pixels drawn across; a glow's blur, counted in pixels of its
    image, shrinks with it, so the glow keeps its size on screen.
    """
    kernels = _GLOW_KERNELS
    __pragma__(
        "js",
        "{}",
        """
        const quality = shadow_filter === 'low'
            ? BABYLON.ShadowGenerator.QUALITY_LOW : BABYLON.ShadowGenerator.QUALITY_MEDIUM;
        for (const light of scene.lights) {
            const shadows = light.getShadowGenerator ? light.getShadowGenerator() : null;
            if (shadows && shadows.usePercentageCloserFiltering) {
                shadows.filteringQuality = quality;
            }
        }
        for (const layer of scene.effectLayers || []) {
            if (layer.blurKernelSize === undefined) continue;
            if (!kernels.has(layer)) kernels.set(layer, layer.blurKernelSize);
            layer.blurKernelSize = Math.max(1, kernels.get(layer) * render_scale);
        }
        """,
    )


def new_gpu_timer(engine: Any) -> Any:
    """Return a timer of the GPU's frames on `engine`, or None where the browser has none."""
    __pragma__(
        "js",
        "{}",
        """
        if (!engine.getCaps().timerQuery) return null;
        try {
            const timer = new BABYLON.EngineInstrumentation(engine);
            timer.captureGPUFrameTime = true;
            return timer;
        } catch (error) {
            return null;
        }
        """,
    )
    return None


def gpu_frame_ms(timer: Any) -> float | None:
    """Return the GPU's time on the last frame timed, in ms, or None when none is timed yet."""
    __pragma__(
        "js",
        "{}",
        """
        const ns = timer.gpuFrameTimeCounter.current;
        return ns > 0 ? ns / 1e6 : null;
        """,
    )
    return None
