/**
 * A fake Web Audio context for unit tests (no real audio in Node): nodes record their
 * connections, parameters record their scheduled values, and the clock is set by the test.
 */

/** One scheduled change of a fake parameter. */
export interface ParamEvent {
  readonly kind: 'set' | 'linear' | 'exponential' | 'target' | 'cancel';
  readonly value: number;
  readonly time: number;
}

export class FakeParam {
  value: number;
  readonly events: ParamEvent[] = [];

  constructor(value: number) {
    this.value = value;
  }

  setValueAtTime(value: number, time: number): this {
    this.events.push({ kind: 'set', value, time });
    this.value = value;
    return this;
  }

  linearRampToValueAtTime(value: number, time: number): this {
    this.events.push({ kind: 'linear', value, time });
    this.value = value;
    return this;
  }

  exponentialRampToValueAtTime(value: number, time: number): this {
    this.events.push({ kind: 'exponential', value, time });
    this.value = value;
    return this;
  }

  setTargetAtTime(value: number, time: number): this {
    this.events.push({ kind: 'target', value, time });
    this.value = value;
    return this;
  }

  cancelScheduledValues(time: number): this {
    this.events.push({ kind: 'cancel', value: this.value, time });
    return this;
  }
}

export class FakeNode {
  readonly outputs: FakeNode[] = [];
  disconnected = false;

  constructor(
    readonly context: FakeAudioContext,
    readonly kind: string,
  ) {
    context.nodes.push(this);
  }

  connect<T extends FakeNode>(node: T): T {
    this.outputs.push(node);
    return node;
  }

  disconnect(): void {
    this.disconnected = true;
    this.outputs.length = 0;
  }
}

export class FakeGain extends FakeNode {
  readonly gain = new FakeParam(1);
}

export class FakeFilter extends FakeNode {
  type = 'lowpass';
  readonly frequency = new FakeParam(350);
  readonly Q = new FakeParam(1);
}

export class FakePanner extends FakeNode {
  readonly pan = new FakeParam(0);
}

export class FakeCompressor extends FakeNode {
  readonly threshold = new FakeParam(-24);
  readonly knee = new FakeParam(30);
  readonly ratio = new FakeParam(12);
  readonly attack = new FakeParam(0.003);
  readonly release = new FakeParam(0.25);
}

class FakeSource extends FakeNode {
  started: number | undefined;
  stopped: number | undefined;

  start(time = 0): void {
    this.started = time;
  }

  stop(time = 0): void {
    this.stopped = time;
  }
}

export class FakeOscillator extends FakeSource {
  type = 'sine';
  readonly frequency = new FakeParam(440);
  readonly detune = new FakeParam(0);
}

export class FakeBufferSource extends FakeSource {
  buffer: unknown = null;
  loop = false;
  readonly playbackRate = new FakeParam(1);
}

/** A fake `AudioContext`: set `currentTime` to move its clock. */
export class FakeAudioContext {
  currentTime = 0;
  readonly sampleRate = 8000;
  state: 'suspended' | 'running' | 'closed' = 'running';
  readonly nodes: FakeNode[] = [];
  readonly destination = new FakeNode(this, 'destination');
  buffers = 0;

  createGain(): FakeGain {
    return new FakeGain(this, 'gain');
  }

  createBiquadFilter(): FakeFilter {
    return new FakeFilter(this, 'filter');
  }

  createStereoPanner(): FakePanner {
    return new FakePanner(this, 'panner');
  }

  createDynamicsCompressor(): FakeCompressor {
    return new FakeCompressor(this, 'compressor');
  }

  createOscillator(): FakeOscillator {
    return new FakeOscillator(this, 'oscillator');
  }

  createBufferSource(): FakeBufferSource {
    return new FakeBufferSource(this, 'buffer-source');
  }

  createBuffer(_channels: number, length: number): { getChannelData: () => Float32Array } {
    this.buffers++;
    const data = new Float32Array(length);
    return { getChannelData: () => data };
  }

  resume(): Promise<void> {
    this.state = 'running';
    return Promise.resolve();
  }

  suspend(): Promise<void> {
    this.state = 'suspended';
    return Promise.resolve();
  }

  /** The sources (oscillators and noise) created so far. */
  sources(): (FakeOscillator | FakeBufferSource)[] {
    return this.nodes.filter(
      (n): n is FakeOscillator | FakeBufferSource =>
        n instanceof FakeOscillator || n instanceof FakeBufferSource,
    );
  }

  /** This context as the real type the engine expects. */
  asContext(): AudioContext {
    return this as unknown as AudioContext;
  }
}
