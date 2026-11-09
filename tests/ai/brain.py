# Copyright (c) 2026 Renaud Guillon
"""The brain: a recurrent neural network that plays the game.

Two convolutional encoders read the playfield grid and the fovea around the ship, a small one the
state vector; a GRU keeps a memory of what it has seen (where a shot was going, which enemy was
about to fire, how a boss moves); three heads choose the move, the bomb and the weapon switch, and a
fourth estimates how well things are going (the value, for learning).

Saved under `data/` (`BRAIN_FILE`): the weights and the shape of the network, with how long it has
learned for.
"""

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import Tensor, nn
from torch.distributions import Categorical

from ai import DATA
from ai.game_env import MOVES
from ai.observation import FIELD_COLS, FIELD_ROWS, FOVEA_SIZE, N_CHANNELS, N_STATE, Observation

BRAIN_FILE = DATA / "brain.pt"
# The brain whose games scored best on average while learning (D-295).
BEST_BRAIN_FILE = DATA / "brain-best.pt"
TRAINER_FILE = DATA / "brain.trainer.pt"
FORMAT = 1


@dataclass
class BrainShape:
    """The sizes of the network's layers.

    `convs`: the filters of each convolution of the grid encoders, each of stride 2 (a brain saved
    before had two, of 32 and 64 filters: the default).
    """

    hidden: int = 384
    field_features: int = 256
    fovea_features: int = 256
    state_features: int = 64
    convs: tuple[int, ...] = (32, 64)


# A brain about 36 times smaller (70 thousand weights against 2.5 million, D-302): three
# convolutions of 16 filters bring each grid down to 3 x 3 before its features, and a memory of 64.
SMALL_SHAPE = BrainShape(
    hidden=64, field_features=64, fovea_features=64, state_features=32, convs=(16, 16, 16)
)
SHAPES = {"big": BrainShape(), "small": SMALL_SHAPE}


@dataclass
class LearnStats:
    """How much the brain has learned: updates, decisions played, episodes and hours.

    `best_score`: the best average score of the games of a report while learning (D-295);
    `best_game`: the best game played while learning.
    """

    updates: int = 0
    decisions: int = 0
    episodes: int = 0
    hours: float = 0.0
    best_score: float = 0.0
    # The game that scored the most while learning: score, reached, cleared, decisions, update.
    best_game: dict[str, Any] = field(default_factory=dict)


def _conv_out(size: int, convs: int) -> int:
    """Size after `convs` convolutions of stride 2 (kernel 3, padding 1)."""
    for _ in range(convs):
        size = (size + 1) // 2
    return size


def _encoder(rows: int, cols: int, features: int, convs: tuple[int, ...]) -> nn.Sequential:
    layers: list[nn.Module] = []
    channels = N_CHANNELS
    for filters in convs:
        layers += [nn.Conv2d(channels, filters, 3, stride=2, padding=1), nn.ReLU()]
        channels = filters
    flat = channels * _conv_out(rows, len(convs)) * _conv_out(cols, len(convs))
    layers += [nn.Flatten(), nn.Linear(flat, features), nn.ReLU()]
    return nn.Sequential(*layers)


class Batch:
    """Observations as tensors: `field` and `fovea` (N, C, H, W), `state` (N, S)."""

    def __init__(self, field: Tensor, fovea: Tensor, state: Tensor) -> None:
        self.field = field
        self.fovea = fovea
        self.state = state

    @staticmethod
    def of(observations: list[Observation]) -> "Batch":
        return Batch(
            torch.as_tensor(np.stack([o.field for o in observations])),
            torch.as_tensor(np.stack([o.fovea for o in observations])),
            torch.as_tensor(np.stack([o.state for o in observations])),
        )


class Decision:
    """What the heads give for a batch: their logits, and the value."""

    def __init__(self, move: Tensor, bomb: Tensor, switch: Tensor, value: Tensor) -> None:
        self.move = move
        self.bomb = bomb
        self.switch = switch
        self.value = value

    def row(self, index: int) -> "Decision":
        """Return the decision of one player of the batch (a batch of one)."""
        part = slice(index, index + 1)
        return Decision(self.move[part], self.bomb[part], self.switch[part], self.value[part])

    def distributions(self) -> tuple[Categorical, Categorical, Categorical]:
        return (
            Categorical(logits=self.move),
            Categorical(logits=self.bomb),
            Categorical(logits=self.switch),
        )

    def log_prob(self, actions: Tensor) -> Tensor:
        """Log-probability of `actions` (N, 3: move, bomb, switch)."""
        move, bomb, switch = self.distributions()
        return (
            move.log_prob(actions[:, 0])
            + bomb.log_prob(actions[:, 1])
            + switch.log_prob(actions[:, 2])
        )

    def entropy(self) -> Tensor:
        move, bomb, switch = self.distributions()
        return move.entropy() + 0.5 * (bomb.entropy() + switch.entropy())

    def sample_with_log_prob(
        self, generator: torch.Generator | None = None
    ) -> tuple[Tensor, Tensor]:
        """Draw actions (N, 3) and return them with their log-probability (N).

        As `sample` then `log_prob`, without building the distributions: the inference server
        does it for every batch (D-298).
        """
        picks, total = [], None
        for logits in (self.move, self.bomb, self.switch):
            log_p = torch.log_softmax(logits, -1)
            pick = torch.multinomial(log_p.exp(), 1, generator=generator)
            chosen = log_p.gather(-1, pick).squeeze(-1)
            picks.append(pick.squeeze(-1))
            total = chosen if total is None else total + chosen
        assert total is not None
        return torch.stack(picks, dim=-1), total

    def sample(self, greedy: bool, generator: torch.Generator | None = None) -> Tensor:
        """Actions (N, 3), the likeliest ones when `greedy`."""
        if greedy:
            return torch.stack(
                [self.move.argmax(-1), self.bomb.argmax(-1), self.switch.argmax(-1)], dim=-1
            )
        picks = [
            torch.multinomial(torch.softmax(logits, -1), 1, generator=generator).squeeze(-1)
            for logits in (self.move, self.bomb, self.switch)
        ]
        return torch.stack(picks, dim=-1)


class Brain(nn.Module):
    """The network: see the module's docstring."""

    def __init__(self, shape: BrainShape | None = None) -> None:
        super().__init__()
        self.shape = shape if shape is not None else BrainShape()
        s = self.shape
        self.field_net = _encoder(FIELD_ROWS, FIELD_COLS, s.field_features, s.convs)
        self.fovea_net = _encoder(FOVEA_SIZE, FOVEA_SIZE, s.fovea_features, s.convs)
        self.state_net = nn.Sequential(nn.Linear(N_STATE, s.state_features), nn.ReLU())
        joined = s.field_features + s.fovea_features + s.state_features
        self.trunk = nn.Sequential(nn.Linear(joined, s.hidden), nn.ReLU())
        # A GRU (cuDNN's on a GPU): the learner replays whole sequences through it at once (D-299).
        self.memory = nn.GRU(s.hidden, s.hidden)
        self.move_head = nn.Linear(s.hidden, len(MOVES))
        self.bomb_head = nn.Linear(s.hidden, 2)
        self.switch_head = nn.Linear(s.hidden, 2)
        self.value_head = nn.Linear(s.hidden, 1)
        self._init_heads()

    def _init_heads(self) -> None:
        for head, gain in (
            (self.move_head, 0.01),
            (self.bomb_head, 0.01),
            (self.switch_head, 0.01),
            (self.value_head, 1.0),
        ):
            nn.init.orthogonal_(head.weight, gain)
            nn.init.zeros_(head.bias)
        # Bombs and switches are rare: start out rarely using them.
        with torch.no_grad():
            self.bomb_head.bias.copy_(torch.tensor([3.0, -3.0]))
            self.switch_head.bias.copy_(torch.tensor([4.0, -4.0]))

    def initial_memory(self, count: int) -> Tensor:
        return torch.zeros(count, self.shape.hidden)

    def encode(self, batch: Batch) -> Tensor:
        """Return the features of each observation, before the memory (N, hidden)."""
        joined = torch.cat(
            [
                self.field_net(batch.field.float()),
                self.fovea_net(batch.fovea.float()),
                self.state_net(batch.state.float()),
            ],
            dim=-1,
        )
        return self.trunk(joined)

    def heads(self, memory: Tensor) -> Decision:
        return Decision(
            self.move_head(memory),
            self.bomb_head(memory),
            self.switch_head(memory),
            self.value_head(memory).squeeze(-1),
        )

    def forward(self, batch: Batch, memory: Tensor) -> tuple[Decision, Tensor]:
        """One step for N players: their decision and their new memory."""
        _, memory = self.memory(self.encode(batch).unsqueeze(0), memory.unsqueeze(0))
        memory = memory.squeeze(0)
        return self.heads(memory), memory

    def unroll(self, batch: Batch, memory: Tensor, starts: Tensor, steps: int) -> Decision:
        """Replay sequences of `steps` steps for N players (inputs flattened time-major, T*N).

        `memory` is each player's memory before the first step; `starts` (T*N) marks the steps that
        begin an episode, where the memory starts over.
        """
        features = self.encode(batch)
        count = memory.shape[0]
        features = features.view(steps, count, -1)
        starts = starts.view(steps, count)
        keep = (1.0 - starts.float()).unsqueeze(-1)
        outputs = features.new_empty(steps, count, memory.shape[-1])
        # The sequences no episode starts in after their first step: all at once.
        whole = ~starts[1:].any(dim=0)
        if whole.any():
            first = (memory * keep[0])[whole]
            replayed, _ = self.memory(features[:, whole], first.unsqueeze(0).contiguous())
            outputs[:, whole] = replayed.to(outputs.dtype)
        # The others step by step, the memory starting over where an episode starts.
        broken = ~whole
        if broken.any():
            state = memory[broken].unsqueeze(0)
            for t in range(steps):
                state = state * keep[t, broken].unsqueeze(0)
                _, state = self.memory(features[t : t + 1, broken], state.contiguous())
                outputs[t, broken] = state[0].to(outputs.dtype)
        return self.heads(outputs.view(steps * count, -1))


def save_brain(brain: Brain, stats: LearnStats, path: Path = BRAIN_FILE) -> None:
    """Save the weights (in float16, D-306), the network's shape and the learning stats.

    Atomically. Half the size of float32, and it decides the same; `make learn` resumes from the
    exact float32 weights of its trainer file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    weights = {
        k: v.detach().cpu().half() if v.is_floating_point() else v.detach().cpu()
        for k, v in brain.state_dict().items()
    }
    saved = {
        "format": FORMAT,
        "shape": asdict(brain.shape),
        "weights": weights,
        "stats": asdict(stats),
    }
    torch.save(saved, tmp)
    tmp.replace(path)


# The first layer of each grid encoder: its weights are (out, channels, 3, 3).
_GRID_INPUTS = ("field_net.0.weight", "fovea_net.0.weight")


def widen_inputs(weights: dict[str, Tensor]) -> None:
    """Give a brain saved with fewer channels the channels added since, unseen (zero weights).

    Channels are only ever added last (`CHANNELS`), so what it learned still reads the same:
    it plays as before and learns what the new ones show.
    """
    for name in _GRID_INPUTS:
        old = weights[name]
        missing = N_CHANNELS - old.shape[1]
        if missing > 0:
            zeros = old.new_zeros(old.shape[0], missing, *old.shape[2:])
            weights[name] = torch.cat([old, zeros], dim=1)


def _cell_to_gru(weights: dict[str, Tensor]) -> None:
    """Rename the memory's weights of a brain saved with a `GRUCell` to a `GRU`'s (D-299).

    The same weights in the same order: what it learned is kept, and its optimiser's state fits.
    """
    for name in ("weight_ih", "weight_hh", "bias_ih", "bias_hh"):
        old = f"memory.{name}"
        if old in weights:
            weights[f"memory.{name}_l0"] = weights.pop(old)


class IncompatibleBrainError(ValueError):
    """A saved brain whose layers do not fit the brain of today (what it sees has changed)."""


def load_brain(path: Path = BRAIN_FILE) -> tuple[Brain, LearnStats]:
    """Load a saved brain and its learning stats (widened to the channels added since)."""
    saved = torch.load(path, map_location="cpu", weights_only=True)
    if saved.get("format") != FORMAT:
        msg = f"{path}: unknown brain format {saved.get('format')}"
        raise ValueError(msg)
    shape = dict(saved["shape"])
    if "convs" in shape:
        shape["convs"] = tuple(shape["convs"])
    brain = Brain(BrainShape(**shape))
    weights = {k: v.float() if v.is_floating_point() else v for k, v in saved["weights"].items()}
    widen_inputs(weights)
    _cell_to_gru(weights)
    try:
        brain.load_state_dict(weights)
    except RuntimeError as error:  # its layers are of other sizes
        msg = (
            f"{path} was learned on another view of the game (the playfield's grid changed, D-301)"
            " and cannot be used: learn a new brain (`make learn LEARN_ARGS=--fresh`)."
        )
        raise IncompatibleBrainError(msg) from error
    # A brain saved before D-306 also kept its learning history (the learning log has it).
    known = {f.name for f in fields(LearnStats)}
    stats = LearnStats(**{k: v for k, v in saved["stats"].items() if k in known})
    return brain, stats
