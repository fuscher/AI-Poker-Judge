"""自定义提示词示例 - 演示如何修改提示词来改变AI的玩法风格"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_default_prompt():
    """显示默认提示词"""
    print("=" * 60)
    print("默认提示词模板")
    print("=" * 60)
    
    default_prompt = '''
你是一个斗地主玩家，现在轮到你出牌。

【你的手牌】
{hand}

【牌局信息】
{last_play_info}

【合法动作】（只能从下面选择一项）
{legal_actions}

请直接输出你选择的动作，只输出牌面（用空格分隔）或输出"不要"。
不要输出任何解释，只输出动作。

你的选择:'''
    
    print(default_prompt)
    print("\n📁 文件位置: aipokerjudge/model/prompts.py")


def print_custom_prompt_examples():
    """自定义提示词示例"""
    print("\n" + "=" * 60)
    print("自定义提示词示例")
    print("=" * 60)
    
    examples = """
【示例1：激进型玩家】
prompt = f\"\"\"
你是一个极度激进的斗地主玩家，喜欢主动出击。

手牌: {hand}
上家出牌: {last_play}
合法动作: {legal_actions}

策略要求：
1. 只要有可能就出牌，不要轻易过牌
2. 优先出大牌压制对手
3. 有炸弹就用，不要留
4. 顺子和对子优先出

只输出你要出的牌，用空格分隔。如果必须过牌，输出"不要"。
\"\"\"

【示例2：保守型玩家】
prompt = f\"\"\"
你是一个保守的斗地主玩家，精打细算。

手牌: {hand}
上家出牌: {last_play}
合法动作: {legal_actions}

策略要求：
1. 尽量保留大牌到最后
2. 能用小牌过就用小牌
3. 不要轻易出炸弹
4. 观察对手牌数，合理控制节奏

只输出你要出的牌，用空格分隔。如果必须过牌，输出"不要"。
\"\"\"

【示例3：心理战型（诈唬）】
prompt = f\"\"\"
你是一个喜欢心理战的斗地主玩家。

手牌: {hand}
上家出牌: {last_play}
合法动作: {legal_actions}

策略要求：
1. 偶尔用中等牌假装是大牌
2. 手牌少时可以出小牌诱导对手
3. 手牌多时出大牌压制
4. 让对手摸不清你的牌力

只输出你要出的牌，用空格分隔。如果必须过牌，输出"不要"。
\"\"\"
"""
    
    print(examples)


def print_implementation_guide():
    """实现指南"""
    print("\n" + "=" * 60)
    print("如何自定义提示词")
    print("=" * 60)
    
    guide = """
【方法1：修改原文件】
直接编辑 aipokerjudge/model/prompts.py 中的 build_decision_prompt 函数

【方法2：继承并覆盖】
创建自定义的提示词构建器：

from aipokerjudge.model.prompts import build_decision_prompt

def build_aggressive_prompt(state, legal_actions):
    # 自定义激进版提示词
    hand = get_hand(state)
    return f\"\"\"
你是激进玩家！手牌: {hand}
必须出牌！合法动作: {legal_actions}
输出你选的牌，不要输出解释。
\"\"\"

# 在 runner 中使用自定义提示词
# 需要修改 batch_runner.py 中的 prompt 构建调用

【方法3：配置化提示词】
在 config.py 中添加：

CUSTOM_SYSTEM_PROMPT_A = "你是保守型玩家..."
CUSTOM_SYSTEM_PROMPT_B = "你是激进型玩家..."

然后在 model/client.py 的 call 方法中拼接 system prompt

【方法4：动态切换】
在运行时根据游戏状态动态选择提示词模板
"""
    
    print(guide)


def print_test_prompt():
    """测试自定义提示词"""
    print("\n" + "=" * 60)
    print("测试自定义提示词")
    print("=" * 60)
    
    test_code = '''
# 快速测试自定义提示词效果
from aipokerjudge.model.client import ModelClient
from aipokerjudge.config import MODEL_A_NAME, MODEL_A_API_KEY, MODEL_A_BASE_URL

# 创建模型
model = ModelClient(MODEL_A_NAME, MODEL_A_API_KEY, MODEL_A_BASE_URL)

# 自定义激进提示词
aggressive_prompt = """
你是激进的斗地主玩家。
手牌: ♥3 ♥4 ♥5 ♥6 ♥7（顺子）
合法动作: 出 ♥3 或 出 ♥3 ♥4 ♥5 ♥6 ♥7
策略：有顺子就出顺子！

输出你选的牌:"""

# 调用模型
response, elapsed = model.call(aggressive_prompt)
print(f"模型决策: {response}")
print(f"耗时: {elapsed:.2f}秒")
'''
    
    print(test_code)


def main():
    print_default_prompt()
    print_custom_prompt_examples()
    print_implementation_guide()
    print_test_prompt()
    
    print("\n" + "=" * 60)
    print("💡 提示：修改 prompt 可以显著改变AI的行为风格")
    print("   建议先测试小批量对局，观察效果后再调整")
    print("=" * 60)


if __name__ == "__main__":
    main()