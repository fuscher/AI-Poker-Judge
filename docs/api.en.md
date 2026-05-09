# API Reference

## Module Structure

```
aipokerjudge/
├── game/              # Game engine
│   ├── engine.py      # DouDiZhuEngine
│   ├── models.py      # GameState, GameStatus, TurnRecord
│   ├── deck.py        # Deck, dealing utilities
│   └── rules.py       # Card pattern recognition & comparison
├── model/             # AI model
│   ├── client.py      # ModelClient (OpenAI-compatible)
│   ├── parser.py      # parse_action (LLM output parser)
│   └── prompts.py     # build_decision_prompt
├── report/
│   └── generator.py   # generate_report, save_report
└── runner/
    ├── batch_runner.py     # BatchRunner, GameRecord, BatchResult
    ├── blackbox_runner.py  # run_blackbox_mode
    └── visual_runner.py    # run_visual_mode
```

---

## Game Engine — `aipokerjudge.game`

### `DouDiZhuEngine`

Simplified 1v1 Dou Di Zhu game state machine (no bidding phase).

```python
from aipokerjudge import DouDiZhuEngine

engine = DouDiZhuEngine(seed=42)
```

| Method | Returns | Description |
|---|---|---|
| `create_state()` | `GameState` | Create a new game state with random deal |
| `get_legal_actions(state)` | `list[list[str]]` | Get legal actions; `[[]]` means pass only |
| `apply_action(state, cards)` | `GameState` | Execute action (`[]` = pass), returns new state |
| `get_current_player_hand(state)` | `list[str]` | Get current player's hand |
| `is_game_over(state)` | `bool` | Check if game is over |
| `get_winner(state)` | `str \| None` | Returns `"A"` or `"B"`, or `None` if ongoing |
| `format_hand(hand)` (static) | `str` | Format hand as space-separated string |

### Data Models

**`GameState`:**

| Field | Type | Description |
|---|---|---|
| `player_a_hand` | `list[str]` | Player A's hand (e.g. `["♥3", "♠5"]`) |
| `player_b_hand` | `list[str]` | Player B's hand |
| `current_player` | `str` | `"A"` or `"B"` |
| `last_play` | `tuple \| None` | `(player, play_type, cards)` |
| `last_play_value` | `int` | Comparison value of last play |
| `turn_count` | `int` | Current turn number |
| `game_status` | `GameStatus` | Game status |

**`GameStatus` (enum):** `ONGOING` / `A_WIN` / `B_WIN`

**`TurnRecord` (dataclass):**

| Field | Type | Description |
|---|---|---|
| `turn` | `int` | Turn number |
| `player` | `str` | `"A"` or `"B"` |
| `action` | `str` | Action description ("Play ♥3" / "Pass") |
| `cards` | `list[str]` | Cards played |
| `response_time_ms` | `int` | Response time in ms |
| `is_valid` | `bool` | Whether the action was legal |
| `hand_before` | `list[str]` | Hand before play |
| `hand_after` | `list[str]` | Hand after play |

### Card Pattern Rules

| Function | Returns | Description |
|---|---|---|
| `parse_rank(card)` | `str` | Extract rank from card (`"♥3"` -> `"3"`) |
| `get_card_value(card)` | `int` | Get numeric comparison value |
| `identify_play_type(cards)` | `str \| None` | Identify pattern: `single`, `pair`, `triplet`, `triplet_with_one`, `straight`, `bomb` |
| `get_play_value(play_type, cards)` | `int` | Get base comparison value (bomb auto +100) |
| `can_beat(last_play, current_cards)` | `bool` | Check if current play beats the last |
| `generate_all_possible_plays(hand)` | `list[list[str]]` | Generate all legal plays (deduplicated, strategy-sorted) |

### Deck Utilities

| Function | Returns | Description |
|---|---|---|
| `create_initial_state(seed)` | `GameState` | Create initial state with random deal |
| `create_state_with_hands(hand_a, hand_b)` | `GameState` | Create state with custom hands |
| `generate_deal_pairs(n_pairs, base_seed)` | `list` | Generate deal pairs for normalization |
| `validate_custom_deal(hand_a, hand_b)` | `str \| None` | Validate custom hand legality |

---

## AI Model — `aipokerjudge.model`

### `ModelClient`

OpenAI-compatible API client.

```python
from aipokerjudge import ModelClient

client = ModelClient(
    model_name="deepseek-chat",
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
    timeout=60
)
```

| Method | Returns | Description |
|---|---|---|
| `check_connection()` | `bool` | Test API connectivity |
| `call(prompt, temperature=0.7, max_tokens=30)` | `(content, elapsed_secs, usage)` | Call model; returns (response_text, elapsed_seconds, token_usage_dict) |

**usage dict fields:** `prompt_tokens`, `completion_tokens`, `total_tokens`

### `parse_action(response, legal_actions)`

Parse LLM output into a game action. Match priority: numeric index > pass keywords > card regex. Returns `list[str]` (cards), `[]` (pass), or `None` (failure).

### `build_decision_prompt(state, legal_actions, turn_history=None)`

Build AI decision prompt with hand info, game state, numbered legal actions, and up to 8 turns of history.

---

## Batch Runner — `aipokerjudge.runner`

### `BatchRunner`

```python
from aipokerjudge import BatchRunner

runner = BatchRunner(model_a, model_b)
```

| Method | Returns | Description |
|---|---|---|
| `run_one_round(round_num, seed, verbose, preset_hands)` | `GameRecord` | Play a single round |
| `run_batch(rounds, seed, verbose, on_progress, do_swap)` | `BatchResult` | Run multiple rounds in batch |

### Runner Modes

| Function | Description |
|---|---|
| `run_visual_mode(runner, rounds, seed, do_swap)` | Dealer mode: step-by-step visualization with custom deal support |
| `run_blackbox_mode(runner, rounds, seed, max_workers, do_swap)` | Benchmark mode: multi-threaded parallel execution with progress bar |

### `GameRecord` (dataclass)

| Field | Type | Description |
|---|---|---|
| `round_num` | `int` | Round number |
| `winner` | `str` | `"A"` or `"B"` |
| `win_reason` | `str` | Win reason |
| `total_turns` | `int` | Total turns |
| `a_violations` / `b_violations` | `int` | Violation count |
| `a_timeouts` / `b_timeouts` | `int` | Timeout count |
| `a_total_response_ms` / `b_total_response_ms` | `int` | Total response time |
| `a_pass_count` / `b_pass_count` | `int` | Pass count |
| `a_bomb_count` / `b_bomb_count` | `int` | Bomb count |
| `a_prompt_tokens` / `b_prompt_tokens` | `int` | Input tokens |
| `a_completion_tokens` / `b_completion_tokens` | `int` | Output tokens |
| `turns_detail` | `list[TurnRecord]` | Turn details |

**Win reasons:**

| Value | Description |
|---|---|
| `"normal"` | All cards played out |
| `"violation"` | Opponent made an illegal move |
| `"timeout"` | Opponent response timeout |
| `"error"` | Opponent API error |
| `"max_turns"` | Reached maximum turn limit |

### `BatchResult` (dataclass)

| Field | Type | Description |
|---|---|---|
| `total_rounds` | `int` | Total rounds |
| `a_wins` / `b_wins` | `int` | Wins count |
| `a_violations` / `b_violations` | `int` | Total violations |
| `a_timeouts` / `b_timeouts` | `int` | Total timeouts |
| `a_avg_response_ms` / `b_avg_response_ms` | `float` | Average response time |
| `avg_turns` | `float` | Average turns per round |
| `a_response_p50` / `b_response_p50` | `float` | Median response time |
| `a_response_p95` / `b_response_p95` | `float` | P95 response time |
| `a_total_prompt_tokens` / `b_total_prompt_tokens` | `int` | Total input tokens |
| `a_total_completion_tokens` / `b_total_completion_tokens` | `int` | Total output tokens |
| `a_wins_as_first` / `a_wins_as_second` | `int` | Wins as first/second player |
| `b_wins_as_first` / `b_wins_as_second` | `int` | Wins as first/second player |
| `elapsed_seconds` | `float` | Total elapsed time |
| `game_records` | `list[GameRecord]` | All game records |
| `start_time` / `end_time` | `str` | ISO format timestamps |

---

## Reports — `aipokerjudge.report`

| Function | Returns | Description |
|---|---|---|
| `generate_report(result, model_a_name, model_b_name)` | `str` | Generate full HTML report with Chart.js (bilingual) |
| `save_report(result, model_a_name, model_b_name, output_dir="reports")` | `str` | Save HTML report and JSON data, returns file path |

---

## CLI

```bash
python -m aipokerjudge
```

Interactive menu:
- `[1]` **Dealer Mode** — step-by-step gameplay, watch LLM decisions live
- `[2]` **Benchmark** — multi-threaded batch testing, generates report on completion
- `[3]` **Configuration** — model settings, rounds, threads, etc.
- `[4]` **Toggle Language** — switch between Chinese/English
- `[0]` **Exit**
