"""国际化 / i18n 模块"""

LANG = "en"  # "zh" | "en"

_STRINGS = {
    # === CLI 主菜单 ===
    "menu_title":          {"zh": "请选择运行模式:",          "en": "Select mode:"},
    "menu_dealer":         {"zh": "荷官模式",                  "en": "Dealer Mode"},
    "menu_benchmark":      {"zh": "基准测试",                  "en": "Benchmark"},
    "menu_config":         {"zh": "配置管理",                  "en": "Configuration"},
    "menu_exit":           {"zh": "退出",                      "en": "Exit"},
    "menu_prompt":         {"zh": "\n请输入选项 (0-4): ",      "en": "\nEnter option (0-4): "},
    "goodbye":             {"zh": "再见！",                    "en": "Goodbye!"},
    "invalid_option":      {"zh": "无效选项",                  "en": "Invalid option"},

    # === 语言切换 ===
    "menu_lang":           {"zh": "语言 (简体中文)",           "en": "Language (English)"},
    "lang_changed":        {"zh": "语言已切换为: 简体中文",    "en": "Language: English"},

    # === 配置菜单 ===
    "cfg_title":           {"zh": "配置管理",                  "en": "Configuration"},
    "cfg_model_a":         {"zh": "模型A",                     "en": "Model A"},
    "cfg_model_b":         {"zh": "模型B",                     "en": "Model B"},
    "cfg_game_params":     {"zh": "游戏参数",                  "en": "Game Parameters"},
    "cfg_name":            {"zh": "名称",                      "en": "Name"},
    "cfg_key":             {"zh": "Key",                       "en": "Key"},
    "cfg_url":             {"zh": "URL",                       "en": "URL"},
    "cfg_rounds":          {"zh": "轮次",                      "en": "Rounds"},
    "cfg_workers":         {"zh": "线程",                      "en": "Workers"},
    "cfg_position_swap":   {"zh": "位置轮换",                  "en": "Position Swap"},
    "cfg_deal_norm":       {"zh": "发牌归一化",                "en": "Deal Norm."},
    "cfg_timeout":         {"zh": "超时",                      "en": "Timeout"},
    "cfg_seed":            {"zh": "种子",                      "en": "Seed"},
    "cfg_random":          {"zh": "随机",                      "en": "Random"},
    "cfg_check_conn":      {"zh": "检查连接",                  "en": "Check Conn."},
    "cfg_return":          {"zh": "返回主菜单",                "en": "Return to Menu"},
    "cfg_enabled":         {"zh": "✓ 启用",                    "en": "✓ On"},
    "cfg_disabled":        {"zh": "✗ 禁用",                    "en": "✗ Off"},
    "cfg_enter_option":    {"zh": "请输入选项: ",             "en": "Enter option: "},
    "cfg_invalid_input":   {"zh": "无效输入",                  "en": "Invalid input"},
    "cfg_prompt_name":     {"zh": "模型{label}名称 [{cur}]: ", "en": "Model {label} name [{cur}]: "},
    "cfg_prompt_key":      {"zh": "模型{label} Key [{cur}]: ", "en": "Model {label} Key [{cur}]: "},
    "cfg_prompt_url":      {"zh": "模型{label} URL [{cur}]: ", "en": "Model {label} URL [{cur}]: "},
    "cfg_prompt_rounds":   {"zh": "轮次 [{cur}]: ",            "en": "Rounds [{cur}]: "},
    "cfg_prompt_workers":  {"zh": "线程数 [{cur}]: ",          "en": "Workers [{cur}]: "},
    "cfg_prompt_timeout":  {"zh": "超时秒数 [{cur}]: ",        "en": "Timeout secs [{cur}]: "},
    "cfg_prompt_seed":     {"zh": "种子值 [{cur}] (r=随机): ","en": "Seed [{cur}] (r=random): "},
    "cfg_timeout_s":       {"zh": "s",                            "en": "s"},

    # === 模型连通检查 ===
    "check_no_key":        {"zh": "模型A Key 未设置",          "en": "Model A Key not set"},
    "check_testing":       {"zh": "正在检测模型{label} ({name})...", "en": "Checking model {label} ({name})..."},
    "check_ok":            {"zh": "✅ 模型{label}已识别: {name}",     "en": "✅ Model {label} ready: {name}"},
    "check_fail":          {"zh": "⚠️ 模型{label}连接失败: {name}",   "en": "⚠️ Model {label} failed: {name}"},
    "check_reconfig":      {"zh": "⚠️ 模型连接失败，仍使用旧配置",    "en": "⚠️ Connection failed, keeping previous config"},

    # === 轮次/种子输入 ===
    "rounds_prompt":       {"zh": "请输入对局轮次 (默认{default}): ", "en": "Enter rounds (default {default}): "},
    "rounds_confirm":      {"zh": "轮次 {n} 较大，确认继续? (y/n): ", "en": "Rounds {n} is high, confirm? (y/n): "},
    "seed_ask":            {"zh": "是否使用固定种子? (y/n, 默认n): ", "en": "Use fixed seed? (y/n, default n): "},
    "seed_prompt":         {"zh": "请输入种子值 (默认{default}): ",    "en": "Enter seed (default {default}): "},

    # === 荷官模式 (visual_runner) ===
    "dealer_title":        {"zh": "荷官模式 - {rounds}局对战",         "en": "Dealer Mode - {rounds} games"},
    "round_x_of_y":        {"zh": "第 {i} / {rounds} 局",             "en": "Round {i} / {rounds}"},
    "deal_pair_normal":    {"zh": "发牌对{pair_id} - 正常",           "en": "Deal Pair {pair_id} - Normal"},
    "deal_pair_swap":      {"zh": "发牌对{pair_id} - 交换",           "en": "Deal Pair {pair_id} - Swapped"},
    "custom_deal_ask":     {"zh": "是否亲自发牌? (y/n, 默认n): ",    "en": "Custom deal? (y/n, default n): "},
    "custom_format":       {"zh": "格式: H3 S4 D5 ... 共34张 (前17=玩家A, 后17=玩家B)", "en": "Format: H3 S4 D5 ... 34 cards (first 17=A, last 17=B)"},
    "custom_suits":        {"zh": "花色: H=♥ S=♠ D=♦ C=♣  点数: 3-10 J Q K A 2", "en": "Suits: H=♥ S=♠ D=♦ C=♣  Ranks: 3-10 J Q K A 2"},
    "custom_fmt_err":      {"zh": "格式错误（共{n}张无效），请检查",   "en": "Format error ({n} invalid), check input"},
    "custom_count_err":    {"zh": "需要34张牌，当前{n}张",             "en": "Need 34 cards, got {n}"},
    "custom_ok":           {"zh": "✅ 通过  玩家A: {hand}",            "en": "✅ OK  Player A: {hand}"},
    "custom_player_b":     {"zh": "         玩家B: {hand}",            "en": "         Player B: {hand}"},
    "card_deal":           {"zh": "本局发牌",                         "en": "Deal"},
    "player_a":            {"zh": "玩家A",                             "en": "Player A"},
    "player_b":            {"zh": "玩家B",                             "en": "Player B"},

    # === 游戏状态 ===
    "turn_info":           {"zh": "【回合{turn}】玩家{player} 出牌: {action}", "en": "[Turn {turn}] Player {player}: {action}"},
    "timeout_warn":        {"zh": "玩家{player} 超时 ({elapsed:.1f}s)，判负",  "en": "Player {player} timed out ({elapsed:.1f}s), lost"},
    "violation_warn":      {"zh": "玩家{player} 违规/错误！输出: {output}...",  "en": "Player {player} violation/error! Output: {output}..."},
    "winner_normal":       {"zh": "本局胜者: 玩家{winner} (正常结束)",        "en": "Winner: Player {winner} (normal)"},
    "winner_violation":    {"zh": "本局胜者: 玩家{winner} (对方违规)",        "en": "Winner: Player {winner} (opponent violation)"},
    "winner_timeout":      {"zh": "本局胜者: 玩家{winner} (对方超时)",        "en": "Winner: Player {winner} (opponent timeout)"},
    "winner_error":        {"zh": "本局胜者: 玩家{winner} (对方API错误)",     "en": "Winner: Player {winner} (opponent API error)"},
    "offender":            {"zh": "违规方",                                   "en": "Offender"},
    "error_from":          {"zh": "错误方",                                   "en": "Error from"},
    "turns_count":         {"zh": "回合数",                                   "en": "Turns"},
    "violation_count":     {"zh": "违规",                                     "en": "Violations"},
    "user_abort":          {"zh": "用户中断测试",                              "en": "Test aborted"},
    "continue_prompt":     {"zh": "\n按 Enter 继续下一局，输入 q 退出: ",    "en": "\nPress Enter for next, q to quit: "},
    "continue_prompt_swap":{"zh": "\n按 Enter 继续下一局（交换位置），输入 q 退出: ", "en": "\nPress Enter for next (swapped), q to quit: "},

    # === 结果摘要 ===
    "results_title":       {"zh": "测试完成!",                                "en": "Test Complete!"},
    "results_score":       {"zh": "最终比分",                                  "en": "Final Score"},
    "results_abnormal":    {"zh": "异常局数",                                  "en": "Abnormal rounds"},
    "results_avg_turns":   {"zh": "平均回合",                                  "en": "Avg turns"},
    "results_bomb":        {"zh": "炸弹使用",                                  "en": "Bombs"},
    "results_violations":  {"zh": "违规",                                     "en": "Violations"},
    "results_timeouts":    {"zh": "超时",                                     "en": "Timeouts"},
    "results_avg_resp":    {"zh": "平均响应",                                 "en": "Avg Response"},
    "results_p95":         {"zh": "P95延迟",                                  "en": "P95 Latency"},
    "results_tokens":      {"zh": "Tokens: A 入{ai}/出{ao} | B 入{bi}/出{bo}", "en": "Tokens: A in{ai}/out{ao} | B in{bi}/out{bo}"},
    "results_position":    {"zh": "正反手: A 先{af}/后{ae} | B 先{bf}/后{be}", "en": "Position: A 1st{af}/2nd{ae} | B 1st{bf}/2nd{be}"},
    "results_elapsed":     {"zh": "总用时",                                   "en": "Elapsed"},

    # === 基准测试 (blackbox_runner) ===
    "blackbox_title":      {"zh": "基准测试 - {rounds}局对战（{pairs}个发牌对，{workers}线程并行）", "en": "Benchmark - {rounds} games ({pairs} pairs, {workers} workers)"},
    "blackbox_title_simple":{"zh": "基准测试 - {rounds}局对战（{workers}线程并行）",                "en": "Benchmark - {rounds} games ({workers} workers)"},
    "blackbox_started":    {"zh": "已启动 {n} 个发牌对，等待首批结果 (timeout={t}s)...",           "en": "{n} deal pairs launched, waiting (timeout={t}s)..."},
    "blackbox_started_simple":{"zh": "已启动 {n} 局任务，等待首批结果 (timeout={t}s)...",           "en": "{n} games launched, waiting (timeout={t}s)..."},
    "blackbox_pair_timeout":{"zh": "发牌对{pair_id}执行超时，跳过",                                 "en": "Deal pair {pair_id} timed out"},
    "blackbox_pair_error": {"zh": "发牌对{pair_id}异常: {e}",                                      "en": "Deal pair {pair_id} error: {e}"},
    "blackbox_round_timeout":{"zh": "第{idx}局执行超时，跳过",                                      "en": "Round {idx} timed out"},

    # === 模型客户端 ===
    "api_error":           {"zh": "模型调用错误 [{name}]: {e}",                  "en": "Model API error [{name}]: {e}"},
    "api_fail_detail":     {"zh": "API调用失败，详见上方错误日志",                "en": "API call failed, see error log above"},

    # === 游戏动作 ===
    "pass_action":         {"zh": "不要",                        "en": "Pass"},
    "pass_no_legal":       {"zh": "不要（无合法动作）",          "en": "Pass (no legal action)"},

    # === 报表保存 ===
    "save_json":           {"zh": "📄 原始数据已保存: {path}",    "en": "📄 Raw data saved: {path}"},
    "save_html":           {"zh": "📄 报表已保存: {path}",        "en": "📄 Report saved: {path}"},
    "save_open_prompt":    {"zh": "\n📂 是否在浏览器中打开报表? (y/n, 默认y): ", "en": "\n📂 Open report in browser? (y/n, default y): "},
    "save_opened":         {"zh": "🌐 已在浏览器中打开: {path}",  "en": "🌐 Opened in browser: {path}"},
}


def t(key: str, **kwargs) -> str:
    """获取当前语言的翻译文本，支持 format 参数"""
    entry = _STRINGS.get(key, {})
    text = entry.get(LANG, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def toggle_lang():
    """切换语言，返回新语言名"""
    global LANG
    LANG = "en" if LANG == "zh" else "zh"
    return t("lang_changed")
