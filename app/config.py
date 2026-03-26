from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    chat_model: str = "qwen-plus"
    embed_model: str = "text-embedding-v3"
    rag_persist_dir: str = "./storage/company_faq"
    docs_dir: str = "./data/docs"
    top_k: int = 4


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY 未设置。请先在 .env 或系统环境变量中配置。")

    return Settings(
        api_key=api_key,
        base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        chat_model=os.getenv("CHAT_MODEL", "qwen-plus"),
        embed_model=os.getenv("EMBED_MODEL", "text-embedding-v3"),
        rag_persist_dir=os.getenv("RAG_PERSIST_DIR", "./storage/company_faq"),
        docs_dir=os.getenv("DOCS_DIR", "./data/docs"),
        top_k=int(os.getenv("TOP_K", "4")),
    )


def ensure_dir(path: str | Path) -> Path:
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj
