"""Fakes of the Web Audio context for the audio tests: nodes that record their connections, their
scheduled parameter changes and their stops, so a test can read what the engine did. Parameters
(`gain`, `frequency`, `threshold`...) are created on first use and hold a real `value`."""

from typing import Any


class FakeParam:
    """An `AudioParam`: a `value` plus the scheduling calls, which are recorded."""

    def __init__(self, value: float = 1.0) -> None:
        self.value = value
        self.events: list[tuple[str, tuple[Any, ...]]] = []

    def setValueAtTime(self, value: float, when: float) -> None:  # noqa: N802
        self.events.append(("setValueAtTime", (value, when)))
        self.value = value

    def setTargetAtTime(self, target: float, when: float, time_constant: float) -> None:  # noqa: N802
        self.events.append(("setTargetAtTime", (target, when, time_constant)))

    def cancelScheduledValues(self, when: float) -> None:  # noqa: N802
        self.events.append(("cancelScheduledValues", (when,)))

    def exponentialRampToValueAtTime(self, value: float, when: float) -> None:  # noqa: N802
        self.events.append(("exponentialRampToValueAtTime", (value, when)))

    def linearRampToValueAtTime(self, value: float, when: float) -> None:  # noqa: N802
        self.events.append(("linearRampToValueAtTime", (value, when)))

    def names(self) -> list[str]:
        return [name for name, _ in self.events]


class FakePromise:
    """A promise that ignores its handlers: `catch` returns the promise, as the DOM's does."""

    def __init__(self) -> None:
        self.caught: list[Any] = []

    def catch(self, handler: Any) -> "FakePromise":
        self.caught.append(handler)
        return self


class FakeNode:
    """An audio node: its parameters (created on use) and where it connects."""

    def __init__(self, kind: str) -> None:
        self.kind = kind
        self.connections: list[Any] = []
        self.disconnected = False
        self.stops: list[float] = []
        self.started: list[float] = []
        self._params: dict[str, FakeParam] = {}

    def __getattr__(self, name: str) -> Any:
        # Only called for names not set on the node: an audio parameter, created on first use.
        if name.startswith("_"):
            raise AttributeError(name)
        params = self.__dict__.setdefault("_params", {})
        if name not in params:
            params[name] = FakeParam(1.0)
        return params[name]

    def __setitem__(self, name: str, value: Any) -> None:
        setattr(self, name, value)

    def connect(self, target: Any) -> Any:
        self.connections.append(target)
        return target

    def disconnect(self) -> None:
        self.disconnected = True
        self.connections = []

    def start(self, when: float = 0) -> None:
        self.started.append(when)

    def stop(self, when: float = 0) -> None:
        self.stops.append(when)


class FakeBuffer:
    """An `AudioBuffer` holding its channels as plain lists."""

    def __init__(self, channels: int, length: int) -> None:
        self.channels = [[0.0] * length for _ in range(channels)]

    def getChannelData(self, channel: int) -> list[float]:  # noqa: N802
        return self.channels[channel]


class FakeContext:
    """An `AudioContext` with a clock and a sample rate the test sets."""

    def __init__(self, sample_rate: int = 1000) -> None:
        self.currentTime = 0.0  # noqa: N815 (Web Audio name)
        self.sampleRate = sample_rate  # noqa: N815
        self.state = "running"
        self.destination = FakeNode("destination")
        self.nodes: list[FakeNode] = []
        self.buffers: list[FakeBuffer] = []
        self.resumed = 0
        self.suspended = 0
        self.promises: list[FakePromise] = []

    def _make(self, kind: str) -> FakeNode:
        node = FakeNode(kind)
        self.nodes.append(node)
        return node

    def createGain(self) -> FakeNode:  # noqa: N802
        return self._make("gain")

    def createStereoPanner(self) -> FakeNode:  # noqa: N802
        return self._make("panner")

    def createDelay(self, max_seconds: float = 1) -> FakeNode:  # noqa: N802
        return self._make("delay")

    def createOscillator(self) -> FakeNode:  # noqa: N802
        return self._make("oscillator")

    def createBiquadFilter(self) -> FakeNode:  # noqa: N802
        return self._make("filter")

    def createBufferSource(self) -> FakeNode:  # noqa: N802
        return self._make("source")

    def createDynamicsCompressor(self) -> FakeNode:  # noqa: N802
        return self._make("compressor")

    def createConvolver(self) -> FakeNode:  # noqa: N802
        return self._make("convolver")

    def createBuffer(self, channels: int, length: int, rate: float) -> FakeBuffer:  # noqa: N802
        buffer = FakeBuffer(channels, length)
        self.buffers.append(buffer)
        return buffer

    def resume(self) -> FakePromise:
        self.resumed += 1
        self.promises.append(FakePromise())
        return self.promises[-1]

    def suspend(self) -> FakePromise:
        self.suspended += 1
        self.promises.append(FakePromise())
        return self.promises[-1]

    def of_kind(self, kind: str) -> list[FakeNode]:
        return [node for node in self.nodes if node.kind == kind]


class FakeVoice:
    """A `Voice` stand-in: an end time and a record of the stops asked for."""

    def __init__(self, end: float, name: str = "") -> None:
        self.end = end
        self.name = name
        self.stops: list[tuple[float, float]] = []

    def stop(self, at: float, fade: float) -> None:
        self.stops.append((at, fade))
