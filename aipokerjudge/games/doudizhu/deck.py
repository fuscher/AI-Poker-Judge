"""Deck management module
牌堆管理模块"""

import random
import re
from typing import List, Tuple, Optional

from aipokerjudge.config import CARD_RANKS


ASCII_SUITS = {'H': '♥', 'S': '♠', 'D': '♦', 'C': '♣'}
UNICODE_SUITS = {'♥': 'H', '♠': 'S', '♦': 'D', '♣': 'C'}
VALID_RANKS = set(CARD_RANKS)


def parse_ascii_card(text: str) -> Optional[str]:
    """Convert ASCII card notation to Unicode (e.g. H3 → ♥3, S10 → ♠10). Returns None if invalid.
    H3 → ♥3, S10 → ♠10。格式无效返回 None"""
    if not text or len(text) < 2:
        return None
    suit = text[0].upper()
    rank = text[1:].upper()
    if suit not in ASCII_SUITS or rank not in VALID_RANKS:
        return None
    return ASCII_SUITS[suit] + rank


def validate_custom_deal(hand_a: List[str], hand_b: List[str]) -> Optional[str]:
    """Validate custom dealt hands, returns None on success or error description on failure.
    校验自定义手牌，返回 None=通过，否则返回错误描述"""
    if len(hand_a) != 17 or len(hand_b) != 17:
        return f"每方必须各17张牌（当前A:{len(hand_a)} B:{len(hand_b)}）"

    all_cards = hand_a + hand_b
    if len(set(all_cards)) != len(all_cards):
        return "存在重复的牌"

    for card in all_cards:
        if len(card) < 2:
            return f"牌面格式错误: {card}"
        suit = card[0]
        rank = card[1:]
        if suit not in UNICODE_SUITS:
            return f"花色无效: {card}"
        if rank not in VALID_RANKS:
            return f"点数无效: {card}"

    return None


class Deck:
    """Deck class
    牌堆类"""
    
    SUITS = ['♥', '♠', '♦', '♣']
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.cards = self._create_deck()
    
    def _create_deck(self) -> List[str]:
        """Create a deck of 54 cards (no jokers)
        创建一副牌（54张，不含大小王）"""
        deck = []
        for suit in self.SUITS:
            for rank in CARD_RANKS:
                deck.append(f"{suit}{rank}")
        return deck
    
    def shuffle(self):
        """Shuffle the deck
        洗牌"""
        random.shuffle(self.cards)
    
    def deal(self, num_cards: int) -> List[str]:
        """Deal a specified number of cards
        发指定数量的牌"""
        if len(self.cards) < num_cards:
            raise ValueError("牌堆牌数不足")
        cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return cards
    
    def reset(self):
        """Reset the deck
        重置牌堆"""
        self.cards = self._create_deck()
        self.shuffle()


def create_initial_state(seed: int = None) -> 'GameState':
    """Create initial game state (random dealing)
    创建初始游戏状态（随机发牌）"""
    from .models import GameState
    
    deck = Deck(seed)
    deck.shuffle()
    
    # Deal: 17 cards each, discard remaining 3
    # 发牌：每人17张，剩余3张弃用
    player_a_hand = deck.deal(17)
    player_b_hand = deck.deal(17)
    # 3 remaining cards discarded (simplified)
    # 剩余3张底牌（简化版弃用）
    
    return GameState(
        player_a_hand=player_a_hand,
        player_b_hand=player_b_hand,
        current_player="A",
        last_play=None,
        last_play_value=-1,
        turn_count=0
    )


def create_state_with_hands(hand_a: List[str], hand_b: List[str]) -> 'GameState':
    """Create game state with specified hands (user dealer mode)
    使用指定的手牌创建游戏状态（用户荷官模式）"""
    from .models import GameState
    
    return GameState(
        player_a_hand=hand_a.copy(),
        player_b_hand=hand_b.copy(),
        current_player="A",
        last_play=None,
        last_play_value=-1,
        turn_count=0
    )


def generate_deal_pairs(n_pairs: int, base_seed: int = 42) -> List[Tuple[List[str], List[str]]]:
    """Generate n_pairs deal pairs, each returns (hand_a, hand_b), for deal normalization
    生成 n_pairs 组发牌对，每组返回 (hand_a, hand_b)，用于发牌归一化"""
    from .models import GameState
    
    pairs = []
    for i in range(n_pairs):
        seed = base_seed + i * 1000 if base_seed is not None else None
        deck = Deck(seed)
        deck.shuffle()
        hand_a = deck.deal(17)
        hand_b = deck.deal(17)
        pairs.append((hand_a, hand_b))
    return pairs