/**
 * Colour helpers for readability (phase 14): luminance, contrast ratio, hue families. Colours
 * are linear RGB, 0..1, unless noted.
 */

export type Rgb = readonly [number, number, number];

/** Relative luminance of a linear RGB colour (WCAG 2), 0..1. */
export function relativeLuminance([r, g, b]: Rgb): number {
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** A gamma-encoded (sRGB) channel byte, 0..255, as linear 0..1. */
export function srgbByteToLinear(byte: number): number {
  const c = byte / 255;
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/** Contrast ratio between two relative luminances (WCAG 2): 1 (none) to 21 (black on white). */
export function contrastRatio(a: number, b: number): number {
  const [hi, lo] = a > b ? [a, b] : [b, a];
  return (hi + 0.05) / (lo + 0.05);
}

/** Hue in degrees [0, 360) and saturation (HSV, 0..1) of a colour; grey has hue 0. */
export function hueSaturation([r, g, b]: Rgb): { hue: number; saturation: number } {
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const chroma = max - min;
  if (chroma <= 0) return { hue: 0, saturation: 0 };
  let sector: number;
  if (max === r) sector = ((g - b) / chroma + 6) % 6;
  else if (max === g) sector = (b - r) / chroma + 2;
  else sector = (r - g) / chroma + 4;
  return { hue: sector * 60, saturation: chroma / max };
}

/**
 * A family of colours: those whose hue lies in `[from, to]` degrees (`from` > `to` wraps past
 * 0), saturated at least `minSaturation`. Greys and whites belong to no family.
 */
export interface ColorFamily {
  readonly from: number;
  readonly to: number;
  readonly minSaturation: number;
}

/** Width of `family`'s hue range, in degrees. */
function span({ from, to }: ColorFamily): number {
  return (to - from + 360) % 360;
}

/** Whether `color` is in `family` (see {@link ColorFamily}). */
export function inFamily(color: Rgb, family: ColorFamily): boolean {
  const { hue, saturation } = hueSaturation(color);
  return saturation >= family.minSaturation && (hue - family.from + 360) % 360 <= span(family);
}

/** `color` with its hue set to `hue`, keeping its HSV value and saturation. */
function withHue(color: Rgb, hue: number): Rgb {
  const max = Math.max(...color);
  const min = Math.min(...color);
  const f = (n: number) => {
    const k = (n + hue / 60) % 6;
    return max - (max - min) * Math.max(0, Math.min(k, 4 - k, 1));
  };
  return [f(5), f(3), f(1)];
}

/**
 * `color` moved into `family` (phase 14, P14-R02): its hue squeezed from the whole wheel into
 * the family's range, in the same order (so different colours stay different), keeping its
 * brightness and saturation. Greys stay as they are.
 */
export function foldIntoFamily(color: Rgb, family: ColorFamily): Rgb {
  const { hue, saturation } = hueSaturation(color);
  if (saturation === 0) return color;
  return withHue(color, (family.from + (hue / 360) * span(family)) % 360);
}

/** A colour seen through a veil of `color` covering it `opacity` (0..1) of the way. */
export function veiled(seen: Rgb, veil: { color: Rgb; opacity: number }): Rgb {
  const k = veil.opacity;
  const mix = (a: number, b: number) => a * (1 - k) + b * k;
  const [r, g, b] = veil.color;
  return [mix(seen[0], r), mix(seen[1], g), mix(seen[2], b)];
}
