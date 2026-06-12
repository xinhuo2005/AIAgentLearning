"""
Day 6 — Agent 循环：连续多工具调用直到任务完成

整合 Day 1-5 学到的所有内容：
  - Day 1-2: LLM 基础调用，理解 message 格式
  - Day 3-4: Tool Calling，多工具调用
  - Day 5: 错误处理与重试
  → Day 6: 一个完整的 "ask + tool" 循环

验收标准：
  问"帮我查一下北京天气，然后把温度从摄氏度转成华氏度"
  Agent 先调 get_weather() 获取温度，再调 calculator() 转换温度
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
# 工具定义
# ============================================================

def get_weather(city: str):
    """查询指定城市的天气（模拟调用天气api）"""
    weather_data = {
        "北京": "晴，温度 25°C，湿度 40%，风力 3 级",
        "上海": "多云，温度 28°C，湿度 65%，风力 2 级",
        "深圳": "阵雨，温度 30°C，湿度 80%，风力 4 级",
        "广州": "雷阵雨，温度 32°C，湿度 85%，风力 3 级",
        "杭州": "阴，温度 22°C，湿度 55%，风力 2 级",
    }
    return weather_data.get(city, f"没查到「{city}」的天气数据，请确认城市名是否正确")


def calculator(expression: str):
    """安全计算数学表达式，支持加减乘除、括号、小数"""
    import re

    if not re.fullmatch(r"[\d\s+\-*/().]+", expression):
        return (
            f"[错误] 表达式包含不支持的字符。"
            "我只支持数字、加减乘除、括号和小数点。例如: (25 * 9/5) + 32"
        )

    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "[错误] 除以零是不允许的"
    except SyntaxError as e:
        return f"[错误] 语法错误: {e}"
    except Exception as e:
        return f"[错误] 计算出错: {e}"


# ============================================================
# 工具 Schema（给 LLM 看的"说明书"）
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气，返回温度、湿度、风力等信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，如「北京」「上海」"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式。摄氏转华氏公式: °F = °C × 9/5 + 32",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 25 * 9/5 + 32"}
                },
                "required": ["expression"],
            },
        },
    },
]

tool_map = {
    "get_weather": get_weather,
    "calculator": calculator,
}

# ============================================================
# 系统提示：告诉 LLM 它是什么角色、怎么工作
# ============================================================

SYSTEM_PROMPT = (
    "你是一个有用的助手，可以查询天气和计算数学表达式。"
    "当用户让你完成一个需要多步骤的任务时，"
    "你需要一步一步调用工具，每次根据上一步的结果决定下一步做什么。"
    "完成所有步骤后，用自然语言总结最终结果给用户。"
)

# ============================================================
# Agent 核心循环
# ============================================================

MAX_TURNS = 10  # 防止死循环的安全上限


def agent_loop(user_input: str, verbose: bool = True):
    """
    Agent 主循环：
    1. 把用户输入发给 LLM
    2. LLM 决定是否调用工具
       - 调工具 → 执行 → 结果返回 LLM → 继续循环
       - 不调工具 → 直接返回文本答案，循环结束
    3. 循环直到 LLM 给出最终答案或超过最大轮次
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for turn in range(1, MAX_TURNS + 1):
        if verbose:
            print(f"\n{'─' * 50}")
            print(f"🔄 第 {turn} 轮")
            print(f"{'─' * 50}")

        response = client.chat.completions.create(
            model=Config.DEFAULT_MODEL,
            messages=messages,
            tools=tools,
        )
        msg = response.choices[0].message

        # LLM 不调工具 → 任务完成，返回文本答案
        if not msg.tool_calls:
            if verbose:
                print(f"\n✅ 任务完成:\n{msg.content}")
            return msg.content

        if verbose:
            print(f"🔧 调用 {len(msg.tool_calls)} 个工具:")

        messages.append(msg)

        for tc in msg.tool_calls:
            func_name = tc.function.name
            func_args = json.loads(tc.function.arguments)

            if verbose:
                print(f"  → {func_name}({json.dumps(func_args, ensure_ascii=False)})")

            result = tool_map[func_name](**func_args)

            if verbose:
                print(f"  ← {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    if verbose:
        print(f"\n⚠️ 达到最大轮次 {MAX_TURNS}，强制停止")
    return None


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("验收测试：查北京天气 → 摄氏度转华氏度")
    print("=" * 60)

    agent_loop("帮我查一下北京天气，然后把温度从摄氏度转成华氏度")

    print("\n\n" + "=" * 60)
    print("额外测试：多城市温度对比哪个天气最高")
    print("=" * 60)

    agent_loop("上海比北京的气温高还是低，差多少？")
