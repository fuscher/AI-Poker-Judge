# 自定义扩展指南

---

## 自定义提示词

编辑 `aipokerjudge/model/prompts.py` 中的 `SYSTEM_PROMPT` 常量即可修改 AI 的策略指令：

```python
# prompts.py
SYSTEM_PROMPT = """你是一个精通斗地主的AI玩家。
策略要点：
1. 尽量出大牌压制对手
2. 保留炸弹作为杀手锏
3. 注意控制手牌数量"""
```

如需更复杂的逻辑，可替换 `build_decision_prompt()` 函数：

```python
from aipokerjudge.model.prompts import build_decision_prompt as original

def my_prompt(state, legal_actions, turn_history=None):
    base = original(state, legal_actions, turn_history)
    return base + "\n额外提示：请优先出单张。"
```

---

## 添加新模型

本项目支持任何兼容 OpenAI 格式的 API。只需在配置中设置对应的名称、密钥和地址：

- **DeepSeek**：`base_url = "https://api.deepseek.com"`
- **OpenAI GPT**：`base_url = "https://api.openai.com/v1"`
- **Anthropic Claude**：通过 `https://api.anthropic.com/v1`（需兼容层）
- **Ollama 本地模型**：`base_url = "http://localhost:11434/v1"`
- **LocalAI**：`base_url = "http://localhost:8080/v1"`
- **vLLM**：`base_url = "http://localhost:8000/v1"`

无需注册新类，直接在配置中填写即可。

---

## 自定义报表

`save_report()` 函数会同时保存 HTML 报表和 JSON 原始数据。你可直接使用 JSON 数据进行二次分析：

```python
from aipokerjudge.report.generator import save_report

# 保存后，在 output_dir 中会生成两个文件：
# - report_20260509_120000.html  (可视化报表)
# - data_20260509_120000.json     (原始数据)
```

### JSON 数据格式

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

如需完全自定义 HTML 模板，可直接修改 `generator.py` 中的 `generate_report()` 函数。

---

## 自定义发牌

在荷官模式下可手动指定手牌：

```python
from aipokerjudge.game.deck import create_state_with_hands

state = create_state_with_hands(
    hand_a=["♥3", "♥4", "♥5", "♥6", "♥7"],  # A 的顺子
    hand_b=["♠A", "♠2"]                        # B 的牌
)
```

也可在运行荷官模式时，在每局开始前按提示输入自定义手牌。

---

## 添加新运行模式

参考现有运行器（`visual_runner.py`、`blackbox_runner.py`）的结构：

1. 在 `aipokerjudge/runner/` 下创建新模块
2. 实现入口函数，接收 `BatchRunner` 实例和参数
3. 在 `aipokerjudge/runner/__init__.py` 中导出
4. 在 `cli.py` 的菜单中添加新选项

---

## 国际化

项目内置中英文双语支持。如需添加新语言的翻译，编辑 `aipokerjudge/i18n.py` 中的 `_STRINGS` 字典：

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
    # 在此添加新语言
}
```

在代码中使用 `t("welcome")` 获取当前语言的翻译。
