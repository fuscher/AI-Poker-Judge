import pytest

from aipokerjudge.game.engine import DouDiZhuEngine
from aipokerjudge.game.models import GameState, GameStatus


def test_engine_creation():
    engine = DouDiZhuEngine(seed=42)
    state = engine.create_state()
    assert isinstance(state, GameState)
    assert state.current_player == "A"


def test_initial_hand_sizes():
    engine = DouDiZhuEngine(seed=42)
    state = engine.create_state()
    total = len(state.player_a_hand) + len(state.player_b_hand)
    assert total == 34  # 17 + 17


def test_get_legal_actions_initial():
    engine = DouDiZhuEngine(seed=42)
    state = engine.create_state()
    legal = engine.get_legal_actions(state)
    assert len(legal) > 0
    # all possible plays should be legal when no last play
    assert all(isinstance(a, list) for a in legal)


def test_apply_action_play_card():
    engine = DouDiZhuEngine(seed=42)
    state = engine.create_state()
    hand_before = state.player_a_hand.copy()
    card = [hand_before[0]]
    state = engine.apply_action(state, card)
    assert len(state.player_a_hand) == 16
    assert state.current_player == "B"
    assert state.last_play is not None


def test_apply_action_pass():
    engine = DouDiZhuEngine(seed=42)
    state = engine.create_state()
    # A plays a card first
    card = [state.player_a_hand[0]]
    state = engine.apply_action(state, card)
    # B passes
    state = engine.apply_action(state, [])
    assert state.last_play is None
    assert state.current_player == "A"


def test_pass_resets_last_play():
    engine = DouDiZhuEngine(seed=42)
    state = engine.create_state()
    card = [state.player_a_hand[0]]
    state = engine.apply_action(state, card)
    assert state.last_play is not None
    state = engine.apply_action(state, [])  # B passes
    assert state.last_play is None


def test_game_over_status():
    engine = DouDiZhuEngine(seed=42)
    state = engine.create_state()
    assert not engine.is_game_over(state)
    assert engine.get_winner(state) is None


def test_get_current_player_hand():
    engine = DouDiZhuEngine(seed=42)
    state = engine.create_state()
    hand_a = engine.get_current_player_hand(state)
    assert hand_a == state.player_a_hand


def test_format_hand():
    hand = ["♥3", "♠5", "♦J"]
    result = DouDiZhuEngine.format_hand(hand)
    assert "♥3" in result
    assert "♠5" in result
