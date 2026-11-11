# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/brain.py`: the network, its memory, saving and loading it."""

from dataclasses import asdict
from pathlib import Path

import torch
from ai.brain import (
    FORMAT,
    SHAPES,
    SMALL_SHAPE,
    Batch,
    Brain,
    BrainShape,
    Decision,
    LearnStats,
    load_brain,
    mask_bomb,
    save_brain,
)
from ai.game_env import MOVES, Action, EpisodeSetup, GameEnv
from ai.observation import CH, N_CHANNELS, N_STATE, STATE_BOMB_ACTIVE, STATE_BOMBS, observe

SMALL = BrainShape(hidden=32, field_features=16, fovea_features=16, state_features=8)


def _batch(count: int) -> Batch:
    env = GameEnv(EpisodeSetup("1-1"))
    observations = []
    for i in range(count):
        env.step(Action(i % len(MOVES)))
        observations.append(observe(env))
    return Batch.of(observations)


def test_a_decision_has_a_move_a_bomb_a_switch_and_a_value() -> None:
    brain = Brain(SMALL)
    decision, memory = brain(_batch(3), brain.initial_memory(3))
    assert decision.move.shape == (3, len(MOVES))
    assert decision.bomb.shape == (3, 2)
    assert decision.switch.shape == (3, 2)
    assert decision.value.shape == (3,)
    assert memory.shape == (3, SMALL.hidden)
    actions = decision.sample(greedy=False)
    assert actions.shape == (3, 3)
    assert decision.log_prob(actions).shape == (3,)
    assert decision.entropy().shape == (3,)


def test_a_new_brain_rarely_bombs_or_switches() -> None:
    brain = Brain(SMALL)
    decision, _ = brain(_batch(2), brain.initial_memory(2))
    greedy = decision.sample(greedy=True)
    assert greedy[:, 1].tolist() == [0, 0]
    assert greedy[:, 2].tolist() == [0, 0]


def test_the_memory_carries_what_was_seen_to_the_next_step() -> None:
    brain = Brain(SMALL)
    batch = _batch(1)
    first, memory = brain(batch, brain.initial_memory(1))
    second, _ = brain(batch, memory)
    assert not torch.allclose(first.value, second.value)


def test_unroll_replays_the_steps_one_by_one_and_starts_over_at_an_episode_start() -> None:
    torch.manual_seed(0)
    brain = Brain(SMALL)
    steps, count = 4, 3
    batch = _batch(steps * count)  # time first: step t of player n is t * count + n
    # Player 0 starts over at step 3, player 1 at step 1 (both step by step); player 2 starts at
    # step 0 only (its sequence replayed whole, D-299).
    starts = torch.tensor([
        False,
        False,
        True,
        False,
        True,
        False,
        False,
        False,
        False,
        True,
        False,
        False,
    ])
    memory0 = torch.randn(count, SMALL.hidden)
    replay = brain.unroll(batch, memory0, starts, steps)
    memory = memory0
    values = []
    for t in range(steps):
        rows = slice(t * count, (t + 1) * count)
        keep = (~starts[rows]).float().unsqueeze(-1)
        one = Batch(batch.field[rows], batch.fovea[rows], batch.state[rows])
        decision, memory = brain(one, memory * keep)
        values.append(decision.value)
    assert torch.allclose(replay.value, torch.cat(values), atol=1e-5)


def test_a_saved_brain_loads_with_its_weights_and_stats(tmp_path: Path) -> None:
    brain = Brain(SMALL)
    stats = LearnStats(updates=3, decisions=100, episodes=2, hours=0.5)
    path = tmp_path / "brain.pt"
    save_brain(brain, stats, path)
    loaded, loaded_stats = load_brain(path)
    assert loaded.shape == SMALL
    assert loaded_stats == stats
    for name, value in brain.state_dict().items():
        # Saved in float16 (D-306), loaded back in float32.
        assert loaded.state_dict()[name].dtype == torch.float32
        assert torch.equal(value.half().float(), loaded.state_dict()[name])


def test_d_306_the_brain_file_keeps_float16_weights(tmp_path: Path) -> None:
    path = tmp_path / "brain.pt"
    save_brain(Brain(SMALL_SHAPE), LearnStats(), path)
    saved = torch.load(path, weights_only=True)
    assert all(v.dtype == torch.float16 for v in saved["weights"].values())
    weights = sum(v.numel() for v in saved["weights"].values())
    assert path.stat().st_size < 2 * weights + 20_000


def test_d_306_a_brain_saved_with_its_learning_history_still_loads(tmp_path: Path) -> None:
    brain = Brain(SMALL)
    path = tmp_path / "old.pt"
    stats = {"updates": 4, "decisions": 0, "episodes": 0, "hours": 0.0, "history": [{"a": 1.0}]}
    torch.save(
        {"format": FORMAT, "shape": asdict(SMALL), "weights": brain.state_dict(), "stats": stats},
        path,
    )
    loaded, loaded_stats = load_brain(path)
    assert loaded_stats == LearnStats(updates=4)
    for name, value in brain.state_dict().items():
        assert torch.equal(value, loaded.state_dict()[name])


def test_a_brain_saved_before_the_last_channels_loads_blind_to_them(tmp_path: Path) -> None:
    """D-282: the healing bonuses' channel, added last, starts unseen (zero weights)."""
    brain = Brain(SMALL)
    weights = {k: v.clone() for k, v in brain.state_dict().items()}
    for name in ("field_net.0.weight", "fovea_net.0.weight"):
        weights[name] = weights[name][:, : CH["bonus_heal"]]
    path = tmp_path / "old.pt"
    stats = {"updates": 1, "decisions": 0, "episodes": 0, "hours": 0.0, "history": []}
    shape = {"hidden": 32, "field_features": 16, "fovea_features": 16, "state_features": 8}
    torch.save({"format": FORMAT, "shape": shape, "weights": weights, "stats": stats}, path)
    loaded, _ = load_brain(path)
    for name in ("field_net.0.weight", "fovea_net.0.weight"):
        widened = loaded.state_dict()[name]
        assert widened.shape[1] == N_CHANNELS
        assert torch.equal(widened[:, : CH["bonus_heal"]], weights[name])
        assert not widened[:, CH["bonus_heal"] :].any()


def test_d_275_a_brain_saved_with_a_gru_cell_loads_into_the_gru(tmp_path: Path) -> None:
    brain = Brain(SMALL)
    weights = {k: v.clone() for k, v in brain.state_dict().items()}
    for name in ("weight_ih", "weight_hh", "bias_ih", "bias_hh"):
        weights[f"memory.{name}"] = weights.pop(f"memory.{name}_l0")
    path = tmp_path / "cell.pt"
    stats = {"updates": 1, "decisions": 0, "episodes": 0, "hours": 0.0, "history": []}
    shape = {"hidden": 32, "field_features": 16, "fovea_features": 16, "state_features": 8}
    torch.save({"format": FORMAT, "shape": shape, "weights": weights, "stats": stats}, path)
    loaded, _ = load_brain(path)
    for name, value in brain.state_dict().items():
        assert torch.equal(value, loaded.state_dict()[name])


def test_d_302_the_small_brain_has_under_a_hundred_thousand_weights() -> None:
    big = sum(p.numel() for p in Brain(SHAPES["big"]).parameters())
    small = sum(p.numel() for p in Brain(SMALL_SHAPE).parameters())
    assert small < 100_000
    assert big > 30 * small


def test_d_302_the_small_brain_decides_for_a_batch() -> None:
    brain = Brain(SMALL_SHAPE)
    decision, memory = brain(_batch(3), brain.initial_memory(3))
    assert decision.move.shape == (3, len(MOVES))
    assert memory.shape == (3, SMALL_SHAPE.hidden)


def test_d_302_a_small_brain_loads_with_its_shape(tmp_path: Path) -> None:
    path = tmp_path / "small.pt"
    save_brain(Brain(SMALL_SHAPE), LearnStats(), path)
    loaded, _ = load_brain(path)
    assert loaded.shape == SMALL_SHAPE


def test_d_302_a_brain_saved_before_its_convolutions_were_given_has_the_old_two(
    tmp_path: Path,
) -> None:
    brain = Brain(SMALL)
    path = tmp_path / "old.pt"
    shape = {"hidden": 32, "field_features": 16, "fovea_features": 16, "state_features": 8}
    stats = {"updates": 1, "decisions": 0, "episodes": 0, "hours": 0.0, "history": []}
    torch.save(
        {"format": FORMAT, "shape": shape, "weights": brain.state_dict(), "stats": stats}, path
    )
    loaded, _ = load_brain(path)
    assert loaded.shape.convs == (32, 64)


def _state(bombs: float, active: float) -> torch.Tensor:
    state = torch.zeros(1, N_STATE)
    state[0, STATE_BOMBS] = bombs
    state[0, STATE_BOMB_ACTIVE] = active
    return state


def test_d_315_a_bomb_that_cannot_go_off_is_never_chosen() -> None:
    logits = torch.tensor([[-5.0, 5.0]])
    for bombs, active in ((0.0, 0.0), (0.4, 1.0)):
        masked = mask_bomb(logits, _state(bombs, active))
        bomb = torch.distributions.Categorical(logits=masked)
        assert bomb.probs[0, 1].item() == 0
        assert bomb.entropy().item() < 1e-6
    assert torch.equal(mask_bomb(logits, _state(0.4, 0.0)), logits)


def test_d_315_the_brain_masks_the_bomb_from_what_it_sees() -> None:
    brain = Brain(SMALL)
    batch = _batch(1)
    batch.state[:, STATE_BOMBS] = 0
    decision, _ = brain(batch, brain.initial_memory(1))
    assert torch.softmax(decision.bomb, -1)[0, 1].item() == 0


def test_d_315_playing_draws_the_move_but_takes_the_likeliest_bomb_and_switch() -> None:
    count = 200
    move = torch.zeros(count, len(MOVES))
    bomb = torch.tensor([[0.0, -0.5]]).repeat(count, 1)  # 38 % of a bomb
    switch = torch.tensor([[-0.5, 0.0]]).repeat(count, 1)  # 62 % of a switch
    decision = Decision(move, bomb, switch, torch.zeros(count))
    actions = decision.sample(greedy=False, generator=torch.Generator().manual_seed(1))
    assert len(set(actions[:, 0].tolist())) > 1
    assert set(actions[:, 1].tolist()) == {0}
    assert set(actions[:, 2].tolist()) == {1}
