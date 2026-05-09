"""Dealer mode runner - real-time game display
荷官模式运行器 - 实时显示对局过程"""

import time
from typing import Optional, List, Tuple
from ..model.client import ModelClient
from ..games.doudizhu.deck import create_initial_state, parse_ascii_card, validate_custom_deal
from ..i18n import t
from .batch_runner import BatchRunner, BatchResult, _percentile, _normalize_swap


def _ask_custom_deal(label: str = "") -> Optional[Tuple[List[str], List[str]]]:
    """Ask user whether to deal manually; returns (hand_a, hand_b) or None (random deal)
    询问用户是否亲自发牌，返回 (hand_a, hand_b) 或 None(随机发牌)"""
    print("\n  " + t("custom_deal_ask"), end="")
    choice = input().strip().lower()
    if choice != 'y':
        return None

    print("  " + t("custom_format"))
    print("  " + t("custom_suits"))

    while True:
        print()
        raw = input("  > ").strip()
        if raw.lower() == 'q':
            return None

        cards = [parse_ascii_card(c) for c in raw.split() if c]
        if None in cards:
            print("  ⚠️ " + t("custom_fmt_err", n=sum(1 for c in cards if c is None)))
            continue
        if len(cards) != 34:
            print("  ⚠️ " + t("custom_count_err", n=len(cards)))
            continue

        hand_a = cards[:17]
        hand_b = cards[17:34]
        err = validate_custom_deal(hand_a, hand_b)
        if err:
            print(f"  ⚠️ {err}")
            continue

        print("  " + t("custom_ok", hand=' '.join(hand_a)))
        print("  " + t("custom_player_b", hand=' '.join(hand_b)))
        return hand_a, hand_b


def run_visual_mode(runner: BatchRunner, rounds: int, seed: int = None,
                    do_swap: bool = None) -> BatchResult:
    from aipokerjudge.config import POSITION_SWAP, DEAL_NORMALIZATION

    if do_swap is None:
        do_swap = POSITION_SWAP or DEAL_NORMALIZATION

    t_start = time.time()

    print(f"\n  " + t("dealer_title", rounds=rounds))
    print("=" * 60)

    results = []
    i = 0
    pair_id = 0

    while i < rounds:
        if do_swap and i + 1 < rounds:
            pair_seed = seed + pair_id * 1000 if seed is not None else None
            swap_label = t("deal_pair_normal", pair_id=pair_id + 1)
            print("\n📍 " + t("round_x_of_y", i=i + 1, rounds=rounds) + f" ({swap_label})")
            print("-" * 40)

            custom = _ask_custom_deal(swap_label)
            if custom:
                hand_a, hand_b = custom
            else:
                base_state = create_initial_state(pair_seed)
                hand_a = list(base_state.player_a_hand)
                hand_b = list(base_state.player_b_hand)

            rec1 = runner.run_one_round(i + 1, None, True, (hand_a, hand_b))
            rec1.deal_pair_id = pair_id
            results.append(rec1)
            _print_round_result(rec1)

            if i + 1 < rounds:
                user_input = input(t("continue_prompt_swap")).strip().lower()
                if user_input == 'q':
                    print(t("user_abort"))
                    break

            swap_label = t("deal_pair_swap", pair_id=pair_id + 1)
            print("\n📍 " + t("round_x_of_y", i=i + 2, rounds=rounds) + f" ({swap_label})")
            print("-" * 40)
            rec2 = runner.run_one_round(i + 2, None, True, (hand_b, hand_a))
            rec2 = _normalize_swap(rec2)
            rec2.deal_pair_id = pair_id
            results.append(rec2)
            _print_round_result(rec2)

            pair_id += 1
            i += 2
        else:
            round_seed = seed + i if seed is not None else None
            print("\n📍 " + t("round_x_of_y", i=i + 1, rounds=rounds))
            print("-" * 40)

            custom = _ask_custom_deal()
            if custom:
                rec = runner.run_one_round(i + 1, None, True, custom)
            else:
                rec = runner.run_one_round(i + 1, round_seed, True)
            results.append(rec)
            _print_round_result(rec)
            i += 1

        if i < rounds:
            user_input = input(t("continue_prompt")).strip().lower()
            if user_input == 'q':
                print(t("user_abort"))
                break

    # Aggregate results
    # 汇总结果
    a_wins = sum(1 for r in results if r.winner == "A")
    b_wins = sum(1 for r in results if r.winner == "B")
    abnormal = sum(1 for r in results if r.win_reason != "normal")

    all_a_rt = []
    all_b_rt = []
    total_a_cards = 0
    total_b_cards = 0
    total_turns = 0
    a_pass = b_pass = a_bomb = b_bomb = 0
    a_pt = b_pt = a_ct = b_ct = 0
    for r in results:
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

    print("\n" + "=" * 60)
    print("📊 " + t("results_title"))
    print(f"   {t('results_score')}: {a_wins} : {b_wins}")
    print(f"   {t('results_abnormal')}: {abnormal}")
    print(f"   {t('results_avg_turns')}: {total_turns / max(1, len(results)):.1f}")
    print(f"   {t('results_bomb')}: A:{a_bomb} B:{b_bomb}")

    total_a_dec = sum(r.a_decision_count for r in results)
    total_b_dec = sum(r.b_decision_count for r in results)

    a_first = sum(1 for r in results if r.deal_pair_id is not None and r.round_num % 2 == 1 and r.winner == "A")
    a_second = sum(1 for r in results if r.deal_pair_id is not None and r.round_num % 2 == 0 and r.winner == "A")
    b_first = sum(1 for r in results if r.deal_pair_id is not None and r.round_num % 2 == 1 and r.winner == "B")
    b_second = sum(1 for r in results if r.deal_pair_id is not None and r.round_num % 2 == 0 and r.winner == "B")

    return BatchResult(
        total_rounds=len(results),
        a_wins=a_wins,
        b_wins=b_wins,
        a_violations=sum(r.a_violations for r in results),
        b_violations=sum(r.b_violations for r in results),
        a_timeouts=sum(r.a_timeouts for r in results),
        b_timeouts=sum(r.b_timeouts for r in results),
        a_avg_response_ms=sum(r.a_total_response_ms for r in results) / max(1, total_a_dec),
        b_avg_response_ms=sum(r.b_total_response_ms for r in results) / max(1, total_b_dec),
        a_normal_wins=sum(1 for r in results if r.winner == "A" and r.win_reason == "normal"),
        b_normal_wins=sum(1 for r in results if r.winner == "B" and r.win_reason == "normal"),
        abnormal_rounds=abnormal,
        game_records=results,
        avg_turns=total_turns / max(1, len(results)),
        a_pass_count=a_pass,
        b_pass_count=b_pass,
        a_bomb_count=a_bomb,
        b_bomb_count=b_bomb,
        a_avg_cards_per_turn=total_a_cards / max(1, total_a_dec),
        b_avg_cards_per_turn=total_b_cards / max(1, total_b_dec),
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


def _print_round_result(rec):
    if rec.win_reason == "normal":
        print("\n🏆 " + t("winner_normal", winner=rec.winner))
    elif rec.win_reason == "violation":
        print("\n🏆 " + t("winner_violation", winner=rec.winner))
        print(f"   ⚠️ {t('offender')}: {t('player_a') if rec.offender == 'A' else t('player_b')}")
    elif rec.win_reason == "timeout":
        print("\n🏆 " + t("winner_timeout", winner=rec.winner))
    elif rec.win_reason == "error":
        print("\n🏆 " + t("winner_error", winner=rec.winner))
        print(f"   ⚠️ {t('error_from')}: {t('player_a') if rec.offender == 'A' else t('player_b')}")
    else:
        print(f"\n🏆 {rec.win_reason}")
    print(f"   {t('turns_count')}: {rec.total_turns}")
    if rec.a_violations > 0 or rec.b_violations > 0:
        print(f"   {t('violation_count')}: A:{rec.a_violations} B:{rec.b_violations}")
