"""HTML 报表生成器 — 硬件监控风格 + 中英双语切换"""

import json
import os
import time
import webbrowser
from datetime import datetime
from typing import List, Any, Dict

from ..runner.batch_runner import BatchResult, GameRecord
from ..i18n import LANG, t


def _fmt_time(secs: float) -> str:
    if secs < 60:
        return f"{secs:.0f}s"
    m, s = divmod(int(secs), 60)
    return f"{m}m {s:02d}s"


def _fmt_num(n: int) -> str:
    return f"{n:,}"


def _build_chart_data(result: BatchResult) -> dict:
    """构建累计胜场数组（Chart.js 用）"""
    rounds = result.total_rounds
    labels = [str(i + 1) for i in range(rounds)]
    a_cum = []
    b_cum = []
    a_sum = 0
    b_sum = 0
    for r in result.game_records:
        if r.winner == "A":
            a_sum += 1
        elif r.winner == "B":
            b_sum += 1
        a_cum.append(a_sum)
        b_cum.append(b_sum)
    return {"labels": labels, "a_wins": a_cum, "b_wins": b_cum}


def generate_report(result: BatchResult, model_a_name: str, model_b_name: str) -> str:
    a_win_rate = result.a_wins / result.total_rounds * 100 if result.total_rounds > 0 else 0
    b_win_rate = result.b_wins / result.total_rounds * 100 if result.total_rounds > 0 else 0
    winner_name = model_a_name if result.a_wins > result.b_wins else (model_b_name if result.b_wins > result.a_wins else "")
    is_draw = result.a_wins == result.b_wins
    winner_display = '<span data-i18n="draw_winner">Draw</span>' if is_draw else ('Model B' if result.b_wins > result.a_wins else 'Model A')
    winner_side = "A" if result.a_wins > result.b_wins else ("B" if result.b_wins > result.a_wins else "-")
    elapsed_str = _fmt_time(result.elapsed_seconds)
    total_tokens = (result.a_total_prompt_tokens + result.a_total_completion_tokens +
                    result.b_total_prompt_tokens + result.b_total_completion_tokens)
    a_total_tokens = result.a_total_prompt_tokens + result.a_total_completion_tokens
    b_total_tokens = result.b_total_prompt_tokens + result.b_total_completion_tokens
    total_violations = result.a_violations + result.b_violations
    total_timeouts = result.a_timeouts + result.b_timeouts
    a_decision_count = sum(r.a_decision_count for r in result.game_records)
    b_decision_count = sum(r.b_decision_count for r in result.game_records)
    a_pass_rate = result.a_pass_count / a_decision_count * 100 if a_decision_count > 0 else 0
    b_pass_rate = result.b_pass_count / b_decision_count * 100 if b_decision_count > 0 else 0
    a_eff_idx = min(100, int(a_win_rate * 0.4 + (200 - min(result.a_avg_response_ms, 2000)) / 2000 * 30 + (2 - min(result.a_avg_cards_per_turn, 2)) / 2 * 30))
    b_eff_idx = min(100, int(b_win_rate * 0.4 + (200 - min(result.b_avg_response_ms, 2000)) / 2000 * 30 + (2 - min(result.b_avg_cards_per_turn, 2)) / 2 * 30))

    chart = _build_chart_data(result)
    chart_json = json.dumps(chart)

    # 异常局明细
    abnormal_records = [r for r in result.game_records if r.win_reason != "normal"]
    abnormal_rows = ""
    if abnormal_records:
        for record in abnormal_records:
            reason_map = {"violation": "Violation", "timeout": "Timeout", "error": "API Error", "max_turns": "Max Turns"}
            reason = reason_map.get(record.win_reason, record.win_reason)
            offender_text = f"Player {record.offender}" if record.offender else "-"
            detail = (record.violation_detail or "-")[:50]
            abnormal_rows += f"""<tr>
<td>{record.round_num}</td>
<td>{'Model A' if record.winner == 'A' else 'Model B'}</td>
<td>{reason}</td>
<td>{offender_text}</td>
<td style="max-width:200px;overflow:hidden;font-size:0.75rem;color:#8A94B0;">{detail}</td>
<td>{record.total_turns}</td></tr>"""
    else:
        abnormal_rows = '<tr><td colspan="6" class="success-message" style="text-align:center;">✅ All games passed integrity check · No violations or timeouts</td></tr>'

    # 正反手卡片
    total_pairs = result.total_rounds // 2
    first_second_html = ""
    if total_pairs > 0 and (result.a_wins_as_first or result.a_wins_as_second or result.b_wins_as_first or result.b_wins_as_second):
        a_first_pct = result.a_wins_as_first / total_pairs * 100 if total_pairs > 0 else 0
        a_second_pct = result.a_wins_as_second / total_pairs * 100 if total_pairs > 0 else 0
        b_first_pct = result.b_wins_as_first / total_pairs * 100 if total_pairs > 0 else 0
        b_second_pct = result.b_wins_as_second / total_pairs * 100 if total_pairs > 0 else 0
        first_adv = ((result.a_wins_as_first + result.b_wins_as_first) / (total_pairs * 2) * 100) if total_pairs > 0 else 0
        first_second_html = f"""
    <div class="card">
        <h2 data-i18n="pos_title">🔄 Position Win Rate</h2>
        <table class="metric-table">
            <thead><tr><th data-i18n="pos_model">Model</th><th data-i18n="pos_first">First (Win%)</th><th data-i18n="pos_second">Second (Win%)</th><th data-i18n="pos_adv">First Advantage</th></tr></thead>
            <tbody>
                <tr><td class="model-badge" style="color:#3B82F6;">{model_a_name}</td><td class="score-a">{a_first_pct:.1f}% ({result.a_wins_as_first}/{total_pairs})</td><td>{a_second_pct:.1f}% ({result.a_wins_as_second}/{total_pairs})</td><td class="{'diff-positive' if a_first_pct > a_second_pct else 'diff-negative'}">{a_first_pct - a_second_pct:+.1f}%</td></tr>
                <tr><td class="model-badge" style="color:#F97316;">{model_b_name}</td><td class="score-a">{b_first_pct:.1f}% ({result.b_wins_as_first}/{total_pairs})</td><td>{b_second_pct:.1f}% ({result.b_wins_as_second}/{total_pairs})</td><td class="{'diff-positive' if b_first_pct > b_second_pct else 'diff-negative'}">{b_first_pct - b_second_pct:+.1f}%</td></tr>
            </tbody>
        </table>
        <p style="margin-top:12px;font-size:0.75rem;color:#9CA3DA;"><span data-i18n="pos_overall">Overall First-Move Win Rate</span>: {first_adv:.1f}%</p>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>AI Poker Battle · Reports</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0B0E17; font-family:'Inter','Segoe UI','Roboto',monospace; padding:32px 24px; color:#EFF2F9; }}
body::before {{ content:""; position:fixed; top:0; left:0; width:100%; height:100%; background-image: linear-gradient(rgba(16,185,129,0.02) 1px,transparent 1px), linear-gradient(90deg,rgba(16,185,129,0.02) 1px,transparent 1px); background-size:32px 32px; pointer-events:none; z-index:0; }}
.container {{ max-width:1400px; margin:0 auto; position:relative; z-index:2; }}
.card {{ background:rgba(18,22,35,0.85); backdrop-filter:blur(2px); border-radius:28px; border:1px solid rgba(48,54,79,0.6); box-shadow:0 20px 35px -12px rgba(0,0,0,0.5),0 0 0 0.5px rgba(255,255,255,0.03) inset; padding:24px 28px; margin-bottom:28px; }}
.card:hover {{ border-color:rgba(72,187,120,0.4); }}
.hero {{ display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; margin-bottom:12px; }}
h1 {{ font-size:1.9rem; font-weight:700; background:linear-gradient(135deg,#E2F0FF 0%,#A0F0FF 100%); background-clip:text; -webkit-background-clip:text; color:transparent; letter-spacing:-0.3px; }}
.timestamp {{ font-family:monospace; font-size:0.8rem; color:#8A94B0; background:#0F111C; padding:6px 14px; border-radius:40px; border:1px solid #2A2F42; }}
.badge-pro {{ background:#10B98120; border:1px solid #10B98160; border-radius:40px; padding:4px 12px; font-size:0.7rem; font-weight:500; color:#6EE7B7; }}
.lang-btn {{ background:#181E2C; border:1px solid #3B82F6; color:#93C5FD; border-radius:40px; padding:6px 16px; font-size:0.75rem; cursor:pointer; margin-left:8px; transition:0.2s; }}
.lang-btn:hover {{ background:#1E2A45; }}
.lang-btn.active {{ background:#3B82F630; border-color:#60A5FA; }}
.stats-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:18px; margin-bottom:28px; }}
.monitor-card {{ background:#0F121E; border-radius:24px; padding:18px 16px; border:1px solid #262C3F; box-shadow:0 4px 12px rgba(0,0,0,0.2); }}
.monitor-card .label {{ font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; font-weight:600; color:#8A93B9; margin-bottom:12px; }}
.monitor-card .value {{ font-size:2.4rem; font-weight:800; line-height:1; color:#F0F3FA; }}
.monitor-card .sub {{ font-size:0.7rem; color:#6C7A9E; margin-top:8px; border-top:1px dashed #262C3F; padding-top:8px; }}
.winner-glow {{ background:linear-gradient(145deg,#0F172A,#1F2937); border-left:4px solid #F59E0B; }}
.winner-glow .value {{ color:#FBBF24; text-shadow:0 0 5px #F59E0B40; }}
.metrics-table-wrapper {{ overflow-x:auto; }}
.metric-table {{ width:100%; border-collapse:separate; border-spacing:0 8px; }}
.metric-table th {{ text-align:left; font-weight:600; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.5px; color:#9CA3DA; padding:8px 12px; }}
.metric-table td {{ background:#0F121E; padding:12px 12px; border-radius:16px; font-weight:500; font-size:0.9rem; border:1px solid #262C3F; }}
.model-badge {{ font-weight:700; font-family:monospace; background:#181E2C; padding:4px 10px; border-radius:40px; font-size:0.75rem; display:inline-block; }}
.score-a {{ color:#3B82F6; font-weight:800; }}
.score-b {{ color:#F97316; font-weight:800; }}
.diff-positive {{ color:#4ADE80; }}
.diff-negative {{ color:#F87171; }}
.chart-container {{ padding:12px 0; }}
canvas {{ max-height:240px; width:100%; }}
.violation-table {{ width:100%; border-collapse:collapse; }}
.violation-table th {{ text-align:left; font-size:0.7rem; font-weight:600; color:#A5B3E0; padding:10px 8px; border-bottom:1px solid #262C3F; }}
.violation-table td {{ padding:12px 8px; border-bottom:1px solid #1E2438; font-size:0.85rem; }}
.success-message {{ color:#34D399; background:#0E251C; border-radius:20px; padding:12px 16px; text-align:center; font-weight:500; }}
.vs-panel {{ display:flex; flex-wrap:wrap; gap:30px; justify-content:space-between; background:#0B0E17; border-radius:32px; padding:20px; margin-top:10px; }}
.model-stats-card {{ flex:1; background:#11141F; border-radius:24px; padding:20px; border:1px solid #29304A; text-align:center; }}
.model-name-large {{ font-size:1.2rem; font-weight:700; margin-bottom:16px; letter-spacing:-0.3px; }}
.metric-row {{ display:flex; justify-content:space-between; font-size:0.82rem; margin:10px 0; padding:4px 0; border-bottom:1px dashed #232838; }}
.cpu-style {{ font-family:monospace; font-size:1.6rem; font-weight:800; color:#FACC15; }}
.footnote {{ text-align:center; font-size:0.7rem; margin-top:20px; color:#5F6C8F; border-top:1px solid #1E2438; padding-top:20px; }}
@media (max-width:720px) {{ body {{ padding:20px 16px; }} .card {{ padding:18px; }} .monitor-card .value {{ font-size:2rem; }} .vs-panel {{ flex-direction:column; }} }}
</style>
</head>
<body>
<div class="container">
<div class="card" style="padding-bottom:18px;">
    <div class="hero">
        <div>
            <h1 data-i18n="hero_title">AI Poker Battle · Reports</h1>
            <div style="display:flex; gap:12px; margin-top:12px; flex-wrap:wrap;">
                <span class="badge-pro">Protocol v1.0</span>
                <span class="badge-pro">{model_a_name} vs {model_b_name}</span>
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
            <button id="lang-btn-en" class="lang-btn active" onclick="setLang('en')">EN</button>
            <button id="lang-btn-zh" class="lang-btn" onclick="setLang('zh')">中文</button>
            <div class="timestamp">🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
    </div>
    <div style="margin-top:12px; font-size:0.75rem; color:#6C7EA5;">
        <span data-i18n="hero_engine">Engine</span>: {model_a_name} vs {model_b_name} · {result.total_rounds} games
    </div>
</div>

<div class="stats-grid">
    <div class="monitor-card winner-glow">
        <div class="label" data-i18n="stat_winner">🏆 Final Winner</div>
        <div class="value">{winner_display}</div>
        <div class="sub">{'' if is_draw else winner_name}</div>
    </div>
    <div class="monitor-card">
        <div class="label" data-i18n="stat_score">Final Score</div>
        <div class="value">{result.a_wins} : {result.b_wins}</div>
        <div class="sub">{a_win_rate:.0f}% : {b_win_rate:.0f}%</div>
    </div>
    <div class="monitor-card">
        <div class="label" data-i18n="stat_rounds">Rounds / Abnormal</div>
        <div class="value">{result.total_rounds} / {result.abnormal_rounds}</div>
        <div class="sub"><span data-i18n="sub_viol">Violations</span> {total_violations} · <span data-i18n="sub_timeout">Timeouts</span> {total_timeouts}</div>
    </div>
    <div class="monitor-card">
        <div class="label" data-i18n="stat_turns">Avg Turns</div>
        <div class="value">{result.avg_turns:.1f}</div>
        <div class="sub" data-i18n="sub_turns">Per Game</div>
    </div>
    <div class="monitor-card">
        <div class="label" data-i18n="stat_elapsed">Elapsed</div>
        <div class="value" style="font-size:1.8rem;">{elapsed_str}</div>
        <div class="sub" data-i18n="sub_elapsed">End-to-end</div>
    </div>
    <div class="monitor-card">
        <div class="label" data-i18n="stat_tokens">Token Throughput</div>
        <div class="value" style="font-size:1.8rem;">{_fmt_num(total_tokens)}</div>
        <div class="sub" data-i18n="sub_tokens">In + Out total</div>
    </div>
</div>

<div class="card">
    <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:16px;">
        <h2 style="font-size:1.3rem; font-weight:600;" data-i18n="metric_title">📟 Core Metrics · Telemetry</h2>
        <span style="font-size:0.7rem; background:#181E2C; padding:4px 12px; border-radius:20px;">ms / tokens</span>
    </div>
    <div class="metrics-table-wrapper">
        <table class="metric-table">
            <thead><tr><th data-i18n="th_metric">Metric</th><th>{model_a_name} (A)</th><th>{model_b_name} (B)</th><th data-i18n="th_diff">Diff</th></tr></thead>
            <tbody>
<tr><td data-i18n="row_wins">Wins</td><td class="score-a">{result.a_wins}</td><td class="score-b">{result.b_wins}</td><td class="{'diff-positive' if result.a_wins > result.b_wins else 'diff-negative'}">{result.a_wins - result.b_wins:+d}</td></tr>
<tr><td data-i18n="row_winrate">Win Rate</td><td>{a_win_rate:.1f}%</td><td>{b_win_rate:.1f}%</td><td class="{'diff-positive' if a_win_rate > b_win_rate else 'diff-negative'}">{a_win_rate - b_win_rate:+.1f}%</td></tr>
<tr><td data-i18n="row_normal_wins">Normal Wins</td><td>{result.a_normal_wins}</td><td>{result.b_normal_wins}</td><td class="{'diff-positive' if result.a_normal_wins > result.b_normal_wins else 'diff-negative'}">{result.a_normal_wins - result.b_normal_wins:+d}</td></tr>
<tr><td data-i18n="row_violations">Violations</td><td>{result.a_violations}</td><td>{result.b_violations}</td><td class="diff-negative">{result.a_violations - result.b_violations:+d}</td></tr>
<tr><td data-i18n="row_timeouts">Timeouts</td><td>{result.a_timeouts}</td><td>{result.b_timeouts}</td><td class="diff-negative">{result.a_timeouts - result.b_timeouts:+d}</td></tr>
<tr><td data-i18n="row_avg_resp">Avg Response</td><td>{result.a_avg_response_ms:.0f} ms</td><td>{result.b_avg_response_ms:.0f} ms</td><td class="{'diff-positive' if result.a_avg_response_ms < result.b_avg_response_ms else 'diff-negative'}">{result.b_avg_response_ms - result.a_avg_response_ms:+.0f} ms</td></tr>
<tr><td data-i18n="row_p50">P50 Response</td><td>{result.a_response_p50:.0f} ms</td><td>{result.b_response_p50:.0f} ms</td><td class="{'diff-positive' if result.a_response_p50 < result.b_response_p50 else 'diff-negative'}">{result.b_response_p50 - result.a_response_p50:+.0f} ms</td></tr>
<tr><td data-i18n="row_p95">P95 Response</td><td>{result.a_response_p95:.0f} ms</td><td>{result.b_response_p95:.0f} ms</td><td class="{'diff-positive' if result.a_response_p95 < result.b_response_p95 else 'diff-negative'}">{result.b_response_p95 - result.a_response_p95:+.0f} ms</td></tr>
<tr><td data-i18n="row_cards_turn">Cards/Turn</td><td>{result.a_avg_cards_per_turn:.2f}</td><td>{result.b_avg_cards_per_turn:.2f}</td><td class="{'diff-positive' if result.a_avg_cards_per_turn > result.b_avg_cards_per_turn else 'diff-negative'}">{result.a_avg_cards_per_turn - result.b_avg_cards_per_turn:+.2f}</td></tr>
<tr><td data-i18n="row_input_tok">Input Tokens</td><td>{_fmt_num(result.a_total_prompt_tokens)}</td><td>{_fmt_num(result.b_total_prompt_tokens)}</td><td class="{'diff-positive' if result.a_total_prompt_tokens > result.b_total_prompt_tokens else 'diff-negative'}">{result.a_total_prompt_tokens - result.b_total_prompt_tokens:+,}</td></tr>
<tr><td data-i18n="row_output_tok">Output Tokens</td><td>{_fmt_num(result.a_total_completion_tokens)}</td><td>{_fmt_num(result.b_total_completion_tokens)}</td><td class="{'diff-positive' if result.a_total_completion_tokens > result.b_total_completion_tokens else 'diff-negative'}">{result.a_total_completion_tokens - result.b_total_completion_tokens:+,}</td></tr>
<tr><td data-i18n="row_total_tok">Total Tokens</td><td>{_fmt_num(a_total_tokens)}</td><td>{_fmt_num(b_total_tokens)}</td><td class="{'diff-positive' if a_total_tokens > b_total_tokens else 'diff-negative'}">{a_total_tokens - b_total_tokens:+,}</td></tr>
            </tbody>
        </table>
    </div>
</div>

<div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h2 style="font-size:1.25rem; font-weight:600;" data-i18n="chart_title">Dynamic Win Trend · Rolling Window</h2>
        <span style="font-size:0.7rem; background:#10B98120; padding:4px 12px; border-radius:30px;" data-i18n="chart_sub">Cumulative Wins</span>
    </div>
    <div class="chart-container">
        <canvas id="winRateChart" style="width:100%; height:220px;"></canvas>
    </div>
</div>

<div class="card">
    <h2 style="font-size:1.25rem; font-weight:600; margin-bottom:18px;" data-i18n="abnormal_title">⚠️ Anomaly Monitor · ECC Check</h2>
    <table class="violation-table">
        <thead><tr><th data-i18n="ab_th_round">Round</th><th data-i18n="ab_th_winner">Winner</th><th data-i18n="ab_th_reason">Reason</th><th data-i18n="ab_th_offender">Offender</th><th data-i18n="ab_th_detail">Detail</th><th data-i18n="ab_th_turns">Turns</th></tr></thead>
        <tbody>{abnormal_rows}</tbody>
    </table>
</div>

{first_second_html}

<div class="card">
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
        <h2 style="font-size:1.25rem; font-weight:600;" data-i18n="dash_title">🎮 Real-Time Performance Dashboard</h2>
        <div style="width:8px; height:8px; background:#10B981; border-radius:50%; box-shadow:0 0 6px #10B981;"></div>
        <span style="font-size:0.7rem;" data-i18n="dash_live">Live Telemetry · Afterburner Style</span>
    </div>
    <div class="vs-panel">
        <div class="model-stats-card">
            <div class="model-name-large">{model_a_name} <span style="font-size:0.7rem; background:#000; padding:2px 8px; border-radius:20px; color:#3B82F6;">Model A</span></div>
            <div class="metric-row"><span data-i18n="dash_avg_resp">⏱️ Avg Response</span><span class="cpu-style">{result.a_avg_response_ms:.0f} ms</span></div>
            <div class="metric-row"><span data-i18n="dash_p95">🔥 P95 Peak</span><span>{result.a_response_p95:.0f} ms</span></div>
            <div class="metric-row"><span data-i18n="dash_vio_to">🚦 Violate/Timeout</span><span style="color:#34D399;">{result.a_violations} / {result.a_timeouts}</span></div>
            <div class="metric-row"><span data-i18n="dash_pass_rate">♻️ Pass Rate</span><span>{a_pass_rate:.1f}%</span></div>
            <div class="metric-row"><span data-i18n="dash_cards">🧠 Cards/Turn</span><span>{result.a_avg_cards_per_turn:.2f}</span></div>
            <div class="metric-row"><span data-i18n="dash_tokens">📦 Tokens</span><span>{_fmt_num(a_total_tokens)}</span></div>
            <div style="margin-top:12px; background:#0A0C14; border-radius:50px; padding:5px; font-size:0.7rem;">
                <span data-i18n="dash_eff_idx">Efficiency Index</span> ▰▰ {'▰' * (a_eff_idx // 10)}{'▱' * (10 - a_eff_idx // 10)} {a_eff_idx}%
            </div>
        </div>
        <div class="model-stats-card" style="border-color:#F9731640;">
            <div class="model-name-large">{model_b_name} <span style="font-size:0.7rem; background:#000; padding:2px 8px; border-radius:20px; color:#F97316;">Model B</span></div>
            <div class="metric-row"><span data-i18n="dash_avg_resp">⏱️ Avg Response</span><span class="cpu-style" style="color:#F97316;">{result.b_avg_response_ms:.0f} ms</span></div>
            <div class="metric-row"><span data-i18n="dash_p95">🔥 P95 Peak</span><span>{result.b_response_p95:.0f} ms</span></div>
            <div class="metric-row"><span data-i18n="dash_vio_to">🚦 Violate/Timeout</span><span style="color:#34D399;">{result.b_violations} / {result.b_timeouts}</span></div>
            <div class="metric-row"><span data-i18n="dash_pass_rate">♻️ Pass Rate</span><span>{b_pass_rate:.1f}%</span></div>
            <div class="metric-row"><span data-i18n="dash_cards">🧠 Cards/Turn</span><span>{result.b_avg_cards_per_turn:.2f}</span></div>
            <div class="metric-row"><span data-i18n="dash_tokens">📦 Tokens</span><span>{_fmt_num(b_total_tokens)}</span></div>
            <div style="margin-top:12px; background:#0A0C14; border-radius:50px; padding:5px; font-size:0.7rem;">
                <span data-i18n="dash_eff_idx">Efficiency Index</span> ▰▰ {'▰' * (b_eff_idx // 10)}{'▱' * (10 - b_eff_idx // 10)} {b_eff_idx}%
                {' <span style="color:#FBBF24;">(Winner)</span>' if b_eff_idx > a_eff_idx else ''}
            </div>
        </div>
    </div>
</div>

<div class="footnote">
    AI Poker Battle · AIPokerJudge Professional Telemetry System<br>
    {model_a_name} vs {model_b_name} · {result.total_rounds} games · Data captured with hardware-grade monitoring
</div>
</div>

<script>
var chartData = {chart_json};

var LANG_DICT = {{
    en: {{
        hero_title: "AI Poker Battle · Reports",
        hero_engine: "Engine",
        stat_winner: "🏆 Final Winner",
        draw_winner: "Draw",
        stat_score: "Final Score",
        stat_rounds: "Rounds / Abnormal",
        stat_turns: "Avg Turns",
        stat_elapsed: "Elapsed",
        stat_tokens: "Token Throughput",
        sub_viol: "Violations",
        sub_timeout: "Timeouts",
        sub_turns: "Per Game",
        sub_elapsed: "End-to-end",
        sub_tokens: "In + Out total",
        metric_title: "📟 Core Metrics · Telemetry",
        th_metric: "Metric",
        th_diff: "Diff",
        row_wins: "Wins",
        row_winrate: "Win Rate",
        row_normal_wins: "Normal Wins",
        row_violations: "Violations",
        row_timeouts: "Timeouts",
        row_avg_resp: "Avg Response",
        row_p50: "P50 Response",
        row_p95: "P95 Response",
        row_cards_turn: "Cards/Turn",
        row_input_tok: "Input Tokens",
        row_output_tok: "Output Tokens",
        row_total_tok: "Total Tokens",
        chart_title: "Dynamic Win Trend · Cumulative Wins",
        chart_sub: "Per Round",
        abnormal_title: "⚠️ Anomaly Monitor · ECC Check",
        ab_th_round: "Round",
        ab_th_winner: "Winner",
        ab_th_reason: "Reason",
        ab_th_offender: "Offender",
        ab_th_detail: "Detail",
        ab_th_turns: "Turns",
        dash_title: "🎮 Real-Time Performance Dashboard",
        dash_live: "Live Telemetry · Afterburner Style",
        dash_avg_resp: "⏱️ Avg Response",
        dash_p95: "🔥 P95 Peak",
        dash_vio_to: "🚦 Violate/Timeout",
        dash_pass_rate: "♻️ Pass Rate",
        dash_cards: "🧠 Cards/Turn",
        dash_tokens: "📦 Tokens",
        dash_eff_idx: "Efficiency Index",
        pos_title: "🔄 Position Win Rate",
        pos_model: "Model",
        pos_first: "First (Win%)",
        pos_second: "Second (Win%)",
        pos_adv: "First Advantage",
        pos_overall: "Overall First-Move Win Rate",
        ch_label_a: "{model_a_name}",
        ch_label_b: "{model_b_name}",
        ch_x: "Round",
        ch_y: "Cumulative Wins"
    }},
    zh: {{
        hero_title: "AI博弈竞技场 · 对战报告",
        hero_engine: "引擎",
        stat_winner: "🏆 最终胜者",
        draw_winner: "平局",
        stat_score: "最终比分",
        stat_rounds: "总局数 / 异常",
        stat_turns: "平均回合",
        stat_elapsed: "端到端耗时",
        stat_tokens: "Token 吞吐",
        sub_viol: "违规",
        sub_timeout: "超时",
        sub_turns: "每局",
        sub_elapsed: "端到端",
        sub_tokens: "输入+输出",
        metric_title: "📟 核心指标 · 遥测对比",
        th_metric: "指标",
        th_diff: "差值",
        row_wins: "胜局",
        row_winrate: "胜率",
        row_normal_wins: "正常胜局",
        row_violations: "违规次数",
        row_timeouts: "超时次数",
        row_avg_resp: "平均响应",
        row_p50: "P50 响应",
        row_p95: "P95 响应",
        row_cards_turn: "出牌/回合",
        row_input_tok: "输入 Tokens",
        row_output_tok: "输出 Tokens",
        row_total_tok: "总 Tokens",
        chart_title: "动态胜率趋势 · 累计胜场",
        chart_sub: "每局",
        abnormal_title: "⚠️ 异常监控 · ECC校验",
        ab_th_round: "局号",
        ab_th_winner: "胜者",
        ab_th_reason: "原因",
        ab_th_offender: "违规方",
        ab_th_detail: "详情",
        ab_th_turns: "回合数",
        dash_title: "🎮 实时性能仪表盘",
        dash_live: "实时遥测 · Afterburner风格",
        dash_avg_resp: "⏱️ 平均响应",
        dash_p95: "🔥 P95峰值",
        dash_vio_to: "🚦 违规/超时",
        dash_pass_rate: "♻️ 弃牌率",
        dash_cards: "🧠 出牌/回合",
        dash_tokens: "📦 Tokens",
        dash_eff_idx: "效能指数",
        pos_title: "🔄 正反手胜率",
        pos_model: "模型",
        pos_first: "先手 (胜率%)",
        pos_second: "后手 (胜率%)",
        pos_adv: "先手优势",
        pos_overall: "先手综合胜率",
        ch_label_a: "{model_a_name}",
        ch_label_b: "{model_b_name}",
        ch_x: "轮次",
        ch_y: "累计胜场"
    }}
}};

var currentLang = "en";
var winChart;

function setLang(lang) {{
    currentLang = lang;
    document.querySelectorAll('[data-i18n]').forEach(function(el) {{
        var key = el.dataset.i18n;
        if (LANG_DICT[lang][key]) el.textContent = LANG_DICT[lang][key];
    }});
    document.querySelectorAll('.lang-btn').forEach(function(b) {{ b.classList.remove('active'); }});
    var btn = document.getElementById('lang-btn-' + lang);
    if (btn) btn.classList.add('active');
    if (winChart) {{
        var d = LANG_DICT[lang];
        winChart.data.datasets[0].label = d.ch_label_a;
        winChart.data.datasets[1].label = d.ch_label_b;
        winChart.options.scales.x.title.text = d.ch_x;
        winChart.options.scales.y.title.text = d.ch_y;
        winChart.update();
    }}
}}

(function() {{
    var ctx = document.getElementById('winRateChart').getContext('2d');
    var d = LANG_DICT[currentLang];
    winChart = new Chart(ctx, {{
        type: 'line',
        data: {{
            labels: chartData.labels,
            datasets: [
                {{
                    label: d.ch_label_a,
                    data: chartData.a_wins,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59,130,246,0.05)',
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: '#3B82F6',
                    tension: 0.2,
                    fill: true
                }},
                {{
                    label: d.ch_label_b,
                    data: chartData.b_wins,
                    borderColor: '#F97316',
                    backgroundColor: 'rgba(249,115,22,0.05)',
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: '#F97316',
                    tension: 0.2,
                    fill: true
                }}
            ]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                tooltip: {{ mode:'index', intersect:false, backgroundColor:'#0F121E', titleColor:'#D9E2FF', bodyColor:'#A0B0E0' }},
                legend: {{ position:'top', labels: {{ color:'#CBD5E8', font:{{ size:11 }}, usePointStyle:true, boxWidth:8 }} }}
            }},
            scales: {{
                y: {{
                    beginAtZero: true,
                    grid: {{ color:'#232842' }},
                    title: {{ display:true, text:d.ch_y, color:'#9BA8D4', font:{{ size:10 }} }},
                    ticks: {{ color:'#B9C4F0' }}
                }},
                x: {{
                    grid: {{ display:false }},
                    title: {{ display:true, text:d.ch_x, color:'#9BA8D4', font:{{ size:10 }} }},
                    ticks: {{ color:'#B9C4F0', font:{{ size:9 }}, maxTicksLimit:20 }}
                }}
            }}
        }}
    }});
}})();
</script>
</body>
</html>"""
    return html


def save_report(result: BatchResult, model_a_name: str, model_b_name: str,
                output_dir: str = "reports") -> str:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.html"
    filepath = os.path.join(output_dir, filename)

    html = generate_report(result, model_a_name, model_b_name)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    json_filename = f"data_{timestamp}.json"
    json_path = os.path.join(output_dir, json_filename)

    def to_serializable(obj: Any) -> Any:
        if hasattr(obj, '__dict__'):
            result_dict = {}
            for k, v in obj.__dict__.items():
                if not k.startswith('_'):
                    result_dict[k] = to_serializable(v)
            return result_dict
        if isinstance(obj, list):
            return [to_serializable(i) for i in obj]
        if isinstance(obj, tuple):
            return list(obj)
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        return str(obj)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result.game_records, f, default=to_serializable, ensure_ascii=False, indent=2)

    print(t("save_json", path=json_path))
    print(t("save_html", path=filepath))

    choice = input(t("save_open_prompt")).strip().lower()
    if choice != 'n':
        webbrowser.open(f'file://{os.path.abspath(filepath)}')
        print(t("save_opened", path=filepath))

    return filepath
