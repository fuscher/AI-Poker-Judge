"""Prompt templates
提示词模板"""

from typing import List, Optional, Dict
from ..games.doudizhu.models import GameState
from ..games.doudizhu.engine import DouDiZhuEngine


HISTORY_MAX_TURNS = 8

_SUIT_MAP = {'♥': 'H', '♠': 'S', '♦': 'D', '♣': 'C'}

SYSTEM_PROMPT = """你是斗地主高手，遵循以下策略：

【核心原则】
1. 开局优先出小单张(3~6)、小对子，消耗弱牌，保留强牌用于压制
2. 炸弹(4张相同)是稀缺资源，仅用于：压制对手关键出牌 或 收尾终结比赛
3. 绝不在开局、空闲回合或无需压制时出炸弹
4. 顺子(5+连续)用于一次性消耗多张中等牌，优先出5~9区间
5. 手中有多张单牌时优先出单张，避免后期被对手的大牌卡死
6. 保留大牌(2、A、K)用于关键回合反击
7. 当合法动作列表中无"不要"选项时，必须出牌，不能过牌

严格只输出数字编号或"不要"，禁止输出任何额外文字。"""


def _to_ascii(card: str) -> str:
    """Convert single card to ASCII format (♥3 → H3)
    单张牌转ASCII格式（♥3 → H3）"""
    if card and card[0] in _SUIT_MAP:
        return _SUIT_MAP[card[0]] + card[1:]
    return card


def _format_hand_ascii(hand: List[str]) -> str:
    """Format hand as ASCII (for AI prompt)
    格式化手牌为ASCII（AI prompt用）"""
    return " ".join(_to_ascii(c) for c in hand)


def build_decision_prompt(
    state: GameState,
    legal_actions: List[List[str]],
    turn_history: Optional[List[Dict]] = None
) -> str:
    engine = DouDiZhuEngine()
    hand = engine.get_current_player_hand(state)
    hand_str = _format_hand_ascii(hand)

    # Format legal actions — display all, use numeric indices
    # 格式化合法动作 — 全部展示，使用数字编号
    legal_lines = []
    for i, action in enumerate(legal_actions):
        if not action:
            legal_lines.append(f" {i + 1}. 不要")
        else:
            legal_lines.append(f" {i + 1}. 出 {_format_hand_ascii(action)}")
    legal_str = "\n".join(legal_lines)

    # Previous player's play info
    # 上家出牌信息
    if state.last_play:
        last_player, play_type, cards = state.last_play
        last_play_info = f"上家（玩家{last_player}）出了: {_format_hand_ascii(cards)} (牌型: {play_type})"
    else:
        last_play_info = "你是首家，可以出任何牌"

    prompt = f"""【你的手牌】
{hand_str}

【牌局信息】
{last_play_info}

【当前回合】
轮到玩家{state.current_player}出牌

【合法动作】（只能选择其中一项，输出对应数字编号）
{legal_str}"""

    # Append current game play history
    # 追加本局出牌历史
    if turn_history:
        max_entries = HISTORY_MAX_TURNS * 2
        recent = turn_history[-max_entries:]
        history_lines = []
        for h in recent:
            history_lines.append(f"  回合{h['turn']}: 玩家{h['player']} {h['action']}")
        prompt += f"\n\n【本局出牌记录】\n" + "\n".join(history_lines)

    prompt += "\n选择编号:"
    return prompt
