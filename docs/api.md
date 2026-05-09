# API 参考文档

## 模块结构

```
aipokerjudge/
├── game/              # 游戏引擎
│   ├── engine.py      # DouDiZhuEngine
│   ├── models.py      # GameState, GameStatus, TurnRecord
│   ├── deck.py        # Deck, 发牌工具
│   └── rules.py       # 牌型识别与比较
├── model/             # AI 模型
│   ├── client.py      # ModelClient（OpenAI 格式）
│   ├── parser.py      # parse_action（LLM 输出解析）
│   └── prompts.py     # build_decision_prompt（提示词构建）
├── report/
│   └── generator.py   # generate_report, save_report
└── runner/
    ├── batch_runner.py     # BatchRunner, GameRecord, BatchResult
    ├── blackbox_runner.py  # run_blackbox_mode
    └── visual_runner.py    # run_visual_mode
```

---

## 游戏引擎 — `aipokerjudge.game`

### `DouDiZhuEngine`

斗地主游戏状态机（简化 1v1 版，无叫地主阶段）。

```python
from aipokerjudge import DouDiZhuEngine

engine = DouDiZhuEngine(seed=42)
```

| 方法 | 返回 | 说明 |
|---|---|---|
| `create_state()` | `GameState` | 创建新游戏状态（随机发牌） |
| `get_legal_actions(state)` | `list[list[str]]` | 获取当前玩家的合法动作，`[[]]` 表示只能过牌 |
| `apply_action(state, cards)` | `GameState` | 执行动作（空列表 `[]` 表示过牌），返回新状态 |
| `get_current_player_hand(state)` | `list[str]` | 获取当前玩家手牌 |
| `is_game_over(state)` | `bool` | 检查游戏是否结束 |
| `get_winner(state)` | `str \| None` | 返回 `"A"` 或 `"B"`，未结束时返回 `None` |
| `format_hand(hand)`（静态） | `str` | 格式化手牌为空格分隔字符串 |

### 数据模型

**`GameState`：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `player_a_hand` | `list[str]` | 玩家 A 手牌（如 `["♥3", "♠5"]`） |
| `player_b_hand` | `list[str]` | 玩家 B 手牌 |
| `current_player` | `str` | `"A"` 或 `"B"` |
| `last_play` | `tuple \| None` | `(player, play_type, cards)` |
| `last_play_value` | `int` | 上家出牌的比较值 |
| `turn_count` | `int` | 当前回合数 |
| `game_status` | `GameStatus` | 游戏状态 |

**`GameStatus`（枚举）：** `ONGOING` / `A_WIN` / `B_WIN`

**`TurnRecord`（数据类）：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `turn` | `int` | 回合数 |
| `player` | `str` | `"A"` 或 `"B"` |
| `action` | `str` | 动作描述（"出 ♥3" / "不要"） |
| `cards` | `list[str]` | 出的牌 |
| `response_time_ms` | `int` | 响应时间（毫秒） |
| `is_valid` | `bool` | 是否合法 |
| `hand_before` | `list[str]` | 出牌前手牌 |
| `hand_after` | `list[str]` | 出牌后手牌 |

### 牌型规则

| 函数 | 返回 | 说明 |
|---|---|---|
| `parse_rank(card)` | `str` | 提取牌面点数（`"♥3"` -> `"3"`） |
| `get_card_value(card)` | `int` | 获取牌面比较值 |
| `identify_play_type(cards)` | `str \| None` | 识别牌型：`single`, `pair`, `triplet`, `triplet_with_one`, `straight`, `bomb` |
| `get_play_value(play_type, cards)` | `int` | 获取牌型的比较基准值（炸弹自动 +100） |
| `can_beat(last_play, current_cards)` | `bool` | 判断是否能压过上家 |
| `generate_all_possible_plays(hand)` | `list[list[str]]` | 生成所有合法出牌组合（去重，按策略排序） |

### 牌堆工具

| 函数 | 返回 | 说明 |
|---|---|---|
| `create_initial_state(seed)` | `GameState` | 随机发牌创建初始状态 |
| `create_state_with_hands(hand_a, hand_b)` | `GameState` | 使用自定义手牌创建状态 |
| `generate_deal_pairs(n_pairs, base_seed)` | `list` | 生成发牌对用于归一化 |
| `validate_custom_deal(hand_a, hand_b)` | `str \| None` | 校验自定义手牌合法性 |

---

## AI 模型 — `aipokerjudge.model`

### `ModelClient`

OpenAI 格式 API 客户端。

```python
from aipokerjudge import ModelClient

client = ModelClient(
    model_name="deepseek-chat",
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
    timeout=60
)
```

| 方法 | 返回 | 说明 |
|---|---|---|
| `check_connection()` | `bool` | 测试 API 连通性 |
| `call(prompt, temperature=0.7, max_tokens=30)` | `(content, elapsed_secs, usage)` | 调用模型，返回（响应文本, 耗时秒数, token用量字典） |

**usage 字典字段：** `prompt_tokens`, `completion_tokens`, `total_tokens`

### `parse_action(response, legal_actions)`

解析 LLM 输出为游戏动作。匹配优先级：数字索引 > 过牌关键词 > 卡牌正则。返回 `list[str]`（出的牌）、`[]`（过牌）或 `None`（解析失败）。

### `build_decision_prompt(state, legal_actions, turn_history=None)`

构建 AI 决策提示词。包含当前手牌、牌局信息、合法动作编号列表和最多 8 回合的出牌历史。

---

## 批量运行 — `aipokerjudge.runner`

### `BatchRunner`

```python
from aipokerjudge import BatchRunner

runner = BatchRunner(model_a, model_b)
```

| 方法 | 返回 | 说明 |
|---|---|---|
| `run_one_round(round_num, seed, verbose, preset_hands)` | `GameRecord` | 执行一局游戏 |
| `run_batch(rounds, seed, verbose, on_progress, do_swap)` | `BatchResult` | 批量运行多局 |

### 运行模式

| 函数 | 说明 |
|---|---|
| `run_visual_mode(runner, rounds, seed, do_swap)` | 荷官模式：实时显示对局过程，支持自定义发牌 |
| `run_blackbox_mode(runner, rounds, seed, max_workers, do_swap)` | 基准模式：多线程并行执行，显示进度条 |

### `GameRecord`（数据类）

| 字段 | 类型 | 说明 |
|---|---|---|
| `round_num` | `int` | 局号 |
| `winner` | `str` | `"A"` 或 `"B"` |
| `win_reason` | `str` | 胜局原因 |
| `total_turns` | `int` | 总回合数 |
| `a_violations` / `b_violations` | `int` | 违规次数 |
| `a_timeouts` / `b_timeouts` | `int` | 超时次数 |
| `a_total_response_ms` / `b_total_response_ms` | `int` | 累计响应时间 |
| `a_pass_count` / `b_pass_count` | `int` | 过牌次数 |
| `a_bomb_count` / `b_bomb_count` | `int` | 炸弹次数 |
| `a_prompt_tokens` / `b_prompt_tokens` | `int` | 输入 tokens |
| `a_completion_tokens` / `b_completion_tokens` | `int` | 输出 tokens |
| `turns_detail` | `list[TurnRecord]` | 回合详情 |

**胜局原因（`win_reason`）：**

| 值 | 说明 |
|---|---|
| `"normal"` | 正常出完所有手牌 |
| `"violation"` | 对手出牌违规 |
| `"timeout"` | 对手响应超时 |
| `"error"` | 对手 API 调用错误 |
| `"max_turns"` | 达到最大回合数上限 |

### `BatchResult`（数据类）

| 字段 | 类型 | 说明 |
|---|---|---|
| `total_rounds` | `int` | 总对局数 |
| `a_wins` / `b_wins` | `int` | 胜局数 |
| `a_violations` / `b_violations` | `int` | 违规总数 |
| `a_timeouts` / `b_timeouts` | `int` | 超时总数 |
| `a_avg_response_ms` / `b_avg_response_ms` | `float` | 平均响应时间 |
| `avg_turns` | `float` | 平均回合数 |
| `a_response_p50` / `b_response_p50` | `float` | 响应时间中位数 |
| `a_response_p95` / `b_response_p95` | `float` | 响应时间 P95 |
| `a_total_prompt_tokens` / `b_total_prompt_tokens` | `int` | 输入 tokens 总数 |
| `a_total_completion_tokens` / `b_total_completion_tokens` | `int` | 输出 tokens 总数 |
| `a_wins_as_first` / `a_wins_as_second` | `int` | 先手/后手胜局 |
| `b_wins_as_first` / `b_wins_as_second` | `int` | 先手/后手胜局 |
| `elapsed_seconds` | `float` | 总耗时 |
| `game_records` | `list[GameRecord]` | 所有单局记录 |
| `start_time` / `end_time` | `str` | ISO 格式时间戳 |

---

## 报表 — `aipokerjudge.report`

| 函数 | 返回 | 说明 |
|---|---|---|
| `generate_report(result, model_a_name, model_b_name)` | `str` | 生成完整 HTML 报表（Chart.js 图表，双语） |
| `save_report(result, model_a_name, model_b_name, output_dir="reports")` | `str` | 保存 HTML 报表和 JSON 数据，返回文件路径 |

---

## CLI 命令行

```bash
python -m aipokerjudge
```

交互式菜单：
- `[1]` **荷官模式** — 逐步对局，实时查看 LLM 决策
- `[2]` **基准测试** — 多线程批量测试，完成后生成报表
- `[3]` **配置管理** — 模型参数、轮次、线程数等
- `[4]` **切换语言** — 中文/English 切换
- `[0]` **退出**
