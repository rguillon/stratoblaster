import type { MenuCommand } from './menu-action';

/**
 * Tap / click on menu entry `tapped` → command (P01-R11, P01-R12): tapping the selected
 * entry confirms it, tapping another entry selects it.
 */
export function pointerCommand(tapped: number, selected: number): MenuCommand {
  return tapped === selected ? 'confirm' : { select: tapped };
}
