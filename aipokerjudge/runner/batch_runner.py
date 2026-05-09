"""Batch test runner - core business logic
批量测试运行器 - 核心业务逻辑"""

import time
from datetime import datetime
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass, field

from ..games.doudizhu.engine import DouDiZhuEngine
from ..games.doudizhu.models import GameState, GameStatus, TurnRecord
from ..games.doudizhu.rules import identify_play_type
from ..model.client import ModelClient
from ..model.prompts import build_decision_prompt
from ..model.parser import parse_action
from aipokerjudge.config import TIMEOUT_SECONDS, MAX_TURNS_PER_GAME, POSITION_SWAP, DEAL_NORMALIZATION
from ..i18n import t


@dataclass
class GameRecord:
    """Game record
    单局记录"""
    round_num: int
    winner: str                      # "A" or "B"
                                     # "A" 或 "B"
    win_reason: str                  # "normal", "violation", "timeout", "error", "max_turns"
                                     # 正常(normal) / 违规(violation) / 超时(timeout) / 错误(error) / 最大回合(max_turns)
    offender: Optional[str]          # Offending side (if any)
                                     # 违规方（如果有）
    total_turns: int
    final_hand_a: List[str]
    final_hand_b: List[str]
    a_violations: int = 0
    b_violations: int = 0
    a_timeouts: int = 0
    b_timeouts: int = 0
    a_total_response_ms: int = 0
    b_total_response_ms: int = 0
    a_decision_count: int = 0
    b_decision_count: int = 0
    seed: Optional[int] = None
    turns_detail: List[TurnRecord] = field(default_factory=list)
    # Benchmark 埋点
    a_pass_count: int = 0
    b_pass_count: int = 0
    a_bomb_count: int = 0
    b_bomb_count: int = 0
    a_cards_played: int = 0
    b_cards_played: int = 0
    a_response_times: List[int] = field(default_factory=list)
    b_response_times: List[int] = field(default_factory=list)
    violation_detail: Optional[str] = None
    deal_pair_id: Optional[int] = None  # Deal normalization: two rounds with the same deal share this ID
                                        # 发牌归一化：同一对手牌的两局共享此ID
    # Token 用量
    a_prompt_tokens: int = 0
    b_prompt_tokens: int = 0
    a_completion_tokens: int = 0
    b_completion_tokens: int = 0


def _percentile(data: List[int], p: float) -> float:
    """Calculate percentile
    计算百分位数"""
    if not data:
        return 0.0
    s = sorted(data)
    idx = int(len(s) * p / 100)
    return float(s[min(idx, len(s) - 1)])


def _normalize_swap(record: GameRecord) -> GameRecord:
    """Swap A/B labels so A=model_a B=model_b (for post-position-swap normalization)
    交换 A/B 标签使 A=model_a B=model_b（用于位置轮换后的归位）"""
    _swap = {"A": "B", "B": "A"}
    record.winner = _swap.get(record.winner, record.winner)
    if record.offender:
        record.offender = _swap.get(record.offender)
    record.final_hand_a, record.final_hand_b = record.final_hand_b, record.final_hand_a
    _paired = ['violations','timeouts','total_response_ms','decision_count',
               'pass_count','bomb_count','cards_played','response_times',
               'prompt_tokens','completion_tokens']
    for attr in _paired:
        a_val = getattr(record, f'a_{attr}')
        b_val = getattr(record, f'b_{attr}')
        setattr(record, f'a_{attr}', b_val)
        setattr(record, f'b_{attr}', a_val)
    for t in record.turns_detail:
        t.player = _swap.get(t.player, t.player)
    return record


@dataclass
class BatchResult:
    """Batch test result
    批量测试结果"""
    total_rounds: int
    a_wins: int
    b_wins: int
    a_violations: int
    b_violations: int
    a_timeouts: int
    b_timeouts: int
    a_avg_response_ms: float
    b_avg_response_ms: float
    a_normal_wins: int               # Normal wins
                                     # 正常结束的胜局
    b_normal_wins: int
    abnormal_rounds: int             # Abnormal rounds
                                     # 异常结束局数
    game_records: List[GameRecord] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""
    # Benchmark 聚合指标
    avg_turns: float = 0.0
    a_pass_count: int = 0
    b_pass_count: int = 0
    a_bomb_count: int = 0
    b_bomb_count: int = 0
    a_avg_cards_per_turn: float = 0.0
    b_avg_cards_per_turn: float = 0.0
    a_response_p50: float = 0.0
    a_response_p95: float = 0.0
    b_response_p50: float = 0.0
    b_response_p95: float = 0.0
    # Token 用量聚合
    a_total_prompt_tokens: int = 0
    b_total_prompt_tokens: int = 0
    a_total_completion_tokens: int = 0
    b_total_completion_tokens: int = 0
    # First/second-hand win rates
    # 正反手胜率
    a_wins_as_first: int = 0       # model_a wins as first player (odd round number)
                                   # model_a 先手（局号奇数）胜局
    a_wins_as_second: int = 0      # model_a wins as second player (even round number)
                                   # model_a 后手（局号偶数）胜局
    b_wins_as_first: int = 0
    b_wins_as_second: int = 0
    elapsed_seconds: float = 0.0


class BatchRunner:
    """Batch test runner
    批量测试运行器"""
    
    def __init__(self, model_a: ModelClient, model_b: ModelClient):
        self.model_a = model_a
        self.model_b = model_b
        self.engine = DouDiZhuEngine()
    
    def run_one_round(self, round_num: int, seed: int = None, 
                      verbose: bool = False,
                      preset_hands: Optional[Tuple[List[str], List[str]]] = None) -> GameRecord:
        """Execute one game round
        执行一局游戏
        
        preset_hands: Optional (hand_for_A, hand_for_B); skips random dealing when provided
        preset_hands: 可选 (hand_for_A, hand_for_B)，提供时跳过随机发牌
        """
        if preset_hands:
            from ..games.doudizhu.deck import create_state_with_hands
            state = create_state_with_hands(preset_hands[0], preset_hands[1])
            used_seed = None
        else:
            if seed is not None:
                self.engine = DouDiZhuEngine(seed)
            state = self.engine.create_state()
            used_seed = seed

        if verbose:
            print("\n  🃏 " + t("card_deal"))
            print(f"  {t('player_a')}: {self.engine.format_hand(state.player_a_hand)}")
            print(f"  {t('player_b')}: {self.engine.format_hand(state.player_b_hand)}")

        record = GameRecord(
            round_num=round_num,
            winner="",
            win_reason="",
            offender=None,
            total_turns=0,
            final_hand_a=[],
            final_hand_b=[],
            seed=used_seed
        )
        
        turn_count = 0
        turn_history = []
        
        while state.game_status == GameStatus.ONGOING and turn_count < MAX_TURNS_PER_GAME:
            turn_count += 1
            
            current = state.current_player
            hand_before = self.engine.get_current_player_hand(state).copy()
            
            # Get legal actions
            # 获取合法动作
            legal_actions = self.engine.get_legal_actions(state)
            
            # Auto-pass if no legal actions available
            # 如果没有合法动作，自动过牌
            if not legal_actions:
                action = []
                is_valid = True
                response_time_ms = 0
                action_desc = t("pass_no_legal")
            else:
                # Call the model
                # 调用模型
                model = self.model_a if current == "A" else self.model_b
                prompt = build_decision_prompt(state, legal_actions, turn_history)
                
                start_time = time.time()
                response, elapsed, usage = model.call(prompt)
                response_time_ms = int(elapsed * 1000)
                
                # Accumulate token usage
                # 累加 token 用量
                if usage:
                    if current == "A":
                        record.a_prompt_tokens += usage.get("prompt_tokens", 0)
                        record.a_completion_tokens += usage.get("completion_tokens", 0)
                    else:
                        record.b_prompt_tokens += usage.get("prompt_tokens", 0)
                        record.b_completion_tokens += usage.get("completion_tokens", 0)
                
                # Check timeout
                # 检查超时
                if elapsed > TIMEOUT_SECONDS:
                    if current == "A":
                        record.a_timeouts += 1
                    else:
                        record.b_timeouts += 1
                    
                    # Timeout → loss
                    # 超时判负
                    winner = "B" if current == "A" else "A"
                    record.winner = winner
                    record.win_reason = "timeout"
                    record.offender = current
                    record.total_turns = turn_count
                    record.final_hand_a = state.player_a_hand
                    record.final_hand_b = state.player_b_hand
                    
                    if verbose:
                        print("  ⚠️ " + t("timeout_warn", player=current, elapsed=elapsed))
                    
                    return record
                
                # Parse action
                # 解析动作
                action = parse_action(response, legal_actions)
                is_valid = action is not None
                action_desc = " ".join(action) if action else t("pass_action")
                
                # Invalid action or model call error
                # 动作不合法或模型调用错误
                if not is_valid:
                    if current == "A":
                        record.a_violations += 1
                    else:
                        record.b_violations += 1
                    
                    record.violation_detail = response or t("api_fail_detail")
                    
                    if verbose:
                        display = (response or "<no response>")[:50]
                        print("  ⚠️ " + t("violation_warn", player=current, output=display))
                    
                    # Determine loss: distinguish API error vs model violation
                    # 判负：区分 API 错误 vs 模型违规
                    winner = "B" if current == "A" else "A"
                    record.winner = winner
                    record.win_reason = "error" if response is None else "violation"
                    record.offender = current
                    record.total_turns = turn_count
                    record.final_hand_a = state.player_a_hand
                    record.final_hand_b = state.player_b_hand
                    
                    return record
            
            # Update response time statistics
            # 更新响应时间统计
            if current == "A":
                record.a_total_response_ms += response_time_ms
                record.a_decision_count += 1
                record.a_response_times.append(response_time_ms)
            else:
                record.b_total_response_ms += response_time_ms
                record.b_decision_count += 1
                record.b_response_times.append(response_time_ms)
            
            # 跟踪 pass / bomb / 出牌效率
            if action:
                cards_count = len(action)
                if current == "A":
                    record.a_cards_played += cards_count
                else:
                    record.b_cards_played += cards_count
                if identify_play_type(action) == 'bomb':
                    if current == "A":
                        record.a_bomb_count += 1
                    else:
                        record.b_bomb_count += 1
            else:
                if current == "A":
                    record.a_pass_count += 1
                else:
                    record.b_pass_count += 1
            
            # Execute action
            # 执行动作
            if verbose:
                print("  " + t("turn_info", turn=turn_count, player=current, action=action_desc))
            
            state = self.engine.apply_action(state, action if action else [])
            
            # Record turn details
            # 记录回合详情
            hand_after = self.engine.get_current_player_hand(state) if current == "A" else state.player_b_hand
            turn_record = TurnRecord(
                turn=turn_count,
                player=current,
                action=action_desc,
                cards=action if action else [],
                response_time_ms=response_time_ms,
                is_valid=is_valid,
                hand_before=hand_before,
                hand_after=hand_after
            )
            record.turns_detail.append(turn_record)
            turn_history.append({
                'turn': turn_count,
                'player': current,
                'action': action_desc,
            })
        
        # Normal end or max turns reached
        # 正常结束或超回合数
        if state.game_status == GameStatus.A_WIN:
            record.winner = "A"
            record.win_reason = "normal"
        elif state.game_status == GameStatus.B_WIN:
            record.winner = "B"
            record.win_reason = "normal"
        else:
            # Max turns exceeded, A wins
            # 超过最大回合数，判A胜
            record.winner = "A"
            record.win_reason = "max_turns"
        
        record.total_turns = turn_count
        record.final_hand_a = state.player_a_hand
        record.final_hand_b = state.player_b_hand
        
        return record
    
    def run_batch(self, rounds: int, seed: int = None, 
                  verbose: bool = False,
                  on_progress: Optional[Callable] = None,
                  do_swap: bool = None) -> BatchResult:
        """Batch run multiple rounds (supports deal normalization + position swap)
        批量运行多局（支持发牌归一化 + 位置轮换）"""
        from ..games.doudizhu.deck import create_initial_state
        
        if do_swap is None:
            do_swap = POSITION_SWAP or DEAL_NORMALIZATION
        
        result = BatchResult(
            total_rounds=rounds,
            a_wins=0,
            b_wins=0,
            a_violations=0,
            b_violations=0,
            a_timeouts=0,
            b_timeouts=0,
            a_avg_response_ms=0,
            b_avg_response_ms=0,
            a_normal_wins=0,
            b_normal_wins=0,
            abnormal_rounds=0,
            start_time=datetime.now().isoformat()
        )
        
        i = 0
        pair_id = 0
        completed = 0
        
        while i < rounds:
            if do_swap and i + 1 < rounds:
                # ---- Deal pair mode: same hand, two rounds swapping positions ----
                # ---- 发牌对模式：同一手牌，两局交换位置 ----
                pair_seed = seed + pair_id * 1000 if seed is not None else None
                base_state = create_initial_state(pair_seed)
                hand_a = list(base_state.player_a_hand)
                hand_b = list(base_state.player_b_hand)
                
                # Round i:   model_a=A(hand_a), model_b=B(hand_b)
                # 局 i:   model_a=A(hand_a), model_b=B(hand_b)
                rec1 = self.run_one_round(i + 1, None, verbose, (hand_a, hand_b))
                rec1.deal_pair_id = pair_id
                self._agg(result, rec1)
                result.game_records.append(rec1)
                completed += 1
                
                # Round i+1: model_a=B(hand_b), model_b=A(hand_a)  ← swap
                # 局 i+1: model_a=B(hand_b), model_b=A(hand_a)  ← 交换
                rec2 = self.run_one_round(i + 2, None, verbose, (hand_b, hand_a))
                rec2 = _normalize_swap(rec2)
                rec2.deal_pair_id = pair_id
                self._agg(result, rec2)
                result.game_records.append(rec2)
                completed += 1
                
                pair_id += 1
                i += 2
            else:
                # ---- Traditional single-round mode ----
                # ---- 传统单局模式 ----
                round_seed = seed + i if seed is not None else None
                rec = self.run_one_round(i + 1, round_seed, verbose)
                self._agg(result, rec)
                result.game_records.append(rec)
                completed += 1
                i += 1
            
            if on_progress:
                on_progress(completed, rounds, result.a_wins, result.b_wins)
            if not verbose and completed % max(1, rounds // 10) == 0:
                print(f"  进度: {completed}/{rounds} 局 (比分: {result.a_wins}:{result.b_wins})")
        
        # Calculate aggregate metrics
        # 计算聚合指标
        total_a_decisions = sum(r.a_decision_count for r in result.game_records)
        total_a_time = sum(r.a_total_response_ms for r in result.game_records)
        total_b_decisions = sum(r.b_decision_count for r in result.game_records)
        total_b_time = sum(r.b_total_response_ms for r in result.game_records)
        
        result.a_avg_response_ms = total_a_time / total_a_decisions if total_a_decisions > 0 else 0
        result.b_avg_response_ms = total_b_time / total_b_decisions if total_b_decisions > 0 else 0
        
        all_a_rt = []
        all_b_rt = []
        total_a_cards = 0
        total_b_cards = 0
        total_turns = 0
        for r in result.game_records:
            all_a_rt.extend(r.a_response_times)
            all_b_rt.extend(r.b_response_times)
            total_a_cards += r.a_cards_played
            total_b_cards += r.b_cards_played
            total_turns += r.total_turns
            result.a_pass_count += r.a_pass_count
            result.b_pass_count += r.b_pass_count
            result.a_bomb_count += r.a_bomb_count
            result.b_bomb_count += r.b_bomb_count
        
        result.avg_turns = total_turns / result.total_rounds if result.total_rounds > 0 else 0.0
        total_a_turns = sum(r.a_decision_count for r in result.game_records)
        total_b_turns = sum(r.b_decision_count for r in result.game_records)
        result.a_avg_cards_per_turn = total_a_cards / total_a_turns if total_a_turns > 0 else 0.0
        result.b_avg_cards_per_turn = total_b_cards / total_b_turns if total_b_turns > 0 else 0.0
        
        result.a_total_prompt_tokens = sum(r.a_prompt_tokens for r in result.game_records)
        result.b_total_prompt_tokens = sum(r.b_prompt_tokens for r in result.game_records)
        result.a_total_completion_tokens = sum(r.a_completion_tokens for r in result.game_records)
        result.b_total_completion_tokens = sum(r.b_completion_tokens for r in result.game_records)
        
        # First/second-hand win rates (deal pair mode: odd rounds = model_a first)
        # 正反手胜率（发牌对模式：奇数局 = model_a 先手）
        for r in result.game_records:
            if r.deal_pair_id is not None:
                if r.round_num % 2 == 1:
                    if r.winner == "A": result.a_wins_as_first += 1
                    if r.winner == "B": result.b_wins_as_first += 1
                else:
                    if r.winner == "A": result.a_wins_as_second += 1
                    if r.winner == "B": result.b_wins_as_second += 1
        
        result.a_response_p50 = _percentile(all_a_rt, 50)
        result.a_response_p95 = _percentile(all_a_rt, 95)
        result.b_response_p50 = _percentile(all_b_rt, 50)
        result.b_response_p95 = _percentile(all_b_rt, 95)
        
        result.end_time = datetime.now().isoformat()
        result.elapsed_seconds = (datetime.fromisoformat(result.end_time) - datetime.fromisoformat(result.start_time)).total_seconds()
        return result
    
    @staticmethod
    def _agg(result: BatchResult, rec: GameRecord):
        """Accumulate game record statistics
        累加单局统计"""
        if rec.winner == "A":
            result.a_wins += 1
            if rec.win_reason == "normal":
                result.a_normal_wins += 1
        elif rec.winner == "B":
            result.b_wins += 1
            if rec.win_reason == "normal":
                result.b_normal_wins += 1
        result.a_violations += rec.a_violations
        result.b_violations += rec.b_violations
        result.a_timeouts += rec.a_timeouts
        result.b_timeouts += rec.b_timeouts
        if rec.win_reason != "normal":
            result.abnormal_rounds += 1