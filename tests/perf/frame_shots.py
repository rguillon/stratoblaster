# Copyright (c) 2026 Renaud Guillon
"""Draw the same frames of two builds and compare them (PERF-03: a change keeps the frames).

Serves an e2e build (`dist-e2e/`, which only moves when stepped, so the same steps give the same
frame on any machine), starts each level asked for at a time of its run, steps it by a number of
frames and saves a screenshot of the canvas. With `--against`, the screenshots of another run are
compared pixel by pixel instead of shown side by side.

    PYTHONPATH=tests uv run python tests/perf/frame_shots.py --out /tmp/after
    PYTHONPATH=tests uv run python tests/perf/frame_shots.py --out /tmp/after --against /tmp/before
"""

import argparse
import base64
import sys
from pathlib import Path

from e2e.menu_helpers import open_debug, step
from measure_perf import _serve
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
# `level@seconds+frames`: the level, where it starts, and the frames stepped before the shot.
SHOTS = "1-1@30+420,1-4@60+420,2-1@40+420,2-3@120+300,3-1@30+600,3-4@90+420,4-1@30+600,4-5@200+600"
# The frame is drawn again this many times, this far apart, before the shot.
SETTLE_DRAWS = 6
SETTLE_MS = 250
# A channel may differ by this much (of 255) before a pixel counts as different.
TOLERANCE = 2


def _out(text: str) -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def take(args: argparse.Namespace) -> None:
    """Save a screenshot of each shot asked for."""
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    server = _serve(Path(args.build), args.port)
    try:
        with sync_playwright() as play:
            browser = play.chromium.launch(channel="chromium", args=args.browser_args.split())
            for shot in args.shots.split(","):
                level, _, rest = shot.partition("@")
                at, _, frames = rest.partition("+")
                page = browser.new_page(
                    viewport={"width": 1280, "height": 720},
                    base_url=f"http://127.0.0.1:{args.port}/",
                )
                open_debug(page, f"?level={level}&t={at}")
                step(page, int(frames))
                # Shaders first needed by this frame compile in the background, and what waits
                # for one is left out: the frame is drawn again until they are all there.
                for _ in range(SETTLE_DRAWS):
                    page.wait_for_timeout(SETTLE_MS)
                    step(page, 0)
                page.locator("#game-canvas").screenshot(path=str(out / (shot + ".png")))
                _out("shot " + shot)
                page.close()
            browser.close()
    finally:
        server.shutdown()


# In a blank page: the pixels of two images that differ by more than `tolerance` on a channel,
# and the box that holds them.
DIFFERENCE = """async ([first, second, tolerance]) => {
  const load = (data) => new Promise((resolve) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.src = 'data:image/png;base64,' + data;
  });
  const pixels = (image) => {
    const canvas = document.createElement('canvas');
    canvas.width = image.width;
    canvas.height = image.height;
    const context = canvas.getContext('2d');
    context.drawImage(image, 0, 0);
    return context.getImageData(0, 0, image.width, image.height).data;
  };
  const a = await load(first);
  const b = await load(second);
  if (a.width !== b.width || a.height !== b.height) return {sizes: true};
  const p = pixels(a);
  const q = pixels(b);
  let count = 0;
  const box = [a.width, a.height, 0, 0];
  for (let i = 0; i < p.length; i += 4) {
    const d = Math.max(Math.abs(p[i] - q[i]), Math.abs(p[i + 1] - q[i + 1]),
      Math.abs(p[i + 2] - q[i + 2]));
    if (d <= tolerance) continue;
    count += 1;
    const x = (i / 4) % a.width;
    const y = Math.floor(i / 4 / a.width);
    box[0] = Math.min(box[0], x);
    box[1] = Math.min(box[1], y);
    box[2] = Math.max(box[2], x);
    box[3] = Math.max(box[3], y);
  }
  return {count: count, total: a.width * a.height, box: box};
}"""


def compare(args: argparse.Namespace) -> None:
    """Write how many pixels of each shot differ from the same shot of `--against`."""
    with sync_playwright() as play:
        browser = play.chromium.launch(channel="chromium")
        page = browser.new_page()
        for path in sorted(Path(args.out).glob("*.png")):
            other = Path(args.against) / path.name
            if not other.exists():
                continue
            images = [base64.b64encode(each.read_bytes()).decode() for each in (path, other)]
            result = page.evaluate(DIFFERENCE, [*images, TOLERANCE])
            if "sizes" in result:
                _out(f"{path.name}: not the same size")
                continue
            share = 100 * result["count"] / result["total"]
            box = result["box"] if result["count"] else None
            _out(f"{path.name}: {result['count']} pixels differ ({share:.3f} %), box {box}")
        browser.close()


def main() -> None:
    """Take the shots, or compare them with another run's."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    parser.add_argument("--out", required=True)
    parser.add_argument("--against", help="directory of another run's shots, to compare with")
    parser.add_argument("--build", default=str(ROOT / "dist-e2e"))
    parser.add_argument("--shots", default=SHOTS)
    parser.add_argument("--port", type=int, default=8773)
    parser.add_argument(
        "--browser-args",
        default="--use-angle=vulkan --enable-features=Vulkan --enable-gpu --ignore-gpu-blocklist",
    )
    args = parser.parse_args()
    if args.against:
        compare(args)
    else:
        take(args)


if __name__ == "__main__":
    main()
