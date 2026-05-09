"""Card pattern recognition and comparison rules
牌型识别和比较规则"""

from typing import List, Dict, Optional, Tuple
from collections import Counter

from aipokerjudge.config import CARD_RANKS, CARD_RANK_VALUE, PLAY_TYPE_PRIORITY


def parse_rank(card: str) -> str:
    """Extract card rank (e.g. ♥3 -> 3, ♠10 -> 10)
    提取牌面点数（如 ♥3 -> 3, ♠10 -> 10）"""
    # Remove suit symbol
    # 去掉花色符号
    if card[0] in ['♥', '♠', '♦', '♣']:
        return card[1:]
    return card


def get_card_value(card: str) -> int:
    """Get card comparison value
    获取牌面的比较值"""
    rank = parse_rank(card)
    return CARD_RANK_VALUE.get(rank, -1)


def group_by_rank(hand: List[str]) -> Dict[str, List[str]]:
    """Group cards by rank
    按点数分组"""
    groups = {}
    for card in hand:
        rank = parse_rank(card)
        if rank not in groups:
            groups[rank] = []
        groups[rank].append(card)
    return groups


def identify_play_type(cards: List[str]) -> Optional[str]:
    """
    Identify card play type
    识别牌型
    Returns: 'single', 'pair', 'triplet', 'triplet_with_one', 'straight', 'bomb' or None
    返回: 'single', 'pair', 'triplet', 'triplet_with_one', 'straight', 'bomb' 或 None
    """
    if not cards:
        return None
    
    n = len(cards)
    ranks = [parse_rank(c) for c in cards]
    rank_values = [CARD_RANK_VALUE[r] for r in ranks]
    rank_values.sort()
    
    # Single
    # 单张
    if n == 1:
        return 'single'
    
    # Pair
    # 对子
    if n == 2 and rank_values[0] == rank_values[1]:
        return 'pair'
    
    # Triplet
    # 三张
    if n == 3 and len(set(ranks)) == 1:
        return 'triplet'
    
    # Triplet with one: 4 cards, 3 of the same rank
    # 三带一：4张牌，其中3张相同
    if n == 4:
        counter = Counter(ranks)
        if 3 in counter.values():
            return 'triplet_with_one'
        # Bomb: 4 of the same rank
        # 炸弹：4张相同
        if len(set(ranks)) == 1:
            return 'bomb'
    
    # Bomb (alternative detection)
    # 炸弹（另一种情况）
    if n == 4 and len(set(ranks)) == 1:
        return 'bomb'
    
    # Straight: at least 5 cards, cannot include 2, consecutive values
    # 顺子：至少5张，不能包含2，点数连续
    if n >= 5 and n <= 12:
        # Straight cannot include 2
        # 顺子不能包含2
        if any(v >= CARD_RANK_VALUE['2'] for v in rank_values):
            return None
        for i in range(len(rank_values) - 1):
            if rank_values[i + 1] - rank_values[i] != 1:
                return None
        return 'straight'
    
    return None


def get_play_value(play_type: str, cards: List[str]) -> int:
    """
    Get the base comparison value of a play type
    获取牌型的比较基准值
    Higher value means stronger cards
    值越大表示牌力越强
    """
    ranks = [parse_rank(c) for c in cards]
    rank_values = [CARD_RANK_VALUE[r] for r in ranks]
    
    if play_type == 'single':
        return rank_values[0]
    elif play_type == 'pair':
        # The larger card in the pair
        # 对子中较大的那张
        return max(rank_values)  # 对子中较大的那张
    elif play_type == 'triplet':
        return rank_values[0]
    elif play_type == 'triplet_with_one':
        # Find the rank that appears three times
        # 找出三张相同的点数
        counter = Counter(ranks)
        for rank, count in counter.items():
            if count == 3:
                return CARD_RANK_VALUE[rank]
    elif play_type == 'straight':
        # Compare using the highest card
        # 用最大牌比较
        return max(rank_values)  # 用最大牌比较
    elif play_type == 'bomb':
        # Bomb beats all normal play types
        # 炸弹大于所有普通牌型
        return rank_values[0] + 100  # 炸弹大于所有普通牌型
    
    return -1


def can_beat(last_play: Optional[Tuple[str, List[str]]], 
             current_cards: List[str]) -> bool:
    """
    Check if the current play can beat the last play
    判断当前出牌是否能压过上家
    last_play: (play_type, cards) or None
    last_play: (play_type, cards) 或 None
    """
    if last_play is None:
        return True
    
    last_type, last_cards = last_play
    current_type = identify_play_type(current_cards)
    
    if current_type is None:
        return False
    
    # Bomb can beat any play
    # 炸弹可以压任何牌
    if current_type == 'bomb':
        if last_type == 'bomb':
            return get_play_value('bomb', current_cards) > get_play_value('bomb', last_cards)
        return True
    
    # Normal play types must match
    # 普通牌型必须相同
    if current_type != last_type:
        return False
    
    return get_play_value(current_type, current_cards) > get_play_value(last_type, last_cards)


def generate_all_possible_plays(hand: List[str]) -> List[List[str]]:
    """
    Generate all possible play combinations from hand (simplified)
    生成手牌所有可能的出牌组合（简化版）
    Returns: list of all possible plays
    返回: 所有可能的出牌列表
    """
    if not hand:
        return []
    
    plays = []
    groups = group_by_rank(hand)
    ranks_list = list(groups.keys())
    
    # Single
    # 单张
    for card in hand:
        plays.append([card])
    
    # Pair
    # 对子
    for rank, cards in groups.items():
        if len(cards) >= 2:
            plays.append(cards[:2])
    
    # Triplet
    # 三张
    for rank, cards in groups.items():
        if len(cards) >= 3:
            plays.append(cards[:3])
    
    # Triplet with one: three of a kind + one other card
    # 三带一：三张 + 一张其他牌
    for rank, cards in groups.items():
        if len(cards) >= 3:
            triplet = cards[:3]
            # Find a single card
            # 找一张单牌
            for other_rank, other_cards in groups.items():
                if other_rank != rank and other_cards:
                    play = triplet + [other_cards[0]]
                    plays.append(play)
                    break
    
    # Bomb
    # 炸弹
    for rank, cards in groups.items():
        if len(cards) >= 4:
            plays.append(cards[:4])
    
    # Straight (simplified: 5-7 cards, excluding 2)
    # 顺子（简化：5-7张顺子，不包含2）
    sorted_ranks = sorted([r for r in ranks_list if r != '2'], 
                          key=lambda x: CARD_RANK_VALUE[x])
    
    for length in range(5, min(8, len(sorted_ranks) + 1)):
        for i in range(len(sorted_ranks) - length + 1):
            is_continuous = True
            for j in range(length - 1):
                v1 = CARD_RANK_VALUE[sorted_ranks[i + j]]
                v2 = CARD_RANK_VALUE[sorted_ranks[i + j + 1]]
                if v2 - v1 != 1:
                    is_continuous = False
                    break
            if is_continuous:
                straight_cards = []
                for j in range(length):
                    rank = sorted_ranks[i + j]
                    straight_cards.append(groups[rank][0])
                plays.append(straight_cards)
    
    # Deduplicate using tuples
    # 去重（用tuple去重）
    unique_plays = []
    seen = set()
    for play in plays:
        key = tuple(sorted(play))
        if key not in seen:
            seen.add(key)
            unique_plays.append(play)
    
    # Sort by strategy priority: singles/small pairs first, bombs last
    # 按策略优先级排序：单张/小对子靠前，炸弹靠末
    unique_plays.sort(key=_action_priority)
    
    return unique_plays


def _action_priority(play: List[str]) -> tuple:
    """Calculate action strategy priority (lower value = higher priority)
    计算动作的策略优先级（数值越小越优先展示）"""
    if not play:
        # "Pass" ranks last
        # "不要"排最末
        return (0,)  # "不要"排最末
    play_type = identify_play_type(play)
    avg_value = sum(get_card_value(c) for c in play) / len(play)
    
    type_order = {
        'single': 1,
        'pair': 2,
        'straight': 3,
        'triplet': 4,
        'triplet_with_one': 5,
        'bomb': 6,
    }
    return (type_order.get(play_type, 99), avg_value)