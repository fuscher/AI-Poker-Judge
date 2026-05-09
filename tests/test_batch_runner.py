import pytest

from aipokerjudge.runner.batch_runner import (
    GameRecord, BatchResult, BatchRunner, _percentile, _normalize_swap
)


class TestGameRecord:
    def test_game_record_creation(self):
        record = GameRecord(
            round_num=1,
            winner="A",
            win_reason="normal",
            offender=None,
            total_turns=10,
            final_hand_a=[],
            final_hand_b=["♥3"],
        )
        assert record.round_num == 1
        assert record.winner == "A"
        assert record.win_reason == "normal"
        assert record.total_turns == 10
        assert record.a_violations == 0
        assert record.b_violations == 0

    def test_game_record_violations(self):
        record = GameRecord(
            round_num=2,
            winner="A",
            win_reason="violation",
            offender="B",
            total_turns=5,
            final_hand_a=["♥3"],
            final_hand_b=["♠4"],
            b_violations=2,
        )
        assert record.win_reason == "violation"
        assert record.offender == "B"
        assert record.b_violations == 2

    def test_game_record_timeouts(self):
        record = GameRecord(
            round_num=3,
            winner="B",
            win_reason="timeout",
            offender="A",
            total_turns=3,
            final_hand_a=["♥3", "♠4"],
            final_hand_b=["♦5"],
            a_timeouts=1,
        )
        assert record.win_reason == "timeout"
        assert record.a_timeouts == 1

    def test_game_record_benchmark_fields(self):
        record = GameRecord(
            round_num=1,
            winner="A",
            win_reason="normal",
            offender=None,
            total_turns=10,
            final_hand_a=[],
            final_hand_b=["♥3"],
            a_pass_count=3,
            b_pass_count=5,
            a_bomb_count=1,
            b_bomb_count=0,
            a_cards_played=15,
            b_cards_played=12,
            a_response_times=[100, 200, 150],
            b_response_times=[300, 400],
        )
        assert record.a_pass_count == 3
        assert record.b_pass_count == 5
        assert record.a_bomb_count == 1
        assert record.b_bomb_count == 0
        assert record.a_cards_played == 15
        assert record.b_cards_played == 12
        assert record.a_response_times == [100, 200, 150]
        assert record.b_response_times == [300, 400]

    def test_game_record_violation_detail(self):
        record = GameRecord(
            round_num=1,
            winner="B",
            win_reason="violation",
            offender="A",
            total_turns=3,
            final_hand_a=["♥3"],
            final_hand_b=["♠4"],
            a_violations=1,
            violation_detail="选择编号: 99",
        )
        assert record.violation_detail == "选择编号: 99"

    def test_game_record_violation_detail_none(self):
        record = GameRecord(
            round_num=2,
            winner="A",
            win_reason="normal",
            offender=None,
            total_turns=8,
            final_hand_a=[],
            final_hand_b=["♥3"],
        )
        assert record.violation_detail is None


class TestPercentile:
    def test_percentile_p50(self):
        data = [100, 200, 300, 400, 500]
        assert _percentile(data, 50) == 300.0

    def test_percentile_p95(self):
        data = list(range(1, 101))
        assert _percentile(data, 95) == 96.0

    def test_percentile_empty(self):
        assert _percentile([], 50) == 0.0

    def test_percentile_single(self):
        assert _percentile([42], 50) == 42.0


class TestBatchResult:
    def test_batch_result_creation(self):
        result = BatchResult(
            total_rounds=10,
            a_wins=6,
            b_wins=4,
            a_violations=0,
            b_violations=1,
            a_timeouts=0,
            b_timeouts=0,
            a_avg_response_ms=500.0,
            b_avg_response_ms=600.0,
            a_normal_wins=6,
            b_normal_wins=3,
            abnormal_rounds=1,
        )
        assert result.total_rounds == 10
        assert result.a_wins == 6
        assert result.b_wins == 4
        assert result.a_normal_wins + result.b_normal_wins + result.abnormal_rounds == 10

    def test_batch_result_game_records(self):
        result = BatchResult(
            total_rounds=2,
            a_wins=1,
            b_wins=1,
            a_violations=0,
            b_violations=0,
            a_timeouts=0,
            b_timeouts=0,
            a_avg_response_ms=0,
            b_avg_response_ms=0,
            a_normal_wins=1,
            b_normal_wins=1,
            abnormal_rounds=0,
        )
        record1 = GameRecord(round_num=1, winner="A", win_reason="normal",
                             offender=None, total_turns=8, final_hand_a=[],
                             final_hand_b=["♥3"])
        record2 = GameRecord(round_num=2, winner="B", win_reason="normal",
                             offender=None, total_turns=9, final_hand_a=["♦5"],
                             final_hand_b=[])
        result.game_records = [record1, record2]
        assert len(result.game_records) == 2
        assert result.game_records[0].winner == "A"
        assert result.game_records[1].winner == "B"

    def test_batch_result_benchmark_fields(self):
        result = BatchResult(
            total_rounds=5,
            a_wins=3,
            b_wins=2,
            a_violations=0,
            b_violations=0,
            a_timeouts=0,
            b_timeouts=0,
            a_avg_response_ms=300.0,
            b_avg_response_ms=400.0,
            a_normal_wins=3,
            b_normal_wins=2,
            abnormal_rounds=0,
            avg_turns=12.4,
            a_pass_count=10,
            b_pass_count=15,
            a_bomb_count=2,
            b_bomb_count=5,
            a_avg_cards_per_turn=1.5,
            b_avg_cards_per_turn=1.2,
            a_response_p50=250.0,
            a_response_p95=500.0,
            b_response_p50=350.0,
            b_response_p95=800.0,
        )
        assert result.avg_turns == 12.4
        assert result.a_pass_count == 10
        assert result.b_pass_count == 15
        assert result.a_bomb_count == 2
        assert result.b_bomb_count == 5
        assert result.a_avg_cards_per_turn == 1.5
        assert result.b_avg_cards_per_turn == 1.2
        assert result.a_response_p50 == 250.0
        assert result.b_response_p95 == 800.0


class TestNormalizeSwap:
    def test_swap_winner(self):
        record = GameRecord(
            round_num=1, winner="A", win_reason="normal",
            offender=None, total_turns=5,
            final_hand_a=["♥3"], final_hand_b=["♠4"],
        )
        swapped = _normalize_swap(record)
        assert swapped.winner == "B"

    def test_swap_offender(self):
        record = GameRecord(
            round_num=1, winner="B", win_reason="violation",
            offender="A", total_turns=3,
            final_hand_a=["♥3"], final_hand_b=["♠4"],
        )
        swapped = _normalize_swap(record)
        assert swapped.offender == "B"

    def test_swap_final_hands(self):
        record = GameRecord(
            round_num=1, winner="A", win_reason="normal",
            offender=None, total_turns=5,
            final_hand_a=["♥3", "♠5"], final_hand_b=["♣7"],
        )
        swapped = _normalize_swap(record)
        assert swapped.final_hand_a == ["♣7"]
        assert swapped.final_hand_b == ["♥3", "♠5"]

    def test_swap_counters(self):
        record = GameRecord(
            round_num=1, winner="A", win_reason="normal",
            offender=None, total_turns=5,
            final_hand_a=[], final_hand_b=[],
            a_violations=2, b_violations=0,
            a_pass_count=3, b_pass_count=1,
            a_bomb_count=1, b_bomb_count=0,
            a_cards_played=10, b_cards_played=7,
            a_decision_count=5, b_decision_count=4,
        )
        swapped = _normalize_swap(record)
        assert swapped.a_violations == 0
        assert swapped.b_violations == 2
        assert swapped.a_pass_count == 1
        assert swapped.b_pass_count == 3
        assert swapped.a_bomb_count == 0
        assert swapped.b_bomb_count == 1
        assert swapped.a_cards_played == 7
        assert swapped.b_cards_played == 10

    def test_swap_turns_detail(self):
        from aipokerjudge.games.doudizhu.models import TurnRecord
        record = GameRecord(
            round_num=1, winner="A", win_reason="normal",
            offender=None, total_turns=2,
            final_hand_a=[], final_hand_b=[],
        )
        record.turns_detail = [
            TurnRecord(turn=1, player="A", action="出", cards=["♥3"],
                       response_time_ms=100, is_valid=True,
                       hand_before=["♥3"], hand_after=[]),
            TurnRecord(turn=2, player="B", action="不要", cards=[],
                       response_time_ms=200, is_valid=True,
                       hand_before=["♠4"], hand_after=["♠4"]),
        ]
        swapped = _normalize_swap(record)
        assert swapped.turns_detail[0].player == "B"
        assert swapped.turns_detail[1].player == "A"

    def test_deal_pair_id(self):
        record = GameRecord(
            round_num=1, winner="A", win_reason="normal",
            offender=None, total_turns=5,
            final_hand_a=[], final_hand_b=[],
            deal_pair_id=42,
        )
        assert record.deal_pair_id == 42
