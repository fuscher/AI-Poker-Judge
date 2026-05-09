# API 文档

## 核心模块

### `aipokerjudge.game` — 游戏引擎

- **`GameEngine`** — 斗地主游戏状态机
  - `__init__(player_names, shuffle_seed)` — 初始化游戏
  - `get_state()` → `GameState` — 获取当前状态
  - `get_current_player()` → `PlayerState` — 获取当前玩家
  - `get_legal_actions(player_index)` → `List[str]` — 获取合法动作
  - `process_auction(player_index, action)` — 处理叫地主
  - `process_play(player_index, cards)` — 处理出牌

### `aipokerjudge.model` — AI 模型

- **`ModelClient`** — OpenAI 格式 API 客户端
- **`ModelFactory`** — 模型工厂，支持注册和创建
- **`OutputParser`** — 解析 LLM 输出为游戏动作
- **`PromptTemplates`** — 提示词模板

### `aipokerjudge.report` — 报表

- **`ReportGenerator`** — 生成 HTML 报表
- **`CSVExporter`** — 导出 CSV
- **`GameStats`** — 统计数据计算

### `aipokerjudge.runner` — 运行器

- **`BatchRunner`** — 批量测试
- **`VisualRunner`** — 可视化模式
- **`BlackboxRunner`** — 黑盒模式
- **`UserRunner`** — 用户荷官模式
