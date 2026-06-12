"""
配置管理：加载 .env 并提供统一的配置入口。
支持 DeepSeek / Anthropic / OpenAI 三种 provider。
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "deepseek")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek-chat")

    # DeepSeek 兼容 OpenAI SDK，只需改 base_url
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    @classmethod
    def get_api_key(cls, provider: str | None = None) -> str:
        """获取指定 provider 的 API Key。"""
        provider = provider or cls.DEFAULT_PROVIDER
        key_map = {
            "deepseek": cls.DEEPSEEK_API_KEY,
            "anthropic": cls.ANTHROPIC_API_KEY,
            "openai": cls.OPENAI_API_KEY,
        }
        return key_map.get(provider, "")

    @classmethod
    def validate(cls) -> list[str]:
        """检查当前 provider 的 API Key 是否已配置。"""
        key = cls.get_api_key()
        if not key or "xxxxx" in key:
            return [cls.DEFAULT_PROVIDER.upper() + "_API_KEY"]
        return []
