import type { LogicalScreen } from '../core/content/game-definition';

/** Where the game stage goes in the window, in CSS pixels. */
export interface StageFit {
  readonly left: number;
  readonly top: number;
  readonly width: number;
  readonly height: number;
  /** CSS pixels per logical pixel. */
  readonly scale: number;
}

/**
 * Largest stage with the logical aspect ratio that fits a `viewWidth × viewHeight` window,
 * centred (GD-02, GD-03): never cropped, never stretched.
 */
export function fitStage(viewWidth: number, viewHeight: number, logical: LogicalScreen): StageFit {
  const scale = Math.max(0, Math.min(viewWidth / logical.width, viewHeight / logical.height));
  const width = Math.floor(logical.width * scale);
  const height = Math.floor(logical.height * scale);
  return {
    left: Math.floor((viewWidth - width) / 2),
    top: Math.floor((viewHeight - height) / 2),
    width,
    height,
    scale,
  };
}

type Styled = Pick<HTMLElement, 'style'>;

/**
 * Places the stage (canvas container) in the window and scales the menu overlay, which is
 * laid out at the logical resolution, to the stage size.
 */
export function applyStageFit(
  stage: Styled,
  overlay: Styled,
  fit: StageFit,
  logical: LogicalScreen,
): void {
  const px = (n: number): string => `${String(n)}px`;
  stage.style.left = px(fit.left);
  stage.style.top = px(fit.top);
  stage.style.width = px(fit.width);
  stage.style.height = px(fit.height);
  overlay.style.width = px(logical.width);
  overlay.style.height = px(logical.height);
  overlay.style.transform = `scale(${String(fit.scale)})`;
}
