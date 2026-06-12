"""
ai-dev-team — Multi-Agent Dev Team with Persistent Learning Memory

入口文件（开发中，目前仅验证环境配置）。
"""
from src.config import Config


def main():
    missing = Config.validate()
    if missing:
        print(f"[WARN] 以下 API Key 未配置: {', '.join(missing)}")
        print("请编辑 .env 文件填入你的 API Key")
    else:
        print("[OK] 环境配置检查通过")

    print(f"  Provider: {Config.DEFAULT_PROVIDER}")
    print(f"  Model: {Config.DEFAULT_MODEL}")


if __name__ == "__main__":
    main()
