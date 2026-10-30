import type { MenuAction } from './menu-action';

/** Anything that produces menu actions once per frame. */
export interface MenuActionSource {
  update(dtSeconds: number): MenuAction[];
}

/** Merges several devices (keyboard, gamepads...) into one stream of menu actions. */
export class MenuInput implements MenuActionSource {
  constructor(private readonly sources: readonly MenuActionSource[]) {}

  update(dtSeconds: number): MenuAction[] {
    return this.sources.flatMap((source) => source.update(dtSeconds));
  }
}
