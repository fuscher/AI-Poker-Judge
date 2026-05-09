# 配置说明

本项目的配置通过编辑 `aipokerjudge/config.py` 或设置环境变量完成，无需 YAML 文件。

---

## 模型配置

### 模型 A

| 配置项 | 环境变量 | 默认值 | 说明 |
|---|---|---|---|
| `MODEL_A_NAME` | `MODEL_A_NAME` | `"deepseek-chat"` | 模型名称 |
| `MODEL_A_API_KEY` | `MODEL_A_API_KEY` | `""`（回退 `OPENAI_API_KEY`） | API 密钥 |
| `MODEL_A_BASE_URL` | `MODEL_A_BASE_URL` | `"https://api.deepseek.com"`（回退 `OPENAI_BASE_URL`） | API 地址 |

### 模型 B

| 配置项 | 环境变量 | 默认值 | 说明 |
|---|---|---|---|
| `MODEL_B_NAME` | `MODEL_B_NAME` | `"deepseek-chat"` | 模型名称 |
| `MODEL_B_API_KEY` | `MODEL_B_API_KEY` | `""`（回退 `OPENAI_API_KEY`） | API 密钥 |
| `MODEL_B_BASE_URL` | `MODEL_B_BASE_URL` | `"https://api.deepseek.com"`（回退 `OPENAI_BASE_URL`） | API 地址 |

> 两个模型可以设为不同的 API，用于 A/B 对比测试。例如模型 A 用 DeepSeek，模型 B 用 GPT-4o。

---

## 游戏配置

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `TIMEOUT_SECONDS` | `60` | 模型响应超时（秒），超时判负 |
| `MAX_TURNS_PER_GAME` | `100` | 单局最大回合数，达到则判平 |
| `DEFAULT_ROUNDS` | `50` | 默认对局轮次 |
| `DEFAULT_SEED` | `42` | 默认随机种子（`None` 表示真随机） |
| `POSITION_SWAP` | `True` | 位置轮换：偶数局交换先手/后手，消除先后手偏差 |
| `DEAL_NORMALIZATION` | `True` | 发牌归一化：相邻两局用同一手牌并交换位置，消除发牌偏差 |

---

## 报表配置

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `REPORT_OUTPUT_DIR` | `"reports"` | 报表输出目录 |
| `SAVE_DETAIL_LOGS` | `True` | 是否保存 JSON 格式详细日志 |
| `BLACKBOX_WORKERS` | `3` | 黑盒模式并行线程数 |

---

## 牌型配置

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `CARD_RANKS` | `['3','4','5','6','7','8','9','10','J','Q','K','A','2']` | 牌面点数排序 |
| `PLAY_TYPE_PRIORITY` | `{'single':1, 'pair':2, 'triplet':3, 'triplet_with_one':4, 'straight':5, 'bomb':10}` | 牌型优先级（出牌策略排序用） |

---

## 环境变量方式

可通过环境变量覆盖配置，适合 CI/CD 或不想修改代码的场景：

```bash
# Windows (PowerShell)
$env:MODEL_A_API_KEY = "sk-xxx"
$env:MODEL_A_BASE_URL = "https://api.openai.com/v1"
$env:MODEL_A_NAME = "gpt-4o"

# Linux/macOS
export MODEL_A_API_KEY="sk-xxx"
export MODEL_A_BASE_URL="https://api.openai.com/v1"
export MODEL_A_NAME="gpt-4o"
```

也可在 `.env` 文件中设置，框架会通过 `os.getenv()` 读取。

---

## 常见配置示例

### DeepSeek vs GPT-4o

```python
# config.py 中修改
MODEL_A_NAME = "deepseek-chat"
MODEL_A_API_KEY = "sk-deepseek-key"
MODEL_A_BASE_URL = "https://api.deepseek.com"

MODEL_B_NAME = "gpt-4o"
MODEL_B_API_KEY = "sk-openai-key"
MODEL_B_BASE_URL = "https://api.openai.com/v1"
```

### 两个本地模型对比（Ollama）

```python
MODEL_A_NAME = "qwen2.5:7b"
MODEL_A_API_KEY = "ollama"  # Ollama 不验证 key
MODEL_A_BASE_URL = "http://localhost:11434/v1"

MODEL_B_NAME = "llama3.1:8b"
MODEL_B_API_KEY = "ollama"
MODEL_B_BASE_URL = "http://localhost:11434/v1"
```
