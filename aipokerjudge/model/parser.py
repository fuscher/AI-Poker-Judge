"""Model output parsing
模型输出解析"""

import re
from typing import List, Optional

# ASCII → Unicode suit conversion (fallback matching)
# ASCII → Unicode 花色转换（回退匹配用）
_ASCII_TO_UNICODE = {'H': '♥', 'S': '♠', 'D': '♦', 'C': '♣'}


def _normalize_card(card: str) -> str:
    """Convert ASCII format card back to Unicode format (H3 → ♥3)
    将 ASCII 格式牌面转回 Unicode 格式（H3 → ♥3）"""
    if card and card[0] in _ASCII_TO_UNICODE:
        return _ASCII_TO_UNICODE[card[0]] + card[1:]
    return card


def parse_action(response: str, legal_actions: List[List[str]]) -> Optional[List[str]]:
    """
    Parse model output and return the selected action.
    Priority: match numeric index first, fall back to string matching.

    response: model output string
    legal_actions: list of legal actions
    Returns: selected card list (empty list means pass), or None if parsing fails or action is illegal
    解析模型输出，返回选中的动作。
    优先匹配数字索引，回退到字符串匹配。

    response: 模型输出的字符串
    legal_actions: 合法动作列表
    返回: 选中的牌列表（空列表代表过牌），如果解析失败或动作不合法返回None
    """
    if not response or not legal_actions:
        return None

    text = response.strip()

    # 1. Priority: numeric index matching (search for standalone digits, exclude card face digits like ♥3 H3)
    # 1. 优先尝试数字索引匹配（全文搜索独立数字，排除牌面中的数字如 ♥3 H3）
    match = re.search(r'(?<![♥♠♦♣HSDC\d])(\d+)(?![♥♠♦♣HSDC\d])', text)
    if match:
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(legal_actions):
            return legal_actions[idx]

    # 2. Fallback: pass keywords
    # 2. 回退：过牌关键词
    text_lower = text.lower()
    if text_lower in ["不要", "pass", "过", "不", "0"]:
        for action in legal_actions:
            if not action:
                return []
        return None

    # 3. Fallback: card regex matching (compatible with Unicode and ASCII, ASCII auto-converted to Unicode)
    # 3. 回退：卡片正则匹配（兼容 Unicode 和 ASCII，ASCII 自动转回 Unicode）
    cards = re.findall(r'[♥♠♦♣HSDC][0-9JQKA10]+', text)
    if cards:
        normalized = [_normalize_card(c) for c in cards]
        cards_sorted = sorted(normalized)
        for legal in legal_actions:
            if legal and sorted(legal) == cards_sorted:
                return legal

    return None


def extract_cards_from_text(text: str) -> List[str]:
    """Extract all cards from text (with suit, compatible with Unicode and ASCII formats)
    从文本中提取所有卡牌（带花色，兼容 Unicode 和 ASCII 格式）"""
    return re.findall(r'[♥♠♦♣HSDC][0-9JQKA10]+', text)
