"""Benchmark runner - parallel batch execution
基准测试运行器 - 并行批量执行"""

import time
from typing import Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from ..model.client import ModelClient
from ..games.doudizhu.deck import generate_deal_pairs
from ..i18n import t
from .batch_runner import (
    BatchRunner, BatchResult, GameRecord, _percentile, _normalize_swap
)


def _fmt_time(secs: float) -> str:
    if secs < 60:
        return f"{secs:.0f}s"
    m, s = divmod(int(secs), 60)
    return f"{m}m{s:02d}s"


def _run_deal_pair(
    model_a: ModelClient, model_b: ModelClient,
    pair_id: int, hand_a: List[str], hand_b: List[str],
    timeout_s: int
) -> Tuple[GameRecord, GameRecord]:
    """Run a deal pair serially in a thread (normal + swap)
    线程内串行跑一个发牌对（正常 + 交换）"""
    runner = BatchRunner(model_a, model_b)

    rec1 = runner.run_one_round(pair_id * 2 + 1, None, False, (hand_a, hand_b))
    rec1.deal_pair_id = pair_id

    rec2 = runner.run_one_round(pair_id * 2 + 2, None, False, (hand_b, hand_a))
    rec2 = _normalize_swap(rec2)
    rec2.deal_pair_id = pair_id

    return rec1, rec2


def run_blackbox_mode(runner: BatchRunner, rounds: int, seed: int = None,
                      max_workers: int = 3, do_swap: bool = None) -> BatchResult:
    """
    Black-box mode: multi-threaded parallel execution (deal normalization + position swap)
    黑盒模式：多线程并行执行（发牌归一化 + 位置轮换）
    """
    from aipokerjudge.config import POSITION_SWAP, DEAL_NORMALIZATION

    if do_swap is None:
        do_swap = POSITION_SWAP or DEAL_NORMALIZATION

    t_start = time.time()

    if do_swap and rounds >= 2:
        num_pairs = rounds // 2
        print(f"\n⚡ " + t("blackbox_title", rounds=rounds, pairs=num_pairs, workers=max_workers))
        print("=" * 60)

        base_seed = seed if seed is not None else 42
        deal_pairs = generate_deal_pairs(num_pairs, base_seed)

        game_records = [None] * rounds
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {}
            for pair_id in range(num_pairs):
                hand_a, hand_b = deal_pairs[pair_id]
                future = pool.submit(
                    _run_deal_pair,
                    runner.model_a, runner.model_b,
                    pair_id, hand_a, hand_b,
                    runner.model_a.timeout
                )
                futures[future] = pair_id

            print("  " + t("blackbox_started", n=num_pairs, t=runner.model_a.timeout))

            for future in as_completed(futures):
                pair_id = futures[future]
                try:
                    rec1, rec2 = future.result(timeout=runner.model_a.timeout + 60)
                    game_records[pair_id * 2] = rec1
                    game_records[pair_id * 2 + 1] = rec2
                except TimeoutError:
                    print("  ⚠️ " + t("blackbox_pair_timeout", pair_id=pair_id + 1))
                except Exception as e:
                    print("  ⚠️ " + t("blackbox_pair_error", pair_id=pair_id + 1, e=e))
                completed += 2

                percent = completed * 100 // rounds
                bar_len = 30
                filled = int(bar_len * completed / rounds)
                bar = '█' * filled + '░' * (bar_len - filled)
                a_wins = sum(1 for r in game_records if r is not None and r.winner == "A")
                b_wins = sum(1 for r in game_records if r is not None and r.winner == "B")
                end_str = "\n" if completed == rounds else "\r"
                print(f"  [{bar}] {percent}% ({completed}/{rounds}) 比分: {a_wins}:{b_wins}", end=end_str)
    else:
        print(f"\n⚡ " + t("blackbox_title_simple", rounds=rounds, workers=max_workers))
        print("=" * 60)

        game_records = [None] * rounds
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {}
            for i in range(rounds):
                round_seed = seed + i if seed is not None else None
                thread_runner = BatchRunner(runner.model_a, runner.model_b)
                future = pool.submit(thread_runner.run_one_round, i + 1, round_seed, False)
                futures[future] = i

            print("  " + t("blackbox_started_simple", n=rounds, t=runner.model_a.timeout))

            for future in as_completed(futures):
                idx = futures[future]
                try:
                    game_records[idx] = future.result(timeout=runner.model_a.timeout + 30)
                except TimeoutError:
                    print("  ⚠️ " + t("blackbox_round_timeout", idx=idx + 1))
                    game_records[idx] = None
                completed += 1

                percent = completed * 100 // rounds
                bar_len = 30
                filled = int(bar_len * completed / rounds)
                bar = '█' * filled + '░' * (bar_len - filled)
                a_wins = sum(1 for r in game_records if r is not None and r.winner == "A")
                b_wins = sum(1 for r in game_records if r is not None and r.winner == "B")
                end_str = "\n" if completed == rounds else "\r"
                print(f"  [{bar}] {percent}% ({completed}/{rounds}) 比分: {a_wins}:{b_wins}", end=end_str)

    # Aggregate results
    # 汇总结果
    records = [r for r in game_records if r is not None]
    a_wins = sum(1 for r in records if r.winner == "A")
    b_wins = sum(1 for r in records if r.winner == "B")
    a_violations = sum(r.a_violations for r in records)
    b_violations = sum(r.b_violations for r in records)
    a_timeouts = sum(r.a_timeouts for r in records)
    b_timeouts = sum(r.b_timeouts for r in records)
    a_normal = sum(1 for r in records if r.winner == "A" and r.win_reason == "normal")
    b_normal = sum(1 for r in records if r.winner == "B" and r.win_reason == "normal")
    abnormal = sum(1 for r in records if r.win_reason != "normal")

    total_a_decisions = sum(r.a_decision_count for r in records)
    total_a_time = sum(r.a_total_response_ms for r in records)
    total_b_decisions = sum(r.b_decision_count for r in records)
    total_b_time = sum(r.b_total_response_ms for r in records)

    all_a_rt = []
    all_b_rt = []
    total_a_cards = 0
    total_b_cards = 0
    total_turns = 0
    a_pass = b_pass = a_bomb = b_bomb = 0
    a_pt = b_pt = a_ct = b_ct = 0
    for r in records:
        all_a_rt.extend(r.a_response_times)
        all_b_rt.extend(r.b_response_times)
        total_a_cards += r.a_cards_played
        total_b_cards += r.b_cards_played
        total_turns += r.total_turns
        a_pass += r.a_pass_count
        b_pass += r.b_pass_count
        a_bomb += r.a_bomb_count
        b_bomb += r.b_bomb_count
        a_pt += r.a_prompt_tokens
        b_pt += r.b_prompt_tokens
        a_ct += r.a_completion_tokens
        b_ct += r.b_completion_tokens

    # First/second-hand win rates
    # 正反手胜率
    a_first = sum(1 for r in records if r.deal_pair_id is not None and r.round_num % 2 == 1 and r.winner == "A")
    a_second = sum(1 for r in records if r.deal_pair_id is not None and r.round_num % 2 == 0 and r.winner == "A")
    b_first = sum(1 for r in records if r.deal_pair_id is not None and r.round_num % 2 == 1 and r.winner == "B")
    b_second = sum(1 for r in records if r.deal_pair_id is not None and r.round_num % 2 == 0 and r.winner == "B")

    result = BatchResult(
        total_rounds=len(records),
        a_wins=a_wins,
        b_wins=b_wins,
        a_violations=a_violations,
        b_violations=b_violations,
        a_timeouts=a_timeouts,
        b_timeouts=b_timeouts,
        a_avg_response_ms=total_a_time / total_a_decisions if total_a_decisions > 0 else 0,
        b_avg_response_ms=total_b_time / total_b_decisions if total_b_decisions > 0 else 0,
        a_normal_wins=a_normal,
        b_normal_wins=b_normal,
        abnormal_rounds=abnormal,
        game_records=records,
        avg_turns=total_turns / max(1, len(records)),
        a_pass_count=a_pass,
        b_pass_count=b_pass,
        a_bomb_count=a_bomb,
        b_bomb_count=b_bomb,
        a_avg_cards_per_turn=total_a_cards / max(1, total_a_decisions),
        b_avg_cards_per_turn=total_b_cards / max(1, total_b_decisions),
        a_response_p50=_percentile(all_a_rt, 50),
        a_response_p95=_percentile(all_a_rt, 95),
        b_response_p50=_percentile(all_b_rt, 50),
        b_response_p95=_percentile(all_b_rt, 95),
        a_total_prompt_tokens=a_pt,
        b_total_prompt_tokens=b_pt,
        a_total_completion_tokens=a_ct,
        b_total_completion_tokens=b_ct,
        a_wins_as_first=a_first,
        a_wins_as_second=a_second,
        b_wins_as_first=b_first,
        b_wins_as_second=b_second,
        elapsed_seconds=time.time() - t_start,
    )

    print("\n📊 " + t("results_title"))
    print(f"   {t('results_elapsed')}: {_fmt_time(result.elapsed_seconds)}")
    print(f"   {t('results_score')}: {result.a_wins} : {result.b_wins}")
    print(f"   {t('results_abnormal')}: {result.abnormal_rounds}")
    print(f"   {t('results_avg_turns')}: {result.avg_turns:.1f}")
    print(f"   {t('results_violations')}: A:{result.a_violations} B:{result.b_violations}")
    print(f"   {t('results_timeouts')}: A:{result.a_timeouts} B:{result.b_timeouts}")
    print(f"   {t('results_avg_resp')}: A:{result.a_avg_response_ms:.0f}ms B:{result.b_avg_response_ms:.0f}ms")
    print(f"   {t('results_p95')}: A:{result.a_response_p95:.0f}ms B:{result.b_response_p95:.0f}ms")
    print(t("results_tokens", ai=result.a_total_prompt_tokens, ao=result.a_total_completion_tokens, bi=result.b_total_prompt_tokens, bo=result.b_total_completion_tokens))
    print(t("results_position", af=result.a_wins_as_first, ae=result.a_wins_as_second, bf=result.b_wins_as_first, be=result.b_wins_as_second))

    return result
