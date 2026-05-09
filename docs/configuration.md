# 配置说明

## 配置文件

项目支持通过 YAML 文件或代码传参配置。

### YAML 配置示例

```yaml
model:
  name: gpt-4o
  api_base: https://api.openai.com/v1
  api_key: sk-xxx
  temperature: 0.7
  max_tokens: 512
  timeout: 30

game:
  num_players: 3
  max_rounds: 100
  shuffle_seed: 42
  verbose: false

log_level: INFO
log_file: logs/poker_judge.log
```

## 模型配置 (`ModelConfig`)

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | `gpt-4o` | 模型名称 |
| `api_base` | str | `https://api.openai.com/v1` | API 地址 |
| `api_key` | str | `""` | API 密钥 |
| `temperature` | float | `0.7` | 生成温度 |
| `max_tokens` | int | `512` | 最大输出 token |
| `timeout` | int | `30` | 超时秒数 |

## 游戏配置 (`GameConfig`)

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `num_players` | int | `3` | 玩家数（固定3） |
| `max_rounds` | int | `100` | 最大回合数 |
| `shuffle_seed` | int | `None` | 洗牌种子 |
| `verbose` | bool | `False` | 详细日志 |
