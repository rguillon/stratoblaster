/** Callbacks of the tappable parts of a menu screen. */
export interface ScreenHandlers {
  /** An entry of the screen was tapped or clicked. */
  readonly onTap: (index: number) => void;
  /** The on-screen Back button was tapped or clicked. */
  readonly onBack: () => void;
  /** Game screen: the touch fire button was pressed (`true`) or let go (P06-R02). */
  readonly onFire?: (held: boolean) => void;
  /** Game screen: a finger dragged over the playfield, by screen pixels (Y down). */
  readonly onDrag?: (dx: number, dy: number) => void;
}
