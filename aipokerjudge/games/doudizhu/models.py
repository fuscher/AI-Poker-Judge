"""Game data structure definitions
游戏数据结构定义"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class GameStatus(Enum):
    """Game status enumeration
    游戏状态枚举"""
    # Ongoing
    # 进行中
    ONGOING = "ongoing"      # 进行中
    # Player A wins
    # 玩家A胜利
    A_WIN = "A_win"          # 玩家A胜利
    # Player B wins
    # 玩家B胜利
    B_WIN = "B_win"          # 玩家B胜利


@dataclass
class TurnRecord:
    """Single turn decision record
    单步决策记录"""
    # Turn number
    # 回合数
    turn: int                          # 回合数
    # "A" or "B"
    # "A" 或 "B"
    player: str                        # "A" 或 "B"
    # Play description (e.g. "Play ♥3" or "Pass")
    # 出牌描述（如"出 ♥3"或"不要"）
    action: str                        # 出牌描述（如"出 ♥3"或"不要"）
    # Cards played (empty list means pass)
    # 出的牌（空列表代表过牌）
    cards: List[str]                   # 出的牌（空列表代表过牌）
    # Response time in milliseconds
    # 响应时间（毫秒）
    response_time_ms: int              # 响应时间（毫秒）
    # Whether the action is valid
    # 动作是否合法
    is_valid: bool                     # 动作是否合法
    # Hand before playing
    # 出牌前手牌
    hand_before: List[str]             # 出牌前手牌
    # Hand after playing
    # 出牌后手牌
    hand_after: List[str]              # 出牌后手牌


@dataclass
class GameState:
    """Game state
    游戏状态"""
    player_a_hand: List[str] = field(default_factory=list)
    player_b_hand: List[str] = field(default_factory=list)
    current_player: str = "A"          # "A" or "B"
    last_play: Optional[Tuple[str, str, List[str]]] = None  # (player, play_type, cards)
    # Comparison value of the last play
    # 上家出牌的比较值
    last_play_value: int = -1          # 上家出牌的比较值
    turn_count: int = 0
    game_status: GameStatus = GameStatus.ONGOING
    
    def clone(self):
        """Deep copy
        深拷贝"""
        import copy
        new_state = GameState(
            player_a_hand=copy.deepcopy(self.player_a_hand),
            player_b_hand=copy.deepcopy(self.player_b_hand),
            current_player=self.current_player,
            last_play=self.last_play,
            last_play_value=self.last_play_value,
            turn_count=self.turn_count,
            game_status=self.game_status
        )
        if self.last_play:
            # Tuples are immutable, directly copy
            # 元组不可变，直接复制
            new_state.last_play = self.last_play  # 元组不可变，直接复制
        return new_state