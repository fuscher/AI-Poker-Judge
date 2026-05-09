# 自定义扩展指南

## 自定义提示词

继承 `PromptTemplates` 并重写方法：

```python
from aipokerjudge.model.prompts import PromptTemplates

class MyPrompts(PromptTemplates):
    @staticmethod
    def system_prompt() -> str:
        return "你是一个谨慎的斗地主AI..."
```

## 添加新模型

通过 `ModelFactory` 注册：

```python
from aipokerjudge.model.factory import ModelFactory
from aipokerjudge.model.client import ModelClient

ModelFactory.register("my-model", ModelClient)
```

## 自定义报表

继承 `ReportGenerator` 添加自定义格式。

## 添加新运行模式

在 `aipokerjudge.runner` 中创建新类，实现 `run()` 方法，
然后在 `cli.py` 中注册为新的 Click 命令。
