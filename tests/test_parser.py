import pytest

from aipokerjudge.model.parser import parse_action, extract_cards_from_text


# ============ 数字索引匹配（新核心逻辑） ============

def test_parse_numeric_index():
    legal = [["♥3"], ["♠4"], ["♦5"], []]
    result = parse_action("2", legal)
    assert result == ["♠4"]


def test_parse_numeric_index_with_extra_text():
    legal = [["♥3"], ["♠4"], []]
    result = parse_action("2  选这个", legal)
    assert result == ["♠4"]


def test_parse_numeric_index_pick_pass():
    legal = [["♥3"], []]
    result = parse_action("2", legal)
    assert result == []


def test_parse_numeric_index_out_of_range():
    legal = [["♥3"], ["♠4"]]
    result = parse_action("99", legal)
    assert result is None


# ============ 过牌关键词回退 ============

def test_parse_pass_chinese():
    legal = [["♥3"], []]
    result = parse_action("不要", legal)
    assert result == []


def test_parse_pass_english():
    legal = [["♥3"], []]
    result = parse_action("pass", legal)
    assert result == []


def test_parse_pass_0():
    legal = [["♥3"], []]
    result = parse_action("0", legal)
    assert result == []


def test_parse_pass_no_legal_pass():
    legal = [["♥3"], ["♠4"]]
    result = parse_action("不要", legal)
    assert result is None


# ============ 旧版卡片匹配回退 ============

def test_parse_cards_fallback():
    legal = [["♥3", "♠3"], ["♦5", "♣5"], []]
    result = parse_action("♥3 ♠3", legal)
    assert result is not None
    assert len(result) == 2


def test_parse_cards_fallback_no_match():
    legal = [["♥3"], []]
    result = parse_action("♥5", legal)
    assert result is None


# ============ 边界情况 ============

def test_parse_empty_response():
    result = parse_action("", [["♥3"]])
    assert result is None


def test_parse_empty_legal_actions():
    result = parse_action("1", [])
    assert result is None


def test_parse_none_response():
    result = parse_action(None, [["♥3"]])
    assert result is None


def test_extract_cards_from_text():
    text = "手牌: ♥3 ♠5 ♦J ♣A"
    cards = extract_cards_from_text(text)
    assert len(cards) == 4
    assert "♥3" in cards
    assert "♠5" in cards


def test_extract_cards_ascii_format():
    text = "H3 S5 DJ CA"
    cards = extract_cards_from_text(text)
    assert len(cards) == 4
    assert "H3" in cards
    assert "S5" in cards


def test_parse_cards_fallback_ascii():
    """模型输出 ASCII 格式牌面，解析器应自动转回 Unicode 匹配"""
    legal = [["♥3", "♠3"], ["♦5", "♣5"], []]
    result = parse_action("H3 S3", legal)
    assert result is not None
    assert len(result) == 2


def test_normalize_card():
    from aipokerjudge.model.parser import _normalize_card
    assert _normalize_card("H3") == "♥3"
    assert _normalize_card("S10") == "♠10"
    assert _normalize_card("DK") == "♦K"
    assert _normalize_card("C2") == "♣2"
    assert _normalize_card("♥A") == "♥A"  # 已经是 Unicode 不变
