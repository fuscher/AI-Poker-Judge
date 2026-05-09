# Configuration Guide

All configuration is done by editing `aipokerjudge/config.py` or setting environment variables — no YAML files needed.

---

## Model Configuration

### Model A

| Setting | Env Variable | Default | Description |
|---|---|---|---|
| `MODEL_A_NAME` | `MODEL_A_NAME` | `"deepseek-chat"` | Model name |
| `MODEL_A_API_KEY` | `MODEL_A_API_KEY` | `""` (falls back to `OPENAI_API_KEY`) | API key |
| `MODEL_A_BASE_URL` | `MODEL_A_BASE_URL` | `"https://api.deepseek.com"` (falls back to `OPENAI_BASE_URL`) | API base URL |

### Model B

| Setting | Env Variable | Default | Description |
|---|---|---|---|
| `MODEL_B_NAME` | `MODEL_B_NAME` | `"deepseek-chat"` | Model name |
| `MODEL_B_API_KEY` | `MODEL_B_API_KEY` | `""` (falls back to `OPENAI_API_KEY`) | API key |
| `MODEL_B_BASE_URL` | `MODEL_B_BASE_URL` | `"https://api.deepseek.com"` (falls back to `OPENAI_BASE_URL`) | API base URL |

> Both models can use different APIs for A/B comparison testing. E.g., Model A uses DeepSeek, Model B uses GPT-4o.

---

## Game Configuration

| Setting | Default | Description |
|---|---|---|
| `TIMEOUT_SECONDS` | `60` | Model response timeout (seconds); timeout = loss |
| `MAX_TURNS_PER_GAME` | `100` | Max turns per round; exceeding = draw |
| `DEFAULT_ROUNDS` | `50` | Default number of rounds |
| `DEFAULT_SEED` | `42` | Random seed (`None` for true random) |
| `POSITION_SWAP` | `True` | Position swapping: swap first/second player on even rounds to eliminate positional bias |
| `DEAL_NORMALIZATION` | `True` | Deal normalization: adjacent rounds use same hands with swapped positions to eliminate deal bias |

---

## Report Configuration

| Setting | Default | Description |
|---|---|---|
| `REPORT_OUTPUT_DIR` | `"reports"` | Report output directory |
| `SAVE_DETAIL_LOGS` | `True` | Whether to save detailed JSON logs |
| `BLACKBOX_WORKERS` | `3` | Number of parallel threads for blackbox mode |

---

## Card Configuration

| Setting | Default | Description |
|---|---|---|
| `CARD_RANKS` | `['3','4','5','6','7','8','9','10','J','Q','K','A','2']` | Card rank ordering |
| `PLAY_TYPE_PRIORITY` | `{'single':1, 'pair':2, 'triplet':3, 'triplet_with_one':4, 'straight':5, 'bomb':10}` | Play type priority (for strategy sorting) |

---

## Using Environment Variables

Override settings via environment variables — useful for CI/CD or when you don't want to modify code:

```bash
# Linux/macOS
export MODEL_A_API_KEY="sk-xxx"
export MODEL_A_BASE_URL="https://api.openai.com/v1"
export MODEL_A_NAME="gpt-4o"

# Windows (PowerShell)
$env:MODEL_A_API_KEY = "sk-xxx"
$env:MODEL_A_BASE_URL = "https://api.openai.com/v1"
$env:MODEL_A_NAME = "gpt-4o"
```

You can also use a `.env` file — the framework reads it via `os.getenv()`.

---

## Common Configuration Examples

### DeepSeek vs GPT-4o

```python
# In config.py
MODEL_A_NAME = "deepseek-chat"
MODEL_A_API_KEY = "sk-deepseek-key"
MODEL_A_BASE_URL = "https://api.deepseek.com"

MODEL_B_NAME = "gpt-4o"
MODEL_B_API_KEY = "sk-openai-key"
MODEL_B_BASE_URL = "https://api.openai.com/v1"
```

### Two Local Models (Ollama)

```python
MODEL_A_NAME = "qwen2.5:7b"
MODEL_A_API_KEY = "ollama"  # Ollama doesn't verify keys
MODEL_A_BASE_URL = "http://localhost:11434/v1"

MODEL_B_NAME = "llama3.1:8b"
MODEL_B_API_KEY = "ollama"
MODEL_B_BASE_URL = "http://localhost:11434/v1"
```
