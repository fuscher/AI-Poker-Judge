# Customization Guide

---

## Custom Prompts

Edit the `SYSTEM_PROMPT` constant in `aipokerjudge/model/prompts.py` to change the AI's strategy instructions:

```python
# prompts.py
SYSTEM_PROMPT = """You are a Dou Di Zhu expert AI player.
Strategy tips:
1. Play high cards to suppress opponents
2. Save bombs as trump cards
3. Keep track of remaining hand size"""
```

For more complex logic, replace the `build_decision_prompt()` function:

```python
from aipokerjudge.model.prompts import build_decision_prompt as original

def my_prompt(state, legal_actions, turn_history=None):
    base = original(state, legal_actions, turn_history)
    return base + "\nAdditional hint: prioritize playing singles."
```

---

## Adding New Models

This project supports any OpenAI-compatible API. Just configure the name, key, and URL:

- **DeepSeek**: `base_url = "https://api.deepseek.com"`
- **OpenAI GPT**: `base_url = "https://api.openai.com/v1"`
- **Anthropic Claude**: via `https://api.anthropic.com/v1` (compatibility layer needed)
- **Ollama (local)**: `base_url = "http://localhost:11434/v1"`
- **LocalAI**: `base_url = "http://localhost:8080/v1"`
- **vLLM**: `base_url = "http://localhost:8000/v1"`

No new class registration required — just fill in the config values.

---

## Custom Reports

`save_report()` saves both an HTML report and raw JSON data. Use the JSON data for custom analysis:

```python
from aipokerjudge.report.generator import save_report

# After saving, two files are generated:
# - report_20260509_120000.html  (visual report)
# - data_20260509_120000.json     (raw data)
```

### JSON Data Format

```json
{
  "total_rounds": 50,
  "a_wins": 28,
  "b_wins": 22,
  "a_avg_response_ms": 1234.5,
  "b_avg_response_ms": 980.2,
  "avg_turns": 15.3,
  "a_violations": 2,
  "b_violations": 5,
  "a_total_prompt_tokens": 150000,
  "b_total_prompt_tokens": 148000,
  "game_records": [
    {
      "round_num": 1,
      "winner": "A",
      "win_reason": "normal",
      "total_turns": 12,
      "turns_detail": [...]
    }
  ]
}
```

For a completely custom HTML template, modify `generate_report()` in `generator.py`.

---

## Custom Dealing

Specify custom hands in dealer mode:

```python
from aipokerjudge.game.deck import create_state_with_hands

state = create_state_with_hands(
    hand_a=["♥3", "♥4", "♥5", "♥6", "♥7"],  # A's straight
    hand_b=["♠A", "♠2"]                        # B's hand
)
```

In dealer mode (`run_visual_mode`), you can also input custom hands interactively before each round.

---

## Adding New Runner Modes

Follow the structure of existing runners (`visual_runner.py`, `blackbox_runner.py`):

1. Create a new module in `aipokerjudge/runner/`
2. Implement an entry function that accepts a `BatchRunner` instance and parameters
3. Export it in `aipokerjudge/runner/__init__.py`
4. Add a new menu option in `cli.py`

---

## Internationalization

The project has built-in bilingual support (Chinese/English). To add a new language, edit the `_STRINGS` dictionary in `aipokerjudge/i18n.py`:

```python
_STRINGS = {
    "zh": {
        "welcome": "欢迎使用 AI 斗地主裁判",
        ...
    },
    "en": {
        "welcome": "Welcome to AI Poker Judge",
        ...
    },
    # Add new language here
}
```

Use `t("welcome")` in code to get the translation for the current language.
