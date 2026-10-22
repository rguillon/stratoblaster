/** A colour (linear RGB, 0..1) at a given height of the sky (-1 = straight down, 1 = straight up). */
export interface GradientStop {
  readonly at: number;
  readonly color: readonly [r: number, g: number, b: number];
}

type Rgb = [number, number, number];

function lerpRgb(a: GradientStop['color'], b: GradientStop['color'], t: number): Rgb {
  const [r1, g1, b1] = a;
  const [r2, g2, b2] = b;
  return [r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t];
}

/** Colour of the gradient at height `y`, linearly interpolated between stops sorted by `at`. */
export function sampleGradient(stops: readonly GradientStop[], y: number): Rgb {
  let previous: GradientStop | undefined;
  for (const stop of stops) {
    if (y <= stop.at) {
      return previous
        ? lerpRgb(previous.color, stop.color, (y - previous.at) / (stop.at - previous.at))
        : [...stop.color];
    }
    previous = stop;
  }
  if (!previous) throw new Error('A gradient needs at least one stop');
  return [...previous.color];
}

// Vertical component of the direction through pixel row `v` (-1 top .. 1 bottom) of each face,
// in the +X, -X, +Y, -Y, +Z, -Z order used by cube textures.
const FACE_HEIGHT: readonly ((u: number, v: number) => number)[] = [
  (u, v) => -v / Math.hypot(1, u, v),
  (u, v) => -v / Math.hypot(1, u, v),
  () => 1,
  () => -1,
  (u, v) => -v / Math.hypot(1, u, v),
  (u, v) => -v / Math.hypot(1, u, v),
];

/** Builds the 6 RGBA8 faces of a cube map whose colour depends only on height. */
export function buildGradientCubeFaces(size: number, stops: readonly GradientStop[]): Uint8Array[] {
  return FACE_HEIGHT.map((height) => {
    const face = new Uint8Array(size * size * 4);
    for (let row = 0; row < size; row++) {
      for (let col = 0; col < size; col++) {
        const u = ((col + 0.5) / size) * 2 - 1;
        const v = ((row + 0.5) / size) * 2 - 1;
        const rgb = sampleGradient(stops, height(u, v));
        face.set(
          [...rgb.map((c) => Math.round(Math.min(1, Math.max(0, c)) * 255)), 255],
          (row * size + col) * 4,
        );
      }
    }
    return face;
  });
}
