/** Tunables of the engine's menu screens (phase 01). Game-specific values are in `src/game/config/`. */
export const MENU_CONFIG = {
  /** `menu_transition_duration`: screen fade, input ignored meanwhile (P01-R15). */
  transitionSeconds: 0.25,
  /** `cookie_max_age`: lifetime of the high score and last ship cookies. */
  cookieMaxAgeDays: 365,
  /** Longest frame time fed to animations, so a stall does not make things jump. */
  maxFrameSeconds: 0.1,
  shipSelect: {
    /** Distance between two ship centres, in world units. */
    spacing: 7,
    /** `ship_select_rotation_speed`. */
    rotationSpeedRadPerSec: 0.5,
    /** Scale of the highlighted ship and of the others (P01-R06). */
    highlightScale: 1.2,
    dimScale: 0.7,
    /** How fast the scales ease towards their target (1/s). */
    scaleEasePerSec: 10,
    camera: {
      alpha: -Math.PI / 2,
      beta: 1.2,
      horizontalFov: 1.0,
      /** Extra room around the row of ships (1 = ships touch the screen edges). */
      framingMargin: 1.05,
      /** Camera target height: positive values move the ships down the screen. */
      targetY: -1.2,
    },
    lights: {
      ambientIntensity: 0.25,
      /** Key light on the highlighted ship only, so the others look dimmed. */
      spotIntensity: 2.6,
      spotDirection: [-0.4, -1, 0.6],
      rimIntensity: 0.8,
      rimDirection: [0.6, -0.3, -1],
    },
    /** Neon ring under the highlighted ship. */
    ring: { diameter: 6.4, thickness: 0.12, y: -1.3, color: [1, 0.92, 0.05] },
  },
  /** Image-based lighting of the menu scenes (procedural, no download). */
  environment: {
    cubeSize: 64,
    intensity: 1.0,
    stops: [
      { at: -1, color: [0.1, 0.06, 0.2] },
      { at: -0.1, color: [0.3, 0.2, 0.45] },
      { at: 0, color: [1, 0.65, 0.85] },
      { at: 0.15, color: [0.6, 0.65, 1] },
      { at: 1, color: [0.9, 0.9, 1] },
    ],
  },
  glow: { intensity: 0.8, blurKernelSize: 48 },
} as const;
