"""游戏数据结构定义"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class GameStatus(Enum):
    """游戏状态枚举"""
    ONGOING = "ongoing"      # 进行中
    A_WIN = "A_win"          # 玩家A胜利
    B_WIN = "B_win"          # 玩家B胜利


@dataclass
class TurnRecord:
    """单步决策记录"""
    turn: int                          # 回合数
    player: str                        # "A" 或 "B"
    action: str                        # 出牌描述（如"出 ♥3"或"不要"）
    cards: List[str]                   # 出的牌（空列表代表过牌）
    response_time_ms: int              # 响应时间（毫秒）
    is_valid: bool                     # 动作是否合法
    hand_before: List[str]             # 出牌前手牌
    hand_after: List[str]              # 出牌后手牌


@dataclass
class GameState:
    """游戏状态"""
    player_a_hand: List[str] = field(default_factory=list)
    player_b_hand: List[str] = field(default_factory=list)
    current_player: str = "A"          # "A" or "B"
    last_play: Optional[Tuple[str, str, List[str]]] = None  # (player, play_type, cards)
    last_play_value: int = -1          # 上家出牌的比较值
    turn_count: int = 0
    game_status: GameStatus = GameStatus.ONGOING
    
    def clone(self):
        """深拷贝"""
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
            new_state.last_play = self.last_play  # 元组不可变，直接复制
        return new_state