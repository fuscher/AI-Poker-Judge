# AI-Poker-Judge

AI vs AI 斗地主对战平台，用于测试 LLM 的决策能力、规则遵循度和性能。

支持任何兼容 OpenAI 格式的 API（DeepSeek、GPT、Claude、Ollama/LocalAI 等）。

## 快速开始

```bash
pip install -r requirements.txt
python -m aipokerjudge
```

## 配置

编辑 `aipokerjudge/config.py` 或设置环境变量：

| 变量 | 说明 | 默认值 |
|---|---|---|
| `MODEL_A_API_KEY` | 模型A API密钥 | `OPENAI_API_KEY` 或 `""` |
| `MODEL_A_BASE_URL` | 模型A API地址 | `OPENAI_BASE_URL` 或 `https://api.deepseek.com` |
| `MODEL_A_NAME` | 模型A名称 | `deepseek-chat` |
| `MODEL_B_*` | 模型B配置（同上） | 同上 |

## 运行模式

- **荷官模式** (`python -m aipokerjudge dealer`)：逐步可视化对局
- **基准模式** (`python -m aipokerjudge benchmark`)：多线程黑盒批量测试
- **交互模式** (`python -m aipokerjudge`)：CLI交互选择

## 项目结构

```
aipokerjudge/
├── game/          # 游戏引擎（牌堆、规则、牌型）
├── model/         # AI模型客户端与提示词
├── report/        # HTML报表生成
└── runner/        # 运行器（批量、黑盒、可视化）
```

## License

MIT
