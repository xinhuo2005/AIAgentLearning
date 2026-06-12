"""
Day 1 — Tool Calling（函数调用）

LLM 本身不会查天气、不会算时间、不会读文件。
但你可以给 LLM 配一些"工具函数"，它需要时会告诉你调用哪个函数、传什么参数。
你执行完把结果返回给它，它再基于结果回答用户。

这就是 Agent 的核心能力：感知（收到结果）→ 决策（选工具）→ 行动（调函数）
"""
import sys
sys.path.insert(0, ".")  # noqa

import json
from openai import OpenAI
from src.config import Config

client = OpenAI(
    api_key=Config.DEEPSEEK_API_KEY,
    base_url=Config.DEEPSEEK_BASE_URL,
)


# ============================================================
# 定义工具：普通 Python 函数 + 描述文档
# ============================================================

def get_weather(city: str):
    """查询指定城市的天气（模拟）"""
    # 真实场景这里会调天气 API
    weather_data = {
        "北京": "晴，25°C，湿度 40%",
        "上海": "多云，28°C，湿度 65%",
        "深圳": "阵雨，30°C，湿度 80%",
    }
    return weather_data.get(city, f"没查到 {city} 的天气")


def calculator(expression: str):
    """计算数学表达式"""
    try:
        return str(eval(expression))  # 仅演示，生产环境别用 eval
    except Exception as e:
        return f"计算出错: {e}"


# ============================================================
# 用 JSON Schema 描述工具（LLM 通过这个理解工具的用途和参数）
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，如 北京"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，如 123*456",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"],
            },
        },
    },
]

# 函数名 → 实际函数 的映射
tool_map = {
    "get_weather": get_weather,
    "calculator": calculator,
}

# ============================================================
# 核心循环：用户提问 → LLM 决定是否调工具 → 执行 → 回到 LLM → 最终回答
# ============================================================

user_question = "我想要计算一下 134 * 100，顺便问一下北京的天气怎么样，跟深圳比怎么样"
print(f"用户: {user_question}\n")

messages = [{"role": "user", "content": user_question}]

# 第一轮：发给 LLM，LLM 决定是否需要调工具
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
)
msg = response.choices[0].message
print(msg)

# 检查 LLM 是否想调工具
if msg.tool_calls:
    print(f"LLM 决定调用 {len(msg.tool_calls)} 个工具:\n")

    # 把 LLM 的回复加入对话历史
    messages.append(msg)

    for tc in msg.tool_calls:
        func_name = tc.function.name
        func_args = json.loads(tc.function.arguments)
        print(f"  → {func_name}({func_args})")

        # 执行工具
        result = tool_map[func_name](**func_args)
        print(f"  ← 返回: {result}")

        # 把工具执行结果加入对话历史
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": result,
        })

    print(f"\n--- 工具执行完毕，LLM 基于结果生成最终回答 ---\n")

    # 第二轮：把工具结果发回给 LLM，让它基于结果回答
    final_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    print(f"助手: {final_response.choices[0].message.content}")
else:
    print(f"助手（直接回答）: {msg.content}")
