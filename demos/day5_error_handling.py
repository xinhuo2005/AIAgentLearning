"""
Day 5 — 错误处理：工具调用失败时如何让 LLM 感知并重试

核心思想：
  - 工具执行失败 ≠ 程序崩溃
  - 把错误信息当作 tool result 返回给 LLM
  - LLM 看到错误后会自动修正参数并重试
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
# 工具函数：有可能会"失败"
# ============================================================

def search_file(filename: str):
    """在项目目录中搜索文件"""
    import glob

    results = glob.glob(f"**/{filename}", recursive=True)
    if not results:
        # 关键：失败不抛异常，而是返回错误描述
        return f"[错误] 未找到文件 '{filename}'。请确认文件名是否正确，或尝试用通配符如 *.py"
    return f"找到 {len(results)} 个文件:\n" + "\n".join(f"  - {r}" for r in results)


def calculator(expression: str):
    """安全计算数学表达式（只允许数字和四则运算）"""
    import re

    # 安全检查：只允许数字、运算符、空格、括号、小数点
    if not re.fullmatch(r"[\d\s+\-*/().]+", expression):
        return (
            f"[错误] 表达式 '{expression}' 包含不允许的字符。"
            "我只支持加减乘除和括号，例如: (10 + 5) * 3"
        )

    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return f"[错误] 除以零是不允许的"
    except SyntaxError as e:
        return f"[错误] 语法错误: {e}。请用正确的数学格式，如 '3 + 4 * 2'"
    except Exception as e:
        return f"[错误] 计算出错: {e}"


# ============================================================
# 工具注册
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_file",
            "description": "在项目目录中搜索文件，支持通配符如 *.py",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名或通配符模式"}
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "安全计算数学表达式，只支持加减乘除和括号",
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

tool_map = {
    "search_file": search_file,
    "calculator": calculator,
}

MAX_TURNS = 5  # 最多 5 轮工具调用，防止无限循环


# ============================================================
# 核心：带错误处理的多轮 Agent 循环
# ============================================================

def agent_loop(user_input: str):
    messages = [{"role": "user", "content": user_input}]

    for turn in range(1, MAX_TURNS + 1):
        print(f"\n{'='*60}")
        print(f"第 {turn} 轮 LLM 调用")
        print(f"{'='*60}")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
        )
        msg = response.choices[0].message

        # 如果不需要调工具，直接返回答案
        if not msg.tool_calls:
            print(f"\n✅ 最终回答:\n{msg.content}")
            return msg.content

        print(f"LLM 决定调用 {len(msg.tool_calls)} 个工具:")
        messages.append(msg)

        for tc in msg.tool_calls:
            func_name = tc.function.name
            func_args = json.loads(tc.function.arguments)
            print(f"  → {func_name}({func_args})")

            result = tool_map[func_name](**func_args)
            print(f"  ← {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # 超过最大轮次
    print(f"\n⚠️ 已达最大轮次 {MAX_TURNS}，强制终止")
    return None


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    # 测试 1：文件搜索失败 → LLM 自动修正
    print("\n" + "="*60)
    print("测试 1：搜索不存在的文件，LLM 应该自动重试")
    print("="*60)
    agent_loop("帮我找一下 main11.py 文件")

    # 测试 2：计算器安全检查 → LLM 修正表达式
    print("\n\n" + "="*60)
    print("测试 2：输入不安全表达式，LLM 应该修正")
    print("="*60)
    agent_loop("帮我算一下 __import__('os').system('dir') + 100")

    # 测试 3：正常成功的场景（对比）
    print("\n\n" + "="*60)
    print("测试 3：正常查询天气（对比）")
    print("="*60)
    agent_loop("帮我算一下 (100 + 200) * 3")
