"""
Day 1 — 第一个 LLM API 调用

DeepSeek API 兼容 OpenAI SDK，只需改 base_url 和 api_key。
"""

import sys
sys.path.insert(0, ".")  # noqa

from openai import OpenAI
from src.config import Config

# 用 OpenAI SDK 连接 DeepSeek
client = OpenAI(
    api_key=Config.DEEPSEEK_API_KEY,
    base_url=Config.DEEPSEEK_BASE_URL,
)

# 最简单的调用
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个 Python 编程助手"},
        {"role": "user", "content": "用一句话解释什么是闭包"},
    ],
)

# response.choices[0].message 就是 Assistant 的回复
reply = response.choices[0].message
# print(response)  # 可以打印完整响应看看结构   

print(f"role: {reply.role}")
print(f"content: {reply.content}")
print(f"token 用量: {response.usage}")
