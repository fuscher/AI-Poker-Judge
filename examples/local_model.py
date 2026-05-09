"""本地模型示例 - 使用 Ollama / LocalAI 等本地服务的示例"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_config_instructions():
    """打印本地模型配置说明"""
    print("=" * 60)
    print("本地模型配置指南")
    print("=" * 60)
    
    print("""
本示例展示如何配置使用本地模型（如 Ollama、LocalAI、vLLM 等）。

【1. 安装 Ollama】（推荐）
   - 访问 https://ollama.ai 下载安装
   - 拉取模型: ollama pull llama3
   - 启动服务: ollama serve (默认端口 11434)

【2. 修改 config.py】
   将以下配置添加到你的 config.py 中：

   # 模型A使用本地模型
   MODEL_A_NAME = "llama3"
   MODEL_A_API_KEY = "ollama"  # 任意非空字符串
   MODEL_A_BASE_URL = "http://localhost:11434/v1"

   # 模型B也可以使用另一个本地模型
   MODEL_B_NAME = "qwen2:7b"
   MODEL_B_API_KEY = "ollama"
   MODEL_B_BASE_URL = "http://localhost:11434/v1"

【3. 支持的其他本地服务】

   | 服务 | Base URL | 说明 |
   |------|----------|------|
   | Ollama | http://localhost:11434/v1 | 最简单，推荐 |
   | LocalAI | http://localhost:8080/v1 | 功能丰富 |
   | vLLM | http://localhost:8000/v1 | 高性能推理 |
   | LM Studio | http://localhost:1234/v1 | GUI界面 |

【4. 验证配置】
   运行以下命令测试连接：

   curl http://localhost:11434/v1/models

【5. 运行测试】
   python -m aipokerjudge

【注意事项】
   - 本地模型响应速度取决于硬件配置
   - 建议使用至少 8GB 显存的 GPU
   - 首次运行会下载模型，需耐心等待
""")


def example_custom_client():
    """自定义客户端示例"""
    print("\n" + "=" * 60)
    print("自定义本地模型客户端示例")
    print("=" * 60)
    
    code_example = '''
from aipokerjudge.model.client import ModelClient

# 创建本地模型客户端
local_model = ModelClient(
    model_name="llama3",
    api_key="ollama",  # 任意值
    base_url="http://localhost:11434/v1"
)

# 测试调用
response, elapsed = local_model.call("你好，请简单介绍一下自己")
print(f"响应: {response}")
print(f"耗时: {elapsed:.2f}秒")
'''
    
    print(code_example)


def example_openai_compatible():
    """OpenAI兼容服务示例"""
    print("\n" + "=" * 60)
    print("其他 OpenAI 兼容服务示例")
    print("=" * 60)
    
    examples = """
# Groq (高速推理)
MODEL_NAME = "llama3-70b-8192"
API_KEY = "your-groq-api-key"
BASE_URL = "https://api.groq.com/openai/v1"

# Together.ai
MODEL_NAME = "meta-llama/Llama-3-70b-chat-hf"
API_KEY = "your-together-api-key"
BASE_URL = "https://api.together.xyz/v1"

# DeepSeek
MODEL_NAME = "deepseek-chat"
API_KEY = "your-deepseek-api-key"
BASE_URL = "https://api.deepseek.com/v1"

# 国内模型 (需要API Key)
# 智谱 GLM-4
MODEL_NAME = "glm-4"
API_KEY = "your-zhipu-api-key"
BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

# 百度文心
MODEL_NAME = "ernie-3.5"
API_KEY = "your-baidu-api-key"
BASE_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
"""
    
    print(examples)


def main():
    print_config_instructions()
    example_custom_client()
    example_openai_compatible()


if __name__ == "__main__":
    main()