# AI-Poker-Judge

> AI vs AI 扑克对战平台 — 测试 LLM 的决策能力、规则遵循度与性能表现。

[English](README.md) | [简体中文](README.zh.md)

---

## 概述

AI-Poker-Judge 是一个简化版 1v1 斗地主测试框架，让两个 AI 模型互相对战，评估它们在策略推理、规则遵循和响应速度方面的表现。支持任何兼容 OpenAI 格式的 API（DeepSeek、GPT、Claude、Ollama 等）。

---

## 特性

- **简化 1v1 斗地主** — 无叫地主阶段、无大小王，专注出牌策略
- **多模型支持** — 任何 OpenAI 兼容 API（DeepSeek、GPT、Claude、Ollama、vLLM）
- **双运行模式** — 荷官模式（逐步可视化）与基准模式（多线程批量测试）
- **丰富报表** — 自动生成 HTML 报表，集成 Chart.js 图表（中英双语）
- **双语 CLI** — 支持中文/英文界面切换
- **位置轮换与发牌归一化** — 消除先后手偏差，实现公平 A/B 对比
- **详细日志** — 每局 JSON 日志，含响应时间、Token 用量、违规记录

---

## 快速开始

```bash
pip install -r requirements.txt
python -m aipokerjudge
```

---

## 配置

编辑 `aipokerjudge/config.py` 或设置环境变量。关键配置：

| 配置项 | 环境变量 | 默认值 | 说明 |
|---|---|---|---|
| `MODEL_A_API_KEY` | `MODEL_A_API_KEY` | `""` | 模型A API密钥 |
| `MODEL_A_BASE_URL` | `MODEL_A_BASE_URL` | `https://api.deepseek.com` | 模型A API地址 |
| `MODEL_A_NAME` | `MODEL_A_NAME` | `deepseek-chat` | 模型A名称 |

模型 B 同理（`MODEL_B_*`）。两个模型可以使用不同的 API 提供商进行 A/B 对比测试。

📖 [完整配置说明](docs/configuration.md)

---

## 使用方法

```bash
python -m aipokerjudge
```

交互式菜单：
- `[1]` **荷官模式** — 实时逐步查看 AI 决策过程
- `[2]` **基准测试** — 多线程批量测试，带进度条
- `[3]` **配置管理** — 调整模型、轮次、线程等参数
- `[4]` **切换语言** — 中文 / English 切换
- `[0]` **退出**

---

## API 参考

关键类与函数：

| 模块 | 主要导出 |
|---|---|
| `aipokerjudge.games.doudizhu.engine` | `DouDiZhuEngine` |
| `aipokerjudge.games.doudizhu.models` | `GameState`, `GameStatus`, `TurnRecord` |
| `aipokerjudge.games.doudizhu.rules` | `identify_play_type`, `can_beat`, `generate_all_possible_plays` |
| `aipokerjudge.model.client` | `ModelClient` |
| `aipokerjudge.model.parser` | `parse_action` |
| `aipokerjudge.model.prompts` | `build_decision_prompt` |
| `aipokerjudge.runner.batch_runner` | `BatchRunner`, `GameRecord`, `BatchResult` |
| `aipokerjudge.report.generator` | `generate_report`, `save_report` |

📖 [完整 API 参考](docs/api.md)

---

## 自定义扩展

- **自定义提示词** — 修改 `prompts.py` 中的 `SYSTEM_PROMPT` 或替换 `build_decision_prompt()`
- **添加新模型** — 任何 OpenAI 兼容 API 开箱即用
- **自定义报表** — 提供 JSON 原始数据可供二次分析
- **新运行模式** — 参考 `visual_runner.py` / `blackbox_runner.py` 的模式
- **国际化** — 在 `i18n.py` 中添加新语言

📖 [自定义扩展指南](docs/customization.md)

---

## 项目结构

```
aipokerjudge/
├── games/          # 游戏模块（可扩展）
│   └── doudizhu/   # 斗地主引擎
│       ├── deck.py     # 发牌与牌堆管理
│       ├── engine.py   # DouDiZhuEngine 游戏状态机
│       ├── models.py   # 数据模型
│       └── rules.py    # 牌型识别与比较
├── model/          # AI 模型集成
│   ├── client.py   # OpenAI 兼容 API 客户端
│   ├── parser.py   # LLM 输出解析器
│   └── prompts.py  # 决策提示词构建
├── report/
│   └── generator.py  # HTML 报表生成器
├── runner/
│   ├── batch_runner.py    # 核心批量运行器
│   ├── blackbox_runner.py # 多线程基准模式
│   └── visual_runner.py   # 荷官可视化模式
├── config.py       # 配置常量
├── cli.py          # CLI 界面
└── i18n.py         # 国际化
```

---

## 许可证

[MIT](LICENSE)
