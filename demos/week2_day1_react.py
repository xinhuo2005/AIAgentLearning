"""
Week 2 Day 1 — ReAct Loop（Reasoning + Acting）

与 Week 1 function calling 的区别：
  - 不用 API 原生的 tools 参数
  - 用 system prompt 约束 LLM 按固定文本格式输出
  - 代码解析文本中的 Action/Action Input，手动执行工具
  - Thought 让每一步推理过程可见

ReAct 格式：
  Thought: 当前需要做什么，为什么
  Action: 工具名
  Action Input: {"param": "value"}
  Observation: 工具执行结果（由代码填入）
  ...重复直到...
  Thought: 信息足够了
  Final Answer: 最终回答
"""

import sys
sys.path.insert(0, ".")  # noqa

import json
import re
from openai import OpenAI
from src.config import Config

client = OpenAI(
    api_key=Config.DEEPSEEK_API_KEY,
    base_url=Config.DEEPSEEK_BASE_URL,
)

# ============================================================
# 工具函数（和 Week 1 一样）
# ============================================================

def get_weather(city: str):
    """查询指定城市的天气"""
    weather_data = {
        "北京": "晴，温度 25°C，湿度 40%，风力 3 级",
        "上海": "多云，温度 28°C，湿度 65%，风力 2 级",
        "深圳": "阵雨，温度 30°C，湿度 80%，风力 4 级",
        "广州": "雷阵雨，温度 32°C，湿度 85%，风力 3 级",
    }
    return weather_data.get(city, f"没查到「{city}」的天气数据")


def calculator(expression: str):
    """安全计算数学表达式。摄氏转华氏公式: °F = °C × 9/5 + 32"""
    try:
        import re as _re
        if not _re.fullmatch(r"[\d\s+\-*/().]+", expression):
            return f"[错误] 表达式包含不支持的字符"
        return str(eval(expression))
    except Exception as e:
        return f"[错误] {e}"


tool_map = {
    "get_weather": get_weather,
    "calculator": calculator,
}

# ============================================================
# System Prompt — ReAct 的核心
# ============================================================

REACT_PROMPT = """你是一个能使用工具的助手。你需要严格按以下格式回复：

问题：每次回复只能包含一段 Thought + 一个 Action + Action Input，或一个 Final Answer。

当你需要调用工具时：
Thought: 对当前情况的推理，为什么需要这个工具
Action: 工具名称
Action Input: 工具参数的 JSON

当工具执行完成后，会给你 Observation。请根据 Observation 决定下一步。

当你获得所有需要的信息后：
Thought: 我已经获得了所有需要的信息
Final Answer: 用自然语言完整回答用户的问题

可用工具：
- get_weather: 查询城市天气，参数 {"city": "城市名"}
- calculator: 计算数学表达式，参数 {"expression": "数学表达式"}

重要：
- Action Input 必须写在一行内
- 一次只能执行一个 Action
- 不要编造 Observation，等待系统返回
- 摄氏转华氏公式: °F = °C × 9/5 + 32"""


# ============================================================
# ReAct 循环
# ============================================================

MAX_TURNS = 10


def react_loop(user_input: str):
    """
    ReAct 主循环：

    1. 用户提问 → 拼入 prompt，要求 LLM 按 Thought/Action 格式输出
    2. 解析 LLM 的文本输出，提取 Action 和 Action Input
    3. 执行工具，把结果作为 Observation 追加
    4. 把 Observation 加回对话，让 LLM 继续
    5. 直到 LLM 输出 Final Answer
    """
    messages = [
        {"role": "system", "content": REACT_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for turn in range(1, MAX_TURNS + 1):
        print(f"\n{'─' * 60}")
        print(f"第 {turn} 轮")
        print(f"{'─' * 60}")

        response = client.chat.completions.create(
            model=Config.DEFAULT_MODEL,
            messages=messages,
        )
        raw = response.choices[0].message.content
        print(f"\nLLM 输出:\n{raw}")

        # 把 LLM 的回复加入对话历史
        messages.append({"role": "assistant", "content": raw})

        # ---- 解析输出 ----

        # 如果 LLM 给出了 Final Answer，结束循环
        if "Final Answer:" in raw:
            # 提取 Final Answer 后的内容
            answer = raw.split("Final Answer:", 1)[1].strip()
            print(f"\n{'=' * 60}")
            print(f"✅ 最终答案:\n{answer}")
            print(f"{'=' * 60}")
            return answer

        # 提取 Action
        action_match = re.search(r"Action:\s*(.+)", raw)
        input_match = re.search(r"Action Input:\s*(.+)", raw)

        if not action_match or not input_match:
            print("⚠️ LLM 输出格式错误，提示它修正")
            messages.append({
                "role": "user",
                "content": "格式错误。请按 Thought/Action/Action Input 格式输出，或给出 Final Answer。"
            })
            continue

        action = action_match.group(1).strip()
        action_input_str = input_match.group(1).strip()

        # 解析参数 JSON
        try:
            args = json.loads(action_input_str)
        except json.JSONDecodeError:
            observation = f"[错误] Action Input 不是合法的 JSON: {action_input_str}"
            messages.append({"role": "user", "content": f"Observation: {observation}"})
            continue

        # 执行工具
        func = tool_map.get(action)
        if not func:
            observation = f"[错误] 未知工具 '{action}'，可用工具: {list(tool_map.keys())}"
        else:
            print(f"\n🔧 执行: {action}({args})")
            observation = func(**args)
            print(f"📋 Observation: {observation}")

        # 把 Observation 追加到对话
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    print(f"\n⚠️ 达到最大轮次 {MAX_TURNS}")
    return None


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    test1 = ['ReAct测试1，查天气然后进行转换', '帮我查一下北京天气，然后把温度从摄氏度转成华氏度']
    test2 = ['ReAct测试2，多城市天气对比', '上海比北京的气温哪个更适合旅游？']

    print("=" * 60)
    # print(test1[0])
    print(test2[0])
    print("=" * 60)
    react_loop(test2[1])

