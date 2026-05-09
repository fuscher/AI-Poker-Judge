"""OpenAI格式模型客户端"""

import time
from typing import Optional, Tuple, Dict
from openai import OpenAI

from aipokerjudge.config import TIMEOUT_SECONDS
from ..i18n import t


class ModelClient:
    """通用OpenAI格式模型客户端，支持GPT、Claude、本地模型等"""

    def __init__(self, model_name: str, api_key: str, base_url: str = None, timeout: int = None):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self.timeout = timeout or TIMEOUT_SECONDS

        self.client = OpenAI(
            api_key=api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

    def check_connection(self) -> bool:
        """发送测试消息验证 API 连通性（含 system prompt，模拟游戏场景）"""
        try:
            from .prompts import SYSTEM_PROMPT
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": "收到请回复 ok"}
                ],
                max_tokens=5
            )
            content = response.choices[0].message.content
            return bool(content and content.strip())
        except Exception:
            return False

    def call(self, prompt: str, temperature: float = 0.7, max_tokens: int = 30) -> Tuple[Optional[str], float, Optional[Dict]]:
        """
        调用模型（非流式，数字索引场景输出极小）
        返回: (响应内容, 耗时秒数, usage字典 或 None)
        """
        from .prompts import SYSTEM_PROMPT
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            elapsed = time.time() - start_time
            content = response.choices[0].message.content
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            return content, elapsed, usage
        except Exception as e:
            elapsed = time.time() - start_time
            print(t("api_error", name=self.model_name, e=e))
            return None, elapsed, None

    def __repr__(self):
        return f"ModelClient(model={self.model_name}, base_url={self.base_url})"
