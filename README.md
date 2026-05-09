# AI-Poker-Judge

> AI vs AI Poker battle platform — Benchmark LLM decision-making, rule adherence & performance.

[简体中文](README.cn.md) | [English](README.md)

---

## Overview

AI-Poker-Judge is a simplified 1v1 Dou Di Zhu testing framework that pits two AI models against each other. It evaluates LLMs on strategic reasoning, rule compliance, and response speed. Supports any OpenAI-compatible API (DeepSeek, GPT, Claude, Ollama, etc.).

---

## Features

- **1v1 Simplified Dou Di Zhu** — No bidding phase, no jokers, pure card-play strategy
- **Multi-Model Support** — Any OpenAI-compatible API (DeepSeek, GPT, Claude, Ollama, vLLM)
- **Two Running Modes** — Dealer mode (step-by-step visualization) & Benchmark mode (multi-threaded batch testing)
- **Rich Reports** — Auto-generated HTML reports with Chart.js visualizations (bilingual)
- **Bilingual CLI** — Chinese/English switchable interface
- **Position Swap & Deal Normalization** — Eliminate first/second player bias for fair A/B comparison
- **Detailed Logging** — Per-round JSON logs with response times, token usage, violation tracking

---

## Quick Start

```bash
pip install -r requirements.txt
python -m aipokerjudge
```

---

## Configuration

Edit `aipokerjudge/config.py` or set environment variables. Key settings:

| Setting | Env Variable | Default | Description |
|---|---|---|---|
| `MODEL_A_API_KEY` | `MODEL_A_API_KEY` | `""` | Model A API key |
| `MODEL_A_BASE_URL` | `MODEL_A_BASE_URL` | `https://api.deepseek.com` | Model A API base URL |
| `MODEL_A_NAME` | `MODEL_A_NAME` | `deepseek-chat` | Model A name |

The same applies to Model B (`MODEL_B_*`). Both models can use different providers for A/B testing.

📖 [Full Configuration Guide](docs/configuration.en.md)

---

## Usage

```bash
python -m aipokerjudge
```

Interactive menu:
- `[1]` **Dealer Mode** — Watch AI decisions in real-time, step by step
- `[2]` **Benchmark** — Multi-threaded batch testing with progress bar
- `[3]` **Configuration** — Adjust models, rounds, threads, etc.
- `[4]` **Toggle Language** — Switch between Chinese / English
- `[0]` **Exit**

---

## API Reference

Key classes and functions:

| Module | Key Exports |
|---|---|
| `aipokerjudge.game.engine` | `DouDiZhuEngine` |
| `aipokerjudge.game.models` | `GameState`, `GameStatus`, `TurnRecord` |
| `aipokerjudge.game.rules` | `identify_play_type`, `can_beat`, `generate_all_possible_plays` |
| `aipokerjudge.model.client` | `ModelClient` |
| `aipokerjudge.model.parser` | `parse_action` |
| `aipokerjudge.model.prompts` | `build_decision_prompt` |
| `aipokerjudge.runner.batch_runner` | `BatchRunner`, `GameRecord`, `BatchResult` |
| `aipokerjudge.report.generator` | `generate_report`, `save_report` |

📖 [Full API Reference](docs/api.en.md)

---

## Customization

- **Custom Prompts** — Edit `SYSTEM_PROMPT` in `prompts.py` or replace `build_decision_prompt()`
- **New Models** — Any OpenAI-compatible API works out of the box
- **Custom Reports** — Raw JSON data available for secondary analysis
- **New Runners** — Follow the pattern in `visual_runner.py` / `blackbox_runner.py`
- **i18n** — Add new languages in `i18n.py`

📖 [Customization Guide](docs/customization.en.md)

---

## Project Structure

```
aipokerjudge/
├── game/           # Engine: deck, rules, card patterns
│   ├── deck.py     # Card dealing & deck management
│   ├── engine.py   # DouDiZhuEngine
│   ├── models.py   # Data models
│   └── rules.py    # Card pattern recognition & comparison
├── model/          # AI model integration
│   ├── client.py   # OpenAI-compatible API client
│   ├── parser.py   # LLM output parser
│   └── prompts.py  # Decision prompt builder
├── report/
│   └── generator.py  # HTML report generator
├── runner/
│   ├── batch_runner.py    # Core batch runner
│   ├── blackbox_runner.py # Multi-threaded benchmark mode
│   └── visual_runner.py   # Dealer visualization mode
├── config.py       # Configuration constants
├── cli.py          # CLI interface
└── i18n.py         # Internationalization
```

---

## License

[MIT](LICENSE)
