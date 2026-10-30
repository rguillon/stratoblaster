/** Minimal canvas shape needed to probe WebGL2, so the check is testable without a DOM. */
export interface CanvasLike {
  getContext(contextId: 'webgl2'): unknown;
}

/** Returns true when the browser can create a WebGL2 context (ENG-06). */
export function hasWebGL2(createCanvas: () => CanvasLike): boolean {
  try {
    return createCanvas().getContext('webgl2') != null;
  } catch {
    return false;
  }
}
