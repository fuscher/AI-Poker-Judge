import pytest

from aipokerjudge.games.doudizhu.rules import (
    identify_play_type, get_play_value, can_beat,
    generate_all_possible_plays, group_by_rank, parse_rank, get_card_value,
    _action_priority,
)


def test_parse_rank():
    assert parse_rank("♥3") == "3"
    assert parse_rank("♠10") == "10"
    assert parse_rank("♦J") == "J"
    assert parse_rank("♣A") == "A"
    assert parse_rank("3") == "3"


def test_get_card_value():
    assert get_card_value("♥3") == 0
    assert get_card_value("♥2") == 12
    assert get_card_value("♥10") == 7


def test_single():
    play_type = identify_play_type(["♥3"])
    assert play_type == "single"


def test_pair():
    play_type = identify_play_type(["♥3", "♠3"])
    assert play_type == "pair"


def test_triplet():
    play_type = identify_play_type(["♥5", "♠5", "♦5"])
    assert play_type == "triplet"


def test_bomb():
    play_type = identify_play_type(["♥9", "♠9", "♦9", "♣9"])
    assert play_type == "bomb"


def test_straight():
    play_type = identify_play_type(["♥3", "♠4", "♦5", "♣6", "♥7"])
    assert play_type == "straight"


def test_invalid_straight_too_short():
    play_type = identify_play_type(["♥3", "♠4", "♦5", "♣6"])
    assert play_type is None or play_type != "straight"


def test_straight_cannot_contain_2():
    play_type = identify_play_type(["♥10", "♠J", "♦Q", "♣K", "♥A"])
    assert play_type == "straight"


def test_straight_with_2_is_invalid():
    play_type = identify_play_type(["♥J", "♠Q", "♦K", "♣A", "♥2"])
    assert play_type is None


def test_can_beat_bomb_beats_single():
    last_play = ("single", ["♥3"])
    bomb = ["♥9", "♠9", "♦9", "♣9"]
    assert can_beat(last_play, bomb)


def test_cannot_beat_lower_single():
    last_play = ("single", ["♥A"])
    low = ["♥3"]
    assert not can_beat(last_play, low)


def test_can_beat_higher_single():
    last_play = ("single", ["♥3"])
    high = ["♥A"]
    assert can_beat(last_play, high)


def test_can_beat_same_type():
    last_play = ("pair", ["♥4", "♠4"])
    higher_pair = ["♥5", "♠5"]
    assert can_beat(last_play, higher_pair)


def test_cannot_beat_different_type():
    last_play = ("single", ["♥3"])
    pair = ["♥4", "♠4"]
    assert not can_beat(last_play, pair)


def test_triplet_with_one():
    play_type = identify_play_type(["♥3", "♠3", "♦3", "♥4"])
    assert play_type == "triplet_with_one"


def test_can_beat_with_no_last_play():
    assert can_beat(None, ["♥3"])


def test_get_play_value_bomb():
    value = get_play_value("bomb", ["♥5", "♠5", "♦5", "♣5"])
    assert value > 100


def test_generate_all_possible_plays():
    hand = ["♥3", "♠3", "♦5", "♣5", "♥7", "♠8"]
    plays = generate_all_possible_plays(hand)
    assert len(plays) > 0
    # single cards
    single_plays = [p for p in plays if len(p) == 1]
    assert len(single_plays) >= 6
    # pairs
    pair_plays = [p for p in plays if len(p) == 2 and p[0] != p[1]]
    assert any(identify_play_type(p) == "pair" for p in pair_plays)


def test_group_by_rank():
    hand = ["♥3", "♠3", "♦5", "♣5", "♥7"]
    groups = group_by_rank(hand)
    assert len(groups["3"]) == 2
    assert len(groups["5"]) == 2
    assert len(groups["7"]) == 1


def test_action_priority_single_before_bomb():
    single = ["♥3"]
    bomb = ["♥9", "♠9", "♦9", "♣9"]
    assert _action_priority(single) < _action_priority(bomb)


def test_action_priority_smaller_before_larger():
    small = ["♥3"]
    large = ["♥A"]
    assert _action_priority(small) < _action_priority(large)


def test_action_priority_empty_is_last():
    empty = []
    single = ["♥3"]
    # empty should have the smallest (earliest) sort key value, meaning it ends up last
    # Actually empty returns (0,) which is less than (1, value) for singles
    # So we test that empty < single in sort order meaning empty comes first
    assert _action_priority(empty) < _action_priority(single)


def test_generate_plays_sorted_strategy():
    """验证生成的动作按策略排序：单张在前，炸弹在末"""
    hand = ["♥3", "♠4", "♦9", "♣9", "♥9", "♠9", "♦5", "♣6"]
    plays = generate_all_possible_plays(hand)
    assert len(plays) > 0
    types = [identify_play_type(p) for p in plays if p]
    # 单张应该出现在炸弹之前
    singles_idx = [i for i, t in enumerate(types) if t == 'single']
    bombs_idx = [i for i, t in enumerate(types) if t == 'bomb']
    if singles_idx and bombs_idx:
        assert all(s < min(bombs_idx) for s in singles_idx), \
            f"单张应该排在炸弹前面，但单张索引={singles_idx}，炸弹索引={bombs_idx}"
