import { PlayerFlight, type FlightBounds } from './player-flight';

/**
 * How the ship comes into a level and leaves it (reviewer, 2026-10-28): it rises from below the
 * screen to its start, the player flies it freely for a while once the level is cleared, then
 * it flies off the top of the screen. Logical pixels and seconds.
 */
export interface JourneyRules {
  /** Seconds to rise from below the screen to the start. */
  readonly arriveSeconds: number;
  /** How far below the bottom of the screen the ship starts. */
  readonly below: number;
  /** Seconds the player keeps the ship once the level is cleared. */
  readonly freeSeconds: number;
  /** The fly-off: its starting speed, its acceleration, and how far past the top it goes. */
  readonly leaveSpeed: number;
  readonly leaveAcceleration: number;
  readonly above: number;
}

/** Where the journey stands: the player only flies the ship in `flying`. */
export type JourneyStage = 'arriving' | 'flying' | 'free' | 'leaving' | 'gone';

/** A ship's position and velocity, as the journey moves it. */
interface Moved {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

const easeOut = (t: number): number => 1 - (1 - t) ** 3;

/** The arrival and the departure of the ship (see {@link JourneyRules}). Pure. */
export class ShipJourney {
  #stage: JourneyStage = 'arriving';
  #time = 0;
  #speed = 0;

  constructor(
    private readonly rules: JourneyRules,
    private readonly start: { readonly x: number; readonly y: number },
    /** Height of the top of the screen. */
    private readonly top: number,
  ) {}

  get stage(): JourneyStage {
    return this.#stage;
  }

  /** Whether the journey moves the ship, not the player (it cannot shoot or be hit then). */
  get scripted(): boolean {
    return this.#stage === 'arriving' || this.#stage === 'leaving' || this.#stage === 'gone';
  }

  /** The ship is at its start, as if it had arrived (a seek, a debug start). */
  skipArrival(ship: Moved): void {
    if (this.#stage !== 'arriving') return;
    Object.assign(ship, { x: this.start.x, y: this.start.y, vx: 0, vy: 0 });
    this.#stage = 'flying';
  }

  /** The level is cleared: the player keeps the ship for `freeSeconds`. */
  clear(): void {
    if (this.#stage !== 'flying' && this.#stage !== 'arriving') return;
    this.#stage = 'free';
    this.#time = 0;
  }

  /** Advances by `dt`, moving `ship` while it arrives or leaves. `ready`: it may leave now. */
  step(dt: number, ship: Moved, bounds: FlightBounds, ready: boolean): void {
    this.#time += dt;
    if (this.#stage === 'arriving') this.#arrive(ship, bounds);
    else if (this.#stage === 'free' && ready && this.#time >= this.rules.freeSeconds) {
      this.#stage = 'leaving';
      this.#speed = Math.max(this.rules.leaveSpeed, ship.vy);
    }
    if (this.#stage === 'leaving') this.#leave(dt, ship);
  }

  #arrive(ship: Moved, bounds: FlightBounds): void {
    const from = bounds.minY - this.rules.below;
    const t = Math.min(1, this.#time / Math.max(1e-6, this.rules.arriveSeconds));
    const y = from + (this.start.y - from) * easeOut(t);
    Object.assign(ship, { x: this.start.x, vx: 0, vy: 0, y });
    if (t >= 1) this.#stage = 'flying';
  }

  #leave(dt: number, ship: Moved): void {
    this.#speed += this.rules.leaveAcceleration * dt;
    ship.vx *= Math.max(0, 1 - 4 * dt);
    ship.x += ship.vx * dt;
    ship.vy = this.#speed;
    ship.y += this.#speed * dt;
    if (ship.y >= this.top + this.rules.above) this.#stage = 'gone';
  }
}

/** What {@link flightOf} needs of a run's options. */
interface FlightOptions {
  readonly ship: {
    readonly start: { readonly x: number; readonly y: number };
    readonly maxSpeed: number;
    readonly accelerationSeconds: number;
  };
  readonly bounds: FlightBounds;
  readonly screen: { readonly height: number };
  readonly journey?: JourneyRules;
}

/** The player's ship, and its journey if `journey` is given, the ship then below the screen. */
export function flightOf(options: FlightOptions): { ship: PlayerFlight; journey?: ShipJourney } {
  const { start, maxSpeed, accelerationSeconds } = options.ship;
  const ship = new PlayerFlight(start, maxSpeed, accelerationSeconds);
  if (!options.journey) return { ship };
  const journey = new ShipJourney(options.journey, start, options.screen.height);
  journey.step(0, ship, options.bounds, false);
  return { ship, journey };
}
