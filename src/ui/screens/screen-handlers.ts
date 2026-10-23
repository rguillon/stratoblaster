/** Callbacks of the tappable parts of a menu screen. */
export interface ScreenHandlers {
  /** An entry of the screen was tapped or clicked. */
  readonly onTap: (index: number) => void;
  /** The on-screen Back button was tapped or clicked. */
  readonly onBack: () => void;
}
