"""Dou Di Zhu game engine - core state machine and turn control
斗地主游戏引擎 - 核心状态机和回合控制"""

from typing import List, Optional, Tuple

from .models import GameState, GameStatus
from .rules import (
    identify_play_type, get_play_value, can_beat, 
    generate_all_possible_plays, group_by_rank
)
from .deck import create_initial_state


class DouDiZhuEngine:
    """Dou Di Zhu game engine (simplified 1v1)
    斗地主游戏引擎（简化版1v1）"""
    
    def __init__(self, seed: int = None):
        self.seed = seed
    
    def create_state(self) -> GameState:
        """Create a new game state
        创建新游戏状态"""
        return create_initial_state(self.seed)
    
    def get_legal_actions(self, state: GameState) -> List[List[str]]:
        """
        Get all legal actions for the current player
        获取当前玩家的所有合法动作
        Returns: list of plays, empty list means can only pass
        返回: 出牌列表，空列表代表只能过牌
        """
        hand = state.player_a_hand if state.current_player == "A" else state.player_b_hand
        
        if not hand:
            return []
        
        # Generate all possible plays
        # 生成所有可能的出牌
        all_possible = generate_all_possible_plays(hand)
        
        # If there is no last play, all plays are legal
        # 如果没有上家出牌，所有出牌都合法
        if state.last_play is None:
            return all_possible
        
        # Filter plays that can beat the last play
        # 有上家出牌，过滤出能压上的
        last_play_info = (state.last_play[1], state.last_play[2])
        legal = []
        for play in all_possible:
            if can_beat(last_play_info, play):
                legal.append(play)
        
        # Passing is always legal (represented by empty list)
        # 过牌总是合法的（用空列表表示）
        return legal if legal else [[]]
    
    def apply_action(self, state: GameState, cards: List[str]) -> GameState:
        """
        Execute an action and return the new state
        执行动作，返回新状态
        cards: list of cards to play, empty list means pass
        cards: 出牌列表，空列表代表过牌
        """
        new_state = state.clone()
        
        # Pass
        # 过牌
        if not cards:  # 过牌
            new_state.current_player = "B" if state.current_player == "A" else "A"
            # Clear last play after passing (next player becomes new starter)
            # 过牌后清空上家记录（让下一家成为新首家）
            new_state.last_play = None
            new_state.last_play_value = -1
        else:
            # Play cards
            # 出牌
            if state.current_player == "A":
                for card in cards:
                    new_state.player_a_hand.remove(card)
            else:
                for card in cards:
                    new_state.player_b_hand.remove(card)
            
            # Record this play
            # 记录本次出牌
            play_type = identify_play_type(cards)
            new_state.last_play = (state.current_player, play_type, cards)
            new_state.last_play_value = get_play_value(play_type, cards)
            new_state.current_player = "B" if state.current_player == "A" else "A"
        
        new_state.turn_count += 1
        
        # Check win/loss
        # 检查胜负
        if len(new_state.player_a_hand) == 0:
            new_state.game_status = GameStatus.A_WIN
        elif len(new_state.player_b_hand) == 0:
            new_state.game_status = GameStatus.B_WIN
        
        return new_state
    
    def get_current_player_hand(self, state: GameState) -> List[str]:
        """Get the current player's hand
        获取当前玩家手牌"""
        return state.player_a_hand if state.current_player == "A" else state.player_b_hand
    
    def is_game_over(self, state: GameState) -> bool:
        """Check if the game is over
        检查游戏是否结束"""
        return state.game_status != GameStatus.ONGOING
    
    def get_winner(self, state: GameState) -> Optional[str]:
        """Get the winner
        获取胜者"""
        if state.game_status == GameStatus.A_WIN:
            return "A"
        elif state.game_status == GameStatus.B_WIN:
            return "B"
        return None
    
    @staticmethod
    def format_hand(hand: List[str]) -> str:
        """Format hand for display
        格式化手牌显示"""
        return " ".join(hand)